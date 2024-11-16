from dataclasses import dataclass
import math

@dataclass
class BoostedTVLConfig:
    initial_boost_share: float        # Initial boost share (e.g., 10%)
    boost_growth_rate: float          # Growth rate for boost
    max_months: int = 60              # Maximum number of months

class BoostedTVLModel:
    def __init__(self, config: BoostedTVLConfig):
        self.config = config
        self.boosted_tvl_history = []
        self.previous_boosted_tvl = 0.0

    def get_boosted_tvl(self, month: int, canopy_tvl: float, move_tvl: float, is_active: bool) -> float:
        """Calculate TVL boosted by Canopy (excluding direct Canopy TVL)."""
        if not is_active:
            self.boosted_tvl_history.append(0.0)
            return 0.0

        # Available TVL for boosting (excluding Canopy TVL)
        available_tvl = move_tvl - canopy_tvl

        # Calculate boost share using sigmoid function
        boost_share = self._calculate_boost_share(month)

        # Calculate boosted TVL
        boosted_tvl = available_tvl * boost_share

        # Ensure total Canopy impact doesn't exceed Move TVL
        boosted_tvl = min(boosted_tvl, available_tvl)

        # Record boosted TVL
        self.boosted_tvl_history.append(boosted_tvl)

        # Update previous boosted TVL for growth rate calculation
        self.previous_boosted_tvl = boosted_tvl

        return boosted_tvl

    def _calculate_boost_share(self, month: int) -> float:
        """Calculate boost share using a sigmoid growth function."""
        normalized_time = (month / self.config.max_months) * 12 - 6  # Example normalization
        sigmoid = 1 / (1 + math.exp(-self.config.boost_growth_rate * normalized_time))
        return self.config.initial_boost_share * sigmoid

    def get_total_canopy_impact(self, month: int, canopy_tvl: float) -> float:
        """Calculate the total canopy impact for the given month."""
        if month < len(self.boosted_tvl_history):
            boosted_tvl = self.boosted_tvl_history[month]
            total_impact = canopy_tvl + boosted_tvl
            return total_impact
        else:
            return canopy_tvl

    def get_annual_boosted_growth_rate(self, month: int) -> float:
        """Calculate the annual boosted TVL growth rate for the given month."""
        if month == 0:
            return 0.0  # No growth in the first month
        if month >= len(self.boosted_tvl_history):
            current_boosted_tvl = self.previous_boosted_tvl
        else:
            current_boosted_tvl = self.boosted_tvl_history[month]

        previous_boosted_tvl = self.boosted_tvl_history[month - 1] if month - 1 < len(self.boosted_tvl_history) else self.previous_boosted_tvl

        if previous_boosted_tvl == 0:
            return 0.0  # Avoid division by zero

        growth_rate = (current_boosted_tvl - previous_boosted_tvl) / previous_boosted_tvl
        return growth_rate * 12  # Annualize the monthly growth rate 