from typing import Dict, List
from .TVLContributions import TVLContribution
from src.Data.deal import Deal, initialize_deals, get_active_deals
import random

class TVLLoader:
    def __init__(self, tvl_model):
        self.tvl_model = tvl_model
        self.id_counter = 1
        self.deals = initialize_deals()
    
    def load_initial_contributions(self):
        """Load initial contributions from unified deals."""
        # Convert deals with TVL components into TVL contributions
        for deal in self.deals:
            if deal.tvl_amount > 0:
                config = {
                    'amount_usd': deal.tvl_amount,
                    'start_month': deal.start_month,
                    'revenue_rate': deal.tvl_revenue_rate,
                    'duration_months': deal.tvl_duration_months,
                    'counterparty': deal.counterparty,
                    'category': deal.tvl_category
                }
                
                # Create contribution from deal
                contrib = self._create_contribution('Contracted', config)
                self.tvl_model.contributions.append(contrib)
                self.id_counter += 1

    def add_new_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
        """Add a new contribution during simulation."""
        contrib = self._create_contribution(tvl_type, config)
        self.tvl_model.contributions.append(contrib)
        self.id_counter += 1
        return contrib

    def _create_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
        """Create a TVL contribution based on type and config."""
        base_params = {
            'id': self.id_counter,
            'tvl_type': tvl_type,
            'amount_usd': config['amount_usd'],
            'start_month': config['start_month'],
            'revenue_rate': config.get('revenue_rate', 0.0)
        }
        
        if tvl_type == 'Contracted':
            base_params.update({
                'end_month': config['start_month'] + config['duration_months'],
                'exit_condition': self.tvl_model.contract_end_condition,
                'counterparty': config.get('counterparty', 'Unknown'),
                'category': config.get('category', 'unknown')
            })
        elif tvl_type == 'Organic':
            base_params.update({
                'decay_rate': config.get('decay_rate', 0.01),
                'exit_condition': self.tvl_model.decay_exit_condition
            })
        elif tvl_type == 'Boosted':
            base_params.update({
                'expected_boost_rate': config.get('expected_boost_rate', 0.05),
                'exit_condition': self.tvl_model.boosted_exit_condition
            })
        
        return TVLContribution(**base_params)

    def add_monthly_contracted_tvl(self, month: int) -> None:
        """Add new monthly contracted TVL after month 3."""
        if month <= 3:
            return
        
        # Create new deals for monthly TVL additions
        volatile_deal = Deal(
            deal_id=f"VOL_{month:03d}",
            counterparty=f"MonthlyVolatile_{month}",
            start_month=month,
            tvl_amount=7_500_000,
            tvl_revenue_rate=0.045,
            tvl_duration_months=6,
            tvl_category="volatile"
        )
        
        lending_deal = Deal(
            deal_id=f"LEND_{month:03d}",
            counterparty=f"MonthlyLending_{month}",
            start_month=month,
            tvl_amount=12_500_000,
            tvl_revenue_rate=0.01,
            tvl_duration_months=6,
            tvl_category="lending"
        )
        
        # Add deals to the deals list
        self.deals.extend([volatile_deal, lending_deal])
        
        # Create and add corresponding TVL contributions
        for deal in [volatile_deal, lending_deal]:
            config = {
                'amount_usd': deal.tvl_amount,
                'start_month': deal.start_month,
                'revenue_rate': deal.tvl_revenue_rate,
                'duration_months': deal.tvl_duration_months,
                'counterparty': deal.counterparty,
                'category': deal.tvl_category
            }
            self.add_new_contribution('Contracted', config)