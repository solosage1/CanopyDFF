from dataclasses import dataclass, field
from typing import List, Dict
from src.Functions.TVLContributions import TVLContribution
from collections import defaultdict

@dataclass
class RevenueModelConfig:
    pass

class RevenueModel:
    def __init__(self, config: RevenueModelConfig, tvl_model):
        self.tvl_model = tvl_model
        self.cumulative_revenue = 0.0
        self.revenue_history = []

    def calculate_revenue(self, month: int) -> Dict[str, float]:
        revenue_by_type = defaultdict(float)
        tvl_by_type = defaultdict(float)
        
        for contrib in self.tvl_model.contributions:
            if contrib.active and contrib.start_month <= month:
                revenue = contrib.calculate_revenue(month)
                revenue_by_type[contrib.tvl_type] += revenue
                revenue_by_type['Total'] += revenue
                tvl_by_type[contrib.tvl_type] += contrib.amount_usd

        # Calculate weighted average rates
        weighted_rates = {}
        for tvl_type in tvl_by_type:
            if tvl_by_type[tvl_type] > 0:
                weighted_rates[tvl_type] = (
                    revenue_by_type[tvl_type] * 12 / tvl_by_type[tvl_type]
                )
            else:
                weighted_rates[tvl_type] = 0.0

        self.cumulative_revenue += revenue_by_type['Total']
        self.revenue_history.append({
            'revenue': revenue_by_type,
            'weighted_rates': weighted_rates
        })
        
        return revenue_by_type