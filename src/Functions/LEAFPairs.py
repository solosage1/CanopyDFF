from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict

@dataclass
class LEAFPairDeal:
    counterparty: str
    amount_usd: float
    num_leaf_tokens: float
    start_month: int
    duration_months: int
    leaf_percentage: float    # Target LEAF ratio (0 to 0.5)
    base_concentration: float
    max_concentration: float

    # Balances (initialized to zero)
    leaf_balance: float = 0.0
    other_balance: float = 0.0

class LEAFPairsConfig:
    # Define any configuration parameters if needed
    pass

class LEAFPairsModel:
    def __init__(self, config: LEAFPairsConfig, deals: List[LEAFPairDeal]):
        self.config = config
        self.deals = deals
        self.balance_history = defaultdict(list)
        self._initialize_deals()

    def _initialize_deals(self):
        for deal in self.deals:
            # Initialize balances based on leaf_percentage
            leaf_investment = deal.amount_usd * deal.leaf_percentage
            deal.num_leaf_tokens = leaf_investment / 1.0  # Assuming initial LEAF price is $1.0
            deal.leaf_balance = deal.num_leaf_tokens
            deal.other_balance = deal.amount_usd - leaf_investment

    def update_deals(self, month: int, leaf_price: float):
        """Update active deals for the given month."""
        active_deals = self.get_active_deals(month)
        for deal in active_deals:
            # Placeholder for deal update logic
            pass  # Implement the logic as needed
        self._record_state(month)

    def get_active_deals(self, month: int) -> List[LEAFPairDeal]:
        """Return deals that are active in the given month."""
        return [
            deal for deal in self.deals
            if deal.start_month <= month < deal.start_month + deal.duration_months
        ]

    def get_total_liquidity(self, month: int, leaf_price: float) -> float:
        """Calculate the total liquidity provided by LEAF pairs."""
        if leaf_price is None:
            raise ValueError("leaf_price cannot be None")

        total_liquidity = 0.0
        active_deals = self.get_active_deals(month)
        for deal in active_deals:
            leaf_value = deal.leaf_balance * leaf_price
            other_value = deal.other_balance
            total_liquidity += leaf_value + other_value
        return total_liquidity

    def _record_state(self, month: int):
        """Record the state of balances for the given month."""
        self.balance_history[month] = [
            (deal.counterparty, deal.leaf_balance, deal.other_balance)
            for deal in self.get_active_deals(month)
        ]

    def add_deal(self, deal: LEAFPairDeal) -> None:
        """Add a new deal to the model."""
        # Validate the deal
        self._validate_deal(deal)
        self.deals.append(deal)

    def _validate_deal(self, deal: LEAFPairDeal) -> None:
        """Validate the inputs of a new deal."""
        if not 0 <= deal.leaf_percentage <= 0.5:
            raise ValueError("LEAF percentage must be between 0% and 50%")
        if not 0 < deal.base_concentration <= 1:
            raise ValueError("Concentration must be between 0% and 100%")
        if any(d.counterparty == deal.counterparty for d in self.deals):
            raise ValueError(f"Deal with {deal.counterparty} already exists")
