# src/Functions/LeafPrice.py

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from src.Data.deal import Deal

@dataclass
class LEAFPriceConfig:
    """Configuration for LEAF price calculations."""
    min_price: float = 0.10        # Minimum allowed LEAF price
    max_price: float = 10.0        # Maximum allowed LEAF price
    price_impact_threshold: float = 0.10  # Maximum price impact allowed (10%)
    initial_price: float = 1.0     # Starting price for LEAF

class LEAFPriceModel:
    """
    Handles LEAF price calculations, including price impact from trades.
    Price is updated based on trade impacts and can be updated multiple times within a month.
    The last price update in a month becomes the month-ending value and cannot be changed afterward.
    """

    def __init__(self, config: LEAFPriceConfig):
        self.config = config
        self.current_price = config.initial_price
        self.price_history: Dict[int, float] = {0: config.initial_price}
        self.monthly_prices_locked: Dict[int, bool] = {}
        self.trade_history: Dict[int, List[float]] = {}

    def calculate_total_liquidity(self, deals: List[Deal], month: int) -> Tuple[float, float]:
        """
        Calculate total LEAF and USD liquidity from all active deals.
        
        Args:
            deals: List of all deals
            month: Current simulation month
            
        Returns:
            Tuple of (leaf_liquidity, usd_liquidity)
        """
        leaf_liquidity = 0.0
        usd_liquidity = 0.0
        
        for deal in deals:
            if (deal.leaf_pair_amount > 0 and 
                deal.start_month <= month < deal.start_month + deal.leaf_duration_months):
                leaf_liquidity += deal.leaf_balance
                usd_liquidity += deal.other_balance
                
        return leaf_liquidity, usd_liquidity

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
            current_price: Current LEAF price
            leaf_liquidity: Amount of LEAF tokens available within the price impact threshold
            usd_liquidity: USD value of paired liquidity within the price impact threshold
            trade_amount_usd: USD value of LEAF to be bought (positive) or sold (negative)

        Returns:
            Tuple of (new_price, actual_price_impact_percentage)
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
                f"Price impact {price_impact:.2%} exceeds threshold of {self.config.price_impact_threshold:.2%}"
            )

        # Calculate new price with linear price impact
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
        deals: List[Deal],
        trade_amount_usd: float
    ) -> float:
        """
        Update the LEAF price due to a trade impact.

        Args:
            month: Current simulation month
            deals: List of all deals
            trade_amount_usd: USD value of LEAF to be bought (positive) or sold (negative)

        Returns:
            The updated LEAF price after the trade impact
        """
        if self.monthly_prices_locked.get(month, False):
            raise ValueError(f"Price for month {month} is already finalized")

        # Calculate total liquidity from all active deals
        leaf_liquidity, usd_liquidity = self.calculate_total_liquidity(deals, month)

        # Calculate new price with impact
        new_price, impact = self.calculate_price_impact(
            self.current_price,
            leaf_liquidity,
            usd_liquidity,
            trade_amount_usd
        )

        # Update state
        self.current_price = new_price
        self.price_history[month] = new_price
        
        # Track trade
        if month not in self.trade_history:
            self.trade_history[month] = []
        self.trade_history[month].append(trade_amount_usd)

        return new_price

    def finalize_month_price(self, month: int) -> None:
        """
        Finalize the LEAF price for the month, preventing further updates.

        Args:
            month: The month to finalize
        """
        self.monthly_prices_locked[month] = True
        self.price_history[month] = self.current_price

    def get_price(self, month: Optional[int] = None) -> float:
        """
        Get the LEAF price for a specific month or current price if month not specified.

        Args:
            month: Optional month to get price for

        Returns:
            LEAF price for the specified month or current price
        """
        if month is None:
            return self.current_price
        return self.price_history.get(month, self.current_price)

    def get_state(self) -> Dict:
        """
        Get the current state of the LEAF price model.

        Returns:
            Dictionary containing current state
        """
        return {
            'current_price': self.current_price,
            'price_history': self.price_history.copy(),
            'trade_history': self.trade_history.copy(),
            'monthly_prices_locked': self.monthly_prices_locked.copy()
        }