import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict
import math

from src.Data.deal import Deal, get_active_deals
from src.Functions.AEGIS import AEGISModel
from src.Functions.Revenue import RevenueModel
from src.Functions.TVLContributions import TVLContribution

@dataclass
class OAKDistributionConfig:
    """Configuration for OAK distribution model."""
    total_oak_supply: float = 500_000
    redemption_start_month: int = 12  # Global start month for any redemptions
    redemption_end_month: int = 48    # After this, max redemption for unlocked tokens
    deals: List[Deal] = field(default_factory=list)

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
        
        # Configure logging
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
        
    def calculate_value_per_oak(
        self,
        aegis_usdc: float,
        aegis_leaf: float,
        current_leaf_price: float,
        total_oak: float
    ) -> float:
        """
        Calculate the current value per OAK token.
        
        Args:
            aegis_usdc: Total USDC in AEGIS
            aegis_leaf: Total LEAF in AEGIS
            current_leaf_price: Current LEAF price
            total_oak: Total unredeemed OAK tokens
            
        Returns:
            float: Value per OAK token. Returns 0 if no OAK tokens exist.
        """
        total_value = aegis_usdc + (aegis_leaf * current_leaf_price)
        return total_value / total_oak if total_oak > 0 else 0
        
    def step(
        self, 
        current_month: int,
        aegis_usdc: float,
        aegis_leaf: float,
        current_leaf_price: float,
        aegis_model: AEGISModel
    ) -> Tuple[float, float, float, float, float]:
        """Process monthly OAK distributions and redemptions."""
        self.current_month = current_month
        total_value = aegis_usdc + (aegis_leaf * current_leaf_price)
        self.logger.debug(f"Processing Month {current_month}: Total Value = ${total_value:.2f}")
        
        # Process distributions first
        distributions = self.process_monthly_distributions(current_month)
        
        # Calculate total unredeemed OAK
        total_oak_before = sum(deal.oak_distributed_amount for deal in self.config.deals)
        self.logger.debug(f"Total OAK before redemption: {total_oak_before}")
        
        # Calculate value per OAK
        value_per_oak = self.calculate_value_per_oak(
            aegis_usdc=aegis_usdc,
            aegis_leaf=aegis_leaf,
            current_leaf_price=current_leaf_price,
            total_oak=total_oak_before
        )
        
        # Process redemptions
        total_redemption = 0.0
        month_redemptions = {}
        
        # Only process redemptions during redemption period
        if current_month >= self.config.redemption_start_month:
            # Calculate redemption progress
            total_redemption_months = self.config.redemption_end_month - self.config.redemption_start_month
            months_into_redemption = current_month - self.config.redemption_start_month
            redemption_progress = min(1.0, max(0.0, months_into_redemption / total_redemption_months))
            
            for deal in self.config.deals:
                if deal.oak_distributed_amount > 0:  # Check if deal has distributed OAK
                    if total_oak_before > 0:
                        current_value = value_per_oak * redemption_progress
                        future_value = value_per_oak
                        
                        months_to_end = self.config.redemption_end_month - current_month
                        years_to_end = months_to_end / 12
                        
                        if current_value > 0 and years_to_end > 0:
                            expected_irr = self.calculate_expected_irr(current_value, future_value, years_to_end)
                            self.logger.debug(f"Expected IRR for {deal.counterparty}: {expected_irr:.2f}% vs Threshold: {deal.oak_irr_threshold}%")
                            
                            if expected_irr < deal.oak_irr_threshold:
                                redemption = deal.oak_distributed_amount
                                total_redemption += redemption
                                month_redemptions[deal.counterparty] = redemption
                                deal.oak_distributed_amount = 0
                                self.logger.info(f"Redeeming {redemption:.0f} OAK from {deal.counterparty}")
        
        # Update remaining supply and history
        self.remaining_oak_supply = total_oak_before - total_redemption
        self.oak_supply_history[current_month] = self.remaining_oak_supply
        
        if month_redemptions:
            self.redemption_history[current_month] = month_redemptions
        
        # Calculate proportional redemptions
        usdc_redemption = aegis_usdc * (total_redemption / total_oak_before) if total_oak_before > 0 else 0
        leaf_redemption = aegis_leaf * (total_redemption / total_oak_before) if total_oak_before > 0 else 0
        
        # Update AEGIS balances and handle redemptions
        if total_redemption > 0:
            aegis_model.update_balances(
                usdc_change=-usdc_redemption,
                leaf_change=-leaf_redemption
            )
            self.logger.info(
                f"Month {current_month}: "
                f"Redeemed {total_redemption:,.2f} OAK, "
                f"USDC: ${usdc_redemption:,.2f}, "
                f"LEAF: {leaf_redemption:,.2f} @ ${current_leaf_price:.2f}"
            )
            print(f"\nOAK Redemptions:")
            print(f"- Amount: {total_redemption:,.2f} OAK")
            print(f"- USDC: ${usdc_redemption:,.2f}")
            print(f"- LEAF: {leaf_redemption:,.2f} @ ${current_leaf_price:.2f}")
            print(f"- Total Value: ${(usdc_redemption + leaf_redemption * current_leaf_price):,.2f}")
        
        # Update AEGIS model
        if current_month >= self.config.redemption_start_month and total_oak_before > 0:
            redemption_rate = total_redemption / total_oak_before if total_oak_before > 0 else 0
            self.logger.debug(f"Redemption rate for month {current_month}: {redemption_rate:.4f}")
            aegis_model.handle_redemptions(current_month, redemption_rate)
            aegis_model.step(current_month)
        
        self.logger.debug(f"Step {current_month} completed.")
        
        return (
            total_redemption,
            total_oak_before,
            self.remaining_oak_supply,
            usdc_redemption,
            leaf_redemption
        )
       
    def process_monthly_distributions(self, current_month: int) -> Dict[str, float]:
        """Process monthly distributions for all deals."""
        distributions = {}
        
        for deal in self.config.deals:
            # Only check vesting completion, not redemption period
            vesting_complete = current_month >= (deal.start_month + deal.oak_vesting_months)
            
            if (deal.oak_amount > 0 and  # Has OAK to distribute
                current_month >= deal.start_month and  # Has started
                not any(month <= current_month and deal.counterparty in dist  # Hasn't distributed yet
                       for month, dist in self.distribution_history.items())):
                    
                amount_to_distribute = deal.oak_amount
                deal.oak_distributed_amount = amount_to_distribute
                deal.oak_amount = 0
                
                distributions[deal.counterparty] = amount_to_distribute
                self.logger.debug(
                    f"Month {current_month}: Cliff distribution of "
                    f"{amount_to_distribute:,.2f} OAK to {deal.counterparty}"
                )
        
        if distributions:
            self.distribution_history[current_month] = distributions.copy()
        
        return distributions
    
    def get_best_case_irr(
        self, 
        current_value: float, 
        future_value: float, 
        years_to_end: float
    ) -> float:
        """
        Calculate the best-case IRR based on current and future values.
        
        Args:
            current_value: Present value based on redemption progress.
            future_value: Full value at the end of redemption.
            years_to_end: Remaining time in years until redemption end.
        
        Returns:
            Best-case annualized IRR as a percentage.
        """
        return self.calculate_expected_irr(current_value, future_value, years_to_end)
    
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
    
    def get_total_distributed_oak(self) -> float:
        """
        Get the total amount of OAK distributed so far.
        
        Returns:
            float: Total distributed OAK
        """
        return self.distributed_amounts[self.current_month]