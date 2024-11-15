# Canopy AEGIS LP Model Specification

`````markdown:Functions/AEGISLP.md

## Purpose
Track and manage AEGIS LP state, including LEAF and USDC balances, redemptions, and market-driven value changes.

## Python Implementation

```python
from dataclasses import dataclass
from typing import Tuple, Dict
from collections import defaultdict

@dataclass
class AEGISLPConfig:
    initial_leaf: float        # Initial LEAF tokens
    initial_leaf_price: float  # Initial LEAF price in USD
    start_month: int = 0       # Starting month number

class AEGISLPModel:
    def __init__(self, config: AEGISLPConfig):
        self.config = config
        self._validate_config()
        
        # Initialize state
        self.current_month = config.start_month
        self.leaf_balance = config.initial_leaf
        self.usdc_balance = config.initial_leaf * config.initial_leaf_price
        self.redemption_history = defaultdict(float)  # month -> redemption percentage
        self.balance_history = defaultdict(lambda: (0.0, 0.0))  # month -> (leaf, usdc)
        
        # Record initial balances
        self.balance_history[config.start_month] = (self.leaf_balance, self.usdc_balance)
        
    def process_month(self, 
                     month: int, 
                     redemption_percentage: float,
                     leaf_price: float,
                     usdc_market_change: float
                     ) -> Tuple[float, float, float, float]:
        """
        Process a month's redemptions and market changes
        
        Args:
            month: Month number since start
            redemption_percentage: Percentage of remaining AEGIS to redeem (0-100)
            leaf_price: Current LEAF price in USD
            usdc_market_change: Net USDC change from LEAF trading
                              (positive = sold LEAF for USDC, negative = bought LEAF with USDC)
            
        Returns:
            Tuple of (leaf_redeemed, usdc_redeemed, new_leaf_balance, new_usdc_balance)
        """
        if month < self.current_month:
            raise ValueError("Cannot process past months")
        if not 0 <= redemption_percentage <= 100:
            raise ValueError("Invalid redemption percentage")
        if leaf_price <= 0:
            raise ValueError("Invalid LEAF price")
            
        # If updating current month, restore previous state
        if month == self.current_month:
            self.leaf_balance, self.usdc_balance = self.balance_history[month - 1]
        elif month > self.current_month + 1:
            raise ValueError("Cannot skip months")
            
        # Calculate redemption amounts (proportional to each asset)
        leaf_redeemed = self.leaf_balance * (redemption_percentage / 100)
        usdc_redeemed = self.usdc_balance * (redemption_percentage / 100)
        
        # Update balances for redemptions
        self.leaf_balance -= leaf_redeemed
        self.usdc_balance -= usdc_redeemed
        
        # Apply market changes from LEAF trading
        if usdc_market_change > 0:
            # Sold LEAF for USDC
            leaf_sold = usdc_market_change / leaf_price
            self.leaf_balance -= leaf_sold
            self.usdc_balance += usdc_market_change
        else:
            # Bought LEAF with USDC
            leaf_bought = abs(usdc_market_change) / leaf_price
            self.leaf_balance += leaf_bought
            self.usdc_balance += usdc_market_change
        
        # Record state
        self.redemption_history[month] = redemption_percentage
        self.balance_history[month] = (self.leaf_balance, self.usdc_balance)
        self.current_month = month
        
        return leaf_redeemed, usdc_redeemed, self.leaf_balance, self.usdc_balance
        
    def get_balances(self, month: int) -> Tuple[float, float]:
        """
        Get LEAF and USDC balances for a given month (read-only)
        
        Args:
            month: Month number to query
            
        Returns:
            Tuple of (leaf_balance, usdc_balance)
        """
        if month > self.current_month:
            raise ValueError("Cannot query future months")
            
        return self.balance_history[month]
        
    def _validate_config(self) -> None:
        """Validate initial configuration"""
        if self.config.initial_leaf <= 0:
            raise ValueError("Invalid initial LEAF amount")
        if self.config.initial_leaf_price <= 0:
            raise ValueError("Invalid initial LEAF price")
        if self.config.start_month < 0:
            raise ValueError("Invalid start month")
```

### Sample Usage
```python
# Initialize AEGIS LP
config = AEGISLPConfig(
    initial_leaf=9000_000,000,    # 900M LEAF
    initial_leaf_price=1.0,    # $1 per LEAF
    start_month=0
)
model = AEGISLPModel(config)

# Process month 1: Sell LEAF for USDC
leaf_out, usdc_out, leaf_balance, usdc_balance = model.process_month(
    month=1,
    redemption_percentage=10.0,  # Redeem 10%
    leaf_price=2.5,             # LEAF price now $2.50
    usdc_market_change=50_000   # Sold LEAF for 50k USDC
)

# Process month 2: Buy LEAF with USDC
leaf_out, usdc_out, leaf_balance, usdc_balance = model.process_month(
    month=2,
    redemption_percentage=5.0,   # Redeem 5%
    leaf_price=2.4,             # LEAF price now $2.40
    usdc_market_change=-24_000  # Bought LEAF with 24k USDC
)
```

## Key Features
1. **State Management**: Tracks LEAF and USDC balances over time
2. **Proportional Redemptions**: Returns assets in proportion to holdings
3. **Market Impact**: Accounts for LEAF trading activity
4. **Historical Tracking**: Maintains redemption and balance history
5. **Balance Queries**: Supports read-only balance checks
6. **Validation**: Ensures valid inputs and state transitions
7. **Month Updates**: Allows updating the current month's data

## Model Capabilities
1. Process monthly redemptions
2. Track LEAF and USDC balances
3. Account for LEAF trading activity
4. Calculate proportional redemption amounts
5. Maintain redemption history
6. Query historical balances
7. Update current month data

## Implementation Details
1. **State Structure**:
   - Current LEAF balance
   - Current USDC balance
   - Redemption history
   - Balance history
   - Current month

2. **Processing Logic**:
   - Redemptions proportional to each asset
   - LEAF trading updates both balances
   - Sequential month processing required
   - Current month updates supported

## Recommended Extensions
1. Add price impact tracking
2. Include volume-based metrics
3. Add trading limits
4. Track historical trading activity
5. Add minimum balance requirements
6. Include fee calculations
7. Add detailed reporting capabilities

## Integration Notes
This model can be integrated with:
1. Price Impact Model
2. Volume Model
3. TVL Model
4. Risk Management System
`````

Key changes made:

1. Updated market change logic to properly reflect LEAF trading
2. Added LEAF balance updates based on trading activity
3. Clarified documentation for usdc_market_change parameter
4. Updated sample usage to show both buying and selling LEAF
5. Added explicit calculations for LEAF amounts traded
6. Improved comments explaining trading impact
7. Updated documentation to reflect trading mechanics
