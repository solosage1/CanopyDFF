# Monthly Simulation Loop Documentation

## Overview
The simulation runs month-by-month, with different components activating at specific months. Each month follows a precise sequence of operations to ensure accurate modeling of the protocol's behavior.

## Monthly Sequence

1. **State Recording** (Month Start)
   - Prints "--- Month {X} ---"
   - Records current state of all TVL contributions using `history_tracker.record_state()`

2. **TVL Processing**
   - Calls `tvl_model.step()` to update all TVL positions
   - Calculates total TVL for the month
   - Stores TVL in `total_tvl_by_month`

3. **Revenue Processing**
   - Gets active contributions for the month
   - Calculates revenue for each contribution using individual revenue rates
   - Aggregates revenue by TVL type
   - Updates cumulative revenue totals
   - Stores in `revenue_by_month` and `cumulative_revenues`

4. **OAK Processing** (if month ≥ 4)
   - Processes monthly OAK distributions
   - Gets current AEGIS balances (USDC and LEAF)
   - Gets current LEAF price
   - Processes OAK redemptions
   - Updates AEGIS balances based on redemptions
   - Records OAK state
   - Prints distribution and redemption details

5. **AEGIS Processing** (if month ≥ 3)
   - Calculates OAK redemption rate
   - Handles redemptions
   - Updates AEGIS state for the month

6. **LEAF Pairs Processing** (if month ≥ 1)
   - Updates all active LEAF pair deals using current price

7. **LEAF Price Processing** (if month ≥ 5)
   - Processes simulated trades ([10_000, -5_000, 15_000] USD)
   - For each trade:
     - Gets current liquidity metrics
     - Updates LEAF price based on trade impact
   - Finalizes month's LEAF price
   - If not active yet, uses initial price (1.0)

8. **End of Month Updates**
   - Updates AEGIS history arrays
   - Records liquidity metrics
   - Records LEAF price
   - Prints monthly summary with revenue details
   - Prints current LEAF price

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
```

## Visualization Outputs

After the simulation completes, the following charts are generated:

1. **TVL Composition** (4x2 grid, position 1)
   - Stacked bar chart showing TVL by type over time
   - Types: ProtocolLocked, Contracted, Organic, Boosted
   - Y-axis in billions USD

2. **TVL Growth Rate** (4x2 grid, position 2)
   - Line chart showing month-over-month TVL growth rate
   - Y-axis in percentage

3. **Revenue Composition** (4x2 grid, position 3)
   - Stacked bar chart showing revenue by TVL type
   - Types: ProtocolLocked, Contracted, Organic, Boosted
   - Y-axis in millions USD

4. **Cumulative Revenue** (4x2 grid, position 4)
   - Line chart showing total cumulative revenue
   - Y-axis in millions USD

5. **LEAF Price** (4x2 grid, position 5)
   - Line chart showing LEAF token price over time
   - Y-axis in USD

6. **Liquidity Metrics** (4x2 grid, position 6)
   - Dual line chart showing LEAF and USDC liquidity
   - Y-axis in millions

7. **OAK Token Status** (4x2 grid, position 7)
   - Area chart showing allocated, distributed, and redeemed OAK
   - Y-axis in millions of tokens

8. **Monthly OAK Redemptions** (4x2 grid, position 8)
   - Bar chart showing monthly OAK redemption amounts
   - Y-axis in millions of tokens