from dataclasses import dataclass
from typing import List, Dict
from src.Functions.TVLContributions import TVLContribution
from src.Functions.TVL import TVLModel
from collections import defaultdict

class RevenueModel:
    def __init__(self, tvl_model: TVLModel):
        self.tvl_model = tvl_model
        self.cumulative_revenue = 0

    def calculate_revenue_from_contributions(self, contributions: List[TVLContribution], month: int) -> Dict[str, float]:
        """Calculate revenue from a list of TVL contributions using their individual revenue rates."""
        # Initialize all TVL types with zero
        revenue_by_type = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        for contribution in contributions:
            if contribution.active:
                revenue = contribution.calculate_revenue(month)
                revenue_by_type[contribution.tvl_type] += revenue
        
        return revenue_by_type