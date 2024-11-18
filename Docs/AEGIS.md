```markdown
# Canopy AEGIS LP Model

## Purpose

The AEGIS Management Model handles the valuation and management of AEGIS LP tokens within the Canopy ecosystem. It manages LEAF and USDC balances, processes monthly redemptions, and ensures financial stability and fairness by handling proportional redemptions based on holdings and market-driven changes.

## Python Implementation

```python
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
        Calculate liquidity within a specified percentage of current price.
        Uses Uniswap V2 mechanics with 5x concentration for USDC.
        
        Args:
            percentage: The percentage range around the current price.
            current_price: The current price of LEAF in USDC.
            
        Returns:
            Tuple containing LEAF and USDC liquidity within the specified range.
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
```

## Implementation Details

### 1. State Structure

- **Current LEAF Balance**: The current amount of LEAF tokens held.
- **Current USDC Balance**: The current amount of USDC held.
- **Redemption History**: Tracks the percentage of AEGIS LP redeemed each month.
- **Balance History**: Records LEAF and USDC balances for each month.
- **Current Month**: Tracks the latest month processed.
- **Leaf Price**: Current price of LEAF in USDC, subject to decay.

### 2. Processing Logic

- **Redemptions Proportional to Holdings**: Ensures fair redemption across all LP holders based on their holdings.
- **LEAF Trading Updates Both Balances**: Reflects the impact of LEAF buying/selling on LEAF and USDC balances.
- **Market Decay Applied Monthly**: LEAF price decays based on the configured decay rate each month.
- **Sequential Month Processing Required**: Maintains chronological integrity by processing months in order.
- **State Recording**: Records LEAF and USDC balances, leaf price, and redemption data for each month.

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

1. **Uniswap V2 Math Module**
   - **Integration**: Utilizes mathematical functions to calculate liquidity within price ranges.
   - **Functionality**: Provides accurate liquidity metrics based on current reserves and price ranges.

2. **LEAF Pairs Model**
   - **Integration**: Shares liquidity metrics to ensure consistent valuation across models.
   - **Functionality**: Coordinates LEAF trading activities with liquidity management.

3. **TVL Model**
   - **Integration**: Uses Total Value Locked (TVL) metrics to evaluate the overall health and scale of the AEGIS LP ecosystem.
   - **Functionality**: Provides insights into capital allocation and investment performance.

4. **Revenue Model**
   - **Integration**: Shares redemption and liquidity data to accurately project revenue streams.
   - **Functionality**: Enhances revenue calculations based on AEGIS LP activities.

5. **Simulation Framework**
   - **Integration**: Incorporates AEGIS model updates into the main simulation loop.
   - **Functionality**: Ensures that AEGIS activities are simulated alongside other financial models.

By focusing solely on managing AEGIS LP tokens, their valuation, and handling monthly redemptions, the AEGIS Management Model maintains clear boundaries and responsibilities within the Canopy ecosystem. This separation of concerns ensures that each module operates efficiently and cohesively without overlapping functionalities.

## Sample Usage

```python
# Initialize AEGIS LP
config = AEGISConfig(
    initial_leaf_balance=900_000_000,    # 900M LEAF
    initial_usdc_balance=900_000,        # $900,000 USDC
    leaf_price_decay_rate=0.005,         # 0.5% monthly decay
    max_months=60                         # 5 years
)
model = AEGISModel(config)

# Process month 1: Sell LEAF for USDC and redeem 2%
leaf_redeemed, usdc_redeemed, new_leaf_balance, new_usdc_balance = model.process_month(
    month=1,
    redemption_percentage=2.0,          # Redeem 2%
    leaf_price=2.5,                      # LEAF price now $2.50
    usdc_market_change=50_000            # Sold LEAF for 50k USDC
)

# Update model state for month 1
model.step(month=1)

# Process month 2: Buy LEAF with USDC and redeem 1%
leaf_redeemed, usdc_redeemed, new_leaf_balance, new_usdc_balance = model.process_month(
    month=2,
    redemption_percentage=1.0,          # Redeem 1%
    leaf_price=2.4,                      # LEAF price now $2.40
    usdc_market_change=-24_000           # Bought LEAF with 24k USDC
)

# Update model state for month 2
model.step(month=2)

# Retrieve balances for month 2
balances = model.get_balances(month=2)
print(f"Month 2 Balances - LEAF: {balances[0]}, USDC: {balances[1]}")
```

## Testing

Unit tests are crucial to ensure that the AEGIS model functions as expected. Below is an example of how to test the `process_month` method.

```python
import unittest
from src.Functions.AEGIS import AEGISConfig, AEGISModel

class TestAEGISModel(unittest.TestCase):
    def setUp(self):
        config = AEGISConfig(
            initial_leaf_balance=1000,
            initial_usdc_balance=1000,
            leaf_price_decay_rate=0.01,
            max_months=12
        )
        self.model = AEGISModel(config)
    
    def test_initial_state(self):
        state = self.model.get_state()
        self.assertEqual(state['leaf_balance'], 1000)
        self.assertEqual(state['usdc_balance'], 1000)
        self.assertEqual(state['leaf_price'], 1.0)
    
    def test_handle_redemptions(self):
        leaf_redeemed, usdc_redeemed = self.model.handle_redemptions(1, 0.1)
        self.assertEqual(leaf_redeemed, 100)
        self.assertEqual(usdc_redeemed, 100)
        self.assertEqual(self.model.leaf_balance, 900)
        self.assertEqual(self.model.usdc_balance, 900)
    
    def test_process_month_sell_leaf(self):
        leaf_redeemed, usdc_redeemed, leaf_balance, usdc_balance = self.model.process_month(
            month=1,
            redemption_percentage=2.0,
            leaf_price=2.5,
            usdc_market_change=50_000
        )
        self.assertEqual(leaf_redeemed, 20.0)
        self.assertEqual(usdc_redeemed, 20.0)
        self.assertAlmostEqual(leaf_balance, 900 - (50_000 / 2.5))
        self.assertAlmostEqual(usdc_balance, 900 + 50_000)
    
    def test_process_month_buy_leaf(self):
        # First process a redemption
        self.model.process_month(
            month=1,
            redemption_percentage=2.0,
            leaf_price=2.5,
            usdc_market_change=50_000
        )
        # Then process buying LEAF
        leaf_redeemed, usdc_redeemed, leaf_balance, usdc_balance = self.model.process_month(
            month=2,
            redemption_percentage=1.0,
            leaf_price=2.4,
            usdc_market_change=-24_000
        )
        self.assertEqual(leaf_redeemed, 16.0)
        self.assertEqual(usdc_redeemed, 16.0)
        self.assertAlmostEqual(leaf_balance, (900 - 50_000 / 2.5) - 16.0 + (24000 / 2.4))
        self.assertAlmostEqual(usdc_balance, (900 + 50_000) - 16.0 + (-24_000))
    
    def test_apply_market_decay(self):
        self.model.apply_market_decay()
        self.assertAlmostEqual(self.model.leaf_price, 0.99)
    
    def test_invalid_redemption_percentage(self):
        with self.assertRaises(ValueError):
            self.model.handle_redemptions(1, -5)
        with self.assertRaises(ValueError):
            self.model.handle_redemptions(1, 150)
    
    def test_invalid_leaf_price(self):
        with self.assertRaises(ValueError):
            self.model.process_month(
                month=1,
                redemption_percentage=10.0,
                leaf_price=0,
                usdc_market_change=1000
            )
    
    def test_duplicate_redemption(self):
        self.model.handle_redemptions(1, 5.0)
        with self.assertRaises(ValueError):
            self.model.handle_redemptions(1, 5.0)

if __name__ == '__main__':
    unittest.main()
```

## Integration with Simulation

The AEGIS model is integrated into the simulation framework to manage LEAF and USDC balances, handle redemptions, and track liquidity metrics alongside other financial models.

```python
# src/Simulations/simulate.py

import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.Revenue import RevenueModel, RevenueModelConfig
from src.Functions.TVLContributions import TVLContribution, TVLContributionHistory
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Data.leaf_deal import initialize_deals
from typing import Dict, List
from src.Functions.AEGIS import AEGISConfig, AEGISModel
import numpy as np # type: ignore

def calculate_leaf_price(month: int, total_liquidity: float) -> float:
    """
    Placeholder function to calculate LEAF price.
    """
    # Implement your LEAF price model here.
    return 1.0  # Placeholder value

def initialize_tvl_contributions(tvl_model: TVLModel, config: Dict) -> None:
    """Initialize all TVL contributions based on simulation config."""
    # Load initial contributions from data file
    tvl_model.loader.load_initial_contributions()

def print_monthly_summary(month: int, monthly_revenue: Dict[str, float], cumulative_revenue: float) -> None:
    """Print a summary of monthly revenue by TVL type."""
    print(f"{month:3d}    {monthly_revenue['ProtocolLocked']/1e6:12.2f} {monthly_revenue['Contracted']/1e6:12.2f} "
          f"{monthly_revenue['Organic']/1e6:12.2f} {monthly_revenue['Boosted']/1e6:12.2f} "
          f"{sum(monthly_revenue.values())/1e6:15.2f} {cumulative_revenue/1e6:20.2f}")

def plot_aegis_data(months: List[int], aegis_model: AEGISModel):
    """Plot AEGIS model data."""
    plt.figure(figsize=(10, 6))

    # LEAF Price Over Time
    plt.subplot(2, 1, 1)
    plt.plot(months, aegis_model.leaf_price_history, label='LEAF Price')
    plt.title('LEAF Price Over Time (AEGIS Model)')
    plt.xlabel('Month')
    plt.ylabel('Price in USDC')
    plt.legend()

    # Balances Over Time
    plt.subplot(2, 1, 2)
    plt.plot(months, aegis_model.leaf_balance_history, label='LEAF Balance')
    plt.plot(months, aegis_model.usdc_balance_history, label='USDC Balance')
    plt.title('AEGIS Balances Over Time')
    plt.xlabel('Month')
    plt.ylabel('Balance')
    plt.legend()

    plt.tight_layout()
    plt.show()

def track_liquidity_metrics(
    month: int,
    price: float,
    aegis_model: AEGISModel,
    leaf_pairs_model: LEAFPairsModel
) -> Dict:
    # Get AEGIS liquidity within 10% of price
    aegis_leaf, aegis_usdc = aegis_model.get_liquidity_within_percentage(10, price)
    
    # Get LEAFPairs liquidity within 10% of price
    leaf_pairs_leaf = 0
    leaf_pairs_other = 0
    active_deals = leaf_pairs_model.get_active_deals(month)
    
    # Get total liquidity across all active deals
    if active_deals:  # Only process if there are active deals
        leaf, other = leaf_pairs_model.get_liquidity_within_percentage(10, price)
        leaf_pairs_leaf = leaf
        leaf_pairs_other = other
    
    return {
        'month': month,
        'price': price,
        'aegis_leaf': aegis_leaf,
        'aegis_usdc': aegis_usdc,
        'leaf_pairs_leaf': leaf_pairs_leaf,
        'leaf_pairs_other': leaf_pairs_other,
        'aegis_total_usd': (aegis_leaf * price) + aegis_usdc,
        'leaf_pairs_total_usd': (leaf_pairs_leaf * price) + leaf_pairs_other
    }

def plot_liquidity_metrics(metrics_history: List[Dict]):
    months = [m['month'] for m in metrics_history]
    
    plt.figure(figsize=(15, 10))
    
    # Plot 1: LEAF Liquidity Comparison
    plt.subplot(2, 2, 1)
    plt.plot(months, [m['aegis_leaf'] for m in metrics_history], label='AEGIS LEAF')
    plt.plot(months, [m['leaf_pairs_leaf'] for m in metrics_history], label='LEAFPairs LEAF')
    plt.title('LEAF Liquidity Within 10% Range')
    plt.xlabel('Month')
    plt.ylabel('LEAF Amount')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Stablecoin Liquidity Comparison
    plt.subplot(2, 2, 2)
    plt.plot(months, [m['aegis_usdc'] for m in metrics_history], label='AEGIS USDC')
    plt.plot(months, [m['leaf_pairs_other'] for m in metrics_history], label='LEAFPairs Other')
    plt.title('Stablecoin Liquidity Within 10% Range')
    plt.xlabel('Month')
    plt.ylabel('USD Amount')
    plt.legend()
    plt.grid(True)
    
    # Plot 3: Total USD Value Comparison
    plt.subplot(2, 2, 3)
    plt.plot(months, [m['aegis_total_usd'] for m in metrics_history], label='AEGIS Total')
    plt.plot(months, [m['leaf_pairs_total_usd'] for m in metrics_history], label='LEAFPairs Total')
    plt.title('Total USD Value Within 10% Range')
    plt.xlabel('Month')
    plt.ylabel('USD Value')
    plt.legend()
    plt.grid(True)
    
    # Plot 4: Combined Liquidity Ratio
    plt.subplot(2, 2, 4)
    ratios = [(m['aegis_total_usd'] + m['leaf_pairs_total_usd']) / (m['aegis_total_usd'] or 1) for m in metrics_history]
    plt.plot(months, ratios)
    plt.title('Combined/AEGIS Liquidity Ratio')
    plt.xlabel('Month')
    plt.ylabel('Ratio')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    # Initialize configuration
    config = {
        'initial_move_tvl': 1_000_000_000,
        'initial_canopy_tvl': 500_000_000,
        'move_growth_rates': [0.10, 0.08, 0.06],
        'min_market_share': 0.05,
        'market_share_decay_rate': 0.01,
        'max_months': 60
    }

    # Define activation months for different features
    activation_months = {
        'LEAF_PAIRS_START_MONTH': 1,
        'BOOST_START_MONTH': 6,
        'AEGIS_START_MONTH': 3,
        'OAK_START_MONTH': 4,
        'MARKET_START_MONTH': 5,
        'PRICE_START_MONTH': 5,
        'DISTRIBUTION_START_MONTH': 5
    }

    # Initialize models
    tvl_model = TVLModel(TVLModelConfig(**config))
    revenue_model = RevenueModel(RevenueModelConfig(), tvl_model=tvl_model)
    leaf_pairs_model = LEAFPairsModel(LEAFPairsConfig(), initialize_deals())

    # Initialize AEGIS model
    aegis_config = AEGISConfig(
        initial_leaf_balance=1_000_000_000,
        initial_usdc_balance=500_000,
        leaf_price_decay_rate=0.005,
        max_months=config['max_months']
    )
    aegis_model = AEGISModel(aegis_config)

    # Initialize history arrays with correct length
    aegis_model.leaf_balance_history = [aegis_config.initial_leaf_balance] * config['max_months']
    aegis_model.usdc_balance_history = [aegis_config.initial_usdc_balance] * config['max_months']
    aegis_model.leaf_price_history = [1.0] * config['max_months']

    # Initialize contributions from data file
    initialize_tvl_contributions(tvl_model, config)

    # Tracking variables
    months = list(range(config['max_months']))
    total_tvl_by_month = []
    revenue_by_month = []
    cumulative_revenues = []
    leaf_prices = []
    metrics_history = []
    history_tracker = TVLContributionHistory()

    # Print header
    print("Month          Protocol     Contracted        Organic        Boosted       Total Rev (M)       Cumulative Rev (M)")
    print("-" * 113)

    # Simulation loop
    for month in months:
        # Record state before updates
        history_tracker.record_state(month, tvl_model.contributions)
        
        # Update TVL and calculate metrics
        tvl_model.step()
        total_tvl = tvl_model.get_total_tvl()
        total_tvl_by_month.append(total_tvl)
        
        # Calculate revenue
        monthly_revenue = revenue_model.calculate_revenue(month)
        revenue_by_month.append(monthly_revenue)
        cumulative_revenues.append(revenue_model.cumulative_revenue)

        # Calculate LEAF price for this month
        leaf_price = calculate_leaf_price(month, total_tvl)
        leaf_prices.append(leaf_price)

        # Update AEGIS model if active
        if month >= activation_months['AEGIS_START_MONTH']:
            aegis_model.handle_redemptions(month, 0.02)  # 2% monthly redemption
            aegis_model.step(month)
            
        # Always update history arrays at the correct index
        aegis_model.leaf_balance_history[month] = aegis_model.leaf_balance
        aegis_model.usdc_balance_history[month] = aegis_model.usdc_balance
        aegis_model.leaf_price_history[month] = leaf_price

        # Update LEAF pairs if active
        if month >= activation_months['LEAF_PAIRS_START_MONTH']:
            leaf_pairs_model.update_deals(month, leaf_price)

        # Track liquidity metrics
        metrics = track_liquidity_metrics(month, leaf_price, aegis_model, leaf_pairs_model)
        metrics_history.append(metrics)

        # Print monthly summary
        print_monthly_summary(month, monthly_revenue, revenue_model.cumulative_revenue)

    # After simulation loop, create all visualizations
    plt.figure(figsize=(15, 10))
    
    # Original TVL Plot
    plt.subplot(3, 2, 1)
    plt.plot(months, total_tvl_by_month)
    plt.title('Total TVL Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (USD)')
    plt.grid(True)

    # Original Revenue Plot
    plt.subplot(3, 2, 2)
    protocol_locked = [rev['ProtocolLocked'] for rev in revenue_by_month]
    contracted = [rev['Contracted'] for rev in revenue_by_month]
    organic = [rev['Organic'] for rev in revenue_by_month]
    boosted = [rev['Boosted'] for rev in revenue_by_month]
    
    plt.plot(months, protocol_locked, label='Protocol Locked')
    plt.plot(months, contracted, label='Contracted')
    plt.plot(months, organic, label='Organic')
    plt.plot(months, boosted, label='Boosted')
    plt.title('Monthly Revenue by Type')
    plt.xlabel('Month')
    plt.ylabel('Revenue (USD)')
    plt.legend()
    plt.grid(True)

    # Original Cumulative Revenue Plot
    plt.subplot(3, 2, 3)
    plt.plot(months, cumulative_revenues)
    plt.title('Cumulative Revenue')
    plt.xlabel('Month')
    plt.ylabel('Revenue (USD)')
    plt.grid(True)

    # LEAF Price Plot
    plt.subplot(3, 2, 4)
    plt.plot(months, leaf_prices)
    plt.title('LEAF Price Over Time')
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.grid(True)

    # AEGIS Balance History
    plt.subplot(3, 2, 5)
    plt.plot(months, aegis_model.leaf_balance_history[:len(months)], label='LEAF Balance')
    plt.plot(months, aegis_model.usdc_balance_history[:len(months)], label='USDC Balance')
    plt.title('AEGIS Balance History')
    plt.xlabel('Month')
    plt.ylabel('Balance')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # Now show the new liquidity metrics plots
    plot_liquidity_metrics(metrics_history)

    # Additional TVL composition analysis
    plt.figure(figsize=(15, 5))
    
    # TVL Composition
    plt.subplot(1, 2, 1)
    tvl_types = ['ProtocolLocked', 'Contracted', 'Organic', 'Boosted']
    bottom = np.zeros(len(months))
    
    for tvl_type in tvl_types:
        values = [sum(c['amount_usd'] for c in history_tracker.get_history(m) 
                 if c['tvl_type'] == tvl_type and c['active']) 
                 for m in months]
        plt.bar(months, values, bottom=bottom, label=tvl_type)
        bottom += np.array(values)
    
    plt.title('TVL Composition Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (USD)')
    plt.legend()
    
    # TVL Growth Rates
    plt.subplot(1, 2, 2)
    growth_rates = [(total_tvl_by_month[i] - total_tvl_by_month[i-1])/total_tvl_by_month[i-1] 
                   if i > 0 and total_tvl_by_month[i-1] != 0 else 0 
                   for i in range(len(months))]
    plt.plot(months, growth_rates)
    plt.title('Monthly TVL Growth Rate')
    plt.xlabel('Month')
    plt.ylabel('Growth Rate')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
```

## Explanation of Integration

1. **Initialization**:
   - The `AEGISModel` is initialized with initial LEAF and USDC balances, a leaf price decay rate, and the total number of simulation months.
   - Histories for LEAF balance, USDC balance, and LEAF price are initialized to track changes over time.

2. **Redemptions Handling**:
   - Each month, if AEGIS is active (`AEGIS_START_MONTH`), redemptions are processed by reducing LEAF and USDC balances proportionally based on the redemption rate.

3. **Market Decay**:
   - The LEAF price decays each month based on the configured decay rate, simulating market-driven price changes.

4. **Liquidity Metrics Tracking**:
   - Liquidity within a 10% range of the current LEAF price is tracked for both AEGIS and LEAFPairs models.
   - Metrics include LEAF liquidity, USDC liquidity, total USD value, and combined liquidity ratios.

5. **Visualization**:
   - Historical data for AEGIS balances and LEAF prices are plotted alongside other financial metrics.
   - Liquidity metrics are visualized to compare AEGIS and LEAFPairs liquidity within specified price ranges.
   - TVL composition and growth rates are also analyzed and visualized.

6. **Simulation Loop**:
   - The simulation runs for the configured number of months, updating all models and tracking necessary metrics each month.
   - Monthly summaries are printed to provide an overview of TVL, revenue, and cumulative revenue.

This integration ensures that the AEGIS model operates in tandem with other financial models, providing comprehensive insights into the dynamics of LEAF and USDC balances, redemptions, and overall liquidity within the Canopy ecosystem.
