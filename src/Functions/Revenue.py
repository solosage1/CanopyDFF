from dataclasses import dataclass
from typing import Dict, List, Optional
from src.Functions.TVL import TVLModel
from src.Functions.TVLContributions import TVLContribution
import logging

@dataclass
class RevenueModelConfig:
    """Configuration for Revenue model."""
    base_revenue_rate: float = 0.02
    revenue_rates: Dict[str, float] = None
    
    def __post_init__(self):
        if self.revenue_rates is None:
            self.revenue_rates = {
                'ProtocolLocked': 0.04,
                'Contracted': 0.025,
                'Organic': 0.02,
                'Boosted': 0.03
            }

class RevenueModel:
    def __init__(self, config: RevenueModelConfig, tvl_model: TVLModel):
        self.config = config
        self.tvl_model = tvl_model
        self.cumulative_revenue = 0.0
        self.revenue_history: Dict[int, Dict[str, float]] = {}
        
        logging.debug(
            f"Initializing Revenue Model:"
            f"\n  Base Rate: {config.base_revenue_rate:.2%}"
            f"\n  Revenue Rates: {config.revenue_rates}"
        )
    
    def calculate_monthly_revenue(self, contributions: List[TVLContribution], month: int) -> Dict[str, float]:
        """Calculate monthly revenue from TVL contributions."""
        return self.calculate_revenue(contributions, month)
    
    def calculate_revenue(self, contributions: List[TVLContribution], month: int) -> Dict[str, float]:
        """Calculate monthly revenue from TVL contributions."""
        revenue_by_type = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        for contribution in contributions:
            if not contribution.active:
                continue
                
            if month < contribution.start_month or (contribution.end_month and month >= contribution.end_month):
                continue
            
            revenue = contribution.calculate_revenue()
            revenue_by_type[contribution.tvl_type] += revenue
            
            logging.debug(
                f"Revenue from contribution {contribution.id}:"
                f"\n  Type: {contribution.tvl_type}"
                f"\n  Amount: ${contribution.amount_usd:,.2f}"
                f"\n  Rate: {contribution.revenue_rate:.2%}"
                f"\n  Revenue: ${revenue:,.2f}"
            )
        
        total_revenue = sum(revenue_by_type.values())
        self.cumulative_revenue += total_revenue
        self.revenue_history[month] = revenue_by_type.copy()
        
        return revenue_by_type
    
    def get_monthly_revenue(self, month: int) -> Optional[Dict[str, float]]:
        """Get revenue breakdown for a specific month."""
        return self.revenue_history.get(month)
    
    def get_total_revenue(self, month: int) -> float:
        """Get total revenue for a specific month."""
        monthly_revenue = self.get_monthly_revenue(month)
        if monthly_revenue:
            return sum(monthly_revenue.values())
        return 0.0
    
    def get_cumulative_revenue(self, through_month: int) -> float:
        """Get cumulative revenue through specified month."""
        return sum(
            sum(monthly_revenue.values())
            for month, monthly_revenue in self.revenue_history.items()
            if month <= through_month
        )
    
    def get_state(self) -> Dict:
        """Get current state of revenue model."""
        return {
            'cumulative_revenue': self.cumulative_revenue,
            'revenue_history': self.revenue_history.copy()
        }