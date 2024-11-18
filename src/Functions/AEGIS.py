from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import defaultdict
from .UniswapV2Math import UniswapV2Math

@dataclass
class AEGISConfig:
    initial_leaf_balance: float
    initial_usdc_balance: float
    leaf_price_decay_rate: float
    max_months: int

class AEGISModel:
    def __init__(self, config: AEGISConfig):
        self.config = config
        self.leaf_balance = config.initial_leaf_balance
        self.usdc_balance = config.initial_usdc_balance
        self.leaf_price = 1.0  # Start at $1
        
        # Track history
        self.leaf_balance_history = []
        self.usdc_balance_history = []
        self.leaf_price_history = []
        self.redemption_history = defaultdict(float)
        
    def get_state(self) -> Dict:
        """Return current state of the model"""
        return {
            'leaf_balance': self.leaf_balance,
            'usdc_balance': self.usdc_balance,
            'leaf_price': self.leaf_price
        }
        
    def handle_redemptions(self, month: int, redemption_rate: float) -> Tuple[float, float]:
        """Process redemptions for the given month"""
        if month in self.redemption_history:
            raise ValueError(f"Redemptions already processed for month {month}")
            
        leaf_to_redeem = self.leaf_balance * redemption_rate
        usdc_to_redeem = self.usdc_balance * redemption_rate
        
        self.leaf_balance -= leaf_to_redeem
        self.usdc_balance -= usdc_to_redeem
        
        self.redemption_history[month] = redemption_rate
        
        return leaf_to_redeem, usdc_to_redeem
        
    def apply_market_decay(self):
        """Apply price decay based on configured rate"""
        self.leaf_price *= (1 - self.config.leaf_price_decay_rate)
        
    def step(self, month: int):
        """Execute one month's worth of updates"""
        # Apply market decay
        self.apply_market_decay()
        
        # Record state
        self.leaf_balance_history.append(self.leaf_balance)
        self.usdc_balance_history.append(self.usdc_balance)
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