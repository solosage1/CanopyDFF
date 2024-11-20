from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict
import math
import random

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
    expected_boost_rate: Optional[float] = None  # Applicable for Boosted TVL
    counterparty: Optional[str] = None  # Added field for contracted TVL
    category: Optional[str] = None  # Added field for contracted TVL type

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
        if not self.active:
            return
        
        if self.tvl_type == 'Organic' and self.decay_rate:
            # Apply decay
            self.amount_usd *= (1 - self.decay_rate)
            if self.amount_usd < 0:
                self.amount_usd = 0
            # Check exit condition after updating amount
            self.check_exit(month)

    def check_exit(self, month: int) -> Optional['TVLContribution']:
        """Check if contract should exit and handle renewal."""
        if not self.active or self.tvl_type != 'Contracted':
            return None
        
        # Only process contracts ending this specific month
        if month == self.end_month:
            if random.random() < 0.5:  # 50% renewal chance
                return TVLContribution(
                    id=self.id + 1000,
                    tvl_type=self.tvl_type,
                    amount_usd=self.amount_usd,
                    start_month=month,
                    revenue_rate=self.revenue_rate,
                    end_month=month + 6,
                    exit_condition=self.exit_condition,
                    counterparty=self.counterparty,
                    category=self.category
                )
            else:
                self.active = False
                print(f"Contract {self.id} ({self.counterparty}) ended at month {month}")
        
        return None

    def on_exit(self, month: int):
        """Handle actions upon exiting the TVL."""
        print(f"{self.tvl_type} TVL {self.id} has exited at month {month}.")
        # Additional logic can be added here if needed

    def renew_contract(self, month: int) -> Optional['TVLContribution']:
        """Attempt to renew the contract with 50% probability."""
        if self.tvl_type != 'Contracted':
            return None
        
        if random.random() < 0.5:  # 50% renewal rate
            return TVLContribution(
                id=self.id + 1000,  # New ID for renewed contract
                tvl_type=self.tvl_type,
                amount_usd=self.amount_usd,
                start_month=month,
                revenue_rate=self.revenue_rate,
                end_month=month + 6,  # 6-month duration
                exit_condition=self.exit_condition,
                counterparty=self.counterparty,
                category=self.category
            )
        return None

    def get_state(self) -> dict:
        """Return the current state of the contribution."""
        return {
            'id': self.id,
            'tvl_type': self.tvl_type,
            'amount_usd': self.amount_usd,
            'active': self.active,
            'accumulated_revenue': self.accumulated_revenue,
            'counterparty': self.counterparty,
            'category': self.category
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
        # Process exits and renewals
        new_contracts = []
        for contribution in self.get_active_contributions():
            renewed = contribution.check_exit(month)
            if renewed:
                new_contracts.append(renewed)
            contribution.update_amount(month)
        
        # Add any renewed contracts
        self.contributions.extend(new_contracts)
        
        # Add monthly new TVL
        self.tvl_model.loader.add_monthly_contracted_tvl(month)
    
    def calculate_total_revenue(self, month: int) -> float:
        """Calculate total revenue from all active contributions for the month."""
        return sum(c.calculate_revenue(month) for c in self.get_active_contributions())
        
    def record_state(self, month: int, contributions: List[TVLContribution]) -> None:
        """Record the state of all contributions for a given month."""
        self.history[month] = [
            {
                'amount_usd': c.amount_usd,
                'tvl_type': c.tvl_type,
                'active': c.active
            }
            for c in contributions
        ]
    
    def get_history(self, month: int) -> List[Dict]:
        """Get the recorded state for a given month."""
        return self.history.get(month, [])