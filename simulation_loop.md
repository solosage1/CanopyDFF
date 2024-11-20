# Monthly Simulation Loop Documentation

## Overview
The simulation runs month-by-month, with different components activating at specific months. Each month follows a precise sequence of operations to ensure accurate modeling of the protocol's behavior.

## Monthly Sequence

1. **State Recording** (Month Start)
   - Prints "--- Month {X} ---"
   - Records current state of all TVL contributions using `history_tracker.record_state()`
   Reference: 
```python:src/Simulations/simulate.py
startLine: 187
endLine: 190
```

2. **TVL Processing**
   - Calls `tvl_model.step()` to update all TVL positions
   - Calculates total TVL for the month
   - Stores TVL in `total_tvl_by_month`
   Reference:
```python:src/Simulations/simulate.py
startLine: 192
endLine: 195
```

3. **Revenue Processing**
   - Gets active contributions for the month
   - Calculates revenue for each contribution using individual revenue rates
   - Aggregates revenue by TVL type
   - Updates cumulative revenue totals
   - Stores in `revenue_by_month` and `cumulative_revenues`
   Reference:
```python:src/Simulations/simulate.py
startLine: 197
endLine: 202
```

4. **OAK Processing** (if month ≥ 4)
   - Processes monthly OAK distributions
   - Gets current AEGIS balances (USDC and LEAF)
   - Gets current LEAF price
   - Processes OAK redemptions
   - Updates AEGIS balances based on redemptions
   - Records OAK state
   - Prints distribution and redemption details
   Reference:
```python:src/Simulations/simulate.py
startLine: 205
endLine: 239
```

5. **AEGIS Processing** (if month ≥ 3)
   - Calculates OAK redemption rate based on total supply
   - Handles redemptions with calculated rate
   - Updates AEGIS state for the month
   Reference:
```python:src/Simulations/simulate.py
startLine: 241
endLine: 253
```

6. **LEAF Pairs Processing** (if month ≥ 1)
   - Updates all active LEAF pair deals using current price
   - Tracks liquidity metrics for active deals
   - Calculates total liquidity across all pairs

7. **LEAF Price Processing**
   - Uses LEAFPriceModel for price calculations
   - Considers current liquidity metrics
   - Updates price based on market conditions
   - Maintains price history for visualization

8. **End of Month Updates**
   - Updates AEGIS history arrays
   - Records liquidity metrics using `track_liquidity_metrics()`
   - Records LEAF price
   - Prints monthly summary with revenue details

## Helper Functions

1. **Track Liquidity Metrics**
   - Monitors AEGIS and LEAF Pairs liquidity
   - Calculates total LEAF and USDC liquidity
   - Returns metrics dictionary
   Reference:
```python:src/Simulations/simulate.py
startLine: 39
endLine: 63
```

2. **Estimate LEAF Price**
   - Uses LEAFPriceModel for calculations
   - Considers current liquidity and trade impact
   Reference:
```python:src/Simulations/simulate.py
startLine: 65
endLine: 86
```

## Visualization Outputs

After the simulation completes, the following charts are generated in a 4x2 grid:

1. **TVL Composition** (Position 1)
   - Stacked bar chart showing TVL by type over time
   - Types: ProtocolLocked, Contracted, Organic, Boosted
   - Y-axis in billions USD

2. **TVL Growth Rate** (Position 2)
   - Line chart showing month-over-month TVL growth rate
   - Y-axis in percentage

3. **Revenue Composition** (Position 3)
   - Stacked bar chart showing revenue by TVL type
   - Y-axis in millions USD

4. **Cumulative Revenue** (Position 4)
   - Line chart showing total cumulative revenue
   - Y-axis in millions USD

5. **LEAF Price** (Position 5)
   - Line chart showing LEAF token price over time
   - Y-axis in USD

6. **Liquidity Metrics** (Position 6)
   - Dual line chart showing LEAF and USDC liquidity
   - Y-axis in millions

7. **OAK Token Status** (Position 7)
   - Area chart showing allocated, distributed, and redeemed OAK
   - Y-axis in millions of tokens
   Reference:
```python:src/Simulations/simulate.py
startLine: 379
endLine: 416
```

8. **Monthly OAK Redemptions** (Position 8)
   - Bar chart showing monthly OAK redemption amounts
   - Y-axis in millions of tokens
   Reference:
```python:src/Simulations/simulate.py
startLine: 418
endLine: 425
```

## Component Activation Schedule

```python
activation_months = {
    'LEAF_PAIRS_START_MONTH': 1,
    'AEGIS_START_MONTH': 3,
    'OAK_START_MONTH': 4,
    'MARKET_START_MONTH': 5,
    'PRICE_START_MONTH': 5,
    'DISTRIBUTION_START_MONTH': 5,
    'BOOST_START_MONTH': 6
}
