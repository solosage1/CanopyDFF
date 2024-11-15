# Canopy AEGIS LP Model

## Purpose

The AEGIS Management Model handles the valuation and management of AEGIS LP tokens within the Canopy ecosystem. It manages LEAF and USDC balances, processes monthly redemptions, and ensures financial stability and fairness by handling proportional redemptions based on holdings and market-driven changes.

## Python Implementation

```python
from dataclasses import dataclass
from typing import Tuple, Dict
from collections import defaultdict

@dataclass
class AEGISLPConfig:
    initial_leaf: float         # Initial LEAF tokens
    initial_usdc: float         # Initial USDC balance
    start_month: int = 0        # Starting month number

class AEGISLPModel:
    def __init__(self, config: AEGISLPConfig):
        self.config = config
        self._validate_config()
        
        # Initialize state
        self.current_month = config.start_month
        self.leaf_balance = config.initial_leaf
        self.usdc_balance = config.initial_usdc
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
            redemption_percentage: Percentage of AEGIS LP to redeem (0-100)
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
            previous_month = month - 1
            if previous_month >= 0:
                self.leaf_balance, self.usdc_balance = self.balance_history[previous_month]
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
        if self.config.initial_usdc < 0:
            raise ValueError("Invalid initial USDC balance")
        if self.config.start_month < 0:
            raise ValueError("Invalid start month")
```

## Key Features

1. **State Management**: Tracks LEAF and USDC balances over time.
2. **Proportional Redemptions**: Processes redemptions by returning assets proportionally based on holdings.
3. **Market Impact**: Accounts for LEAF trading activities that affect LEAF and USDC balances.
4. **Historical Tracking**: Maintains a history of redemptions and balances for each month.
5. **Balance Queries**: Supports read-only balance checks for any past month.
6. **Validation**: Ensures valid inputs and state transitions to maintain integrity.
7. **Month Updates**: Allows updating the current month's data without skipping any months.

## Model Capabilities

1. **Process Monthly Redemptions**:
   - Handles the redemption of AEGIS LP tokens by decreasing LEAF and USDC balances proportionally.
   
2. **Track LEAF and USDC Balances**:
   - Maintains up-to-date balances of LEAF and USDC, reflecting redemptions and market changes.
   
3. **Account for LEAF Trading Activity**:
   - Adjusts balances based on LEAF being bought or sold, impacting USDC holdings accordingly.
   
4. **Calculate Proportional Redemption Amounts**:
   - Ensures that redemptions are handled fairly based on the proportion of holdings.
   
5. **Maintain Redemption History**:
   - Keeps a record of redemption percentages for each month.
   
6. **Query Historical Balances**:
   - Allows retrieval of LEAF and USDC balances for any processed month.
   
7. **Update Current Month Data**:
   - Supports incremental updates to the model on a month-by-month basis.

## Implementation Details

1. **State Structure**:
   - **Current LEAF Balance**: The current amount of LEAF tokens held.
   - **Current USDC Balance**: The current amount of USDC held.
   - **Redemption History**: Tracks the percentage of AEGIS LP redeemed each month.
   - **Balance History**: Records LEAF and USDC balances for each month.
   - **Current Month**: Tracks the latest month processed.
   
2. **Processing Logic**:
   - **Redemptions Proportional to Holdings**: Ensures fair redemption across all LP holders based on their holdings.
   - **LEAF Trading Updates Both Balances**: Reflects the impact of LEAF buying/selling on LEAF and USDC balances.
   - **Sequential Month Processing Required**: Maintains chronological integrity by processing months in order.
   - **Current Month Updates Supported**: Allows for accurate tracking and state updates as each month progresses.

## Recommended Extensions

1. **Add Price Impact Tracking**:
   - Enhance the model to monitor how LEAF trading activities influence its market price over time.
   
2. **Include Volume-Based Metrics**:
   - Incorporate metrics that evaluate trading volumes and their effects on liquidity and token stability.
   
3. **Add Trading Limits**:
   - Implement constraints to prevent excessive buying or selling that could destabilize the LEAF market.
   
4. **Track Historical Trading Activity**:
   - Maintain a detailed log of all trading activities for auditing and performance review purposes.
   
5. **Add Minimum Balance Requirements**:
   - Ensure that the model maintains a minimum balance of LEAF and USDC to sustain operational stability.
   
6. **Include Fee Calculations**:
   - Integrate fee structures to account for transactional costs associated with LEAF trading.
   
7. **Add Detailed Reporting Capabilities**:
   - Develop comprehensive reporting tools to visualize and analyze AEGIS LP performance and financial metrics.

## Integration Notes

This model can be integrated with:

1. **Price Impact Model**
   - **Integration**: Provides metrics on how LEAF trading affects market prices.
   - **Functionality**: Adjusts strategic decisions based on price fluctuations.
   
2. **Volume Model**
   - **Integration**: Utilizes trading volume data to assess market participation and liquidity efficiency.
   - **Functionality**: Enhances understanding of market dynamics and trading behaviors.
   
3. **TVL Model**
   - **Integration**: Uses Total Value Locked (TVL) metrics to evaluate the overall health and scale of the AEGIS LP ecosystem.
   - **Functionality**: Provides insights into capital allocation and investment performance.
   
4. **Risk Management System**
   - **Integration**: Incorporates risk assessment data to manage potential vulnerabilities within AEGIS LP operations.
   - **Functionality**: Ensures resilience against market volatility and unexpected financial events.

By focusing solely on managing AEGIS LP tokens, their valuation, and handling monthly redemptions, the AEGIS Management Model maintains clear boundaries and responsibilities within the Canopy ecosystem. This separation of concerns ensures that each module operates efficiently and cohesively without overlapping functionalities.

## Sample Usage

```python
# Initialize AEGIS LP
config = AEGISLPConfig(
    initial_leaf=900_000_000,    # 900M LEAF
    initial_usdc=900_000_000 * 1.0,    # $1 per LEAF
    start_month=0
)
model = AEGISLPModel(config)

# Process month 1: Sell LEAF for USDC
leaf_out, usdc_out, leaf_balance, usdc_balance = model.process_month(
    month=1,
    redemption_percentage=10.0,  # Redeem 10%
    leaf_price=2.5,              # LEAF price now $2.50
    usdc_market_change=50_000     # Sold LEAF for 50k USDC
)

# Process month 2: Buy LEAF with USDC
leaf_out, usdc_out, leaf_balance, usdc_balance = model.process_month(
    month=2,
    redemption_percentage=5.0,    # Redeem 5%
    leaf_price=2.4,               # LEAF price now $2.40
    usdc_market_change=-24_000     # Bought LEAF with 24k USDC
)
```
