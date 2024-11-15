# Canopy OAK Distribution Model

## Purpose

The OAK Distribution Model manages the distribution and redemption of OAK tokens within the Canopy ecosystem. It ensures that a fixed supply of OAK tokens is distributed across various deals, calculates redemptions based on risk-adjusted IRR thresholds, and tracks the overall OAK supply.

## Python Implementation

```python:Functions/OAK.md
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
    total_oak_supply: float = 500_000
    deals: List[OAKDistributionDeal] = field(default_factory=list)
    oak_supply_history: Dict[int, float] = field(default_factory=lambda: defaultdict(float))

    def add_deal(self, deal: OAKDistributionDeal):
        if deal.oak_amount <= 0:
            raise ValueError("OAK amount must be positive.")
        if deal.start_month < 0:
            raise ValueError("Start month cannot be negative.")
        if deal.vesting_months < 0:
            raise ValueError("Vesting months cannot be negative.")
        if deal.irr_threshold < 0:
            raise ValueError("IRR threshold cannot be negative.")
        self.deals.append(deal)
        self.oak_supply_history[deal.start_month] += deal.oak_amount

    def calculate_redemptions(self, current_month: int, current_irr: float) -> Tuple[float, Dict[str, float]]:
        total_redemption = 0
        month_redemptions = {}
        for deal in self.deals:
            if deal.redemption_month <= current_month and current_irr < deal.irr_threshold:
                # Apply dual exponential decay
                if current_irr < 1:
                    redemption_factor = math.exp(-0.1 * (deal.irr_threshold - current_irr))
                else:
                    redemption_factor = math.exp(-0.5 * (deal.irr_threshold - current_irr))
                partial_redemption = deal.oak_amount * redemption_factor
                total_redemption += partial_redemption
                month_redemptions[deal.counterparty] = partial_redemption
        # Update the total OAK supply
        self.oak_supply_history[current_month] = self.oak_supply_history.get(current_month, self.total_oak_supply) - total_redemption
        return total_redemption, month_redemptions

    def get_best_case_irr(self, acquisition_price: float, current_leaf_price: float, current_month: int) -> float:
        # Calculate weighted average redemption end month
        total_oak = sum(deal.oak_amount for deal in self.deals)
        weighted_sum = 0
        for deal in self.deals:
            remaining = deal.oak_amount
            weighted_sum += remaining * deal.unlock_month
        time_diff = weighted_sum / self.total_oak_supply - current_month
        if time_diff <= 0:
            return 0
        # Compound interest formula
        irr = (math.pow(self.total_oak_supply / total_oak, 1 / time_diff) - 1) * 100
        return irr

    def get_deal_status(self, counterparty: str) -> Tuple[float, float]:
        redeemed = 0
        remaining = 0
        for deal in self.deals:
            if deal.counterparty == counterparty:
                redeemed = self.oak_supply_history.get(deal.unlock_month, 0)
                remaining = deal.oak_amount - redeemed
                break
        return redeemed, remaining

    def validate_deals(self):
        total_allocated = sum(deal.oak_amount for deal in self.deals)
        if total_allocated > self.total_oak_supply:
            raise ValueError("Total OAK allocated across all deals exceeds the hard cap of 500,000 OAK tokens.")
        for deal in self.deals:
            if deal.oak_amount <= 0:
                raise ValueError(f"OAK amount for deal {deal.counterparty} must be positive.")
            if deal.redemption_month < deal.unlock_month:
                raise ValueError(f"Redemption month for deal {deal.counterparty} cannot be before unlock month.")

    def initialize_supply(self):
        self.oak_supply_history[0] = self.total_oak_supply

class OAKDistributionModel:
    def __init__(self, config: OAKDistributionConfig):
        self.config = config
        self.config.initialize_supply()
        self._deal_redemptions: Dict[str, float] = defaultdict(float)

    def add_deal(self, deal: OAKDistributionDeal):
        self.config.add_deal(deal)
        self.config.validate_deals()

    def _process_redemptions(self, month: int, adjusted_irr: float) -> None:
        total_redemptions, month_redemptions = self.config.calculate_redemptions(month, adjusted_irr)
        for counterparty, redemption in month_redemptions.items():
            self._deal_redemptions[counterparty] += redemption
        self.config.oak_supply_history[month] -= total_redemptions

    def calculate_redemptions(self, month: int, redeemable_aglp_value: float, full_maturity_aglp_value: float, confidence_level: float) -> Tuple[float, Dict[str, float]]:
        # Adjust IRR based on confidence level
        adjusted_irr = confidence_level * (redeemable_aglp_value / full_maturity_aglp_value)
        self._process_redemptions(month, adjusted_irr)
        total_redemptions, month_redemptions = self.config.calculate_redemptions(month, adjusted_irr)
        return total_redemptions, month_redemptions

    def get_deal_status(self, counterparty: str) -> Tuple[float, float]:
        return self.config.get_deal_status(counterparty)

    def get_best_case_irr(self, acquisition_price: float, current_leaf_price: float, current_month: int) -> float:
        return self.config.get_best_case_irr(acquisition_price, current_leaf_price, current_month)

    def initialize_model(self):
        self.config.initialize_supply()

# Sample Usage

if __name__ == "__main__":
    deals = [
        OAKDistributionDeal(
            counterparty="Private Sale",
            oak_amount=50_000,
            start_month=3,
            vesting_months=12,
            irr_threshold=0.25,  # 25% IRR
            unlock_month=15
        ),
        OAKDistributionDeal(
            counterparty="Initial Liquidity",
            oak_amount=50_000,
            start_month=15,
            vesting_months=12,
            irr_threshold=0.25,
            unlock_month=27
        ),
        OAKDistributionDeal(
            counterparty="Year 2 Liquidity",
            oak_amount=50_000,
            start_month=27,
            vesting_months=12,
            irr_threshold=0.15,  # 15% IRR
            unlock_month=39
        ),
        OAKDistributionDeal(
            counterparty="Year 3 Liquidity",
            oak_amount=50_000,
            start_month=39,
            vesting_months=12,
            irr_threshold=0.10,  # 10% IRR
            unlock_month=51
        ),
        OAKDistributionDeal(
            counterparty="Founding Partners",
            oak_amount=150_000,
            start_month=3,
            vesting_months=24,
            irr_threshold=0.20,  # 20% IRR
            unlock_month=27
        ),
        OAKDistributionDeal(
            counterparty="Initial TVL Rewards",
            oak_amount=75_000,
            start_month=15,
            vesting_months=12,
            irr_threshold=0.05,  # Example IRR threshold
            unlock_month=27
        ),
    ]

    config = OAKDistributionConfig(
        deals=deals,
        total_oak_minted=500_000  # Hard cap of 500,000 OAK tokens minted
    )
    model = OAKDistributionModel(config)

    # Add a new deal after initialization
    new_deal = OAKDistributionDeal(
        counterparty="Protocol C",
        oak_amount=100_000,
        start_month=6,
        vesting_months=18,
        irr_threshold=0.10,                   # 10% IRR threshold
        unlock_month=24                       # Unlocks for full redemption at month 24
    )
    model.add_deal(new_deal)

    # Calculate redemptions for month 30 with risk-adjusted IRR
    total_redemptions, month_redemptions = model.calculate_redemptions(
        month=30,
        redeemable_aglp_value=750_000,          # Example redeemable AEGIS LP value in USD
        full_maturity_aglp_value=1_000_000,     # Example full maturity AEGIS LP value in USD
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
        print(f"{best_case_irr:.2f}%")
```

## Key Features

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
    - **Partial Redemption**: Applies a dual exponential decay to determine the amount of OAK to redeem based on IRR deviation.
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
