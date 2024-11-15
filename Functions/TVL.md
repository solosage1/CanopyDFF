# Canopy TVL Model Specification

TVL.md

## Initial Conditions (as of Month 0)
- Move Blockchain Total TVL: $800M
- Canopy TVL: $300M
- Initial Canopy Market Share: 37.5%

## Key Growth Assumptions

### Move Blockchain Growth
1. Base annual growth rate for Move ecosystem
   - Higher growth in early years, moderating over time
   - Year 1: 200% annual growth
   - Year 2: 150% annual growth
   - Year 3: 100% annual growth
   - Year 4: 75% annual growth
   - Year 5: 50% annual growth

### Canopy Market Share Decay
1. Market share decline rate
   - Starting from 37.5%
   - Gradual decline as competitors enter
   - Exponential decay function with floor
   - Minimum market share floor: 10%

## Python Implementation

### Model Definition
```python
import math
from dataclasses import dataclass
from typing import Tuple

@dataclass
class TVLModelConfig:
    initial_move_tvl: float          # Initial Move TVL in USD
    initial_canopy_tvl: float        # Initial Canopy TVL in USD
    move_growth_rates: list[float]   # Annual growth rates for Move by year
    min_market_share: float          # Minimum market share floor
    market_share_decay_rate: float   # Rate at which market share declines

class TVLModel:
    def __init__(self, config: TVLModelConfig):
        self.config = config
        self._initial_market_share = config.initial_canopy_tvl / config.initial_move_tvl

    def get_tvl(self, month: int) -> Tuple[float, float]:
        """
        Calculate Move and Canopy TVL for a given month
        
        Args:
            month: Number of months since start (0-based)
            
        Returns:
            Tuple of (move_tvl, canopy_tvl) in USD
        """
        move_tvl = self._calculate_move_tvl(month)
        canopy_share = self._calculate_canopy_share(month)
        canopy_tvl = move_tvl * canopy_share
        return move_tvl, canopy_tvl

    def _calculate_move_tvl(self, month: int) -> float:
        """Private helper to calculate Move TVL"""
        year = month // 12
        if year >= len(self.config.move_growth_rates):
            year = len(self.config.move_growth_rates) - 1
            
        annual_rate = self.config.move_growth_rates[year]
        monthly_rate = (1 + annual_rate) ** (1/12) - 1
        
        return self.config.initial_move_tvl * (1 + monthly_rate) ** month

    def _calculate_canopy_share(self, month: int) -> float:
        """Private helper to calculate Canopy's market share"""
        decay = math.exp(-self.config.market_share_decay_rate * month)
        share = (self.config.min_market_share + 
                (self._initial_market_share - self.config.min_market_share) * decay)
        return max(share, self.config.min_market_share)
```

### Sample Usage
```python
# Initialize model with configuration
config = TVLModelConfig(
    initial_move_tvl=800_000_000,
    initial_canopy_tvl=300_000_000,
    move_growth_rates=[2.0, 1.5, 1.0, 0.75, 0.5],
    min_market_share=0.10,
    market_share_decay_rate=0.04
)

model = TVLModel(config)

# Get TVL projections for any month
month_12_move_tvl, month_12_canopy_tvl = model.get_tvl(12)
month_24_move_tvl, month_24_canopy_tvl = model.get_tvl(24)
```

## Implementation Details

### Key Features
1. **Single Public Interface**: The `get_tvl()` method provides a clean, simple interface for retrieving TVL projections
2. **Encapsulated Configuration**: All model parameters are contained in the `TVLModelConfig` dataclass
3. **Type Safety**: Full type hints throughout the implementation
4. **Private Helper Methods**: Internal calculations are hidden from the public interface
5. **Immutable Configuration**: Configuration is set once at initialization

### Mathematical Models Used
1. **Move TVL Growth**:
   - Converts annual rates to monthly compound growth
   - TVL(t) = Initial_TVL * (1 + monthly_rate)^t

2. **Market Share Decay**:
   - Exponential decay with floor
   - Share(t) = min_share + (initial_share - min_share) * e^(-decay_rate * t)

## Model Assumptions and Limitations

### Key Assumptions
1. Growth Pattern Assumptions
   - Move blockchain growth follows a predictable pattern
   - Growth rates decline in a stepwise manner annually
   - No major market crashes or black swan events

2. Market Share Assumptions
   - Market share decline follows exponential decay
   - Competitive pressures increase over time
   - Floor exists due to first-mover advantage
   - No major competitive disruptions

3. Market Conditions
   - No regulatory changes affecting TVL
   - Continuous market operation
   - No major technical failures

### Model Limitations
1. **Simplifications**
   - Does not account for seasonal variations
   - Assumes smooth transitions between growth rates
   - Does not model specific competitor actions
   - Does not account for network effects

2. **Technical Limitations**
   - Fixed growth rate periods (annual)
   - Deterministic (no randomness/monte carlo)
   - No feedback loops between Move and Canopy growth

## Recommended Extensions

The model can be enhanced by:
1. Adding seasonal variations through multiplicative factors
2. Incorporating market shock scenarios
3. Adding competitive entry events
4. Including network effect multipliers
5. Adding risk-adjusted scenarios through Monte Carlo simulation
6. Implementing feedback loops between Move and Canopy growth

## Sensitivity Analysis Recommendations

Key variables to test:
1. Move growth rates
2. Market share decay rate
3. Minimum market share floor
4. Initial TVL values

For each variable, recommend testing:
- Base case
- Optimistic case (+25%)
- Pessimistic case (-25%)
- Extreme cases (±50%)
````
