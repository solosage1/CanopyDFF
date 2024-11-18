# src/Functions/LeafPrice.py

from dataclasses import dataclass
from typing import Tuple

@dataclass
class LEAFPriceConfig:
    """Configuration for LEAF price calculations."""
    min_price: float        # Minimum allowed LEAF price
    max_price: float        # Maximum allowed LEAF price
    price_impact_threshold: float  # Maximum price impact allowed (e.g., 0.10 for 10%)

class LEAFPriceModel:
    """
    Handles LEAF price calculations, including price impact from trades.
    Price is updated based on trade impacts and can be updated multiple times within a month.
    The last price update in a month becomes the month-ending value and cannot be changed afterward.
    """

    def __init__(self, config: LEAFPriceConfig):
        self.config = config
        self.price_history = {}
        self.current_price = None  # Will be set when the simulation starts
        self.monthly_prices_locked = {}  # Tracks if the price for a month is finalized

    def initialize_price(self, initial_price: float):
        """Initialize the starting price of LEAF."""
        self.current_price = initial_price

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
            leaf_liquidity (float): Amount of LEAF tokens available within the price impact threshold
            usd_liquidity (float): USD value of paired liquidity within the price impact threshold
            trade_amount_usd (float): USD value of LEAF to be bought (positive) or sold (negative)

        Returns:
            Tuple[float, float]: (new_price, actual_price_impact_percentage)
        """
        if leaf_liquidity <= 0 or usd_liquidity <= 0:
            raise ValueError("Liquidity must be greater than 0")

        # Calculate total liquidity value
        total_liquidity = usd_liquidity + (leaf_liquidity * current_price)

        # Calculate price impact
        price_impact = trade_amount_usd / total_liquidity

        # Check if price impact exceeds threshold
        if abs(price_impact) > self.config.price_impact_threshold:
            raise ValueError(
                f"Price impact {price_impact:.2%} exceeds the allowed threshold of {self.config.price_impact_threshold:.2%}"
            )

        # Calculate new price with linear price impact
        # Positive trade_amount_usd (buying) increases price, negative (selling) decreases price
        price_change = current_price * price_impact
        new_price = current_price + price_change

        # Ensure price stays within bounds
        new_price = max(self.config.min_price, min(self.config.max_price, new_price))

        # Calculate actual price impact percentage
        actual_price_impact = (new_price - current_price) / current_price

        return new_price, actual_price_impact

    def update_price(
        self,
        month: int,
        leaf_liquidity: float,
        usd_liquidity: float,
        trade_amount_usd: float
    ) -> float:
        """
        Update the LEAF price due to a trade impact.

        Args:
            month (int): Current simulation month
            leaf_liquidity (float): Amount of LEAF tokens available within the price impact threshold
            usd_liquidity (float): USD value of paired liquidity within the price impact threshold
            trade_amount_usd (float): USD value of LEAF to be bought (positive) or sold (negative)

        Returns:
            float: The updated LEAF price after the trade impact
        """
        if self.monthly_prices_locked.get(month, False):
            raise ValueError(f"Price for month {month} is already finalized and cannot be updated.")

        new_price, _ = self.calculate_price_impact(
            self.current_price,
            leaf_liquidity,
            usd_liquidity,
            trade_amount_usd
        )

        self.current_price = new_price
        self.price_history[month] = new_price

        return new_price

    def finalize_month_price(self, month: int):
        """
        Finalize the LEAF price for the month, preventing further updates.

        Args:
            month (int): The month to finalize
        """
        self.monthly_prices_locked[month] = True

    def get_current_price(self, month: int) -> float:
        """
        Get the LEAF price for the current month.

        Args:
            month (int): Current simulation month

        Returns:
            float: Current LEAF price
        """
        # If the price has not been initialized, raise an error
        if self.current_price is None:
            raise ValueError("LEAF price has not been initialized.")

        return self.current_price