# Monthly Simulation Loop Documentation

## Overview
The simulation runs month-by-month, tracking the interaction between AEGIS, LEAF Pairs, TVL, and OAK token systems. The implementation is found in:
```python:src/Simulations/simulate.py
startLine: 1
endLine: 385
```

## Monthly Update Sequence

1. **Initialize Month**
   - Current month counter is incremented
   - LEAF price is calculated (currently fixed at $1.00)

2. **TVL Updates**
   - TVL model processes new contributions
   - Categories updated:
     - Protocol-locked TVL
     - Contracted TVL
     - Organic TVL
     - Boosted TVL
   - New deals are activated if their start month matches current month

3. **LEAF Pairs Updates**
   - Active deals are retrieved for current month
   - Each deal's liquidity is updated based on:
     - Current LEAF price
     - Deal's target LEAF percentage
     - Concentration parameters
   - Inactive deals are filtered out

4. **AEGIS Updates**
   - LEAF balance updated
   - USDC balance updated
   - Price impact calculated
   - State recorded in history

5. **OAK Token Processing**
   - New distributions processed
   - Redemptions handled
   - Supply updated
   - History recorded

6. **Metrics Collection**
   ```python
   metrics = {
       'month': current_month,
       'total_leaf': total_leaf,
       'total_usdc': total_usdc,
       'total_value': total_usdc + (total_leaf * current_leaf_price),
       'tvl': tvl_model.get_current_tvl(),
       'leaf_price': current_leaf_price
   }
   metrics_history.append(metrics)
   ```

7. **Revenue Calculation**
   - Monthly revenue calculated per category
   - Added to cumulative totals
   - Stored in revenue history

8. **State Recording**
   - All model states saved to respective histories
   - Monthly metrics added to metrics history
   - Revenue data recorded

## Core Components

1. **Initialization**
   - Logging setup with rotation (keeps last 3 log files)
   - TVL contributions loaded via TVLLoader
   - AEGIS, LEAF Pairs, and OAK models initialized
   - Initial metrics tracking setup

2. **LEAF Price Model**
   - Currently using placeholder price of $1.00
   - Future implementation needed for dynamic pricing

3. **Liquidity Tracking**
   ```python
   def track_liquidity_metrics(month, current_leaf_price, aegis_model, leaf_pairs_model):
       # Get AEGIS state
       aegis_state = aegis_model.get_state()
       total_leaf = aegis_state['leaf_balance']
       total_usdc = aegis_state['usdc_balance']
       
       # Add LEAF pair balances
       active_deals = leaf_pairs_model.get_active_deals(month)
       for deal in active_deals:
           total_leaf += deal.leaf_balance
           total_usdc += deal.other_balance
           
       return {
           'month': month,
           'total_leaf': total_leaf,
           'total_usdc': total_usdc,
           'total_value': total_usdc + (total_leaf * current_leaf_price)
       }
   ```

## Visualization Components

1. **TVL Composition Plot**
   - Protocol-locked TVL
   - Contracted TVL
   - Organic TVL
   - Boosted TVL
   - All values shown in billions USD

2. **AEGIS Metrics**
   - LEAF balance over time
   - USDC balance over time
   - LEAF price history

3. **LEAF Pairs Activity**
   - Number of active pairs over time
   - Total liquidity provided

4. **OAK Token Metrics**
   - Allocated tokens
   - Distributed tokens
   - Redeemed tokens
   - Monthly redemption amounts

## Data Collection

1. **Metrics History**
   - Monthly TVL by category
   - Total LEAF and USDC liquidity
   - Current LEAF price
   - Total system value

2. **Revenue Tracking**
   - Monthly revenue by category
   - Cumulative revenue over time
   - Revenue shown in millions USD

## Current Implementation Status

1. **Working Components**
   - Monthly update sequence
   - Logging system with rotation
   - Basic TVL tracking
   - LEAF Pairs liquidity tracking
   - AEGIS balance tracking
   - OAK token distribution/redemption
   - Visualization of all metrics

2. **Pending Implementation**
   - Dynamic LEAF pricing model
   - Market impact on liquidity
   - Advanced TVL growth modeling
   - Revenue rate adjustments

## Output Format

1. **Console Output**
   - Monthly summaries of revenue
   - Final metrics summary
   - System status updates

2. **Visual Output**
   - 4x2 grid of plots showing:
     - TVL composition
     - Revenue trends
     - AEGIS metrics
     - LEAF Pairs activity
     - OAK token status
     - Monthly redemptions

3. **Logging Output**
   - Detailed system events
   - Error tracking
   - Performance metrics
   - Stored in rotating log files

## Future Enhancements Needed
- Implementation of dynamic LEAF pricing
- Integration of market impact calculations
- Advanced TVL modeling
- Revenue rate adjustments based on market conditions
- Enhanced error handling and recovery



Here's the exact monthly update sequence from our simulation:

````markdown:simulation_loop.md
## Exact Monthly Update Sequence

1. **Start Month**
   ```python
   for month in range(1, simulation_months + 1):
       current_leaf_price = calculate_leaf_price(month, total_liquidity)
   ```

2. **TVL Model Updates**
   ```python
   # Process TVL contributions for this month
   tvl_model.update_tvl(month)
   
   # Get new TVL state
   current_tvl = tvl_model.get_current_tvl()
   ```

3. **LEAF Pairs Updates**
   ```python
   # Update all active LEAF pairs
   leaf_pairs_model.update_deals(month, current_leaf_price)
   
   # Get current liquidity state
   leaf_pairs_leaf, leaf_pairs_usdc = leaf_pairs_model.get_liquidity_within_percentage(
       percentage=5.0,  # Standard 5% range
       current_price=current_leaf_price
   )
   ```

4. **AEGIS Updates**
   ```python
   # Update AEGIS model
   aegis_model.update_state(month, current_leaf_price)
   
   # Get current AEGIS liquidity
   aegis_leaf, aegis_usdc = aegis_model.get_liquidity_within_percentage(
       percentage=5.0,  # Standard 5% range
       current_price=current_leaf_price
   )
   ```

5. **OAK Token Updates**
   ```python
   # Process OAK distributions
   oak_model.process_distributions(month)
   
   # Handle OAK redemptions
   oak_model.process_redemptions(month)
   ```

6. **Track Monthly Metrics**
   ```python
   # Calculate total liquidity
   metrics = track_liquidity_metrics(
       month=month,
       current_leaf_price=current_leaf_price,
       aegis_model=aegis_model,
       leaf_pairs_model=leaf_pairs_model
   )
   
   # Add TVL data
   metrics['tvl'] = current_tvl
   metrics['leaf_price'] = current_leaf_price
   
   # Store metrics
   metrics_history.append(metrics)
   ```

7. **Calculate Monthly Revenue**
   ```python
   # Get revenue for each category
   monthly_revenue = revenue_model.calculate_monthly_revenue(
       month=month,
       tvl=current_tvl,
       leaf_price=current_leaf_price
   )
   
   # Update cumulative revenue
   cumulative_revenue += sum(monthly_revenue.values())
   
   # Store revenue data
   revenue_history.append(monthly_revenue)
   ```

8. **Print Monthly Summary**
   ```python
   print_monthly_summary(
       month=month,
       monthly_revenue=monthly_revenue,
       cumulative_revenue=cumulative_revenue
   )
   ```

9. **End Month Processing**
   ```python
   # Record states in history
   aegis_model.record_state(month)
   leaf_pairs_model.record_state(month)
   oak_model.record_state(month)
   ```

## Key Monthly Interactions

1. **Liquidity Flow**
   - AEGIS provides base liquidity (1B LEAF, 100M USDC)
   - LEAF Pairs add additional liquidity through deals
   - Both systems maintain separate concentration mechanisms

2. **Price Impact**
   - AEGIS uses constant product formula
   - LEAF Pairs use modified concentration based on balance vs target
   - Combined impact affects overall LEAF price (currently fixed at $1.00)

3. **TVL Integration**
   - New TVL activates deals in LEAF Pairs
   - TVL categories affect revenue calculations
   - OAK distributions tied to TVL milestones

4. **Revenue Generation**
   - Based on current TVL levels
   - Affected by LEAF price
   - Distributed across different categories
   - Impacts future TVL growth

5. **State Management**
   - Each system maintains its own state
   - Monthly metrics capture overall system health
   - Historical data stored for analysis and visualization
````

This represents the exact sequence of operations that occur each month in our current simulation implementation. Would you like me to explain any particular part in more detail?