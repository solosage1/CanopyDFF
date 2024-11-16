import math
from dataclasses import dataclass
from typing import Tuple

@dataclass
class TVLModelConfig:
    initial_move_tvl: float          # Initial Move TVL in USD
    initial_canopy_tvl: float        # Initial Canopy TVL in USD
    move_growth_rates: list[float]   # Annual growth rates for Move by year
    min_market_share: float          # Minimum market share floor
    market_share_decay_rate: float   # Rate at which market share declines
    initial_boost_share: float       # Initial boost share (e.g., 10%)
    boost_growth_rate: float         # Growth rate for boost

class BoostedTVLModel:
    def __init__(self, initial_boost_share: float, growth_rate: float, max_months: int = 60):
        self.initial_boost_share = initial_boost_share
        self.growth_rate = growth_rate
        self.max_months = max_months

    def get_boosted_tvl(self, month: int, canopy_tvl: float, move_tvl: float) -> float:
        """Calculate TVL boosted by Canopy (excluding direct Canopy TVL)"""
        # Available TVL for boosting (excluding Canopy TVL)
        available_tvl = move_tvl - canopy_tvl

        # Calculate boost share using sigmoid function
        boost_share = self._calculate_boost_share(month)

        # Calculate boosted TVL
        boosted_tvl = available_tvl * boost_share

        # Ensure total Canopy impact doesn't exceed Move TVL
        max_allowed_boost = available_tvl
        return min(boosted_tvl, max_allowed_boost)

    def _calculate_boost_share(self, month: int) -> float:
        normalized_time = (month / self.max_months * 12) - 6
        sigmoid = 1 / (1 + math.exp(-self.growth_rate * normalized_time))
        return self.initial_boost_share * (1 + sigmoid)

class TVLModel:
    def __init__(self, config: TVLModelConfig):
        self.config = config
        self._initial_market_share = config.initial_canopy_tvl / config.initial_move_tvl
        self._validate_config()

        self.boosted_model = BoostedTVLModel(
            initial_boost_share=config.initial_boost_share,
            growth_rate=config.boost_growth_rate,
            max_months=60
        )

    def get_tvls(self, month: int) -> Tuple[float, float, float]:
        """Returns (move_tvl, canopy_tvl, boosted_by_canopy_tvl)"""
        move_tvl = self._calculate_move_tvl(month)
        canopy_share = self._calculate_canopy_share(month)
        canopy_tvl = move_tvl * canopy_share
        boosted_tvl = self.boosted_model.get_boosted_tvl(month, canopy_tvl, move_tvl)

        return move_tvl, canopy_tvl, boosted_tvl

    def _calculate_move_tvl(self, month: int) -> float:
        year = month // 12
        month_in_year = month % 12

        if year >= len(self.config.move_growth_rates):
            cumulative_growth = 1.0
            for rate in self.config.move_growth_rates:
                cumulative_growth *= (1 + rate)
            return self.config.initial_move_tvl * cumulative_growth

        cumulative_growth = 1.0
        for i in range(year):
            cumulative_growth *= (1 + self.config.move_growth_rates[i])

        current_rate = self.config.move_growth_rates[year]
        monthly_rate = (1 + current_rate) ** (1/12) - 1
        current_year_growth = (1 + monthly_rate) ** month_in_year

        return self.config.initial_move_tvl * cumulative_growth * current_year_growth

    def _calculate_canopy_share(self, month: int) -> float:
        decay = math.exp(-self.config.market_share_decay_rate * month/12)
        share = (self.config.min_market_share + 
                (self._initial_market_share - self.config.min_market_share) * decay)
        return max(share, self.config.min_market_share)

    def _validate_config(self) -> None:
        if self.config.initial_move_tvl <= 0:
            raise ValueError("Initial Move TVL must be positive")
        if self.config.initial_canopy_tvl <= 0:
            raise ValueError("Initial Canopy TVL must be positive")
        if self.config.initial_canopy_tvl > self.config.initial_move_tvl:
            raise ValueError("Canopy TVL cannot exceed Move TVL")
        if not self.config.move_growth_rates:
            raise ValueError("Must provide at least one growth rate")
        if any(r < -1 for r in self.config.move_growth_rates):
            raise ValueError("Growth rates cannot be less than -100%") 