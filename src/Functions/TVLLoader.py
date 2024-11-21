from typing import Dict, List, TYPE_CHECKING

# Prevent circular imports while still getting type hints
if TYPE_CHECKING:
    from src.Functions.TVL import TVLModel

from .TVLContributions import TVLContribution
from src.Data.deal import Deal, initialize_deals, get_active_deals
import random
import logging

class TVLLoader:
    def __init__(self, tvl_model: 'TVLModel', organic_config: Dict):
        """Initialize the TVLLoader with the TVLModel."""
        self.tvl_model = tvl_model
        self.id_counter = 1
        self.deals = initialize_deals()
        
        # Use configuration from simulation
        self.organic_ratio = organic_config['conversion_ratio']
        self.organic_decay_rate = organic_config['decay_rate']
        self.organic_duration = organic_config['duration_months']
        
        # Load initial contributions
        initial_contributions = self.load_initial_contributions(self.deals)
        for contribution in initial_contributions:
            self.tvl_model.add_contribution(contribution)
            # Add organic contribution for initial TVL
            if contribution.tvl_type == "Contracted":
                self._add_organic_contribution(contribution)
    
    def process_month(self, month: int) -> None:
        """Process TVL changes for the current month."""
        # Add monthly contracted TVL after month 3
        self.add_monthly_contracted_tvl(month)
        
        # Step the TVL model
        self.tvl_model.step()
        
        # Log monthly TVL state
        tvl_state = self.tvl_model.get_current_tvl_by_type()
        logging.debug(f"\nMonth {month} TVL Breakdown:")
        for tvl_type, amount in tvl_state.items():
            logging.debug(f"- {tvl_type}: ${amount:,.2f}")
    
    def load_initial_contributions(self, deals: List[Deal]) -> List[TVLContribution]:
        """Load initial TVL contributions from deals."""
        contributions = []
        for deal in deals:
            if deal.tvl_amount > 0 and deal.tvl_type != 'none':
                end_month = deal.start_month + deal.tvl_duration_months
                contribution = TVLContribution(
                    id=self.id_counter,
                    tvl_type=deal.tvl_type,
                    amount_usd=deal.tvl_amount,
                    revenue_rate=deal.tvl_revenue_rate,
                    active=deal.tvl_active,
                    end_month=end_month,
                    start_month=deal.start_month,
                    counterparty=deal.counterparty
                )
                logging.debug(
                    f"Creating TVL Contribution:"
                    f"\n  ID: {self.id_counter}"
                    f"\n  Type: {deal.tvl_type}"
                    f"\n  Amount: ${deal.tvl_amount:,.2f}"
                    f"\n  Start Month: {deal.start_month}"
                    f"\n  End Month: {end_month}"
                )
                self.id_counter += 1
                contributions.append(contribution)
        logging.info(f"Loaded {len(contributions)} initial TVL contributions")
        return contributions
    
    def _add_organic_contribution(self, source_contribution: TVLContribution) -> None:
        """Create an organic TVL contribution based on a percentage of the source."""
        organic_amount = source_contribution.amount_usd * self.organic_ratio
        
        end_month = source_contribution.start_month + self.organic_duration
        
        organic_contribution = TVLContribution(
            id=self.id_counter,
            tvl_type="Organic",
            counterparty=f"Organic_{source_contribution.counterparty}",
            amount_usd=organic_amount,
            start_month=source_contribution.start_month,
            end_month=end_month,
            revenue_rate=self.tvl_model.config.revenue_rates['Organic'],
            active=True,
            decay_rate=self.organic_decay_rate
        )
        
        self.id_counter += 1
        self.tvl_model.add_contribution(organic_contribution)
        logging.debug(
            f"Added organic contribution:"
            f"\n  ID: {organic_contribution.id}"
            f"\n  Amount: ${organic_amount:,.2f}"
            f"\n  Based on: {source_contribution.counterparty}"
            f"\n  Decay Rate: {self.organic_decay_rate:.1%}/month"
            f"\n  Duration: {self.organic_duration} months"
        )
    
    def add_monthly_contracted_tvl(self, month: int) -> None:
        """Add new monthly contracted TVL after month 3."""
        if month <= 3:
            logging.debug(f"No monthly TVL additions for month {month}")
            return
        
        # Create new deals for monthly TVL additions
        new_deal = Deal(
            deal_id=f"CONTRACT_{month:03d}",
            counterparty=f"MonthlyContract_{month}",
            start_month=month,
            tvl_amount=20_000_000,  # Combined amount
            tvl_revenue_rate=0.025,  # Average rate
            tvl_duration_months=6,
            tvl_type="Contracted"
        )
        
        # Add deal to the deals list
        self.deals.append(new_deal)
        logging.debug(f"Added new deal: {new_deal.deal_id} with TVL amount ${new_deal.tvl_amount}")
        
        # Create and add corresponding TVL contribution
        config = {
            'amount_usd': new_deal.tvl_amount,
            'start_month': new_deal.start_month,
            'revenue_rate': new_deal.tvl_revenue_rate,
            'duration_months': new_deal.tvl_duration_months,
            'counterparty': new_deal.counterparty
        }
        self.add_new_contribution('Contracted', config)
    
    def add_new_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
        """Add a new contribution during simulation."""
        contrib = self._create_contribution(tvl_type, config)
        self.tvl_model.add_contribution(contrib)
        
        # Add organic growth for contracted TVL
        if tvl_type == "Contracted":
            self._add_organic_contribution(contrib)
            
        logging.debug(f"Added new TVL Contribution ID {contrib.id} of type {tvl_type}")
        return contrib
    
    def _create_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
        """Create a TVL contribution based on type and config."""
        end_month = config['start_month'] + config['duration_months']
        
        contribution = TVLContribution(
            id=self.id_counter,
            counterparty=config['counterparty'],
            amount_usd=config['amount_usd'],
            revenue_rate=config.get('revenue_rate', 0.0),
            start_month=config['start_month'],
            end_month=end_month,
            tvl_type=tvl_type,
            active=True
        )
        self.id_counter += 1
        return contribution