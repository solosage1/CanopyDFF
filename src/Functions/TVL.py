from dataclasses import dataclass, field
from typing import List, Dict
from src.Functions.TVLContributions import TVLContribution
from src.Functions.TVLLoader import TVLLoader
import random

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
        self.contributions: List[TVLContribution] = []
        self.month: int = 0
        self.loader = TVLLoader(self)
        self.initialize_contributions()

    def initialize_contributions(self):
        # Initialize contributions based on the configuration
        pass

    def add_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
        """Add a new contribution during simulation."""
        return self.loader.add_new_contribution(tvl_type, config)

    def step(self):
        """Process one month of TVL changes."""
        # First add new monthly TVL
        self.loader.add_monthly_contracted_tvl(self.month)
        
        # Then process existing contracts
        new_contracts = []
        expired_contracts = []
        
        for contrib in self.contributions:
            if contrib.active:
                if contrib.tvl_type == 'Contracted' and self.month == contrib.end_month:
                    # Process contract renewal
                    if random.random() < 0.5:  # 50% renewal chance
                        new_contract = TVLContribution(
                            id=contrib.id + 1000,
                            tvl_type='Contracted',
                            amount_usd=contrib.amount_usd,
                            start_month=self.month,
                            revenue_rate=contrib.revenue_rate,
                            end_month=self.month + 6,
                            counterparty=contrib.counterparty,
                            category=contrib.category
                        )
                        new_contracts.append(new_contract)
                        print(f"Contract renewed: ${contrib.amount_usd:,.0f} from {contrib.counterparty}")
                    contrib.active = False
                    expired_contracts.append(contrib)
                    print(f"Contract expired: ${contrib.amount_usd:,.0f} from {contrib.counterparty}")
                
                # Update amounts for active contributions
                contrib.update_amount(self.month)
        
        # Add new contracts
        self.contributions.extend(new_contracts)
        
        # Increment month
        self.month += 1
        
        return new_contracts, expired_contracts

    def get_total_tvl(self) -> float:
        """Calculate total active TVL."""
        return sum(c.amount_usd for c in self.contributions if c.active)

    def get_tvl_by_category(self) -> dict:
        """Get TVL breakdown by category."""
        categories = {'volatile': 0, 'lending': 0}
        for c in self.contributions:
            if c.active and c.category:
                categories[c.category] += c.amount_usd
        return categories

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

    def get_active_contributions(self, month: int) -> List[TVLContribution]:
        """Return a list of all active contributions for the given month."""
        return [c for c in self.contributions if c.active]