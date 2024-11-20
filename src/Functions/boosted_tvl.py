from dataclasses import dataclass
from typing import Dict, List, Optional
from src.Data.deal import Deal, get_active_deals

@dataclass
class BoostedTVLConfig:
    """Configuration for Boosted TVL calculations."""
    min_boost_rate: float = 0.10  # Minimum boost rate (10%)
    max_boost_rate: float = 0.50  # Maximum boost rate (50%)
    base_irr_threshold: float = 30.0  # Base IRR threshold for boost calculation

class BoostedTVLModel:
    """Handles boosted TVL calculations and tracking."""
    
    def __init__(self, config: BoostedTVLConfig):
        self.config = config
        self.boost_history: Dict[int, Dict[str, float]] = {}
        
    def calculate_boost_rate(self, deal: Deal, month: int) -> float:
        """
        Calculate boost rate for a deal based on its OAK IRR threshold.
        
        Args:
            deal: Deal to calculate boost rate for
            month: Current month
            
        Returns:
            Calculated boost rate
        """
        if not deal.oak_irr_threshold:
            return 0.0
            
        # Calculate boost rate based on IRR threshold
        # Higher IRR threshold = lower boost rate
        normalized_irr = deal.oak_irr_threshold / self.config.base_irr_threshold
        boost_rate = max(
            self.config.min_boost_rate,
            min(
                self.config.max_boost_rate,
                self.config.max_boost_rate * (1 / normalized_irr)
            )
        )
        
        return boost_rate
    
    def get_boosted_tvl(self, deals: List[Deal], month: int) -> Dict[str, float]:
        """
        Calculate boosted TVL amounts for active deals.
        
        Args:
            deals: List of all deals
            month: Current month
            
        Returns:
            Dictionary with boosted TVL amounts by counterparty
        """
        boosted_tvl: Dict[str, float] = {}
        active_deals = get_active_deals(deals, month)
        
        for deal in active_deals:
            if deal.oak_amount > 0 and deal.tvl_amount > 0:
                boost_rate = self.calculate_boost_rate(deal, month)
                boosted_amount = deal.tvl_amount * boost_rate
                boosted_tvl[deal.counterparty] = boosted_amount
        
        # Store in history
        self.boost_history[month] = boosted_tvl.copy()
        
        return boosted_tvl
    
    def get_total_boosted_tvl(self, month: int) -> float:
        """Get total boosted TVL for a specific month."""
        if month in self.boost_history:
            return sum(self.boost_history[month].values())
        return 0.0
    
    def get_boost_rate_for_deal(self, deal: Deal, month: int) -> Optional[float]:
        """Get boost rate for a specific deal."""
        if deal.oak_amount > 0 and deal.tvl_amount > 0:
            return self.calculate_boost_rate(deal, month)
        return None
    
    def get_state(self) -> Dict:
        """Get current state of boosted TVL model."""
        return {
            'boost_history': {
                month: amounts.copy() 
                for month, amounts in self.boost_history.items()
            }
        }