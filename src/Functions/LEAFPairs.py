from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import defaultdict
from .UniswapV2Math import UniswapV2Math
from src.Data.deal import Deal

@dataclass
class LEAFPairsConfig:
    """Configuration for LEAF pairs model."""
    pass

class LEAFPairsModel:
    def __init__(self, config: LEAFPairsConfig, deals: List[Deal]):
        self.config = config
        self.deals = [deal for deal in deals if deal.leaf_pair_amount > 0]
        self.balance_history = defaultdict(list)
        self.month = 0
        self._initialize_deals()

    def _initialize_deals(self):
        for deal in self.deals:
            # Initialize balances based on leaf_percentage
            leaf_investment = deal.leaf_pair_amount * deal.leaf_percentage
            deal.num_leaf_tokens = leaf_investment / 1.0  # Assuming initial LEAF price is $1.0
            deal.leaf_balance = deal.num_leaf_tokens
            deal.other_balance = deal.leaf_pair_amount - leaf_investment

    def update_deals(self, month: int, leaf_price: float):
        """Update active deals for the given month."""
        active_deals = self.get_active_deals(month)
        for deal in active_deals:
            # Placeholder for deal update logic
            pass  # Implement the logic as needed
        self._record_state(month)

    def get_active_deals(self, month: int) -> List[Deal]:
        """Return deals that are active in the given month."""
        return [
            deal for deal in self.deals
            if deal.start_month <= month < deal.start_month + deal.leaf_duration_months
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

    def add_deal(self, deal: Deal) -> None:
        """Add a new deal to the model."""
        if deal.leaf_pair_amount > 0:
            self._validate_deal(deal)
            self.deals.append(deal)

    def _validate_deal(self, deal: Deal) -> None:
        """Validate the inputs of a new deal."""
        if not 0 <= deal.leaf_percentage <= 0.5:
            raise ValueError("LEAF percentage must be between 0% and 50%")
        if not 0 < deal.leaf_base_concentration <= 1:
            raise ValueError("Concentration must be between 0% and 100%")
        if any(d.counterparty == deal.counterparty for d in self.deals):
            raise ValueError(f"Deal with {deal.counterparty} already exists")

    def get_liquidity_within_percentage(self, percentage: float, current_price: float, deal_index: int = None) -> Tuple[float, float]:
        active_deals = self.get_active_deals(self.month)
        if deal_index is not None:
            active_deals = [active_deals[deal_index]]
        
        total_leaf_within_range = 0.0
        total_other_within_range = 0.0
        
        for deal in active_deals:
            if deal.leaf_balance == 0:
                continue
                
            # Calculate current LEAF ratio
            total_value = (deal.leaf_balance * current_price) + deal.other_balance
            current_leaf_ratio = (deal.leaf_balance * current_price) / total_value
            
            # Set concentration levels based on LEAF ratio vs target
            leaf_heavy = current_leaf_ratio > deal.leaf_percentage
            
            # Get concentrations
            leaf_concentration = deal.leaf_base_concentration * 10 if leaf_heavy else 1.0
            other_concentration = 1.0 if leaf_heavy else deal.leaf_base_concentration * 10
            
            # Calculate liquidity using shared math
            leaf_amount, other_amount = UniswapV2Math.get_liquidity_within_range(
                x_reserve=deal.leaf_balance,
                y_reserve=deal.other_balance,
                current_price=current_price,
                price_range_percentage=percentage,
                x_concentration=leaf_concentration,
                y_concentration=other_concentration
            )
            
            total_leaf_within_range += leaf_amount
            total_other_within_range += other_amount
        
        return round(total_leaf_within_range, 8), round(total_other_within_range, 8)

    def get_leaf_liquidity(self) -> float:
        """Get the total amount of LEAF tokens in active liquidity pairs."""
        active_deals = self.get_active_deals(self.month)
        return sum(deal.leaf_balance for deal in active_deals)

    def get_usd_liquidity(self) -> float:
        """Get the total USD value in active liquidity pairs."""
        active_deals = self.get_active_deals(self.month)
        return sum(deal.other_balance for deal in active_deals)
