# Canopy Influenced TVL Model Specification

Functions/InfluencedTVL.md

## Initial Conditions

- Initial Non-Canopy TVL Influence: 10%
- Target Non-Canopy TVL Influence (5y): 50%
- Growth Pattern: Sigmoid curve (slow start, accelerated middle, plateau)

## Python Implementation

```python
import math
from dataclasses import dataclass

@dataclass
class InfluencedTVLConfig:
    initial_influence_share: float    # Initial % of non-Canopy TVL that is influenced
    target_influence_share: float     # Target % of non-Canopy TVL that is influenced
    growth_rate: float               # Rate of influence growth
    max_months: int = 60             # Number of months to reach target (default 5 years)

class InfluencedTVLModel:
    def __init__(self, config: InfluencedTVLConfig):
        self.config = config
        self._influence_range = config.target_influence_share - config.initial_influence_share

    def get_influenced_tvl(self, month: int, canopy_tvl: float, move_tvl: float) -> float:
        """
        Calculate Canopy's influenced TVL for a given month
        
        Args:
            month: Number of months since start (0-based)
            canopy_tvl: Canopy's direct TVL for the month
            move_tvl: Total Move TVL for the month
            
        Returns:
            Influenced TVL amount in USD (excluding Canopy's direct TVL)
        """
        # Calculate non-Canopy TVL
        non_canopy_tvl = move_tvl - canopy_tvl
        
        # Calculate influence percentage using sigmoid function
        influence_share = self._calculate_influence_share(month)
        
        # Calculate influenced TVL
        influenced_tvl = non_canopy_tvl * influence_share
        
        return influenced_tvl

    def _calculate_influence_share(self, month: int) -> float:
        """
        Calculate the share of non-Canopy TVL that is influenced using sigmoid function
        """
        # Normalize month to -6 to 6 range for sigmoid
        normalized_time = (month / self.config.max_months * 12) - 6
        
        # Sigmoid function for smooth S-curve growth
        sigmoid = 1 / (1 + math.exp(-self.config.growth_rate * normalized_time))
        
        # Scale sigmoid output (0-1) to desired range
        influence_share = (self.config.initial_influence_share + 
                         self._influence_range * sigmoid)
        
        return min(influence_share, self.config.target_influence_share)
```

### Sample Usage
```python
# Initialize influenced TVL model
config = InfluencedTVLConfig(
    initial_influence_share=0.10,    # Start at 10% influence
    target_influence_share=0.50,     # Target 50% influence
    growth_rate=1.0,                 # Growth rate parameter
    max_months=60                    # 5-year projection
)

influenced_model = InfluencedTVLModel(config)

# Calculate influenced TVL for a specific month
month = 24
canopy_tvl = 500_000_000
move_tvl = 2_000_000_000
influenced_tvl = influenced_model.get_influenced_tvl(month, canopy_tvl, move_tvl)
```

## Key Features

1. **Sigmoid Growth Pattern**: Uses S-curve for realistic influence growth
2. **Configurable Parameters**: All key assumptions adjustable through config
3. **Simple Interface**: Single method to calculate influenced TVL
4. **Bounded Growth**: Never exceeds target influence share

## Mathematical Model

1. **Sigmoid Function**:
   - Normalized time: t = (month/max_months * 12) - 6
   - Base sigmoid: S(t) = 1 / (1 + e^(-growth_rate * t))
   - Scaled influence: influence = initial + range * S(t)

## Model Assumptions

1. Influence growth follows S-curve pattern
2. Influence is calculated as percentage of non-Canopy TVL
3. Growth plateaus at target influence share
4. Network effects create accelerating middle period

## Limitations

1. Does not account for:
   - Market conditions impact on influence
   - Competitive responses
   - Geographic variations
   - Protocol-specific factors

## Recommended Extensions

1. Add market condition modifiers
2. Include competitive response factors
3. Add geographic distribution modeling
4. Implement protocol-specific influence rates
5. Add confidence intervals

## Integration with TVL Model
This model is designed to work alongside the TVL model:

1. First calculate Move and Canopy TVL using TVL model
2. Pass results to Influenced TVL model
3. Combine direct and influenced TVL for total impact

## Sensitivity Analysis Recommendations

Key variables to test:

1. Initial influence share
2. Target influence share
3. Growth rate parameter
4. Time to target (max_months)

Test scenarios:

- Base case
- Aggressive growth (higher growth rate)
- Conservative growth (lower growth rate)
- Extended timeline (longer max_months)
- Compressed timeline (shorter max_months)

`````

This influenced TVL model:

1. Uses a sigmoid function for realistic S-curve growth
2. Maintains clear separation from direct TVL
3. Provides configurable parameters
4. Can be easily integrated with the existing TVL model
