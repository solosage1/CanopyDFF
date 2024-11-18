from typing import Dict, List
from .TVLContributions import TVLContribution
from src.Data.initial_contributions import INITIAL_CONTRIBUTIONS

class TVLLoader:
    def __init__(self, tvl_model):
        self.tvl_model = tvl_model
        self.id_counter = 1
    
    def load_initial_contributions(self):
        """Load all initial contributions from config."""
        for tvl_type, contributions in INITIAL_CONTRIBUTIONS.items():
            for config in contributions:
                contrib = self._create_contribution(tvl_type, config)
                self.tvl_model.contributions.append(contrib)
                self.id_counter += 1
    
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
                'exit_condition': self.tvl_model.contract_end_condition
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