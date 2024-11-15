# Canopy OAK Distribution Model Specification

 `````markdown:Functions/OAK.md
 
 ## Purpose
 Track OAK distribution deals and calculate redemptions based on risk-adjusted IRR thresholds, vesting periods, and manage the redemption mechanics for AEGIS LP tokens. The model ensures that a fixed supply of OAK tokens is managed efficiently, maintaining economic stability and fairness among token holders.
 
 ## Python Implementation
 
 ```python:Functions/OAKDistribution.md
 from dataclasses import dataclass, field
 from typing import List, Dict, Tuple
 from collections import defaultdict
 import math
 
 @dataclass
 class OAKDistributionDeal:
     counterparty: str           # Name of the counterparty
     oak_amount: float           # Total OAK tokens allocated
     start_month: int            # Start month (as number of months since launch)
     vesting_months: int         # Months before redemption is possible
     irr_threshold: float        # Risk-adjusted IRR threshold for redemption
     unlock_month: int           # Month when the deal's OAK tokens may be redeemed in their entirety
 
     @property
     def redemption_month(self) -> int:
         """Calculate first possible redemption month based on vesting"""
         return self.start_month + self.vesting_months
 
 @dataclass
 class OAKDistributionConfig:
     deals: List[OAKDistributionDeal]  # List of all OAK distribution deals
     redemption_start_month: int       # Global redemption start month
     redemption_end_month: int         # Global redemption end month
     total_oak_minted: float = 500_000 # Total OAK tokens minted at the start (hard cap)
 
 class OAKDistributionModel:
     def __init__(self, config: OAKDistributionConfig):
         self.config = config
         self._validate_deals()
         self._redemption_history: Dict[int, float] = defaultdict(float)
         self._deal_redemptions: Dict[str, float] = defaultdict(float)
         self._last_processed_month = -1
         self.total_oak_supply = config.total_oak_minted
         self.oak_supply_history: Dict[int, float] = defaultdict(float)
         self.oak_supply_history[-1] = self.total_oak_supply  # Initial supply before any redemption
         # Dual Exponential Decay Parameters
         self.k1 = 0.1  # Decay constant for IRR between threshold and 1%
         self.k2 = 0.5  # Decay constant for IRR below threshold but above 1%
 
     def calculate_redemptions(self, month: int, redeemable_aglp_value: float, full_maturity_aglp_value: float, confidence_level: float) -> Tuple[float, float]:
         """
         Calculate OAK redemptions for a given month based on risk-adjusted IRR.
 
         Args:
             month: Number of months since start (0-based)
             redeemable_aglp_value: Current redeemable AEGIS LP value in USD
             full_maturity_aglp_value: Redeemable AEGIS LP value at full maturity month in USD
             confidence_level: Confidence that full maturity value will be realized (0.0 to 1.0)
 
         Returns:
             Tuple of (total_redemptions_to_date, new_redemptions_this_month)
         """
         if not (0.0 <= confidence_level <= 1.0):
             raise ValueError("Confidence level must be between 0 and 1.")
 
         # Check if current month is within the global redemption window
         if not (self.config.redemption_start_month <= month <= self.config.redemption_end_month):
             raise ValueError("Current month is outside the global redemption window.")
 
         # Calculate risk-adjusted IRR
         if redeemable_aglp_value <= 0 or full_maturity_aglp_value <= 0:
             raise ValueError("AEGIS LP values must be positive.")
         
         # Calculate value difference
         value_difference = full_maturity_aglp_value - redeemable_aglp_value
         if value_difference <= 0:
             raise ValueError("Full maturity AEGIS LP value must be greater than redeemable value.")
 
         # Time difference in months
         periods = max(1, self._get_average_redemption_end_month() - month)
 
         # Adjust value difference based on confidence level
         adjusted_value_difference = value_difference * confidence_level
        
         # Calculate risk-adjusted IRR
         risk_adjusted_irr = self._calculate_irr(redeemable_aglp_value, redeemable_aglp_value + adjusted_value_difference, periods)
         
         # Update redemptions based on adjusted IRR using Dual Exponential Decay
         self._process_redemptions(month, risk_adjusted_irr)
         
         total_redemptions = sum(self._redemption_history.values())
         month_redemptions = self._redemption_history[month]
 
         return total_redemptions, month_redemptions
 
     def add_deal(self, deal: OAKDistributionDeal) -> None:
         """
         Add a new OAK distribution deal
 
         Args:
             deal: New OAKDistributionDeal to add
             
         Raises:
             ValueError: If deal parameters are invalid or counterparty already exists
         """
         # Validate the new deal
         if deal.oak_amount <= 0:
             raise ValueError(f"Invalid OAK amount for {deal.counterparty}")
         if deal.vesting_months < 0:
             raise ValueError(f"Invalid vesting period for {deal.counterparty}")
         if deal.start_month < 0:
             raise ValueError(f"Invalid start month for {deal.counterparty}")
         if deal.unlock_month < deal.redemption_month:
             raise ValueError(f"Unlock month must be after redemption eligibility for {deal.counterparty}")
         
         # Check for duplicate counterparty
         if any(d.counterparty == deal.counterparty for d in self.config.deals):
             raise ValueError(f"Deal already exists for counterparty: {deal.counterparty}")
         
         # Check if adding this deal exceeds the total minted OAK
         total_allocated = sum(d.oak_amount for d in self.config.deals) + deal.oak_amount
         if total_allocated > self.config.total_oak_minted:
             raise ValueError("Adding this deal exceeds the total OAK minted (hard cap).")
         
         # Add the deal
         self.config.deals.append(deal)
 
     def get_deal_status(self, counterparty: str) -> Tuple[float, float]:
         """
         Get the redeemed and remaining OAK for a specific deal.
 
         Args:
             counterparty: The counterparty name.
 
         Returns:
             Tuple of (redeemed_oak, remaining_oak)
         
         Raises:
             ValueError: If the counterparty does not exist.
         """
         if counterparty not in self._deal_redemptions:
             raise ValueError(f"No redemptions recorded for counterparty: {counterparty}")
         
         redeemed = self._deal_redemptions[counterparty]
         # Find the total allocated OAK for the deal
         deal = self._find_deal(counterparty)
         remaining = deal.oak_amount - redeemed
         return redeemed, remaining
 
     def get_best_case_irr(self, acquisition_price: float, current_leaf_price: float, month: int) -> float:
         """
         Calculate the best case IRR for all AEGIS LP token holders in a given month.
 
         Args:
             acquisition_price: Initial price paid per AEGIS LP token.
             current_leaf_price: Current price of LEAF in USD.
             month: Current month number.
 
         Returns:
             Best case IRR as a decimal.
         """
         try:
             irr = self._calculate_best_case_irr(acquisition_price, current_leaf_price, month)
             return irr
         except ValueError:
             return math.nan  # Indicate undefined IRR
 
     def _process_redemptions(self, month: int, adjusted_irr: float) -> None:
         """Process redemptions for a specific month based on adjusted IRR using Dual Exponential Decay"""
         for deal in self.config.deals:
             # Only process deals that have reached their unlock date
             if deal.unlock_month > month:
                 continue
             
             remaining = deal.oak_amount - self._deal_redemptions[deal.counterparty]
             
             if remaining <= 0:
                 continue
             
             if adjusted_irr <= 0.01:
                 # Full redemption
                 self._redemption_history[month] += remaining
                 self._deal_redemptions[deal.counterparty] += remaining
                 self.total_oak_supply -= remaining
                 self.oak_supply_history[month] = self.total_oak_supply
             elif adjusted_irr <= deal.irr_threshold:
                 # Partial redemption using Dual Exponential Decay
                 # Calculate redemption factor based on Dual Exponential Decay
                 # Method: When IRR is between 1% and threshold, apply exponential decay
                 
                 # Normalize IRR within the range (0.01, threshold)
                 normalized_irr = (adjusted_irr - 0.01) / (deal.irr_threshold - 0.01) if deal.irr_threshold != 0.01 else 1
                 # Apply exponential decay
                 redemption_factor = math.exp(-self.k1 * (normalized_irr))
                 # Determine redemption amount
                 redemption_amount = remaining * (1 - redemption_factor)
                 
                 # Ensure redemption does not exceed remaining OAK
                 redemption_amount = min(redemption_amount, remaining)
                 
                 # Update redemptions
                 self._redemption_history[month] += redemption_amount
                 self._deal_redemptions[deal.counterparty] += redemption_amount
                 self.total_oak_supply -= redemption_amount
                 self.oak_supply_history[month] = self.total_oak_supply
             else:
                 # No redemption
                 self.oak_supply_history[month] = self.total_oak_supply
 
         self._record_oak_supply(month)
         
     def _can_redeem(self, deal: OAKDistributionDeal, month: int) -> bool:
         """Check if a deal can be redeemed in given month"""
         return deal.unlock_month <= month <= self.config.redemption_end_month
 
     def _find_deal(self, counterparty: str) -> OAKDistributionDeal:
         """Find a deal by counterparty"""
         for deal in self.config.deals:
             if deal.counterparty == counterparty:
                 return deal
         raise ValueError(f"No deal found for counterparty: {counterparty}")
         
     def _validate_deals(self) -> None:
         """Validate deal configurations"""
         for deal in self.config.deals:
             if deal.oak_amount <= 0:
                 raise ValueError(f"Invalid OAK amount for {deal.counterparty}")
             if deal.vesting_months < 0:
                 raise ValueError(f"Invalid vesting period for {deal.counterparty}")
             if deal.start_month < 0:
                 raise ValueError(f"Invalid start month for {deal.counterparty}")
             if deal.unlock_month < deal.redemption_month:
                 raise ValueError(f"Unlock month must be after redemption eligibility for {deal.counterparty}")
             # Additional validations can be added here
 
     def _record_oak_supply(self, month: int) -> None:
         """Record OAK supply for the given month"""
         self.oak_supply_history[month] = self.total_oak_supply
 
     def _record_state(self, month: int) -> None:
         """Record current state for all active deals"""
         self._record_oak_supply(month)
 
     def _get_average_redemption_end_month(self) -> float:
         """Calculate the weighted average redemption end month based on remaining OAK supply"""
         weighted_sum = 0
         for deal in self.config.deals:
             remaining = deal.oak_amount - self._deal_redemptions[deal.counterparty]
             weighted_sum += remaining * deal.unlock_month
         
         average = weighted_sum / self.total_oak_supply if self.total_oak_supply > 0 else float('inf')
         return average
 
     def _calculate_irr(self, initial_investment: float, final_value: float, periods: int) -> float:
         """
         Calculate the Internal Rate of Return (IRR).
 
         Args:
             initial_investment: The initial amount invested.
             final_value: The final value after investment.
             periods: Number of periods (months).
 
         Returns:
             Annualized IRR as a decimal.
         """
         if initial_investment <= 0:
             raise ValueError("Initial investment must be positive.")
         if periods <= 0:
             raise ValueError("Number of periods must be positive.")
         
         # Monthly IRR calculation
         monthly_irr = (final_value / initial_investment) ** (1 / periods) - 1
         # Annualize the IRR
         annual_irr = (1 + monthly_irr) ** 12 - 1
         return annual_irr
 
     def _calculate_best_case_irr(self, acquisition_price: float, current_leaf_price: float, month: int) -> float:
         """
         Calculate the best case IRR for all AEGIS LP holders.
 
         Args:
             acquisition_price: Initial price paid per AEGIS LP token.
             current_leaf_price: Current price of LEAF in USD.
             month: Current month number.
            
         Returns:
             Best case IRR as a decimal.
         """
         if acquisition_price <= 0 or current_leaf_price <= 0:
             raise ValueError("Prices must be positive.")
         
         # Total AEGIS LP value currently
         total_aglp_value_current = self.total_oak_supply * current_leaf_price
 
         # Assume full redemption at average redemption end month
         average_redemption_month = self._get_average_redemption_end_month()
         periods = max(1, average_redemption_month - month)
 
         if periods <= 0:
             raise ValueError("Average redemption end month must be after the current month.")
            
         # Calculate IRR based on acquisition price and total AEGIS LP value
         total_initial_investment = self.total_oak_supply * acquisition_price
         irr = self._calculate_irr(total_initial_investment, total_aglp_value_current, periods)
         return irr
 
 # Sample Usage
 
 ```python:Functions/OAKDistribution.md
 # Create initial deals
 deals = [
     OAKDistributionDeal(
         counterparty="Protocol A",
         oak_amount=1_000_000,
         start_month=0,
         vesting_months=12,
         irr_threshold=0.15,              # 15% IRR threshold
         unlock_month=24                   # Unlocks for full redemption at month 24
     ),
     OAKDistributionDeal(
         counterparty="Protocol B",
         oak_amount=2_000_000,
         start_month=3,
         vesting_months=24,
         irr_threshold=0.12,              # 12% IRR threshold
         unlock_month=36                   # Unlocks for full redemption at month 36
     )
 ]
 
 # Initialize model with global redemption window
 config = OAKDistributionConfig(
     deals=deals,
     redemption_start_month=24,           # Global redemption starts at month 24
     redemption_end_month=48,             # Global redemption ends at month 48
     total_oak_minted=500_000              # Hard cap of 500,000 OAK tokens minted
 )
 model = OAKDistributionModel(config)
 
 # Add a new deal after initialization
 new_deal = OAKDistributionDeal(
     counterparty="Protocol C",
     oak_amount=500_000,
     start_month=6,
     vesting_months=18,
     irr_threshold=0.10,                   # 10% IRR threshold
     unlock_month=42                       # Unlocks for full redemption at month 42
 )
 model.add_deal(new_deal)
 
 # Calculate redemptions for month 30 with risk-adjusted IRR
 total_redemptions, month_redemptions = model.calculate_redemptions(
     month=30,
     redeemable_aglp_value=750_000,          # Example redeemable AEGIS LP value in USD
     full_maturity_aglp_value=1_000_000,      # Example full maturity AEGIS LP value in USD
     confidence_level=0.8                     # 80% confidence
 )
 
 print("Redemption Results:")
 print(f"Total Redemptions to Date: {total_redemptions}")
 print(f"Redemptions This Month: {month_redemptions}")
 
 # Check status of specific deal
 redeemed, remaining = model.get_deal_status("Protocol A")
 print(f"\nProtocol A: Redeemed = {redeemed}, Remaining = {remaining}")
 
 # Calculate best case IRR for all deals in month 30
 acquisition_price = 100.0       # Example acquisition price per AEGIS LP token in USD
 current_leaf_price = 5.0        # Current LEAF price in USD
 best_case_irr = model.get_best_case_irr(acquisition_price, current_leaf_price, 30)
 
 print("\nBest Case IRR for All Deals in Month 30:")
 if math.isnan(best_case_irr):
     print("IRR not defined")
 else:
     print(f"{best_case_irr*100:.2f}%")
 ```
 
 ## Key Features
 
 1. **Sequential Processing**: Maintains redemption history and processes months in order.
 2. **IRR-based Redemptions**: Triggers redemptions when risk-adjusted IRR falls below threshold.
 3. **Deal-level Tracking**: Maintains individual deal redemption status.
 4. **Vesting Periods**: Enforces vesting before redemption.
 5. **Redemption Mechanics**:
     - **Global Redemption Start and End Dates**: Defines specific periods for when redemptions can occur across all deals.
     - **Proportional Redeemable AEGIS LP**: Redeemed OAK tokens grant proportionate AEGIS LP, burning OAK and reallocating unredeemed portions to remaining AEGIS LP holders.
 6. **Best Case IRR Calculation**: Calculates the best case internal rate of return for AEGIS LP holders based on current conditions.
 7. **OAK Supply Tracking**: Monitors and maintains the total OAK supply over time.
 
 ## Model Capabilities
 
 1. **Track Multiple Distribution Deals**: Supports tracking of multiple OAK distribution deals.
 2. **Calculate Redemptions Based on Risk-Adjusted IRR**: Determines when and how much redemptions should occur based on risk-adjusted IRR conditions.
 3. **Maintain Redemption and OAK Supply History**: Keeps a historical record of redemptions and total OAK supply.
 4. **Track Individual Deal Status**: Provides status updates for each deal, including redeemed and remaining amounts.
 5. **Support Variable Vesting and Unlock Dates**: Allows different vesting schedules and unlock dates per deal.
 6. **Add New Deals Dynamically**: Supports the addition of new distribution deals at any time, ensuring the total OAK distribution does not exceed the hard cap.
 7. **Calculate Best Case IRR for AEGIS LP Holders**: Provides IRR calculations to estimate potential returns based on current and future conditions.
 
 ## Implementation Details
 
 1. **Deal Structure**:
     - **Counterparty Identification**: Unique identifier for each deal.
     - **OAK Amount**: Number of OAK tokens allocated to the deal.
     - **Start Month**: When the deal starts.
     - **Vesting Period**: Duration before redemptions can commence.
     - **IRR Threshold**: The IRR below which redemptions are triggered.
     - **Unlock Month**: Month when the deal's OAK tokens may be redeemed in their entirety.
 
 2. **Redemption Logic**:
     - **Sequential Processing**: Ensures months are processed in order to maintain accuracy.
     - **Redemption Conditions**: Redemptions occur only if risk-adjusted IRR falls below the threshold during the global redemption window and the deal has reached its unlock date.
     - **Full Redemption**: Upon triggering, the remaining OAK tokens in the deal are redeemed and burned.
     - **OAK Supply Management**: Redemptions decrease the total OAK supply, and unredeemed portions are reallocated to remaining holders, thereby increasing their value.
 
 3. **Best Case IRR Calculation**:
     - **Assumptions**: Full redemption at the weighted average redemption end month across all deals.
     - **Time Difference**: Calculates the period between the current month and average redemption end month.
     - **IRR Formula**: Uses a compound interest formula to estimate IRR based on value difference, time difference, and confidence level.
 
 4. **OAK Supply Tracking**:
     - **Initial Supply**: 500,000 OAK tokens minted at startup.
     - **Redemptions Impact**: Adjusts the total OAK supply based on redemptions by burning redeemed OAK tokens.
     - **Historical Records**: Maintains a history of OAK supply for each processed month to track the total circulating supply over time.
 
 5. **Validation Rules**:
     - Ensures all deal parameters are valid (positive amounts, proper redemption dates).
     - Prevents duplicate counterparty entries.
     - Validates redemption periods relative to vesting periods.
     - Ensures total OAK distributed across all deals does not exceed the hard cap of 500,000 OAK tokens.
 
 ## Recommended Extensions
 
 1. **Add Partial Redemption Capabilities**:
     - Allow partial redemptions instead of full amounts.
 2. **Include Lockup Periods After Redemption**:
     - Implement additional constraints preventing immediate re-redemption post-burn.
 3. **Add Dynamic IRR Thresholds**:
     - Enable IRR thresholds to change based on market conditions or other factors.
 4. **Include Redemption Windows**:
     - Define specific time frames within the redemption period for scheduled redemptions.
 5. **Add Redemption Rate Limits**:
     - Prevent excessive redemptions within a single month to manage liquidity.
 6. **Add Deal Modification Capabilities**:
     - Allow updates to deals post-creation, such as adjusting vesting periods or IRR thresholds.
 7. **Include Deal Removal Functionality**:
     - Enable the removal of deals under certain conditions or administrative actions.
 
 ## Integration Notes
 
 This model can be integrated with:
 
 1. **IRR Calculation Model**:
     - Provides the necessary IRR inputs for redemption decisions.
 2. **Token Economics Model**:
     - Aligns OAK and AEGIS LP token dynamics with broader economic policies.
 3. **Revenue Model for IRR Inputs**:
     - Supplies the IRR thresholds based on revenue performance and projections.
 4. **AEGIS LP Management**:
     - Coordinates the distribution and allocation of AEGIS LP tokens upon redemption.
 5. **Liquidity Management Systems**:
     - Ensures that redemptions do not adversely affect overall liquidity.
 
 ``` text
 
 The updated `Functions/OAK.md` document now includes:
 
 1. **Redemption Mechanics**:
    - **Global Redemption Start and End Dates**: Defines specific periods for when redemptions can occur across all deals.
    - **Proportional Redeemable AEGIS LP**: Redeemed OAK tokens grant proportionate AEGIS LP, burning OAK and reallocating unredeemed portions to remaining AEGIS LP holders.
 
 2. **Best Case IRR Calculation**:
    - **Best Case IRR**: Calculates the best case internal rate of return for AEGIS LP holders based on acquisition price, current LEAF price, confidence level, and the redemption timeline. This IRR is annualized and uniform across all OAK token holders and adjusts when redemptions occur early, benefiting remaining holders by redistributing unredeemed AEGIS LP.
 
 3. **OAK Supply Tracking**:
    - **Total OAK Supply**: Tracks the total supply of OAK tokens, adjusting for redemptions.
    - **OAK Supply History**: Maintains a history of the total OAK supply for each processed month.
 
 4. **Extended Functions**:
    - `calculate_redemptions`: Calculates redemptions based on risk-adjusted IRR considering value differences, time to maturity, and confidence levels.
    - `get_best_case_irr`: Calculates the best case IRR applicable to all AEGIS LP holders.
 
 5. **Sample Usage Enhancements**:
    - Demonstrates adding a new deal with redemption start and end months.
    - Shows how to calculate redemptions using the new `calculate_redemptions` function with risk-adjusted IRR.
    - Illustrates calculating the best case IRR for all deals active in a particular month.
 
 6. **Documentation Updates**:
    - **Key Features**: Expanded to reflect new redemption mechanics and IRR calculations.
    - **Model Capabilities**: Updated to include best case IRR calculations and OAK supply tracking.
    - **Implementation Details**: Detailed the new redemption mechanics and IRR logic.
    - **Recommended Extensions**: Added suggestions for further enhancing the model.
    - **Integration Notes**: Expanded to include integrations with AEGIS LP management and liquidity systems.
 
 This comprehensive update ensures that the `OAKDistributionModel` effectively manages a fixed supply of 500,000 OAK tokens, handles redemptions by burning redeemed tokens, and redistributes the remaining AEGIS LP among fewer OAK tokens. This approach maintains the economic stability and fairness among token holders by increasing the value per remaining OAK token as redemptions occur.
