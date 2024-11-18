from dataclasses import dataclass, field
from typing import List, Dict
from src.Functions.TVLContributions import TVLContribution
from src.Functions.TVLLoader import TVLLoader

@dataclass
class TVLModelConfig:
    # Market parameters
    initial_move_tvl: float
    initial_canopy_tvl: float
    move_growth_rates: List[float]
    min_market_share: float
    market_share_decay_rate: float
    max_months: int = 60

class TVLModel:
    def __init__(self, config: TVLModelConfig):
        self.config = config
        self.contributions = []
        self.month = 0
        self.loader = TVLLoader(self)

    def add_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
        """Add a new contribution during simulation."""
        return self.loader.add_new_contribution(tvl_type, config)

    def step(self):
        """Advance the model by one month."""
        for contrib in self.contributions:
            if contrib.start_month <= self.month:
                contrib.update_amount(self.month)
                contrib.check_exit(self.month)
        self.month += 1

    def get_total_tvl(self) -> float:
        """Calculate total active TVL."""
        return sum(contrib.amount_usd for contrib in self.contributions if contrib.active)

    # Exit conditions
    def contract_end_condition(self, contribution: TVLContribution, month: int) -> bool:
        return month >= contribution.end_month

    def decay_exit_condition(self, contribution: TVLContribution, month: int) -> bool:
        return contribution.amount_usd <= 0

    def boosted_exit_condition(self, contribution: TVLContribution, month: int) -> bool:
        actual_boost_rate = self.get_actual_boost_rate(contribution, month)
        return actual_boost_rate < contribution.expected_boost_rate

    def get_actual_boost_rate(self, contribution: TVLContribution, month: int) -> float:
        # Placeholder for actual boost rate calculation
        return contribution.expected_boost_rate * max(0.5, 1 - 0.01 * month)