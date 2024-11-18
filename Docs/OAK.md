Here's the complete updated OAK.md file:

```markdown:Docs/OAK.md
# Canopy OAK Distribution Model

## Overview

The OAK Distribution Model manages the distribution and redemption of OAK tokens within the Canopy ecosystem. The model was integrated into the simulation framework to track and visualize OAK token distributions and redemptions over time.

## Implementation Details

### 1. Core Components

#### OAK Distribution Configuration
- Total OAK supply: 500,000 tokens (hard cap)
- Distribution deals defined in `src/Data/oak_deals.py`
- Each deal includes:
  - Counterparty identification
  - OAK amount allocation
  - Start month
  - Vesting period
  - IRR threshold
  - Unlock month

#### Model Integration
The OAK model was integrated into the main simulation loop in:
```python:src/Simulations/simulate.py
startLine: 25
endLine: 48
```

### 2. Key Features

#### IRR-Based Redemption Logic
- Redemptions occur when risk-adjusted IRR falls below deal thresholds
- IRR calculation based on:
  - TVL performance
  - Revenue generation
  - Time to maturity
  - Current month's metrics

#### Supply Tracking
- Monitors total OAK supply (500,000 initial)
- Tracks remaining supply after redemptions
- Maintains historical supply records
- Records redemptions by counterparty

### 3. Visualization Integration

Four key charts were added to the simulation output:

1. **OAK Supply Over Time**
   - Tracks remaining OAK supply
   - Shows impact of redemptions on total supply

2. **Monthly OAK Redemptions**
   - Bar chart showing redemption volume by month
   - Helps identify peak redemption periods

3. **Cumulative OAK Redemptions**
   - Running total of all redemptions
   - Visualizes redemption pace over time

4. **Redemptions by Counterparty**
   - Individual redemption tracks for each deal
   - Compares redemption patterns across counterparties

### 4. Testing Implementation

Comprehensive testing was added in:
```python:Tests/test_OAK.py
startLine: 19
endLine: 160
```

Key test scenarios include:
- Deal validation
- IRR calculations
- Full 48-month simulations
- Redemption accuracy verification
- Supply tracking validation

### 5. Model Assumptions

As documented in:
```markdown:Assumptions.md
startLine: 218
endLine: 237
```

### 6. Integration with Other Models

The OAK model interfaces with:
1. TVL Model - for performance metrics
2. Revenue Model - for IRR calculations
3. AEGIS Model - for LP token management
4. LEAF Pairs Model - for price impact assessment

### 7. Simulation Results

The integrated OAK model produces:
- Monthly redemption statistics
- Supply tracking metrics
- IRR performance data
- Counterparty redemption patterns

### 8. Future Enhancements

Planned improvements include:
1. Dynamic IRR thresholds
2. Partial redemption capabilities
3. Lockup period implementation
4. Redemption rate limits
5. Enhanced deal modification features

## Technical Documentation

### Model Initialization
```python
oak_deals = get_oak_distribution_deals()
oak_config = OAKDistributionConfig(
    total_oak_supply=500_000,
    deals=oak_deals
)
oak_model = OAKModel(oak_config)
```

### Simulation Integration
```python
if month >= activation_months['OAK_START_MONTH']:
    current_irr = calculate_current_irr(month, total_tvl, revenue_model.cumulative_revenue)
    oak_model.step(current_month=month, current_irr=current_irr)
    oak_states.append(oak_model.get_state())
```

### Visualization Implementation
```python
plot_oak_distributions(oak_states)
```

## Conclusion

The OAK Distribution Model successfully:
1. Manages OAK token distribution and redemption
2. Integrates with existing simulation framework
3. Provides clear visualization of token dynamics
4. Maintains accurate supply tracking
5. Implements IRR-based redemption logic

The model now serves as a core component of the Canopy ecosystem simulation, providing valuable insights into token distribution patterns and redemption behaviors.
