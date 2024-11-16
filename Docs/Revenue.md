```markdown:Docs/Revenue.md
# Canopy Revenue Model Specification

## Overview

The Revenue Model (`src/Functions/Revenue.py`) is designed to project revenue streams based on the Total Value Locked (TVL) composition within the Canopy ecosystem. Leveraging the existing TVL projections, the Revenue Model calculates both volatile and stable revenues, adapting to market dynamics over time. Revenue calculations are integrated into the simulation workflow (`src/Simulations/simulate.py`) and are accompanied by dedicated visualizations to provide clear insights into revenue trends.

## Initial Conditions

- **Initial Volatile TVL Share**: 10%
- **Initial Stable TVL Share**: 90%
- **Initial Volatile Revenue Rate**: 5% annually
- **Initial Stable Revenue Rate**: 1% annually
- **Target Volatile TVL Share (5 years)**: 20%
- **Target Stable TVL Share (5 years)**: 80%
- **Target Volatile Revenue Rate (5 years)**: 1% annually
- **Target Stable Revenue Rate (5 years)**: 0.1% annually

## Python Implementation

```python:src/Functions/Revenue.py
from dataclasses import dataclass
import math

@dataclass
class RevenueModelConfig:
    # Initial TVL composition
    initial_volatile_share: float    # Initial % of TVL that is volatile
    
    # Revenue rates (annual)
    initial_volatile_rate: float     # Initial revenue rate for volatile TVL
    initial_stable_rate: float       # Initial revenue rate for stable TVL
    target_volatile_rate: float      # Target revenue rate for volatile TVL
    target_stable_rate: float        # Target revenue rate for stable TVL
    
    # Decay rates
    revenue_rate_decay: float        # How quickly revenue rates decline
    volatile_share_growth: float     # How quickly volatile share grows
    
    # Target volatile share
    target_volatile_share: float     # Long-term target for volatile share

class RevenueModel:
    def __init__(self, config: RevenueModelConfig):
        self.config = config
        self._initial_stable_share = 1 - config.initial_volatile_share
        self._target_stable_share = 1 - config.target_volatile_share

    def calculate_revenue(self, month: int, tvl: float) -> float:
        """
        Calculate monthly revenue based on TVL and time since launch
        
        Args:
            month: Number of months since start (0-based)
            tvl: Total TVL amount in USD
            
        Returns:
            Monthly revenue in USD
        """
        # Calculate current TVL composition
        volatile_share = self._calculate_volatile_share(month)
        stable_share = 1 - volatile_share
        
        # Calculate current revenue rates (monthly)
        volatile_rate = self._calculate_volatile_rate(month)
        stable_rate = self._calculate_stable_rate(month)
        
        # Calculate revenue components
        volatile_tvl = tvl * volatile_share
        stable_tvl = tvl * stable_share
        
        volatile_revenue = volatile_tvl * volatile_rate
        stable_revenue = stable_tvl * stable_rate
        
        return volatile_revenue + stable_revenue

    def _calculate_volatile_share(self, month: int) -> float:
        """Calculate the volatile share of TVL for given month"""
        share_range = self.config.target_volatile_share - self.config.initial_volatile_share
        progress = 1 - math.exp(-self.config.volatile_share_growth * month)
        return self.config.initial_volatile_share + (share_range * progress)

    def _calculate_volatile_rate(self, month: int) -> float:
        """Calculate monthly revenue rate for volatile TVL"""
        annual_rate = self._calculate_decaying_rate(
            month,
            self.config.initial_volatile_rate,
            self.config.target_volatile_rate
        )
        return annual_rate / 12  # Convert to monthly rate

    def _calculate_stable_rate(self, month: int) -> float:
        """Calculate monthly revenue rate for stable TVL"""
        annual_rate = self._calculate_decaying_rate(
            month,
            self.config.initial_stable_rate,
            self.config.target_stable_rate
        )
        return annual_rate / 12  # Convert to monthly rate

    def _calculate_decaying_rate(self, month: int, initial_rate: float, target_rate: float) -> float:
        """Helper to calculate exponentially decaying rate"""
        rate_range = initial_rate - target_rate
        decay = math.exp(-self.config.revenue_rate_decay * month)
        return target_rate + (rate_range * decay)
```

### Sample Usage

```python
# Initialize revenue model
config = RevenueModelConfig(
    initial_volatile_share=0.10,     # 10% volatile at start
    initial_volatile_rate=0.05,      # 5% annual revenue rate for volatile
    initial_stable_rate=0.01,        # 1% annual revenue rate for stable
    target_volatile_rate=0.01,       # 1% target annual revenue rate for volatile
    target_stable_rate=0.001,        # 0.1% target annual revenue rate for stable
    revenue_rate_decay=0.03,         # Revenue rate decay parameter
    volatile_share_growth=0.02,      # Volatile share growth parameter
    target_volatile_share=0.20       # Target 20% volatile share
)

revenue_model = RevenueModel(config)

# Calculate revenue for a specific month and TVL
month = 12
tvl = 1_000_000_000
monthly_revenue = revenue_model.calculate_revenue(month, tvl)
```

## Implementation Details

### Integration with Simulation (`simulate.py`)

1. **Import Revenue Model**:
    ```python
    from src.Functions.Revenue import RevenueModel, RevenueModelConfig
    ```

2. **Initialize Revenue Model**:
    ```python
    revenue_config = RevenueModelConfig(
        initial_volatile_share=0.10,
        initial_volatile_rate=0.05,
        initial_stable_rate=0.01,
        target_volatile_rate=0.01,
        target_stable_rate=0.001,
        revenue_rate_decay=0.03,
        volatile_share_growth=0.02,
        target_volatile_share=0.20
    )
    
    revenue_model = RevenueModel(revenue_config)
    ```

3. **Calculate and Store Revenue**:
    Within the simulation loop, calculate revenue for each month and store the results.
    ```python
    revenues = []
    
    for month in months:
        move_tvl, canopy_tvl, boosted_tvl = model.get_tvls(month)
        current_tvl = move_tvl  # Assuming revenue is based on total Move TVL
        revenue = revenue_model.calculate_revenue(month, current_tvl)
        revenues.append(revenue)
    ```

4. **Generate Revenue Graphs**:
    Create separate plots for revenue visualization.
    ```python
    # Plot Revenue Over Time
    plt.figure(figsize=(14, 7))
    plt.plot(months, revenues, label='Monthly Revenue', color='gold', linewidth=2)
    plt.title('Monthly Revenue Over 60 Months')
    plt.xlabel('Month')
    plt.ylabel('Revenue (USD)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    ```

## Key Features

1. **Composition Tracking**: Models the transition from stable to volatile TVL over time using sigmoid growth.
2. **Rate Decay**: Implements exponential decay for both volatile and stable revenue rates.
3. **Single Interface**: Provides a straightforward `calculate_revenue()` method for projecting monthly revenues.
4. **Configurable Parameters**: Allows all key assumptions and growth factors to be easily adjusted via the configuration.

## Model Assumptions

1. **Exponential Decay for Revenue Rates**: Revenue rates decline exponentially towards target rates.
2. **Smooth Transition in TVL Composition**: The shift from stable to volatile TVL follows a continuous sigmoid curve.
3. **Monthly Revenue Calculation**: Revenue is calculated on a monthly basis derived from annual rates.
4. **Independent Decay Rates**: Volatile and stable revenue rates decay independently of each other.

## Integration with Simulation

- **Revenue Calculation**: Integrated within `simulate.py` to calculate revenue alongside TVL metrics.
- **Visualization**: Dedicated revenue graphs are generated to provide clear insights separate from TVL visualizations.
- **Data Output**: Revenue data is included in the simulation's data tables for comprehensive analysis.

## Limitations

1. **Market Volatility Impacts**: Does not account for sudden market changes affecting TVL composition.
2. **Competitive Pressure on Rates**: Revenue rates are not dynamically adjusted based on competitor actions.
3. **Seasonal Variations**: Ignores potential seasonal effects on revenue generation.
4. **Network Effects**: Network-driven factors influencing revenue growth are not modeled.
5. **Regulatory Changes**: Does not incorporate potential regulatory impacts on revenue rates.

## Recommended Extensions

1. **Add Market Shock Scenarios**: Incorporate sudden changes in revenue rates to simulate market disruptions.
2. **Include Competitive Pressure Modeling**: Adjust revenue rates based on competitive dynamics and market share shifts.
3. **Add Seasonal Adjustment Factors**: Model seasonal trends affecting revenue generation.
4. **Implement Correlation with TVL Growth**: Integrate TVL growth influences directly into revenue projections.
5. **Add Risk-Adjusted Scenarios**: Incorporate risk factors to adjust revenue projections based on varying conditions.

```

```python:src/Functions/Revenue.py
from dataclasses import dataclass
import math

@dataclass
class RevenueModelConfig:
    # Initial TVL composition
    initial_volatile_share: float    # Initial % of TVL that is volatile
    
    # Revenue rates (annual)
    initial_volatile_rate: float     # Initial revenue rate for volatile TVL
    initial_stable_rate: float       # Initial revenue rate for stable TVL
    target_volatile_rate: float      # Target revenue rate for volatile TVL
    target_stable_rate: float        # Target revenue rate for stable TVL
    
    # Decay rates
    revenue_rate_decay: float        # How quickly revenue rates decline
    volatile_share_growth: float     # How quickly volatile share grows
    
    # Target volatile share
    target_volatile_share: float     # Long-term target for volatile share

class RevenueModel:
    def __init__(self, config: RevenueModelConfig):
        self.config = config
        self._initial_stable_share = 1 - config.initial_volatile_share
        self._target_stable_share = 1 - config.target_volatile_share

    def calculate_revenue(self, month: int, tvl: float) -> float:
        """
        Calculate monthly revenue based on TVL and time since launch
        
        Args:
            month: Number of months since start (0-based)
            tvl: Total TVL amount in USD
            
        Returns:
            Monthly revenue in USD
        """
        # Calculate current TVL composition
        volatile_share = self._calculate_volatile_share(month)
        stable_share = 1 - volatile_share
        
        # Calculate current revenue rates (monthly)
        volatile_rate = self._calculate_volatile_rate(month)
        stable_rate = self._calculate_stable_rate(month)
        
        # Calculate revenue components
        volatile_tvl = tvl * volatile_share
        stable_tvl = tvl * stable_share
        
        volatile_revenue = volatile_tvl * volatile_rate
        stable_revenue = stable_tvl * stable_rate
        
        return volatile_revenue + stable_revenue

    def _calculate_volatile_share(self, month: int) -> float:
        """Calculate the volatile share of TVL for given month"""
        share_range = self.config.target_volatile_share - self.config.initial_volatile_share
        progress = 1 - math.exp(-self.config.volatile_share_growth * month)
        return self.config.initial_volatile_share + (share_range * progress)

    def _calculate_volatile_rate(self, month: int) -> float:
        """Calculate monthly revenue rate for volatile TVL"""
        annual_rate = self._calculate_decaying_rate(
            month,
            self.config.initial_volatile_rate,
            self.config.target_volatile_rate
        )
        return annual_rate / 12  # Convert to monthly rate

    def _calculate_stable_rate(self, month: int) -> float:
        """Calculate monthly revenue rate for stable TVL"""
        annual_rate = self._calculate_decaying_rate(
            month,
            self.config.initial_stable_rate,
            self.config.target_stable_rate
        )
        return annual_rate / 12  # Convert to monthly rate

    def _calculate_decaying_rate(self, month: int, initial_rate: float, target_rate: float) -> float:
        """Helper to calculate exponentially decaying rate"""
        rate_range = initial_rate - target_rate
        decay = math.exp(-self.config.revenue_rate_decay * month)
        return target_rate + (rate_range * decay)