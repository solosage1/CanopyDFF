from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict
import math

@dataclass
class OAKDistributionDeal:
    """Configuration for individual OAK distribution deals."""
    counterparty: str           # Name of the counterparty
    oak_amount: float           # Total OAK tokens allocated
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
    redemption_start_month: int = 12  # Add global redemption start month
    deals: List[OAKDistributionDeal] = field(default_factory=list)

class OAKModel:
    """Handles OAK token distribution and redemption logic."""
    
    def __init__(self, config: OAKDistributionConfig):
        self.config = config
        self.total_oak_supply = config.total_oak_supply
        self.remaining_oak_supply = config.total_oak_supply
        self.deals = config.deals.copy()
        self.oak_supply_history: Dict[int, float] = {}
        self.redemption_history: Dict[int, Dict[str, float]] = defaultdict(dict)
        self.month = 0
        self.validate_deals()

    def validate_deals(self) -> None:
        """Validate that all deals are properly configured."""
        total_allocated = sum(deal.oak_amount for deal in self.deals)
        if total_allocated > self.total_oak_supply:
            raise ValueError(f"Total allocated OAK ({total_allocated}) exceeds supply ({self.total_oak_supply})")
        
        for deal in self.deals:
            if deal.start_month < 0:
                raise ValueError(f"Invalid start month for {deal.counterparty}: {deal.start_month}")
            if deal.vesting_months < 0:
                raise ValueError(f"Invalid vesting months for {deal.counterparty}: {deal.vesting_months}")
            if deal.unlock_month < deal.redemption_month:
                raise ValueError(f"Unlock month must be after redemption month for {deal.counterparty}")

    def step(self, current_month: int, current_irr: float) -> Tuple[float, float, float]:
        """
        Process redemptions and update OAK supply for the current month.
        
        Args:
            current_month: Current simulation month
            current_irr: Current IRR value
        
        Returns:
            Tuple containing:
            - total_redemption: Amount redeemed this month
            - supply_before: Total supply before redemptions
            - supply_after: Total supply after redemptions
        """
        self.month = current_month
        total_redemption, month_redemptions, supply_before, supply_after = self.calculate_redemptions(
            current_month, current_irr
        )
        
        # Update remaining OAK supply
        self.remaining_oak_supply = supply_after
        
        # Record supply history
        self.oak_supply_history[current_month] = supply_after
        
        # Record redemptions for this month
        self.redemption_history[current_month] = month_redemptions

        return total_redemption, supply_before, supply_after

    def calculate_redemptions(self, current_month: int, current_irr: float) -> Tuple[float, Dict[str, float], float, float]:
        """
        Calculate redemptions for the current month based on deals.
        
        Args:
            current_month: Current simulation month
            current_irr: Current IRR value
            
        Returns:
            Tuple containing:
            - total_redemption: Total amount being redeemed this month
            - month_redemptions: Dict of redemptions by counterparty
            - total_supply_before: Total OAK supply before redemptions
            - total_supply_after: Total OAK supply after redemptions
        """
        total_redemption = 0.0
        month_redemptions = {}
        total_supply_before = self.remaining_oak_supply

        for deal in self.deals:
            if current_month < deal.redemption_month:
                continue
                
            if deal.oak_amount <= 0:
                continue
                
            if current_irr >= deal.irr_threshold:
                continue
                
            # Calculate redemption amount
            redeem_amount = deal.oak_amount
            month_redemptions[deal.counterparty] = redeem_amount
            total_redemption += redeem_amount
            deal.oak_amount -= redeem_amount
            # Ensure we don't have tiny remaining amounts
            if deal.oak_amount < 1e-6:
                deal.oak_amount = 0
        
        return (
            round(total_redemption, 8),
            month_redemptions,
            total_supply_before,
            total_supply_before - total_redemption
        )

    def get_monthly_redemption_amount(self, month: int) -> float:
        """
        Get the total redemption amount for the current month.
        
        Args:
            month: Current simulation month
            
        Returns:
            float: Total OAK tokens redeemed in this month
        """
        return sum(self.redemption_history.get(month, {}).values())

    def get_state(self) -> Dict:
        """
        Return the current state of the OAK model.
        
        Returns:
            Dict containing current state information
        """
        return {
            'month': self.month,
            'remaining_oak_supply': self.remaining_oak_supply,
            'oak_supply_history': dict(self.oak_supply_history),
            'redemption_history': dict(self.redemption_history)
        }

    def get_best_case_irr(self, acquisition_price: float, current_leaf_price: float, current_month: int) -> float:
        """
        Calculate the best case IRR for AEGIS LP holders.
        
        Args:
            acquisition_price: Initial LEAF price
            current_leaf_price: Current LEAF price
            current_month: Current simulation month
            
        Returns:
            float: Best case IRR percentage
        """
        # Weighted average redemption end month
        total_oak = sum(deal.oak_amount for deal in self.deals)
        if total_oak == 0:
            return 0.0
        
        weighted_sum = 0.0
        for deal in self.deals:
            weighted_sum += deal.oak_amount * deal.unlock_month
        
        average_unlock_month = weighted_sum / total_oak
        time_diff_years = (average_unlock_month - current_month) / 12
        
        if time_diff_years <= 0:
            return 0.0
            
        # Calculate IRR using the formula: IRR = (FV / PV)^(1/n) - 1
        future_value = current_leaf_price
        present_value = acquisition_price
        irr = (math.pow(future_value / present_value, 1 / time_diff_years) - 1) * 100
        return irr 