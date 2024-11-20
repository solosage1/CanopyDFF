import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict
import math

@dataclass
class OAKDistributionDeal:
    """Configuration for individual OAK distribution deals."""
    counterparty: str           # Name of the counterparty
    oak_amount: float          # Total OAK tokens allocated
    start_month: int           # Start month (as number of months since launch)
    vesting_months: int        # Months before redemption is possible
    irr_threshold: float       # Risk-adjusted IRR threshold for redemption
    distributed_amount: float = 0.0  # Track amount distributed so far

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
        self.current_month = 0
        self.remaining_oak_supply = config.total_oak_supply
        self.oak_supply_history = {}
        self.redemption_history = {}
        self.distribution_history = {}
        self.distributed_amounts = defaultdict(float)  # Use defaultdict for automatic 0 initialization
        
        # Use existing logger if available, otherwise create new one
        self.logger = logging.getLogger(f"{__name__}.OAKModel")
        if not self.logger.handlers:  # Only add handler if none exists
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        
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
        """Process monthly OAK distributions and redemptions."""
        self.current_month = current_month
        total_value = aegis_usdc + (aegis_leaf * current_leaf_price)
        self.logger.debug(f"Processing Month {current_month}: Total Value = ${total_value:.2f}")
        
        # Process distributions first
        distributions = self.process_monthly_distributions(current_month)
        
        # Calculate total unredeemed OAK (use distributed_amount)
        total_oak_before = sum(deal.distributed_amount for deal in self.config.deals)
        
        # Track unredeemed OAK before processing any redemptions
        self.logger.debug(f"Total OAK before redemption: {total_oak_before}")
        
        # Process redemptions
        total_redemption = 0.0
        month_redemptions = {}
        
        for deal in self.config.deals:
            if (current_month >= self.config.redemption_start_month and
                current_month >= deal.redemption_month and
                deal.distributed_amount > 0):  # Check distributed amount instead of oak_amount
                
                # Calculate redemption progress
                total_redemption_months = self.config.redemption_end_month - self.config.redemption_start_month
                months_into_redemption = current_month - self.config.redemption_start_month
                redemption_progress = min(1.0, max(0.0, months_into_redemption / total_redemption_months))
                
                if total_oak_before > 0:
                    value_per_oak = total_value / total_oak_before
                    current_value = value_per_oak * redemption_progress
                    future_value = value_per_oak
                    
                    months_to_end = self.config.redemption_end_month - current_month
                    years_to_end = months_to_end / 12
                    
                    if current_value > 0 and years_to_end > 0:
                        expected_irr = self.calculate_expected_irr(current_value, future_value, years_to_end)
                        self.logger.debug(f"Expected IRR for {deal.counterparty}: {expected_irr:.2f}% vs Threshold: {deal.irr_threshold}%")
                        
                        if expected_irr < deal.irr_threshold:
                            redemption = deal.distributed_amount
                            total_redemption += redemption
                            month_redemptions[deal.counterparty] = redemption
                            deal.distributed_amount = 0
                            self.logger.info(f"Redeeming {redemption:.0f} OAK from {deal.counterparty}")
        
        # Update remaining supply and history
        self.remaining_oak_supply = total_oak_before - total_redemption
        self.oak_supply_history[current_month] = self.remaining_oak_supply
        
        if month_redemptions:
            self.redemption_history[current_month] = month_redemptions
        
        # Calculate proportional redemptions
        usdc_redemption = aegis_usdc * (total_redemption / total_oak_before) if total_oak_before > 0 else 0
        leaf_redemption = aegis_leaf * (total_redemption / total_oak_before) if total_oak_before > 0 else 0
        
        return (
            total_redemption,
            total_oak_before,
            self.remaining_oak_supply,
            usdc_redemption,
            leaf_redemption
        )

    def get_best_case_irr(
        self,
        aegis_usdc: float,         # Total USDC in AEGIS
        aegis_leaf: float,         # Total LEAF in AEGIS
        current_leaf_price: float, # Current LEAF price
        current_month: int         # Current month in simulation
    ) -> float:
        """
        Calculate best-case IRR for OAK tokens based on current state.
        
        The IRR represents the annualized return OAK holders could achieve by waiting 
        until redemption_end_month instead of redeeming now.
        
        Args:
            aegis_usdc: Total USDC in AEGIS
            aegis_leaf: Total LEAF in AEGIS
            current_leaf_price: Current LEAF price
            current_month: Current month in simulation
            
        Returns:
            float: Annualized IRR as a percentage
        """
        if current_month >= self.config.redemption_end_month:
            return 0.0

        total_value = aegis_usdc + (aegis_leaf * current_leaf_price)
        if total_value == 0 or self.remaining_oak_supply == 0:
            return 0.0

        # Calculate redemption progress (0 to 1)
        total_redemption_months = self.config.redemption_end_month - self.config.redemption_start_month
        months_into_redemption = current_month - self.config.redemption_start_month
        redemption_progress = min(1.0, max(0.0, months_into_redemption / total_redemption_months))

        # Calculate current and future values per OAK
        value_per_oak = total_value / self.remaining_oak_supply
        current_value = value_per_oak * redemption_progress  # Current value based on progress
        future_value = value_per_oak  # Full value at end

        # Calculate time remaining until redemption_end_month
        months_to_end = self.config.redemption_end_month - current_month
        years_to_end = months_to_end / 12

        if current_value > 0 and years_to_end > 0:
            try:
                irr = ((future_value / current_value) ** (1 / years_to_end) - 1) * 100
                return max(0.0, irr)
            except (ValueError, ZeroDivisionError):
                return 0.0
        
        return 0.0

    def get_state(self) -> Dict[str, any]:
        """Retrieve the current state of the OAKModel."""
        current_redemptions = self.redemption_history.get(self.current_month, {})
        total_redemption = sum(current_redemptions.values()) if current_redemptions else 0
        
        return {
            "current_month": self.current_month,
            "remaining_oak_supply": self.remaining_oak_supply,
            "oak_supply_history": self.oak_supply_history,
            "redemption_history": self.redemption_history,
            "distribution_history": self.distribution_history,
            "redemption_amount": total_redemption,
            "deals": self.config.deals
        }

    def get_monthly_redemption_amount(self, month: int) -> float:
        """
        Get the total amount of OAK redeemed in a specific month.
        
        Args:
            month: The month to check
            
        Returns:
            float: Total amount of OAK redeemed in the specified month
        """
        return sum(self.redemption_history.get(month, {}).values())

    def process_monthly_distributions(self, current_month: int) -> Dict[str, float]:
        """Process monthly distributions for all deals."""
        distributions = {}
        
        for deal in self.config.deals:
            # Only distribute if:
            # 1. We've reached redemption month
            # 2. There's OAK to distribute
            # 3. Haven't distributed yet (check distribution history)
            if (current_month >= deal.redemption_month and 
                deal.oak_amount > 0 and
                not any(month <= current_month and deal.counterparty in dist 
                       for month, dist in self.distribution_history.items())):
                
                amount_to_distribute = deal.oak_amount
                deal.distributed_amount = amount_to_distribute
                deal.oak_amount = 0
                
                distributions[deal.counterparty] = amount_to_distribute
                self.logger.debug(
                    f"Month {current_month}: Cliff distribution of "
                    f"{amount_to_distribute:,.2f} OAK to {deal.counterparty}"
                )
        
        if distributions:
            self.distribution_history[current_month] = distributions.copy()
        
        return distributions