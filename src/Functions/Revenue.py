from dataclasses import dataclass

@dataclass
class RevenueModelConfig:
    # Initial TVL composition
    initial_volatile_share: float    # Initial % of TVL that is volatile
    target_volatile_share: float     # Target % of TVL that is volatile
    volatile_share_growth: float     # Growth rate for volatile TVL share

    # Revenue rates (annual)
    initial_volatile_rate: float     # Initial revenue rate for volatile TVL
    target_volatile_rate: float      # Target revenue rate for volatile TVL
    initial_stable_rate: float       # Initial revenue rate for stable TVL
    target_stable_rate: float        # Target revenue rate for stable TVL

    # Decay parameters
    share_growth_duration: int       # Duration over which volatile share grows to target (in months)

class RevenueModel:
    def __init__(self, config: RevenueModelConfig):
        self.config = config

    def calculate_revenue(self, month: int, tvl: float) -> tuple:
        """
        Calculate monthly revenue based on TVL and time since launch.

        Args:
            month: Number of months since start (0-based)
            tvl: Total TVL amount in USD

        Returns:
            A tuple containing:
                - Stable TVL Revenue (USD)
                - Volatile TVL Revenue (USD)
                - Total Revenue (USD)
        """
        # Calculate current TVL composition
        volatile_share = self._calculate_volatile_share(month)
        stable_share = 1 - volatile_share

        # Calculate current revenue rates
        volatile_rate = self._calculate_volatile_rate(month)
        stable_rate = self._calculate_stable_rate(month)

        # TVL allocations
        volatile_tvl = tvl * volatile_share
        stable_tvl = tvl * stable_share

        # Revenue calculations
        volatile_revenue = volatile_tvl * (volatile_rate / 12)  # Convert annual rate to monthly
        stable_revenue = stable_tvl * (stable_rate / 12)

        total_revenue = volatile_revenue + stable_revenue

        return stable_revenue, volatile_revenue, total_revenue

    def _calculate_volatile_share(self, month: int) -> float:
        """Calculate the volatile share of TVL for a given month."""
        if self.config.share_growth_duration == 0:
            return self.config.target_volatile_share

        progress = min(month / self.config.share_growth_duration, 1.0)
        volatile_share = (
            self.config.initial_volatile_share +
            (self.config.target_volatile_share - self.config.initial_volatile_share) * progress
        )
        return volatile_share

    def _calculate_volatile_rate(self, month: int) -> float:
        """Calculate annual revenue rate for volatile TVL."""
        if self.config.share_growth_duration == 0:
            return self.config.target_volatile_rate

        progress = min(month / self.config.share_growth_duration, 1.0)
        volatile_rate = (
            self.config.initial_volatile_rate +
            (self.config.target_volatile_rate - self.config.initial_volatile_rate) * progress
        )
        return volatile_rate

    def _calculate_stable_rate(self, month: int) -> float:
        """Calculate annual revenue rate for stable TVL."""
        if self.config.share_growth_duration == 0:
            return self.config.target_stable_rate

        progress = min(month / self.config.share_growth_duration, 1.0)
        stable_rate = (
            self.config.initial_stable_rate +
            (self.config.target_stable_rate - self.config.initial_stable_rate) * progress
        )
        return stable_rate