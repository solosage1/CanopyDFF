from typing import Tuple

class UniswapV2Math:
    @staticmethod
    def get_liquidity_within_range(
        x_reserve: float,  # Token X balance (e.g., LEAF)
        y_reserve: float,  # Token Y balance (e.g., USDC)
        current_price: float,
        price_range_percentage: float,
        x_concentration: float = 1.0,
        y_concentration: float = 1.0
    ) -> Tuple[float, float]:
        """
        Calculate liquidity within a given price range using Uniswap V2 mechanics.
        """
        if price_range_percentage <= 0 or price_range_percentage >= 100:
            raise ValueError("Price range percentage must be between 0 and 100")
            
        # Calculate price bounds
        price_diff_ratio = price_range_percentage / 100
        price_upper = current_price * (1 + price_diff_ratio)
        price_lower = current_price * (1 - price_diff_ratio)
        
        # Calculate virtual reserves that would give us the current price
        # Use geometric mean of reserves and adjust for price
        virtual_x = (x_reserve * y_reserve / current_price) ** 0.5
        virtual_y = virtual_x * current_price
        
        # Calculate the base Uniswap V2 liquidity depth
        L = (virtual_x * virtual_y) ** 0.5
        
        # Calculate base amounts within range using price-adjusted formula
        x_within_range = L * (1/price_lower**0.5 - 1/price_upper**0.5)
        y_within_range = L * (price_upper**0.5 - price_lower**0.5)
        
        # Apply concentration adjustments
        x_within_range *= x_concentration
        y_within_range *= y_concentration
        
        # Scale based on actual reserves vs virtual reserves
        x_scale = x_reserve / virtual_x if virtual_x > 0 else 0
        y_scale = y_reserve / virtual_y if virtual_y > 0 else 0
        
        x_within_range *= x_scale
        y_within_range *= y_scale
        
        # Price impact adjustment
        price_factor = current_price ** 0.5
        x_within_range /= price_factor
        y_within_range *= price_factor
        
        # Ensure we don't exceed actual balances
        x_within_range = min(x_within_range, x_reserve)
        y_within_range = min(y_within_range, y_reserve)
        
        return round(x_within_range, 8), round(y_within_range, 8) 