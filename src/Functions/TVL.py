from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import defaultdict
from src.Data.deal import Deal, get_active_deals
from src.Functions.TVLContributions import TVLContribution

@dataclass
class TVLModelConfig:
    """Configuration for TVL model."""
    max_months: int = 48
    initial_tvl: float = 0.0

class TVLModel:
    """Model for tracking and calculating Total Value Locked (TVL)."""
    
    def __init__(self, config: TVLModelConfig):
        self.config = config
        self.current_month = 0
        self.total_tvl = config.initial_tvl
        
        # Track TVL by type and category
        self.tvl_by_type: Dict[str, float] = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        self.tvl_by_category: Dict[str, float] = {
            'volatile': 0.0,
            'lending': 0.0
        }
        
        # Historical tracking
        self.tvl_history: Dict[int, float] = defaultdict(float)
        self.tvl_by_type_history: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.tvl_by_category_history: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.contributions: List[TVLContribution] = []
        
    def calculate_tvl_from_deals(self, deals: List[Deal], month: int) -> Dict[str, float]:
        """
        Calculate TVL from active deals for the given month.
        
        Args:
            deals: List of all deals
            month: Current month
            
        Returns:
            Dictionary of TVL amounts by category
        """
        tvl_amounts = {
            'volatile': 0.0,
            'lending': 0.0
        }
        
        active_deals = get_active_deals(deals, month)
        
        for deal in active_deals:
            if deal.tvl_category in tvl_amounts:
                tvl_amount = deal.tvl_amount
                
                # Apply linear ramping if specified
                if deal.linear_ramp_months > 0:
                    months_active = month - deal.start_month
                    ramp_progress = min(1.0, months_active / deal.linear_ramp_months)
                    tvl_amount *= ramp_progress
                
                tvl_amounts[deal.tvl_category] += tvl_amount
        
        return tvl_amounts
    
    def step(self, deals: List[Deal], month: int) -> None:
        """
        Advance the TVL model by one month.
        
        Args:
            deals: List of all deals
            month: Current month to process
        """
        self.current_month = month
        
        # Calculate TVL from deals
        tvl_amounts = self.calculate_tvl_from_deals(deals, month)
        
        # Update current TVL amounts
        self.tvl_by_category = tvl_amounts.copy()
        self.total_tvl = sum(tvl_amounts.values())
        
        # Update history
        self.tvl_history[month] = self.total_tvl
        self.tvl_by_category_history[month] = tvl_amounts.copy()
    
    def get_tvl_at_month(self, month: int) -> Optional[float]:
        """Get total TVL for a specific month."""
        return self.tvl_history.get(month)
    
    def get_tvl_by_category_at_month(self, month: int) -> Optional[Dict[str, float]]:
        """Get TVL breakdown by category for a specific month."""
        return self.tvl_by_category_history.get(month)
    
    def get_current_tvl(self) -> float:
        """Get current total TVL."""
        return self.total_tvl
    
    def get_current_tvl_by_category(self) -> Dict[str, float]:
        """Get current TVL breakdown by category."""
        return self.tvl_by_category.copy()
    
    def add_contribution(self, contribution: TVLContribution) -> None:
        """
        Add a TVL contribution (legacy support).
        
        Args:
            contribution: TVL contribution to add
        """
        self.contributions.append(contribution)
    
    def get_state(self) -> Dict:
        """
        Get current state of TVL model.
        
        Returns:
            Dictionary containing current state
        """
        return {
            'current_month': self.current_month,
            'total_tvl': self.total_tvl,
            'tvl_by_category': self.tvl_by_category.copy(),
            'tvl_history': dict(self.tvl_history),
            'tvl_by_category_history': {
                month: cats.copy() 
                for month, cats in self.tvl_by_category_history.items()
            }
        }
    
    def get_tvl_by_type(self, deals: List[Deal], month: int) -> Dict[str, float]:
        """Get TVL amounts grouped by type."""
        active_deals = [d for d in deals if d.start_month <= month < (d.start_month + d.tvl_duration_months)]
        
        tvl_by_type = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        for deal in active_deals:
            if deal.tvl_amount > 0 and deal.tvl_type in tvl_by_type:
                tvl_by_type[deal.tvl_type] += deal.tvl_amount
            
        # Update history
        self.tvl_by_type_history[month] = tvl_by_type.copy()
        return tvl_by_type