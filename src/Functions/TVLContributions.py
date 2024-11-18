from dataclasses import dataclass, field
from typing import Optional, Callable, List
import math

@dataclass
class TVLContribution:
    id: int
    tvl_type: str  # 'ProtocolLocked', 'Contracted', 'Organic', 'Boosted'
    amount_usd: float
    start_month: int
    active: bool = True
    revenue_rate: float = 0.0  # Annual revenue rate as a decimal
    accumulated_revenue: float = 0.0
    exit_condition: Optional[Callable[['TVLContribution', int], bool]] = None
    end_month: Optional[int] = None  # Applicable for Contracted TVL
    decay_rate: Optional[float] = None  # Applicable for Organic TVL
    expected_boost_rate: Optional[float] = None  # Applicable for Boosted TVL (annual APR)

    def calculate_revenue(self, month: int) -> float:
        """Calculate and accumulate revenue based on the revenue rate."""
        if not self.active:
            return 0.0
        monthly_rate = (1 + self.revenue_rate) ** (1 / 12) - 1  # Compound interest
        revenue = self.amount_usd * monthly_rate
        self.accumulated_revenue += revenue
        return revenue

    def update_amount(self, month: int):
        """Update the amount_usd based on specific TVL type behaviors."""
        if self.tvl_type == 'Organic' and self.decay_rate:
            # Apply decay
            self.amount_usd *= (1 - self.decay_rate)
            if self.amount_usd < 0:
                self.amount_usd = 0
            # Check exit condition after updating amount
            self.check_exit(month)

    def check_exit(self, month: int):
        """Check if the TVL should exit based on its exit condition."""
        if not self.active:
            return
        if self.exit_condition and self.exit_condition(self, month):
            self.active = False
            self.on_exit(month)

    def on_exit(self, month: int):
        """Handle actions upon exiting the TVL."""
        print(f"{self.tvl_type} TVL {self.id} has exited at month {month}.")
        # Additional logic can be added here if needed

    def get_state(self) -> dict:
        """Return the current state of the contribution."""
        return {
            'id': self.id,
            'tvl_type': self.tvl_type,
            'amount_usd': self.amount_usd,
            'active': self.active,
            'accumulated_revenue': self.accumulated_revenue,
        } 

@dataclass
class TVLContributionHistory:
    contributions: list[TVLContribution] = field(default_factory=list)
    history: dict[int, list[dict]] = field(default_factory=dict)
    
    def add_contribution(self, contribution: TVLContribution):
        """Add a new TVL contribution to the history."""
        self.contributions.append(contribution)
    
    def get_active_contributions(self) -> list[TVLContribution]:
        """Return a list of all active contributions."""
        return [c for c in self.contributions if c.active]
    
    def calculate_total_tvl(self) -> float:
        """Calculate the sum of all active TVL amounts."""
        return sum(c.amount_usd for c in self.get_active_contributions())
    
    def update_all(self, month: int):
        """Update all active contributions for the given month."""
        for contribution in self.get_active_contributions():
            contribution.update_amount(month)
            contribution.check_exit(month)
    
    def calculate_total_revenue(self, month: int) -> float:
        """Calculate total revenue from all active contributions for the month."""
        return sum(c.calculate_revenue(month) for c in self.get_active_contributions())
        
    def record_state(self, month: int, contributions: list[TVLContribution]):
        """Record the state of all contributions for a given month."""
        self.history[month] = [contrib.get_state() for contrib in contributions]
    
    def get_history(self, month: int) -> list[dict]:
        """Get the recorded state of all contributions for a given month."""
        return self.history.get(month, [])