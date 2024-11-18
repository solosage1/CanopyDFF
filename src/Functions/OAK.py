import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict
import math

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

@dataclass
class OAKDistributionDeal:
    """Configuration for individual OAK distribution deals."""
    counterparty: str           # Name of the counterparty
    oak_amount: float          # Total OAK tokens allocated
    start_month: int           # Start month (as number of months since launch)
    vesting_months: int        # Months before redemption is possible
    irr_threshold: float       # Risk-adjusted IRR threshold for redemption
    unlock_month: int          # Month when the deal's OAK tokens may be redeemed in their entirety

    @property
    def redemption_month(self) -> int:
        """Calculate first possible redemption month based on vesting."""
        return self.start_month + self.vesting_months

@dataclass
class OAKDistributionConfig:
    """Configuration for OAK distribution model."""
    total_oak_supply: float = 500_000
    redemption_start_month: int = 12  # Global start month for any redemptions
    redemption_end_month: int = 48    # After this, max redemption for unlocked tokens
    deals: List[OAKDistributionDeal] = field(default_factory=list)

class OAKModel:
    """Model for simulating OAK token distribution and redemption."""
    
    def __init__(self, config: OAKDistributionConfig):
        self.config = config
        self.remaining_oak_supply = config.total_oak_supply
        self.oak_supply_history: Dict[int, float] = {}
        self.redemption_history: Dict[int, Dict[str, float]] = {}
        self.month = 0
        self.logger = logging.getLogger(__name__)  # Initialize logger within the class
        self.logger.debug("Initialized OAKModel")

    def calculate_expected_irr(self, current_value: float, future_value: float, years_to_end: float) -> float:
        """
        Calculate the expected IRR based on current and future values over the remaining years.
        
        Args:
            current_value: The present value based on redemption progress.
            future_value: The full value at the end of the redemption period.
            years_to_end: The remaining time in years until redemption end.
        
        Returns:
            Expected annualized IRR as a percentage.
        """
        try:
            expected_irr = ((future_value / current_value) ** (1 / years_to_end) - 1) * 100
            return expected_irr
        except (ValueError, ZeroDivisionError) as e:
            self.logger.error(f"Error calculating IRR: {e}")
            return -float('inf')  # Assign a very low IRR to trigger redemption

    def step(
        self, 
        current_month: int,
        aegis_usdc: float,
        aegis_leaf: float,
        current_leaf_price: float
    ) -> Tuple[float, float, float, float, float]:
        """Process redemptions and update OAK supply for the current month."""
        self.month = current_month
        total_value = aegis_usdc + (aegis_leaf * current_leaf_price)
        self.logger.debug(f"Processing Month {current_month}: Total Value = ${total_value:.2f}")
        
        # Track unredeemed OAK before processing any redemptions
        total_oak_before = sum(deal.oak_amount for deal in self.config.deals)
        self.logger.debug(f"Total OAK before redemption: {total_oak_before}")
        
        # Process redemptions
        total_redemption = 0.0
        month_redemptions = {}
        
        for deal in self.config.deals:
            self.logger.debug(f"Evaluating deal {deal.counterparty}: OAK Amount = {deal.oak_amount}, IRR Threshold = {deal.irr_threshold}%")
            if (current_month >= self.config.redemption_start_month and
                current_month >= deal.redemption_month and
                current_month >= deal.unlock_month and
                deal.oak_amount > 0):  # Ensure deal has remaining OAK
                
                # Calculate redemption progress (0 to 1)
                total_redemption_months = self.config.redemption_end_month - self.config.redemption_start_month
                months_into_redemption = current_month - self.config.redemption_start_month
                redemption_progress = min(1.0, max(0.0, months_into_redemption / total_redemption_months))
                self.logger.debug(f"Redemption progress for {deal.counterparty}: {redemption_progress:.2%}")
                
                # Calculate values based on current OAK supply
                total_oak_remaining = total_oak_before - total_redemption
                if total_oak_remaining > 0:
                    value_per_oak = total_value / total_oak_remaining
                    current_value = value_per_oak * redemption_progress  # Current value based on progress
                    future_value = value_per_oak  # Full value at end
                    self.logger.debug(f"Value per OAK: ${value_per_oak:.6f}, Current Value: ${current_value:.6f}, Future Value: ${future_value:.6f}")
                    
                    # Calculate time remaining
                    months_to_end = self.config.redemption_end_month - current_month
                    years_to_end = months_to_end / 12
                    self.logger.debug(f"Months to end: {months_to_end}, Years to end: {years_to_end:.4f}")
                    
                    if current_value > 0 and years_to_end > 0:
                        expected_irr = self.calculate_expected_irr(current_value, future_value, years_to_end)
                        self.logger.debug(f"Expected IRR for {deal.counterparty}: {expected_irr:.2f}% vs Threshold: {deal.irr_threshold}%")
                        
                        # Trigger redemption if IRR falls below threshold
                        if expected_irr < deal.irr_threshold:
                            redemption = deal.oak_amount
                            total_redemption += redemption
                            month_redemptions[deal.counterparty] = redemption
                            deal.oak_amount = 0
                            self.logger.info(f"Redeeming {redemption:.0f} OAK from {deal.counterparty} (IRR: {expected_irr:.2f}% < Threshold: {deal.irr_threshold}%)")
                else:
                    self.logger.warning(f"No OAK remaining to redeem for {deal.counterparty}")
        
        # Update OAK supply after all redemptions
        self.remaining_oak_supply = total_oak_before - total_redemption
        self.oak_supply_history[current_month] = self.remaining_oak_supply
        
        if month_redemptions:
            self.redemption_history[current_month] = month_redemptions
            self.logger.info(f"Total redemption this month: {total_redemption}")
        else:
            self.logger.info("No redemptions this month")
    
        # Calculate proportional redemptions of USDC and LEAF
        if total_oak_before > 0:
            usdc_redemption = aegis_usdc * (total_redemption / total_oak_before)
            leaf_redemption = aegis_leaf * (total_redemption / total_oak_before)
        else:
            usdc_redemption = 0
            leaf_redemption = 0
    
        self.logger.info(f"USDC redeemed: ${usdc_redemption:.2f}, LEAF redeemed: {leaf_redemption:.2f}")
        self.logger.debug(f"Remaining OAK supply: {self.remaining_oak_supply}")
    
        return (
            total_redemption,
            total_oak_before,
            self.remaining_oak_supply,
            usdc_redemption,
            leaf_redemption
        )

    def get_best_case_irr(
        self,
        acquisition_price: float,
        current_leaf_price: float,
        current_month: int
    ) -> float:
        """
        Calculate best-case IRR for OAK tokens based on current state.
        
        Args:
            acquisition_price: Original LEAF price when OAK was acquired
            current_leaf_price: Current LEAF price
            current_month: Current month in simulation
            
        Returns:
            Annualized IRR as a percentage
        """
        if current_month >= self.config.redemption_end_month:
            return 0.0
        
        if current_month < self.config.redemption_start_month:
            years_to_start = (self.config.redemption_start_month - current_month) / 12
            value_ratio = current_leaf_price / acquisition_price
            return (value_ratio ** (1/max(years_to_start, 0.1)) - 1) * 100
                
        years_held = max((current_month - self.config.redemption_start_month) / 12, 0.1)
        value_ratio = current_leaf_price / acquisition_price
        
        # Calculate annualized return
        irr = (value_ratio ** (1/years_held) - 1) * 100
        
        return max(0.0, irr)

    def get_state(self) -> Dict[str, any]:
        """
        Retrieve the current state of the OAKModel.
        
        Returns:
            A dictionary containing current OAK supply, redemption history, and other relevant metrics.
        """
        return {
            "current_month": self.month,
            "remaining_oak_supply": self.remaining_oak_supply,
            "oak_supply_history": self.oak_supply_history,
            "redemption_history": self.redemption_history,
        }