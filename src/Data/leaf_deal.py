from src.Functions.LEAFPairs import LEAFPairDeal
from typing import List

def initialize_deals() -> List[LEAFPairDeal]:
    """Initialize deals with starting concentrations."""
    return [
        LEAFPairDeal(
            counterparty="Move",
            amount_usd=1_500_000,
            num_leaf_tokens=0,
            start_month=1,
            duration_months=60,
            leaf_percentage=0.35,
            base_concentration=0.5,
            max_concentration=0.8,
            leaf_balance=0.0,
            other_balance=0.0
        ),
        # Add additional deals as needed
    ]