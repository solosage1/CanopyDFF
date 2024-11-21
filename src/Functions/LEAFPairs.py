from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import defaultdict
from .UniswapV2Math import UniswapV2Math
from src.Data.deal import Deal
import logging

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
            # Initialize using explicit LEAF tokens amount
            deal.leaf_balance = deal.leaf_tokens
            deal.other_balance = deal.leaf_pair_amount - (deal.leaf_tokens * 1.0)  # Assuming $1.0 initial price

    def update_deals(self, month: int, leaf_price: float) -> float:
        """Update active deals for the given month. Returns LEAF tokens to buy."""
        self.month = month
        active_deals = self.get_active_deals(month)
        
        # Calculate LEAF needed to reach target ratios
        leaf_needed = self.calculate_leaf_needed(leaf_price)
        
        # Record state
        self._record_state(month)
        
        return leaf_needed

    def calculate_leaf_needed(self, current_price: float) -> Tuple[Dict[str, float], float]:
        """Calculate how many LEAF tokens need to be bought to reach target ratios."""
        active_deals = self.get_active_deals(self.month)
        deal_deficits: Dict[str, float] = {}
        total_leaf_short = 0.0
        
        for deal in active_deals:
            # Calculate current and target LEAF value
            total_value = (deal.leaf_balance * current_price) + deal.other_balance
            current_leaf_value = deal.leaf_balance * current_price
            target_leaf_value = total_value * deal.target_ratio
            
            # Calculate shortage
            if current_leaf_value < target_leaf_value:
                leaf_short = (target_leaf_value - current_leaf_value) / current_price
                deal_deficits[deal.deal_id] = leaf_short
                total_leaf_short += leaf_short
        
        return deal_deficits, total_leaf_short

    def distribute_purchased_leaf(self, leaf_amount: float, deal_deficits: Dict[str, float]) -> None:
        """Distribute purchased LEAF to deals proportionally to their deficits."""
        total_deficit = sum(deal_deficits.values())
        if total_deficit == 0:
            return

        for deal_id, deficit in deal_deficits.items():
            # Find the deal
            deal = next(d for d in self.deals if d.deal_id == deal_id)
            
            # Calculate proportion of LEAF to give this deal
            proportion = deficit / total_deficit
            leaf_to_add = leaf_amount * proportion
            
            # Update deal balances
            deal.leaf_balance += leaf_to_add
            logging.info(f"Deal {deal_id} received {leaf_to_add:,.2f} LEAF")

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
        if not 0 <= deal.target_ratio <= 0.5:
            raise ValueError("Target ratio must be between 0% and 50%")
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
                # USDC-only pool: Use max concentration (8x)
                usdc_concentration = deal.leaf_max_concentration * 10  # 0.8 * 10 = 8x UniswapV2
                usdc_in_range = (deal.other_balance * percentage / 100.0) * usdc_concentration
                total_other_within_range += usdc_in_range
                continue
            
            # Calculate current LEAF ratio vs target
            total_value = (deal.leaf_balance * current_price) + deal.other_balance
            current_leaf_ratio = (deal.leaf_balance * current_price) / total_value
            target_ratio = deal.target_ratio
            
            # Determine concentration based on LEAF balance health
            if current_leaf_ratio < target_ratio * 0.9:  # Low on LEAF
                leaf_concentration = 1.0  # UniswapV2 base
                other_concentration = deal.leaf_max_concentration * 10  # 8x for USDC
            elif current_leaf_ratio > target_ratio * 1.1:  # Too much LEAF
                leaf_concentration = deal.leaf_max_concentration * 10  # 8x for LEAF
                other_concentration = 1.0  # UniswapV2 base for USDC
            else:  # Healthy balance
                leaf_concentration = deal.leaf_base_concentration * 10  # 5x for both
                other_concentration = deal.leaf_base_concentration * 10  # 5x for both
            
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

    def get_state(self) -> Dict:
        """Get current state of LEAF pairs model."""
        active_deals = self.get_active_deals(self.month)
        return {
            'total_leaf': sum(deal.leaf_balance for deal in active_deals),
            'total_usd': sum(deal.other_balance for deal in active_deals),
            'active_deals': len(active_deals),
            'balance_history': dict(self.balance_history)
        }

    def step(self, month: int) -> None:
        """Process one time step in the LEAF pairs model."""
        self.month = month
        active_deals = self.get_active_deals(month)
        
        # Record state for this month
        self._record_state(month)
        
        logging.debug(f"\nMonth {month} LEAF Pairs:")
        logging.debug(f"- Active Deals: {len(active_deals)}")
        logging.debug(f"- Total LEAF: {self.get_leaf_liquidity():,.2f}")
        logging.debug(f"- Total USD: ${self.get_usd_liquidity():,.2f}")
