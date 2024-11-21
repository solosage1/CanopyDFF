from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
from src.Data.deal import Deal, get_active_deals
from src.Functions.TVLContributions import TVLContribution
import logging

@dataclass
class TVLModelConfig:
    """Configuration for TVL model."""
    max_months: int = 48
    initial_tvl: float = 0.0
    revenue_rates: Dict[str, float] = None
    
    def __post_init__(self):
        if self.revenue_rates is None:
            # These are annual rates that will be converted to monthly
            self.revenue_rates = {
                'ProtocolLocked': 0.04,  # 4% annual revenue rate
                'Contracted': 0.025,     # 2.5% annual revenue rate
                'Organic': 0.02,         # 2% annual revenue rate
                'Boosted': 0.03          # 3% annual revenue rate
            }

class TVLModel:
    """Model for tracking and calculating Total Value Locked (TVL)."""
    
    def __init__(self, config: TVLModelConfig):
        self.config = config
        self.current_month = 0
        self.contributions: List[TVLContribution] = []
        
        # Track current TVL by type
        self.tvl_by_type: Dict[str, float] = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        # Historical tracking
        self.tvl_history: Dict[int, float] = defaultdict(float)
        self.tvl_by_type_history: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.contribution_history: Dict[int, List[TVLContribution]] = {}
        
        logging.debug(f"Initialized TVL Model with config: {config}")
    
    def step(self):
        """Process one time step in the TVL model."""
        self.current_month += 1
        
        # Reset TVL amounts for the new month
        self.tvl_by_type = {k: 0.0 for k in self.tvl_by_type}
        
        # Process active contributions with decay
        for contribution in self.contributions:
            if not self._is_contribution_active(contribution):
                continue
                
            current_amount = contribution.get_current_amount(self.current_month)
            self.tvl_by_type[contribution.tvl_type] += current_amount
            
        # Record history
        self._record_state()
        
        logging.debug(f"Month {self.current_month} TVL: ${sum(self.tvl_by_type.values()):,.2f}")
    
    def _is_contribution_active(self, contribution: TVLContribution) -> bool:
        """Check if a contribution is active for the current month."""
        return (contribution.active and 
                contribution.start_month <= self.current_month and 
                (not contribution.end_month or self.current_month < contribution.end_month))
    
    def _record_state(self):
        """Record the current state in history."""
        # Record TVL amounts
        total_tvl = sum(self.tvl_by_type.values())
        self.tvl_history[self.current_month] = total_tvl
        self.tvl_by_type_history[self.current_month] = self.tvl_by_type.copy()
        
        # Record contributions (deep copy to preserve state)
        self.contribution_history[self.current_month] = [
            TVLContribution(
                id=c.id,
                counterparty=c.counterparty,
                amount_usd=c.amount_usd,
                revenue_rate=c.revenue_rate,
                start_month=c.start_month,
                end_month=c.end_month,
                tvl_type=c.tvl_type,
                active=c.active
            ) for c in self.contributions
        ]
    
    def get_tvl_at_month(self, month: int) -> Optional[float]:
        """Get total TVL for a specific month."""
        return self.tvl_history.get(month)
    
    def get_tvl_by_type_at_month(self, month: int) -> Optional[Dict[str, float]]:
        """Get TVL breakdown by type for a specific month."""
        return self.tvl_by_type_history.get(month)
    
    def get_current_tvl(self) -> float:
        """Get current total TVL."""
        return sum(self.tvl_by_type.values())
    
    def get_current_tvl_by_type(self) -> Dict[str, float]:
        """Get current TVL breakdown by type."""
        return self.tvl_by_type.copy()
    
    def add_contribution(self, contribution: TVLContribution) -> None:
        """
        Add a TVL contribution.
        
        Args:
            contribution: TVL contribution to add
        """
        self.contributions.append(contribution)
    
    def get_state(self) -> Dict:
        """Get current state with detailed value breakdown."""
        # Calculate total TVL from tvl_by_type instead of using non-existent total_tvl attribute
        total_value = sum(self.tvl_by_type.values())
        
        print(f"\nTotal Value Breakdown (Month {self.current_month}):")
        print(f"- Protocol Locked TVL: ${self.tvl_by_type['ProtocolLocked']:,.2f}")
        print(f"- Contracted TVL: ${self.tvl_by_type['Contracted']:,.2f}")
        print(f"- Organic TVL: ${self.tvl_by_type['Organic']:,.2f}")
        print(f"- Boosted TVL: ${self.tvl_by_type['Boosted']:,.2f}")
        print(f"- Total TVL: ${total_value:,.2f}")
        
        return {
            'current_month': self.current_month,
            'total_tvl': total_value,
            'tvl_by_type': self.tvl_by_type.copy(),
            'tvl_history': dict(self.tvl_history),
            'tvl_by_type_history': {
                month: cats.copy() 
                for month, cats in self.tvl_by_type_history.items()
            }
        }
    
    def calculate_monthly_revenue(self, contributions: List[TVLContribution], month: int) -> Dict[str, float]:
        """Calculate monthly revenue from TVL contributions"""
        revenue_by_category = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        for contribution in contributions:
            if not contribution.active:
                logging.debug(f"Skipping inactive contribution ID {contribution.id}")
                continue
                
            if month < contribution.start_month or (contribution.end_month and month >= contribution.end_month):
                logging.debug(f"Skipping out-of-range contribution ID {contribution.id}")
                continue
                
            # Calculate this contribution's revenue using its specific rate
            contribution_revenue = contribution.calculate_revenue()
            
            logging.debug(
                f"Processing contribution {contribution.id}:"
                f"\n  Type: {contribution.tvl_type}"
                f"\n  Amount: ${contribution.amount_usd:,.2f}"
                f"\n  Rate: {contribution.revenue_rate:.2%}"
                f"\n  Revenue: ${contribution_revenue:,.2f}"
            )
            
            revenue_by_category[contribution.tvl_type] += contribution_revenue
        
        return revenue_by_category