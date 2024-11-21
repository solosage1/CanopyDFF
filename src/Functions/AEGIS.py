from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import defaultdict
from .UniswapV2Math import UniswapV2Math
from src.Data.deal import Deal
import logging

@dataclass
class AEGISConfig:
    """Configuration for AEGIS model."""
    initial_leaf_balance: float = 1_000_000_000  # 1 billion LEAF
    initial_usdc_balance: float = 100_000        # 100k USDC
    max_months: int = 60
    oak_to_usdc_rate: float = 1.0
    oak_to_leaf_rate: float = 1.0

class AEGISModel:
    def __init__(self, config: AEGISConfig):
        self.config = config
        self.leaf_balance = config.initial_leaf_balance
        self.usdc_balance = config.initial_usdc_balance
        self.leaf_price = 1.0  # Start at $1
        self.oak_to_usdc_rate = config.oak_to_usdc_rate
        self.oak_to_leaf_rate = config.oak_to_leaf_rate
        
        # Track history
        self.leaf_balance_history = defaultdict(float)
        self.usdc_balance_history = defaultdict(float)
        self.leaf_price_history = []
        self.redemption_history = defaultdict(float)
        
        # Initialize history with starting values
        self.leaf_balance_history[0] = self.leaf_balance
        self.usdc_balance_history[0] = self.usdc_balance
        self.leaf_price_history.append(self.leaf_price)
        
    def get_state(self) -> Dict:
        """Return current state of the model"""
        return {
            'leaf_balance': self.leaf_balance,
            'usdc_balance': self.usdc_balance,
            'leaf_price': self.leaf_price,
            'oak_to_usdc_rate': self.oak_to_usdc_rate,
            'oak_to_leaf_rate': self.oak_to_leaf_rate
        }
        
    def handle_redemptions(self, month: int, redemption_rate: float) -> Tuple[float, float]:
        """Process redemptions for the given month
        
        Args:
            month (int): Current month
            redemption_rate (float): Rate of redemption (0-1)
        
        Returns:
            Tuple[float, float]: Amount of LEAF and USDC redeemed
        """
        if month in self.redemption_history:
            raise ValueError(f"Redemptions already processed for month {month}")
            
        leaf_to_redeem = self.leaf_balance * redemption_rate
        usdc_to_redeem = self.usdc_balance * redemption_rate
        
        self.leaf_balance -= leaf_to_redeem
        self.usdc_balance -= usdc_to_redeem
        
        self.redemption_history[month] = redemption_rate
        
        return leaf_to_redeem, usdc_to_redeem
        
    def step(self, month: int):
        """Execute one month's worth of updates"""
        # Record state
        self.leaf_balance_history[month] = self.leaf_balance
        self.usdc_balance_history[month] = self.usdc_balance
        self.leaf_price_history.append(self.leaf_price)
        
    def get_liquidity_within_percentage(self, percentage: float, current_price: float) -> Tuple[float, float]:
        """
        Calculate liquidity within percentage of current price.
        Uses Uniswap V2 mechanics with 5x concentration for USDC.
        """
        if percentage <= 0 or percentage >= 100:
            raise ValueError("Percentage must be between 0 and 100")
        
        if self.leaf_balance == 0 or self.usdc_balance == 0:
            return 0.0, 0.0
            
        # Use shared Uniswap V2 math
        return UniswapV2Math.get_liquidity_within_range(
            x_reserve=self.leaf_balance,
            y_reserve=self.usdc_balance,
            current_price=current_price,
            price_range_percentage=percentage,
            x_concentration=1.0,  # 1x for LEAF
            y_concentration=5.0   # 5x for USDC
        )

    def update_balances(self, usdc_change: float = 0, leaf_change: float = 0) -> None:
        """
        Update AEGIS balances based on changes in USDC and LEAF.
        
        Args:
            usdc_change: Change in USDC balance (positive for increase)
            leaf_change: Change in LEAF balance (positive for increase)
        """
        self.usdc_balance += usdc_change
        self.leaf_balance += leaf_change
        
        # Ensure balances don't go negative
        self.usdc_balance = max(0, self.usdc_balance)
        self.leaf_balance = max(0, self.leaf_balance)

    def sell_leaf(self, leaf_amount: float, current_price: float) -> Tuple[float, float]:
        """Sell LEAF tokens at current price. Returns (leaf_sold, usdc_received)."""
        if leaf_amount <= 0:
            return 0.0, 0.0
            
        if leaf_amount > self.leaf_balance:
            logging.warning(f"Requested to sell {leaf_amount:,.2f} LEAF but only have {self.leaf_balance:,.2f}")
            leaf_amount = self.leaf_balance
            
        usdc_received = leaf_amount * current_price
        self.leaf_balance -= leaf_amount
        self.usdc_balance += usdc_received
        
        logging.info(f"AEGIS sold {leaf_amount:,.2f} LEAF for {usdc_received:,.2f} USDC")
        return leaf_amount, usdc_received