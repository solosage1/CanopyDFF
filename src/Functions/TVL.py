from dataclasses import dataclass
from typing import Tuple, List
import math

@dataclass
class TVLModelConfig:
    initial_move_tvl: float                    # Initial Move TVL in USD
    initial_canopy_tvl: float                  # Initial Canopy TVL in USD
    move_growth_rates: List[float]             # Annual growth rates for Move by year
    min_market_share: float                    # Minimum market share floor
    market_share_decay_rate: float             # Rate at which market share declines

class TVLModel:
    def __init__(self, config: TVLModelConfig):
        self.config = config
        self._initial_market_share = config.initial_canopy_tvl / config.initial_move_tvl
        self._validate_config()

    def get_tvls(self, month: int) -> Tuple[float, float]:
        """Returns (move_tvl, canopy_tvl)"""
        move_tvl = self._calculate_move_tvl(month)
        canopy_share = self._calculate_canopy_share(month)
        canopy_tvl = move_tvl * canopy_share

        return move_tvl, canopy_tvl

    def _calculate_move_tvl(self, month: int) -> float:
        """Calculate the total Move TVL for the given month."""
        year = month // 12
        month_in_year = month % 12

        if year >= len(self.config.move_growth_rates):
            # Apply the last growth rate for remaining months
            annual_rate = self.config.move_growth_rates[-1]
        else:
            # Interpolate between current and next year's rate if available
            current_rate = self.config.move_growth_rates[year]
            if year + 1 < len(self.config.move_growth_rates):
                next_rate = self.config.move_growth_rates[year + 1]
                # Linear interpolation between rates based on month
                annual_rate = current_rate + (next_rate - current_rate) * (month_in_year / 12)
            else:
                annual_rate = current_rate

        monthly_rate = (1 + annual_rate) ** (1/12) - 1  # Monthly growth rate
        cumulative_months = month  # Total months since start
        move_tvl = self.config.initial_move_tvl * ((1 + monthly_rate) ** cumulative_months)

        return move_tvl

    def _calculate_canopy_share(self, month: int) -> float:
        """Calculate Canopy's market share for the given month."""
        decay = math.exp(-self.config.market_share_decay_rate * month / 12)
        share = (
            self.config.min_market_share +
            (self._initial_market_share - self.config.min_market_share) * decay
        )
        return max(share, self.config.min_market_share)

    def _validate_config(self) -> None:
        if self.config.initial_move_tvl <= 0:
            raise ValueError("Initial Move TVL must be positive")
        if self.config.initial_canopy_tvl < 0:
            raise ValueError("Initial Canopy TVL cannot be negative")
        if self.config.initial_canopy_tvl > self.config.initial_move_tvl:
            raise ValueError("Canopy TVL cannot exceed Move TVL")
        if not self.config.move_growth_rates:
            raise ValueError("Must provide at least one growth rate")
        if any(r < -1 for r in self.config.move_growth_rates):
            raise ValueError("Growth rates cannot be less than -100%") 