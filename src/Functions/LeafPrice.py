# src/Functions/LeafPrice.py

from dataclasses import dataclass
from typing import Tuple

@dataclass
class LEAFPriceConfig:
    """Configuration for LEAF price calculations"""
    min_price: float = 0.1  # Minimum allowed LEAF price
    max_price: float = 10.0  # Maximum allowed LEAF price
    price_impact_threshold: float = 0.10  # Maximum price impact allowed (10%)
    initial_price: float = 1.0  # Initial LEAF price
    stability_period: int = 12  # Number of months for stability period
    monthly_growth_rate: float = 0.05  # Monthly growth rate

class LEAFPriceModel:
    """
    Handles LEAF price calculations including price impact from trades
    """
    def __init__(self, config: LEAFPriceConfig):
        self.config = config
        self.price_history = {}
        self.current_price = config.initial_price

    def calculate_price_impact(
        self,
        current_price: float,
        leaf_liquidity: float,
        usd_liquidity: float,
        trade_amount_usd: float
    ) -> Tuple[float, float]:
        """
        Calculate the price impact of a trade and return the new price.
        
        Args:
            current_price (float): Current LEAF price
            leaf_liquidity (float): Amount of LEAF tokens available within 10% of current price
            usd_liquidity (float): USD value of paired liquidity within 10% of current price
            trade_amount_usd (float): USD value of LEAF to be bought (positive) or sold (negative)
        
        Returns:
            Tuple[float, float]: (new_price, price_impact_percentage)
        """
        if leaf_liquidity <= 0 or usd_liquidity <= 0:
            raise ValueError("Liquidity must be greater than 0")

        # Calculate total liquidity value
        total_liquidity = usd_liquidity + (leaf_liquidity * current_price)
        
        # Calculate price impact
        price_impact = trade_amount_usd / total_liquidity
        
        # Calculate new price with linear price impact
        # Positive trade_amount (buying) increases price, negative (selling) decreases price
        price_change = current_price * price_impact
        new_price = current_price + price_change
        
        # Ensure price stays within bounds
        new_price = max(self.config.min_price, min(self.config.max_price, new_price))
        
        # Calculate actual price impact percentage
        actual_price_impact = (new_price - current_price) / current_price
        
        # Validate price impact doesn't exceed threshold
        if abs(actual_price_impact) > self.config.price_impact_threshold:
            raise ValueError(
                f"Price impact ({actual_price_impact:.2%}) exceeds maximum allowed ({self.config.price_impact_threshold:.2%})"
            )
        
        return new_price, actual_price_impact

    def get_leaf_price(
        self,
        month: int,
        current_price: float,
        leaf_liquidity: float,
        usd_liquidity: float,
        trade_amount_usd: float = 0.0
    ) -> float:
        """
        Calculate the new LEAF price based on current state and any trades.
        
        Args:
            month (int): Current month in simulation
            current_price (float): Current LEAF price
            leaf_liquidity (float): Amount of LEAF tokens available within 10% of current price
            usd_liquidity (float): USD value of paired liquidity within 10% of current price
            trade_amount_usd (float): USD value of LEAF to be bought (positive) or sold (negative)
        
        Returns:
            float: New LEAF price
        """
        try:
            new_price, _ = self.calculate_price_impact(
                current_price,
                leaf_liquidity,
                usd_liquidity,
                trade_amount_usd
            )
            return new_price
        except ValueError as e:
            # Log the error and return current price if there's an issue
            print(f"Warning: Price calculation failed - {str(e)}")
            return current_price

    def estimate_max_trade_size(
        self,
        current_price: float,
        leaf_liquidity: float,
        usd_liquidity: float,
        is_buy: bool
    ) -> float:
        """
        Estimate the maximum trade size possible within price impact threshold.
        
        Args:
            current_price (float): Current LEAF price
            leaf_liquidity (float): Amount of LEAF tokens available within 10% of current price
            usd_liquidity (float): USD value of paired liquidity within 10% of current price
            is_buy (bool): True for buy orders, False for sell orders
        
        Returns:
            float: Maximum trade size in USD
        """
        total_liquidity = usd_liquidity + (leaf_liquidity * current_price)
        max_trade = total_liquidity * self.config.price_impact_threshold
        
        return max_trade if is_buy else -max_trade

    def get_current_price(self, month: int) -> float:
        """
        Get the LEAF price for the current month.
        
        Args:
            month: Current simulation month
            
        Returns:
            float: Current LEAF price
        """
        # If we have a recorded price for this month, return it
        if month in self.price_history:
            return self.price_history[month]
            
        # Otherwise calculate based on config parameters
        if month <= self.config.stability_period:
            # During stability period, maintain initial price
            price = self.config.initial_price
        else:
            # After stability period, apply growth rate
            months_since_stability = month - self.config.stability_period
            price = self.config.initial_price * (1 + self.config.monthly_growth_rate) ** months_since_stability
            
        # Store in history and return
        self.price_history[month] = price
        self.current_price = price
        return price

    def update_price(self, month: int, new_price: float) -> None:
        """
        Update the price for a specific month.
        
        Args:
            month: Month to update
            new_price: New price value
        """
        self.price_history[month] = new_price
        if month == max(self.price_history.keys()):
            self.current_price = new_price