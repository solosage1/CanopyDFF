# Canopy Revenue Model Specification

## Initial Conditions

- Initial Volatile TVL Share: 10%
- Initial Stable TVL Share: 90%
- Initial Volatile Revenue Rate: 5% annually
- Initial Stable Revenue Rate: 1% annually
- Target Volatile TVL Share (5y): 20%
- Target Stable TVL Share (5y): 80%
- Target Volatile Revenue Rate (5y): 1% annually
- Target Stable Revenue Rate (5y): 0.1% annually

## Python Implementation

```python
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

## Key Features

1. **Composition Tracking**: Models shift from stable to volatile TVL over time
2. **Rate Decay**: Models declining revenue rates for both types of TVL
3. **Single Interface**: Simple `calculate_revenue()` method for revenue projection
4. **Configurable Parameters**: All key assumptions can be adjusted through config

## Model Assumptions

1. Exponential decay for revenue rates
2. Smooth transition in TVL composition
3. Monthly revenue calculation from annual rates
4. Independent decay rates for volatile and stable TVL

## Limitations

1. Does not account for:
   - Market volatility impacts
   - Competitive pressure on rates
   - Seasonal variations
   - Network effects
   - Regulatory changes

## Recommended Extensions

1. Add market shock scenarios
2. Include competitive pressure modeling
3. Add seasonal adjustment factors
4. Implement correlation with TVL growth
5. Add risk-adjusted scenarios
