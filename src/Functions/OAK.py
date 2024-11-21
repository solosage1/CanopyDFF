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
    redemption_start_month: int = 3   # Global start month for any redemptions
    redemption_end_month: int = 48    # After this, max redemption for unlocked tokens
    deals: List[Deal] = field(default_factory=list)

class OAKModel:
    """Model for simulating OAK token distribution and redemption."""
    
    def __init__(self, config: OAKDistributionConfig, aegis_model: AEGISModel):
        self.config = config
        self.aegis_model = aegis_model  # Store AEGIS model reference
        self.current_month = 0
        
        # All OAK are minted at initialization
        self.total_oak_supply = config.total_oak_supply
        self.allocated_oak = sum(deal.oak_amount for deal in config.deals)  # Total allocated to deals
        self.distributed_oak = 0  # Actually distributed to counterparties
        self.redeemed_oak = 0  # Redeemed from supply
        self.remaining_oak_supply = self.total_oak_supply
        
        # Tracking histories
        self.oak_supply_history = {}
        self.redemption_history = {}
        self.distribution_history = {}
        self.distributed_amounts = defaultdict(float)
        
        # Initialize logging state tracking
        self._last_logged_values = {
            'total_value': None,
            'irr': None,
            'month': None
        }
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages
        self.logger.propagate = True  # Ensure messages propagate to root logger
        
        # Log initial state
        self.logger.info("\n=== Starting OAK Model ===")
        self.logger.info(f"Total Supply: {self.total_oak_supply:,.2f}")
        self.logger.info(f"Allocated to Deals: {self.allocated_oak:,.2f}")
        
        # Validate total allocations don't exceed supply
        if self.allocated_oak > self.total_oak_supply:
            raise ValueError(f"Total allocated OAK ({self.allocated_oak}) exceeds supply ({self.total_oak_supply})")
        
        # Calculate total redemption period length
        self.redemption_period_months = config.redemption_end_month - config.redemption_start_month
        
        self.last_oak_value = None
        self.last_irr_value = None
    
    def _should_log_changes(self, value_per_oak: float, irr: float) -> bool:
        """Determine if changes are significant enough to log."""
        return (
            self._last_logged_values['total_value'] is None or
            abs(value_per_oak - self._last_logged_values['total_value']) > 0.01 or
            self._last_logged_values['irr'] is None or
            abs(irr - self._last_logged_values['irr']) > 1.0
        )
    
    def _log_monthly_status(self, month: int, value_per_oak: float, irr: float = None):
        """Log monthly status if significant changes occurred."""
        if irr is not None and self._should_log_changes(value_per_oak, irr):
            self.logger.info(f"\n=== Month {month} Status ===")
            self.logger.info(f"Value per OAK: ${value_per_oak:,.2f}")
            self.logger.info(f"Expected IRR: {irr:.1f}%")
            self._log_redemption_status(irr)
            
            self._last_logged_values.update({
                'total_value': value_per_oak,
                'irr': irr,
                'month': month
            })
    
    def _log_redemption_status(self, irr: float):
        """Log redemption eligibility for each deal and process redemptions."""
        if irr == float('-inf'):
            self.logger.info("IRR calculation not possible - likely zero current value")
            return
            
        self.logger.info("\nRedemption Status:")
        for deal in self.config.deals:
            if deal.oak_distributed_amount > 0:
                is_eligible = irr < deal.oak_irr_threshold
                status = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE"
                self.logger.info(
                    f"  {deal.counterparty}: {status} "
                    f"(IRR: {irr:.1f}% vs threshold: {deal.oak_irr_threshold:.1f}%)"
                )
                
                # Process redemption if eligible
                if is_eligible and not deal.redeemed:
                    self.redeem_oak(deal.oak_distributed_amount)
                    deal.redeemed = True  # Mark as redeemed to prevent double redemption
    
    def calculate_expected_irr(self, current_value: float, future_value: float, years_to_end: float) -> float:
        """Calculate the expected IRR based on current and future values."""
        try:
            if current_value <= 0 or years_to_end <= 0:
                return float('-inf')
            expected_irr = ((future_value / current_value) ** (1 / years_to_end) - 1) * 100
            return expected_irr
        except (ValueError, ZeroDivisionError) as e:
            self.logger.error(f"Error calculating IRR: {e}")
            return float('-inf')
        
    def calculate_value_per_oak(self, aegis_usdc: float, aegis_leaf: float, 
                                current_leaf_price: float) -> float:
        """Calculate the current value per unredeemed OAK token."""
        total_value = aegis_usdc + (aegis_leaf * current_leaf_price)
        unredeemed = self.total_oak_supply - self.redeemed_oak
        
        if unredeemed <= 0:
            return 0.0
        
        value_per_oak = total_value / unredeemed
        
        # Only log if value has changed significantly
        if self.last_oak_value is None or abs(value_per_oak - self.last_oak_value) > 0.01:
            logging.debug("\nOAK Value Calculation:")
            logging.debug(f"  Total Value: ${total_value:,.2f}")
            logging.debug(f"  Unredeemed OAK: {unredeemed:,.2f}")
            logging.debug(f"  Value per OAK: ${value_per_oak:,.2f}")
            self.last_oak_value = value_per_oak
        
        return value_per_oak
        
    def _calculate_monthly_metrics(self, month: int, value_per_oak: float, current_leaf_price: float) -> Tuple[float, float]:
        """Calculate current value and IRR for OAK tokens."""
        if month < self.config.redemption_start_month:
            return 0, 0
        
        # Calculate redemption progress
        total_redemption_months = self.config.redemption_end_month - self.config.redemption_start_month
        months_into_redemption = month - self.config.redemption_start_month
        redemption_progress = min(months_into_redemption / total_redemption_months, 1.0)
        
        # Calculate total value using LEAF price for LEAF balance and direct USDC
        total_value = (self.aegis_model.usdc_balance + 
                      (self.aegis_model.leaf_balance * current_leaf_price))
        
        # Calculate redemption value (current value) and total value (future value)
        redemption_value = total_value * redemption_progress
        redemption_value_per_token = redemption_value / self.total_oak_supply
        total_value_per_token = total_value / self.total_oak_supply
        
        # Calculate years remaining for IRR calculation
        years_remaining = max((self.config.redemption_end_month - month) / 12, 0.0001)
        
        # Calculate IRR using redemption value as current value and total value as future value
        irr = self.calculate_expected_irr(redemption_value_per_token, total_value_per_token, years_remaining)
        
        # Only log if IRR has changed significantly
        if self.last_irr_value is None or abs(irr - self.last_irr_value) > 0.0001:
            logging.debug("\nIRR Calculation:")
            logging.debug(f"  Total Value: ${total_value:,.2f}")
            logging.debug(f"  Redemption Progress: {redemption_progress:.2%}")
            logging.debug(f"  Redemption Value: ${redemption_value:,.2f}")
            logging.debug(f"  Redemption Value per Token: ${redemption_value_per_token:,.2f}")
            logging.debug(f"  Total Value per Token: ${total_value_per_token:,.2f}")
            logging.debug(f"  Years Remaining: {years_remaining:.2f}")
            logging.debug(f"  IRR: {irr:.2f}%")
            self.last_irr_value = irr
        
        return redemption_value, irr
    
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
        Get the total amount of OAK distributed up to the current month.
        
        Returns:
            float: Cumulative distributed OAK
        """
        return sum(amount for month, amount in self.distributed_amounts.items() if month <= self.current_month)
    
    def calculate_redemption_value(self, oak_amount: float, current_leaf_price: float) -> Dict[str, float]:
        """Calculate redemption value based on AEGIS balances."""
        oak_share = oak_amount / self.config.total_oak_supply
        
        usdc_value = self.aegis_model.usdc_balance * oak_share
        leaf_amount = self.aegis_model.leaf_balance * oak_share
        leaf_value = leaf_amount * current_leaf_price
        total_value = usdc_value + leaf_value
        
        self.logger.debug(f"\nOAK Redemption Calculation:")
        self.logger.debug(f"- OAK Amount: {oak_amount:,.2f}")
        self.logger.debug(f"- OAK Share: {oak_share:.4%}")
        self.logger.debug(f"- USDC Value: ${usdc_value:,.2f}")
        self.logger.debug(f"- LEAF Amount: {leaf_amount:,.2f}")
        self.logger.debug(f"- LEAF Value: ${leaf_value:,.2f}")
        self.logger.debug(f"- Total Value: ${total_value:,.2f}")
        
        return {
            'usdc_value': usdc_value,
            'leaf_amount': leaf_amount,
            'total_value': total_value
        }
    
    def redeem_oak(self, oak_amount: float) -> None:
        """Redeem OAK tokens from supply."""
        unredeemed_supply = self.total_oak_supply - self.redeemed_oak
        if oak_amount > unredeemed_supply:
            self.logger.warning(
                f"Attempting to redeem {oak_amount:,.2f} OAK, but only "
                f"{unredeemed_supply:,.2f} unredeemed available."
            )
            oak_amount = unredeemed_supply
        
        self.redeemed_oak += oak_amount
        self.logger.info(
            f"Redeemed {oak_amount:,.2f} OAK. "
            f"Total redeemed: {self.redeemed_oak:,.2f}, "
            f"Remaining unredeemed: {self.total_oak_supply - self.redeemed_oak:,.2f}"
        )
    
    def process_monthly_distributions(self, month: int) -> Dict[str, float]:
        """Process monthly OAK distributions."""
        distributions = {}
        month_distributed = 0.0
        
        for deal in self.config.deals:
            if self._should_distribute(deal, month):
                # Distribute full amount at once
                amount = deal.oak_amount  # Changed from monthly_amount to full amount
                deal.oak_distributed_amount = amount
                month_distributed += amount
                distributions[deal.counterparty] = amount
                
                self.logger.debug(
                    f"Distributing {amount:,.2f} OAK to {deal.counterparty} "
                    f"({deal.oak_distributed_amount:,.2f}/{deal.oak_amount:,.2f})"
                )
        
        if distributions:
            self.distribution_history[month] = distributions
            self.distributed_amounts[month] = month_distributed
            self.distributed_oak += month_distributed
            
            self.logger.info(f"Total OAK distributed this month: {month_distributed:,.2f}")
        
        return distributions
    
    def _should_distribute(self, deal: Deal, month: int) -> bool:
        """
        Determine if a deal should receive OAK distribution this month.
        
        Args:
            deal: The deal to check
            month: Current month
            
        Returns:
            bool: True if deal should receive distribution
        """
        # Check if deal has started
        if month < deal.start_month:
            return False
            
        # Check if deal has already received distribution
        if deal.oak_distributed_amount >= deal.oak_amount:
            return False
            
        # Check if vesting period is complete
        months_vesting = month - deal.start_month + 1  # +1 to include the starting month
        if months_vesting == deal.oak_vesting_months:  # Changed from > to ==
            return True
            
        return False
    
    def step(self, current_month: int, aegis_usdc: float, aegis_leaf: float, 
             current_leaf_price: float, aegis_model: AEGISModel) -> None:
        """Process a single month step in the model."""
        self.current_month = current_month
        self.logger.info(f"\n=== Month {current_month} ===")
        
        # Process distributions first
        distributions = self.process_monthly_distributions(current_month)
        
        # Calculate value metrics
        value_per_oak = self.calculate_value_per_oak(aegis_usdc, aegis_leaf, current_leaf_price)
        
        # Only calculate IRR and check redemptions during redemption period
        if current_month >= self.config.redemption_start_month:
            current_value, irr = self._calculate_monthly_metrics(current_month, value_per_oak, current_leaf_price)
            
            # Check each deal for redemption eligibility
            for deal in self.config.deals:
                if deal.oak_distributed_amount > 0 and not deal.redeemed:
                    if irr < deal.oak_irr_threshold:
                        self.logger.info(
                            f"\nRedemption triggered for {deal.counterparty}:"
                            f"\n  IRR: {irr:.1f}% < Threshold: {deal.oak_irr_threshold:.1f}%"
                            f"\n  Amount: {deal.oak_distributed_amount:,.2f} OAK"
                        )
                        self.redeem_oak(deal.oak_distributed_amount)
                        deal.redeemed = True
            
            # Log status
            self._log_monthly_status(current_month, value_per_oak, irr)
    
    def calculate_weighted_avg_irr_threshold(self) -> float:
        """Calculate weighted average IRR threshold based on OAK distribution amounts."""
        total_distributed = self.get_total_distributed_oak()
        if total_distributed == 0:
            return 0.0
        
        weighted_sum = sum(
            deal.oak_distributed_amount * deal.oak_irr_threshold 
            for deal in self.config.deals
        )
        weighted_avg = weighted_sum / total_distributed
        
        # Ensure minimum threshold is 0
        return max(0.0, weighted_avg)