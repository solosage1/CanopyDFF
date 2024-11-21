from dataclasses import dataclass, field
from typing import Dict, List, Optional
from src.Data.deal import Deal

@dataclass
class TVLContribution:
    """Represents a single TVL contribution."""
    id: int
    counterparty: str
    amount_usd: float
    revenue_rate: float
    start_month: int
    end_month: Optional[int]
    tvl_type: str
    active: bool = True
    decay_rate: float = 0.0  # Monthly decay rate (e.g., 0.05 for 5% monthly decay)
    initial_amount: float = field(init=False)
    
    def __post_init__(self):
        self.initial_amount = self.amount_usd
    
    def get_current_amount(self, current_month: int) -> float:
        """Calculate current amount considering decay if applicable."""
        if not self.active or current_month < self.start_month:
            return 0.0
            
        if self.end_month and current_month >= self.end_month:
            return 0.0
            
        if self.decay_rate == 0.0:
            return self.amount_usd
            
        months_elapsed = current_month - self.start_month
        decay_factor = (1 - self.decay_rate) ** months_elapsed
        return self.initial_amount * decay_factor
    
    def calculate_revenue(self) -> float:
        """Calculate monthly revenue for this contribution."""
        # Convert annual rate to monthly rate
        monthly_rate = self.revenue_rate / 12
        return self.amount_usd * monthly_rate