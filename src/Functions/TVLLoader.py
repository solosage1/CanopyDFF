from typing import Dict, List
from .TVLContributions import TVLContribution
from src.Data.initial_contributions import INITIAL_CONTRIBUTIONS, RAMP_SCHEDULE, COUNTERPARTIES
import random

class TVLLoader:
    def __init__(self, tvl_model):
        self.tvl_model = tvl_model
        self.id_counter = 1
    
    def load_initial_contributions(self):
        """Load initial contributions and ramp schedule."""
        # Load initial contributions
        for tvl_type, contributions in INITIAL_CONTRIBUTIONS.items():
            for config in contributions:
                contrib = self._create_contribution(tvl_type, config)
                self.tvl_model.contributions.append(contrib)
                self.id_counter += 1
        
        # Load ramp schedule
        for ramp in RAMP_SCHEDULE:
            if ramp['month'] <= 3:  # Only process first 3 months
                # Add volatile portion
                self.add_new_contribution('Contracted', {
                    'amount_usd': ramp['volatile'],
                    'start_month': ramp['month'],
                    'revenue_rate': 0.045,
                    'duration_months': 6,
                    'counterparty': random.choice(COUNTERPARTIES),
                    'category': 'volatile'
                })
                
                # Add lending portion
                self.add_new_contribution('Contracted', {
                    'amount_usd': ramp['lending'],
                    'start_month': ramp['month'],
                    'revenue_rate': 0.01,
                    'duration_months': 6,
                    'counterparty': random.choice(COUNTERPARTIES),
                    'category': 'lending'
                })
    
    def add_new_contribution(self, tvl_type: str, config: Dict):
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
        
        # Add $20M monthly ($7.5M volatile, $12.5M lending)
        self.add_new_contribution('Contracted', {
            'amount_usd': 7_500_000,
            'start_month': month,
            'revenue_rate': 0.045,
            'duration_months': 6,
            'counterparty': random.choice(COUNTERPARTIES),
            'category': 'volatile'
        })
        
        self.add_new_contribution('Contracted', {
            'amount_usd': 12_500_000,
            'start_month': month,
            'revenue_rate': 0.01,
            'duration_months': 6,
            'counterparty': random.choice(COUNTERPARTIES),
            'category': 'lending'
        })