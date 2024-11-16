# Canopy TVL Model Specification

## Terminology

- **Move TVL**: Total value locked in the Move ecosystem
- **Canopy TVL**: Value locked directly through Canopy's platform
- **Boosted by Canopy TVL**: Value locked elsewhere but boosted through Canopy's features
- **Total Canopy Impact**: Sum of Canopy TVL and Boosted by Canopy TVL (always < Move TVL)

## Initial Conditions (as of Month 0)

- Move Blockchain Total TVL: $800M
- Canopy TVL: $350M
- Initial Canopy Market Share: 43.75%
- Initial Boost Share: 10% of non-Canopy TVL

## Key Growth Assumptions

### Move Blockchain Growth

Annual growth rates for Move ecosystem:

- Year 1: 150% annual growth
- Year 2: 100% annual growth
- Year 3: 75% annual growth
- Year 4: 50% annual growth
- Year 5: 40% annual growth

### Canopy Market Share

- Starting from 43.75% (350M/800M)
- Exponential decay as competitors enter
- Minimum market share floor: 10%
- Market share decay rate: 2% annually

### Boosted TVL Growth

- Initial boost: 10% of available non-Canopy TVL
- Growth follows sigmoid curve (S-curve)
- Boost share increases with network effects
- Cannot exceed available non-Canopy TVL

## Implementation Details

### 1. Model Configuration

The TVLModelConfig dataclass centralizes all parameters:

```python
@dataclass
class TVLModelConfig:
    initial_move_tvl: float          # Initial Move TVL in USD
    initial_canopy_tvl: float        # Initial Canopy TVL in USD
    move_growth_rates: list[float]   # Annual growth rates for Move by year
    min_market_share: float          # Minimum market share floor
    market_share_decay_rate: float   # Rate at which market share declines
    initial_boost_share: float       # Initial boost share
    boost_growth_rate: float         # Growth rate for boost
```

### 2. Move TVL Calculation

- Compounds annual growth rates monthly
- Handles transition between years
- Maintains constant growth after year 5
Reference implementation:

```python:src/Functions/TVL.py
startLine: 61
endLine: 78
```

### 3. Canopy TVL Calculation

- Applies market share to total Move TVL
- Uses exponential decay for market share
- Enforces minimum market share floor
Reference implementation:

```python:src/Functions/TVL.py
startLine: 80
endLine: 84
```

### 4. Boosted TVL Calculation

- Calculates available TVL (Move TVL - Canopy TVL)
- Applies sigmoid growth function to boost share
- Ensures total Canopy impact < Move TVL
Reference implementation:

```python:src/Functions/TVL.py
startLine: 15
endLine: 39
```

### 5. Simulation

The simulation runs for 60 months (5 years) and:

- Tracks all TVL metrics monthly
- Calculates annual growth rates
- Generates visualization plots
- Outputs detailed data tables
Reference implementation:

```python:src/Simulations/simulate.py
startLine: 4
endLine: 83
```

## Model Constraints

1. **TVL Hierarchy**
   - Move TVL > Total Canopy Impact
   - Total Canopy Impact = Canopy TVL + Boosted TVL
   - Boosted TVL ≤ (Move TVL - Canopy TVL)

2. **Growth Constraints**
   - Market share ≥ Minimum floor (10%)
   - Boost share ≤ 100% of available TVL
   - All TVL values must be positive

## Model Limitations

1. **Simplifications**
   - No seasonal variations
   - Smooth transitions between growth rates
   - Deterministic growth patterns
   - No external market shocks

2. **Technical Constraints**
   - Fixed annual growth rate periods
   - No Monte Carlo/probabilistic modeling
   - Limited feedback loops between metrics

## Recommended Extensions

1. **Enhanced Modeling**
   - Add seasonal adjustment factors
   - Implement market shock scenarios
   - Include competitive dynamics
   - Add network effect multipliers

2. **Risk Analysis**
   - Monte Carlo simulations
   - Sensitivity analysis on key parameters
   - Scenario modeling (bull/bear cases)
   - Stress testing

3. **Validation**
   - Backtesting against historical data
   - Peer comparison analysis
   - Regular recalibration process
