# CanopyDFF Implementation Order

## Repository Overview

The CanopyDFF repository comprises several interconnected models for Canopy's tokenomics and financial projections:

1. **TVL Model (`TVL.md`)**: Projects overall TVL growth, Canopy TVL, and Boosted TVL.
2. **Revenue Model (`Revenue.md`)**: Projects revenue based on TVL composition.
3. **LEAF Pairs Model (`LEAFPairs.md`)**: Handles liquidity pairs involving LEAF tokens.
4. **AEGIS Model (`AEGIS.md`)**: Manages LEAF and USDC balances and redemptions.
5. **OAK Distribution Model (`OAK.md`)**: Manages OAK token distribution and redemption.

## Completed Implementations

### 1. TVL Model (`TVL.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Combined TVL, Boosted TVL, and Total Impact into a single unified model.
- Core implementation in `src/Functions/TVL.py`.
- Simulation and visualization integrated into `src/Simulations/simulate.py`.

**Key Components**:

1. **TVLModelConfig**

    ```python:src/Functions/TVL.py
    @dataclass
    class TVLModelConfig:
        # Market parameters
        initial_move_tvl: float
        initial_canopy_tvl: float
        move_growth_rates: List[float]
        min_market_share: float
        market_share_decay_rate: float
        max_months: int = 60
    ```

2. **TVLModel**

    ```python:src/Functions/TVL.py
    class TVLModel:
        def __init__(self, config: TVLModelConfig):
            self.config = config
            self.contributions = []
            self.month = 0
            self.loader = TVLLoader(self)
        
        def add_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
            """Add a new contribution during simulation."""
            return self.loader.add_new_contribution(tvl_type, config)
        
        def step(self):
            """Advance the model by one month."""
            for contrib in self.contributions:
                if contrib.start_month <= self.month:
                    contrib.update_amount(self.month)
                    contrib.check_exit(self.month)
            self.month += 1
        
        def get_total_tvl(self) -> float:
            """Calculate total active TVL."""
            return sum(contrib.amount_usd for contrib in self.contributions if contrib.active)
        
        # Exit conditions
        def contract_end_condition(self, contribution: TVLContribution, month: int) -> bool:
            return month >= contribution.end_month
        
        def decay_exit_condition(self, contribution: TVLContribution, month: int) -> bool:
            return contribution.amount_usd <= 0
        
        def boosted_exit_condition(self, contribution: TVLContribution, month: int) -> bool:
            actual_boost_rate = self.get_actual_boost_rate(contribution, month)
            return actual_boost_rate < contribution.expected_boost_rate
        
        def get_actual_boost_rate(self, contribution: TVLContribution, month: int) -> float:
            # Placeholder for actual boost rate calculation
            return contribution.expected_boost_rate * max(0.5, 1 - 0.01 * month)
    ```

### 2. Revenue Model (`Revenue.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Implemented revenue calculation based on TVL composition.
- Core implementation in `src/Functions/Revenue.py`.
- Integrated revenue calculations into simulation in `src/Simulations/simulate.py`.

**Key Components**:

1. **RevenueModelConfig**

    ```python:src/Functions/Revenue.py
    @dataclass
    class RevenueModelConfig:
        pass
    ```

2. **RevenueModel**

    ```python:src/Functions/Revenue.py
    class RevenueModel:
        def __init__(self, config: RevenueModelConfig, tvl_model):
            self.tvl_model = tvl_model
            self.cumulative_revenue = 0.0
            self.revenue_history = []
    
        def calculate_revenue(self, month: int) -> Dict[str, float]:
            revenue_by_type = defaultdict(float)
            tvl_by_type = defaultdict(float)
            
            for contrib in self.tvl_model.contributions:
                if contrib.active and contrib.start_month <= month:
                    revenue = contrib.calculate_revenue(month)
                    revenue_by_type[contrib.tvl_type] += revenue
                    revenue_by_type['Total'] += revenue
                    tvl_by_type[contrib.tvl_type] += contrib.amount_usd
    
            # Calculate weighted average rates
            weighted_rates = {}
            for tvl_type in tvl_by_type:
                if tvl_by_type[tvl_type] > 0:
                    weighted_rates[tvl_type] = (
                        revenue_by_type[tvl_type] * 12 / tvl_by_type[tvl_type]
                    )
                else:
                    weighted_rates[tvl_type] = 0.0
    
            self.cumulative_revenue += revenue_by_type['Total']
            self.revenue_history.append({
                'revenue': revenue_by_type,
                'weighted_rates': weighted_rates
            })
            
            return revenue_by_type
    ```

3. **Simulation Integration**

    ```python:src/Simulations/simulate.py
    # Inside simulate.py

    def main():
        # ... [previous code]

        # Initialize models
        tvl_model = TVLModel(TVLModelConfig(**config))
        revenue_model = RevenueModel(RevenueModelConfig(), tvl_model=tvl_model)
        # ... [rest of the code]
    ```

### 3. LEAF Pairs Model (`LEAFPairs.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Handles liquidity pairs involving LEAF tokens, including deal initialization and liquidity calculations.
- Core implementation in `src/Functions/LEAFPairs.py`.
- Integrated LEAF Pairs logic into simulation in `src/Simulations/simulate.py`.
- Debugged and resolved issues related to LEAF price calculations.

**Key Components**:

1. **LEAFPairDeal**

    ```python:src/Functions/LEAFPairs.py
    @dataclass
    class LEAFPairDeal:
        counterparty: str
        amount_usd: float
        num_leaf_tokens: float
        start_month: int
        duration_months: int
        leaf_percentage: float    # Target LEAF ratio (0 to 0.5)
        base_concentration: float
        max_concentration: float
    
        # Balances (initialized to zero)
        leaf_balance: float = 0.0
        other_balance: float = 0.0
    ```

2. **LEAFPairsModel**

    ```python:src/Functions/LEAFPairs.py
    class LEAFPairsModel:
        def __init__(self, config: LEAFPairsConfig, deals: List[LEAFPairDeal]):
            self.config = config
            self.deals = deals
            self.balance_history = defaultdict(list)
            self._initialize_deals()
    
        def _initialize_deals(self):
            for deal in self.deals:
                # Initialize balances based on leaf_percentage
                leaf_investment = deal.amount_usd * deal.leaf_percentage
                deal.num_leaf_tokens = leaf_investment / 1.0  # Assuming initial LEAF price is $1.0
                deal.leaf_balance = deal.num_leaf_tokens
                deal.other_balance = deal.amount_usd - leaf_investment
    
        def update_deals(self, month: int, leaf_price: float):
            """Update active deals for the given month."""
            active_deals = self.get_active_deals(month)
            for deal in active_deals:
                # Placeholder for deal update logic
                pass  # Implement the logic as needed
            self._record_state(month)
    
        def get_active_deals(self, month: int) -> List[LEAFPairDeal]:
            """Return deals that are active in the given month."""
            return [
                deal for deal in self.deals
                if deal.start_month <= month < deal.start_month + deal.duration_months
            ]
    
        def get_total_liquidity(self, month: int, leaf_price: float) -> float:
            """Calculate the total liquidity provided by LEAF pairs."""
            if leaf_price is None:
                raise ValueError("leaf_price cannot be None")
    
            total_liquidity = 0.0
            active_deals = self.get_active_deals(month)
            for deal in active_deals:
                leaf_value = deal.leaf_balance * leaf_price
                other_value = deal.other_balance
                total_liquidity += leaf_value + other_value
            return total_liquidity
    
        def _record_state(self, month: int):
            """Record the state of balances for the given month."""
            self.balance_history[month] = [
                (deal.counterparty, deal.leaf_balance, deal.other_balance)
                for deal in self.get_active_deals(month)
            ]
    
        def add_deal(self, deal: LEAFPairDeal) -> None:
            """Add a new deal to the model."""
            # Validate the deal
            self._validate_deal(deal)
            self.deals.append(deal)
    
        def _validate_deal(self, deal: LEAFPairDeal) -> None:
            """Validate the inputs of a new deal."""
            if not 0 <= deal.leaf_percentage <= 0.5:
                raise ValueError("LEAF percentage must be between 0% and 50%")
            if not 0 < deal.base_concentration <= 1:
                raise ValueError("Concentration must be between 0% and 100%")
            if any(d.counterparty == deal.counterparty for d in self.deals):
                raise ValueError(f"Deal with {deal.counterparty} already exists")
    ```

3. **Data Initialization**

    ```python:src/Data/leaf_deal.py
    from src.Functions.LEAFPairs import LEAFPairDeal
    from typing import List
    
    def initialize_deals() -> List[LEAFPairDeal]:
        """Initialize deals with starting concentrations."""
        return [
            LEAFPairDeal(
                counterparty="Move",
                amount_usd=1_500_000,
                num_leaf_tokens=0,
                start_month=1,
                duration_months=60,
                leaf_percentage=0.35,
                base_concentration=0.5,
                max_concentration=0.8,
                leaf_balance=0.0,
                other_balance=0.0
            ),
            # Add additional deals as needed
        ]
    ```

4. **Leaf Price Function**

    ```python:src/Functions/LeafPrice.py
    # src/Functions/LeafPrice.py
    
    def get_leaf_price(month: int) -> float:
        """
        Returns the LEAF price for the given month.
        Currently, it returns a fixed value of 1.0.
    
        Args:
            month (int): The current month in the simulation.
    
        Returns:
            float: The LEAF price.
        """
        return 1.0
    ```

### 4. TVL Contribution Classes (`TVLContributions.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Manages individual TVL contributions, their states, revenue calculations, and exit conditions.
- Core implementation in `src/Functions/TVLContributions.py`.
- Integrated into TVL Model and Revenue Model.

**Key Components**:

1. **TVLContribution**

    ```python:src/Functions/TVLContributions.py
    @dataclass
    class TVLContribution:
        id: int
        tvl_type: str  # 'ProtocolLocked', 'Contracted', 'Organic', 'Boosted'
        amount_usd: float
        start_month: int
        active: bool = True
        revenue_rate: float = 0.0  # Annual revenue rate as a decimal
        accumulated_revenue: float = 0.0
        exit_condition: Optional[Callable[['TVLContribution', int], bool]] = None
        end_month: Optional[int] = None  # Applicable for Contracted TVL
        decay_rate: Optional[float] = None  # Applicable for Organic TVL
        expected_boost_rate: Optional[float] = None  # Applicable for Boosted TVL (annual APR)
    
        def calculate_revenue(self, month: int) -> float:
            """Calculate and accumulate revenue based on the revenue rate."""
            if not self.active:
                return 0.0
            monthly_rate = (1 + self.revenue_rate) ** (1 / 12) - 1  # Compound interest
            revenue = self.amount_usd * monthly_rate
            self.accumulated_revenue += revenue
            return revenue
    
        def update_amount(self, month: int):
            """Update the amount_usd based on specific TVL type behaviors."""
            if self.tvl_type == 'Organic' and self.decay_rate:
                # Apply decay
                self.amount_usd *= (1 - self.decay_rate)
                if self.amount_usd < 0:
                    self.amount_usd = 0
                # Check exit condition after updating amount
                self.check_exit(month)
    
        def check_exit(self, month: int):
            """Check if the TVL should exit based on its exit condition."""
            if not self.active:
                return
            if self.exit_condition and self.exit_condition(self, month):
                self.active = False
                self.on_exit(month)
    
        def on_exit(self, month: int):
            """Handle actions upon exiting the TVL."""
            print(f"{self.tvl_type} TVL {self.id} has exited at month {month}.")
            # Additional logic can be added here if needed
    
        def get_state(self) -> dict:
            """Return the current state of the contribution."""
            return {
                'id': self.id,
                'tvl_type': self.tvl_type,
                'amount_usd': self.amount_usd,
                'active': self.active,
                'accumulated_revenue': self.accumulated_revenue,
            } 
    ```

2. **TVLContributionHistory**

    ```python:src/Functions/TVLContributions.py
    @dataclass
    class TVLContributionHistory:
        contributions: list[TVLContribution] = field(default_factory=list)
        history: dict[int, list[dict]] = field(default_factory=dict)
        
        def add_contribution(self, contribution: TVLContribution):
            """Add a new TVL contribution to the history."""
            self.contributions.append(contribution)
        
        def get_active_contributions(self) -> list[TVLContribution]:
            """Return a list of all active contributions."""
            return [c for c in self.contributions if c.active]
        
        def calculate_total_tvl(self) -> float:
            """Calculate the sum of all active TVL amounts."""
            return sum(c.amount_usd for c in self.get_active_contributions())
        
        def update_all(self, month: int):
            """Update all active contributions for the given month."""
            for contribution in self.get_active_contributions():
                contribution.update_amount(month)
                contribution.check_exit(month)
        
        def calculate_total_revenue(self, month: int) -> float:
            """Calculate total revenue from all active contributions for the month."""
            return sum(c.calculate_revenue(month) for c in self.get_active_contributions())
            
        def record_state(self, month: int, contributions: list[TVLContribution]):
            """Record the state of all contributions for a given month."""
            self.history[month] = [contrib.get_state() for contrib in contributions]
        
        def get_history(self, month: int) -> list[dict]:
            """Get the recorded state of all contributions for a given month."""
            return self.history.get(month, [])
    ```

### 5. TVL Loader (`TVLLoader.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Loads initial and new TVL contributions into the TVL Model.
- Core implementation in `src/Functions/TVLLoader.py`.
- Utilizes initial data from `src/Data/initial_contributions.py`.

**Key Components**:

1. **TVLLoader**

    ```python:src/Functions/TVLLoader.py
    from typing import Dict, List
    from .TVLContributions import TVLContribution
    from src.Data.initial_contributions import INITIAL_CONTRIBUTIONS
    
    class TVLLoader:
        def __init__(self, tvl_model):
            self.tvl_model = tvl_model
            self.id_counter = 1
        
        def load_initial_contributions(self):
            """Load all initial contributions from config."""
            for tvl_type, contributions in INITIAL_CONTRIBUTIONS.items():
                for config in contributions:
                    contrib = self._create_contribution(tvl_type, config)
                    self.tvl_model.contributions.append(contrib)
                    self.id_counter += 1
        
        def add_new_contribution(self, tvl_type: str, config: Dict):
            """Add a new contribution during simulation."""
            contrib = self._create_contribution(tvl_type, config)
            self.tvl_model.contributions.append(contrib)
            self.id_counter += 1
            return contrib
        
        def _create_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
            """Create a TVL contribution based on type and config."""
            base_params = {
                'id': self.id_counter,
                'tvl_type': tvl_type,
                'amount_usd': config['amount_usd'],
                'start_month': config['start_month'],
                'revenue_rate': config.get('revenue_rate', 0.0)
            }
            
            if tvl_type == 'Contracted':
                base_params.update({
                    'end_month': config['start_month'] + config['duration_months'],
                    'exit_condition': self.tvl_model.contract_end_condition
                })
            elif tvl_type == 'Organic':
                base_params.update({
                    'decay_rate': config.get('decay_rate', 0.01),
                    'exit_condition': self.tvl_model.decay_exit_condition
                })
            elif tvl_type == 'Boosted':
                base_params.update({
                    'expected_boost_rate': config.get('expected_boost_rate', 0.05),
                    'exit_condition': self.tvl_model.boosted_exit_condition
                })
            
            return TVLContribution(**base_params) 
    ```

### 6. Boosted TVL Model (`boosted_tvl.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Manages TVL boosted by Canopy, excluding direct Canopy TVL.
- Core implementation in `src/Functions/boosted_tvl.py`.

**Key Components**:

1. **BoostedTVLModel**

    ```python:src/Functions/boosted_tvl.py
    from dataclasses import dataclass
    import math
    
    @dataclass
    class BoostedTVLConfig:
        initial_boost_share: float        # Initial boost share (e.g., 10%)
        boost_growth_rate: float          # Growth rate for boost
        max_months: int = 60              # Maximum number of months
    
    class BoostedTVLModel:
        def __init__(self, config: BoostedTVLConfig):
            self.config = config
            self.boosted_tvl_history = []
            self.previous_boosted_tvl = 0.0
    
        def get_boosted_tvl(self, month: int, canopy_tvl: float, move_tvl: float, is_active: bool) -> float:
            """Calculate TVL boosted by Canopy (excluding direct Canopy TVL)."""
            if not is_active:
                self.boosted_tvl_history.append(0.0)
                return 0.0
    
            # Available TVL for boosting (excluding Canopy TVL)
            available_tvl = move_tvl - canopy_tvl
    
            # Calculate boost share using sigmoid function
            boost_share = self._calculate_boost_share(month)
    
            # Calculate boosted TVL
            boosted_tvl = available_tvl * boost_share
    
            # Ensure total Canopy impact doesn't exceed Move TVL
            boosted_tvl = min(boosted_tvl, available_tvl)
    
            # Record boosted TVL
            self.boosted_tvl_history.append(boosted_tvl)
    
            # Update previous boosted TVL for growth rate calculation
            self.previous_boosted_tvl = boosted_tvl
    
            return boosted_tvl
    
        def _calculate_boost_share(self, month: int) -> float:
            """Calculate boost share using a sigmoid growth function."""
            normalized_time = (month / self.config.max_months) * 12 - 6  # Example normalization
            sigmoid = 1 / (1 + math.exp(-self.config.boost_growth_rate * normalized_time))
            return self.config.initial_boost_share * sigmoid
    
        def get_total_canopy_impact(self, month: int, canopy_tvl: float) -> float:
            """Calculate the total canopy impact for the given month."""
            if month < len(self.boosted_tvl_history):
                boosted_tvl = self.boosted_tvl_history[month]
                total_impact = canopy_tvl + boosted_tvl
                return total_impact
            else:
                return canopy_tvl
    
        def get_annual_boosted_growth_rate(self, month: int) -> float:
            """Calculate the annual boosted TVL growth rate for the given month."""
            if month == 0:
                return 0.0  # No growth in the first month
            if month >= len(self.boosted_tvl_history):
                current_boosted_tvl = self.previous_boosted_tvl
            else:
                current_boosted_tvl = self.boosted_tvl_history[month]
    
            previous_boosted_tvl = self.boosted_tvl_history[month - 1] if month - 1 < len(self.boosted_tvl_history) else self.previous_boosted_tvl
    
            if previous_boosted_tvl == 0:
                return 0.0  # Avoid division by zero
    
            growth_rate = (current_boosted_tvl - previous_boosted_tvl) / previous_boosted_tvl
            return growth_rate * 12  # Annualize the monthly growth rate 
    ```

### 7. Run Simulation (`run_simulation.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Entry point for running the simulation.
- Executes the `main` function from `src/Simulations/simulate.py`.
- Located at the root of the repository.

**Key Components**:

1. **Run Simulation Script**

    ```python:run_simulation.py
    from src.Simulations.simulate import main
    
    if __name__ == "__main__":
        main() 
    ```

### 8. Initial Contributions Data (`initial_contributions.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Defines the initial TVL contributions across different TVL types.
- Located in `src/Data/initial_contributions.py`.

**Key Components**:

1. **Initial Contributions**

    ```python:src/Data/initial_contributions.py
    from typing import List, Dict
    
    INITIAL_CONTRIBUTIONS = {
        'ProtocolLocked': [
            {
                'amount_usd': 50_000_000,
                'start_month': 3,
                'revenue_rate': 0.005
            },
            {
                'amount_usd': 1_500_000,
                'start_month': 0,
                'revenue_rate': 0.04
            }
        ],
        'Contracted': [
            {
                'amount_usd': 200_000_000,
                'start_month': 0,
                'revenue_rate': 0.01,
                'duration_months': 12
            },
            {
                'amount_usd': 200_000_000,
                'start_month': 0,
                'revenue_rate': 0.045,
                'duration_months': 12
            }
        ],
        'Organic': [
            {
                'amount_usd': 16_000_000,
                'start_month': 0,
                'revenue_rate': 0.03,
                'decay_rate': 0.01
            }
        ],
        'Boosted': [
            {
                'amount_usd': 10_000_000,
                'start_month': 6,
                'revenue_rate': 0.01,
                'expected_boost_rate': 0.05
            }
        ]
    }
    ```
    
### 9. TVL Contributions Tests (`test_TVLContributions.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Contains unit tests for the `TVLContribution` and related functionalities.
- Located in `Tests/test_TVLContributions.py`.

**Key Components**:

1. **TVLContribution Unit Tests**

    ```python:Tests/test_TVLContributions.py
    import unittest
    from src.Functions.TVLContributions import TVLContribution
    from src.Functions.TVL import TVLModel, TVLModelConfig
    from src.Functions.TVLLoader import TVLLoader
    
    class TestTVLContributions(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            """Set up test fixtures."""
            cls.tvl_model = TVLModel(TVLModelConfig(
                initial_move_tvl=1_000_000_000,
                initial_canopy_tvl=500_000_000,
                move_growth_rates=[0.10, 0.08, 0.06],
                min_market_share=0.05,
                market_share_decay_rate=0.01,
                max_months=60
            ))
            cls.loader = TVLLoader(cls.tvl_model)
    
        def create_protocol_locked_tvl(self) -> TVLContribution:
            """Factory method for creating protocol locked TVL."""
            return TVLContribution(
                id=1,
                tvl_type='ProtocolLocked',
                amount_usd=5_000_000,
                start_month=0,
                revenue_rate=0.05
            )
    
        def create_contracted_tvl(self) -> TVLContribution:
            """Factory method for creating contracted TVL."""
            return TVLContribution(
                id=2,
                tvl_type='Contracted',
                amount_usd=2_000_000,
                start_month=0,
                revenue_rate=0.04,
                end_month=12,
                exit_condition=self.tvl_model.contract_end_condition
            )
    
        def create_organic_tvl(self) -> TVLContribution:
            """Factory method for creating organic TVL."""
            return TVLContribution(
                id=3,
                tvl_type='Organic',
                amount_usd=1_000_000,
                start_month=0,
                revenue_rate=0.03,
                decay_rate=0.15,
                exit_condition=lambda c, m: c.amount_usd < 1000
            )
    
        def create_boosted_tvl(self) -> TVLContribution:
            """Factory method for creating boosted TVL."""
            return TVLContribution(
                id=4,
                tvl_type='Boosted',
                amount_usd=3_000_000,
                start_month=0,
                revenue_rate=0.06,
                expected_boost_rate=0.05,
                exit_condition=lambda c, m: c.expected_boost_rate < 0.04
            )
    
        def test_protocol_locked_tvl(self):
            contrib = self.create_protocol_locked_tvl()
            self.assertTrue(contrib.active)
            revenue = contrib.calculate_revenue(1)
            expected_revenue = 5_000_000 * ((1 + 0.05) ** (1 / 12) - 1)
            self.assertAlmostEqual(revenue, expected_revenue, places=2)
            contrib.check_exit(100)
            self.assertTrue(contrib.active)
        
        def test_contracted_tvl_exit(self):
            contrib = self.create_contracted_tvl()
            self.assertTrue(contrib.active)
            contrib.check_exit(12)
            self.assertFalse(contrib.active)
    
        def test_organic_tvl_decay(self):
            contrib = self.create_organic_tvl()
            self.assertTrue(contrib.active)
            for month in range(1, 51):
                contrib.update_amount(month)
                if not contrib.active:
                    break
            self.assertFalse(contrib.active)
            self.assertLess(contrib.amount_usd, 1000)
    
        def test_boosted_tvl_exit(self):
            contrib = self.create_boosted_tvl()
            self.assertTrue(contrib.active)
            for month in range(1, 13):
                contrib.expected_boost_rate *= 0.95
                contrib.check_exit(month)
                if not contrib.active:
                    break
            self.assertFalse(contrib.active)
            self.assertLess(contrib.expected_boost_rate, 0.04)
    
        def test_calculate_revenue(self):
            contrib = TVLContribution(
                id=5,
                tvl_type='ProtocolLocked',
                amount_usd=1_000_000,
                start_month=0,
                revenue_rate=0.12
            )
            revenue = contrib.calculate_revenue(0)
            expected_revenue = 1_000_000 * ((1 + 0.12) ** (1 / 12) - 1)
            self.assertAlmostEqual(revenue, expected_revenue, places=2)
    
        def test_update_amount_organic(self):
            contrib = TVLContribution(
                id=6,
                tvl_type='Organic',
                amount_usd=500_000,
                start_month=0,
                decay_rate=0.02
            )
            contrib.update_amount(1)
            expected_amount = 500_000 * (1 - 0.02)
            self.assertAlmostEqual(contrib.amount_usd, expected_amount, places=2)
    
    if __name__ == '__main__':
        unittest.main()
    ```

## Remaining Implementation Order

### 4. AEGIS Model (`AEGIS.md`)

**Status**: 🔜 Pending

**Reasoning**: Depends on the LEAF Pairs model for balance management and requires coordination with other components for comprehensive tokenomics.

**Implementation Plan**:

- **Create `src/Functions/AEGIS.py`**:
  - Implement LEAF/USDC balance tracking.
  - Add redemption mechanics.
  - Model market-driven changes and interactions with other models.

- **Integrate into Simulation**:
  - Update `src/Simulations/simulate.py` to incorporate AEGIS model activities.
  - Ensure proper coordination with TVL, Revenue, and LEAF Pairs models.

- **Testing**:
  - Develop unit tests for AEGIS functionalities.
  - Conduct integration tests with existing models.

- **Documentation**:
  - Create comprehensive documentation in `Docs/AEGIS.md`.
  - Include usage examples and implementation notes.

### 5. OAK Distribution Model (`OAK.md`)

**Status**: 🔜 Pending

**Reasoning**: Most complex model requiring all other components to be in place for effective distribution and redemption mechanisms.

**Implementation Plan**:

- **Create `src/Functions/OAK.py`**:
  - Implement distribution logic for OAK tokens.
  - Add redemption calculations and mechanisms.
  - Model risk-adjusted returns and interaction with other financial models.

- **Integrate into Simulation**:
  - Update `src/Simulations/simulate.py` to incorporate OAK Distribution activities.
  - Ensure synchronization with TVL, Revenue, LEAF Pairs, and AEGIS models.

- **Testing**:
  - Develop unit tests for OAK Distribution functionalities.
  - Conduct integration tests with existing models.

- **Documentation**:
  - Create comprehensive documentation in `Docs/OAK.md`.
  - Include usage examples and implementation notes.

## Development Guidelines

### 1. Module Structure

```plaintext
src/
  Functions/
    TVL.py                     ✅ Completed
    Revenue.py                 ✅ Completed
    LEAFPairs.py               ✅ Completed
    AEGIS.py                   🔜 Pending
    OAK.py                     🔜 Pending
    LeafPrice.py               ✅ Completed
    TVLLoader.py               ✅ Completed
    boosted_tvl.py             ✅ Completed
    TVLContributions.py        ✅ Completed
  Simulations/
    simulate.py                ✅ Completed
  Data/
    leaf_deal.py               ✅ Completed
    initial_contributions.py   ✅ Completed
Tests/
  test_TVLContributions.py    ✅ Completed
Docs/
  TVL.md                      ✅ Completed
  Revenue.md                  ✅ Completed
  LEAFPairs.md                ✅ Completed
  AEGIS.md                    🔜 Pending
  OAK.md                      🔜 Pending
```

### 2. Testing Strategy

- **Unit Tests**:
  - Developed unit tests for `TVLContribution` and related functionalities in `Tests/test_TVLContributions.py` to ensure individual components work as expected.

- **Integration Tests**:
  - Plan to develop integration tests once AEGIS and OAK models are implemented to test interactions between dependent models (e.g., how AEGIS interacts with LEAF Pairs).

- **Scenario Testing**:
  - Implement scenario analyses for edge cases and varying market conditions after completing all models.

### 3. Documentation Requirements

- **Comprehensive Docstrings**:
  - All classes, methods, and functions include clear and descriptive docstrings to enhance understandability.

- **Updated Markdown Specifications**:
  - Maintain up-to-date documentation in the `Docs/` directory for each model, ensuring consistency with the actual implementation.

- **Implementation Notes**:
  - Document any assumptions, design choices, and dependencies within the respective markdown files.

- **Usage Examples**:
  - Provide examples in the documentation to demonstrate how each model and function should be used, aiding future development and onboarding.

### 4. Code Quality

- **Type Hints**:
  - Utilize type hints for all functions and methods to enhance readability and maintainability across the codebase.

- **Error Handling**:
  - Implement robust error handling to manage unexpected inputs and states, ensuring the simulation's stability.

- **Input Validation**:
  - Validate all inputs to functions and methods to ensure data integrity and prevent potential bugs.

- **Performance Optimization**:
  - Optimize code for performance, especially within simulation loops and calculations, to handle large datasets efficiently.

## Additional Recommendations

### 1. Configuration Management

- **Centralize Parameters**:
  - Store all configurable parameters in centralized configuration files to simplify adjustments and maintenance.

- **Document Assumption Changes**:
  - Track and document any changes to assumptions in a version-controlled manner to maintain transparency and traceability.

- **Version Control for Scenarios**:
  - Manage different simulation scenarios through version control to facilitate testing and comparisons.

### 2. Visualization

- **Consistent Plotting Styles**:
  - Maintain uniform styles and color schemes across all visualizations for clarity and professionalism.

- **Interactive Dashboards**:
  - Consider developing interactive dashboards to allow dynamic exploration of simulation results, enhancing data analysis capabilities.

- **Export Capabilities**:
  - Enable exporting of plots and data for reporting and further analysis, supporting better decision-making processes.

### 3. Validation

- **Cross-Check Calculations**:
  - Regularly verify that all calculations align with the documented assumptions and specifications to ensure accuracy.

- **Peer Review Process**:
  - Implement a peer review process for all code changes to catch potential issues early and maintain code quality.

- **Regular Calibration**:
  - Adjust models based on real-world data and feedback to enhance accuracy and relevance of the simulations.

### 4. Maintenance

- **Regular Code Reviews**:
  - Schedule periodic code reviews to ensure code quality and adherence to best practices, fostering continuous improvement.

- **Performance Monitoring**:
  - Monitor the performance of simulations and models, optimizing as necessary to maintain efficiency.

- **Documentation Updates**:
  - Keep all documentation up to date with the latest changes and implementations, ensuring it remains a reliable resource.

## Additional Code Components

### 5. TVLContribution Classes

**Status**: ✅ Completed

**Key Components**:

1. **TVLContribution**

    ```python:src/Functions/TVLContributions.py
    @dataclass
    class TVLContribution:
        id: int
        tvl_type: str  # 'ProtocolLocked', 'Contracted', 'Organic', 'Boosted'
        amount_usd: float
        start_month: int
        active: bool = True
        revenue_rate: float = 0.0  # Annual revenue rate as a decimal
        accumulated_revenue: float = 0.0
        exit_condition: Optional[Callable[['TVLContribution', int], bool]] = None
        end_month: Optional[int] = None  # Applicable for Contracted TVL
        decay_rate: Optional[float] = None  # Applicable for Organic TVL
        expected_boost_rate: Optional[float] = None  # Applicable for Boosted TVL (annual APR)
    
        def calculate_revenue(self, month: int) -> float:
            """Calculate and accumulate revenue based on the revenue rate."""
            if not self.active:
                return 0.0
            monthly_rate = (1 + self.revenue_rate) ** (1 / 12) - 1  # Compound interest
            revenue = self.amount_usd * monthly_rate
            self.accumulated_revenue += revenue
            return revenue
    
        def update_amount(self, month: int):
            """Update the amount_usd based on specific TVL type behaviors."""
            if self.tvl_type == 'Organic' and self.decay_rate:
                # Apply decay
                self.amount_usd *= (1 - self.decay_rate)
                if self.amount_usd < 0:
                    self.amount_usd = 0
                # Check exit condition after updating amount
                self.check_exit(month)
    
        def check_exit(self, month: int):
            """Check if the TVL should exit based on its exit condition."""
            if not self.active:
                return
            if self.exit_condition and self.exit_condition(self, month):
                self.active = False
                self.on_exit(month)
    
        def on_exit(self, month: int):
            """Handle actions upon exiting the TVL."""
            print(f"{self.tvl_type} TVL {self.id} has exited at month {month}.")
            # Additional logic can be added here if needed
    
        def get_state(self) -> dict:
            """Return the current state of the contribution."""
            return {
                'id': self.id,
                'tvl_type': self.tvl_type,
                'amount_usd': self.amount_usd,
                'active': self.active,
                'accumulated_revenue': self.accumulated_revenue,
            } 
    ```

2. **TVLContributionHistory**

    ```python:src/Functions/TVLContributions.py
    @dataclass
    class TVLContributionHistory:
        contributions: list[TVLContribution] = field(default_factory=list)
        history: dict[int, list[dict]] = field(default_factory=dict)
        
        def add_contribution(self, contribution: TVLContribution):
            """Add a new TVL contribution to the history."""
            self.contributions.append(contribution)
        
        def get_active_contributions(self) -> list[TVLContribution]:
            """Return a list of all active contributions."""
            return [c for c in self.contributions if c.active]
        
        def calculate_total_tvl(self) -> float:
            """Calculate the sum of all active TVL amounts."""
            return sum(c.amount_usd for c in self.get_active_contributions())
        
        def update_all(self, month: int):
            """Update all active contributions for the given month."""
            for contribution in self.get_active_contributions():
                contribution.update_amount(month)
                contribution.check_exit(month)
        
        def calculate_total_revenue(self, month: int) -> float:
            """Calculate total revenue from all active contributions for the month."""
            return sum(c.calculate_revenue(month) for c in self.get_active_contributions())
            
        def record_state(self, month: int, contributions: list[TVLContribution]):
            """Record the state of all contributions for a given month."""
            self.history[month] = [contrib.get_state() for contrib in contributions]
        
        def get_history(self, month: int) -> list[dict]:
            """Get the recorded state of all contributions for a given month."""
            return self.history.get(month, [])
    ```

### 6. TVLLoader

**Status**: ✅ Completed

**Key Components**:

1. **TVLLoader**

    ```python:src/Functions/TVLLoader.py
    from typing import Dict, List
    from .TVLContributions import TVLContribution
    from src.Data.initial_contributions import INITIAL_CONTRIBUTIONS
    
    class TVLLoader:
        def __init__(self, tvl_model):
            self.tvl_model = tvl_model
            self.id_counter = 1
        
        def load_initial_contributions(self):
            """Load all initial contributions from config."""
            for tvl_type, contributions in INITIAL_CONTRIBUTIONS.items():
                for config in contributions:
                    contrib = self._create_contribution(tvl_type, config)
                    self.tvl_model.contributions.append(contrib)
                    self.id_counter += 1
        
        def add_new_contribution(self, tvl_type: str, config: Dict):
            """Add a new contribution during simulation."""
            contrib = self._create_contribution(tvl_type, config)
            self.tvl_model.contributions.append(contrib)
            self.id_counter += 1
            return contrib
        
        def _create_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
            """Create a TVL contribution based on type and config."""
            base_params = {
                'id': self.id_counter,
                'tvl_type': tvl_type,
                'amount_usd': config['amount_usd'],
                'start_month': config['start_month'],
                'revenue_rate': config.get('revenue_rate', 0.0)
            }
            
            if tvl_type == 'Contracted':
                base_params.update({
                    'end_month': config['start_month'] + config['duration_months'],
                    'exit_condition': self.tvl_model.contract_end_condition
                })
            elif tvl_type == 'Organic':
                base_params.update({
                    'decay_rate': config.get('decay_rate', 0.01),
                    'exit_condition': self.tvl_model.decay_exit_condition
                })
            elif tvl_type == 'Boosted':
                base_params.update({
                    'expected_boost_rate': config.get('expected_boost_rate', 0.05),
                    'exit_condition': self.tvl_model.boosted_exit_condition
                })
            
            return TVLContribution(**base_params) 
    ```

### 7. Boosted TVL Model

**Status**: ✅ Completed

**Key Components**:

1. **BoostedTVLModel**

    ```python:src/Functions/boosted_tvl.py
    from dataclasses import dataclass
    import math
    
    @dataclass
    class BoostedTVLConfig:
        initial_boost_share: float        # Initial boost share (e.g., 10%)
        boost_growth_rate: float          # Growth rate for boost
        max_months: int = 60              # Maximum number of months
    
    class BoostedTVLModel:
        def __init__(self, config: BoostedTVLConfig):
            self.config = config
            self.boosted_tvl_history = []
            self.previous_boosted_tvl = 0.0
    
        def get_boosted_tvl(self, month: int, canopy_tvl: float, move_tvl: float, is_active: bool) -> float:
            """Calculate TVL boosted by Canopy (excluding direct Canopy TVL)."""
            if not is_active:
                self.boosted_tvl_history.append(0.0)
                return 0.0
    
            # Available TVL for boosting (excluding Canopy TVL)
            available_tvl = move_tvl - canopy_tvl
    
            # Calculate boost share using sigmoid function
            boost_share = self._calculate_boost_share(month)
    
            # Calculate boosted TVL
            boosted_tvl = available_tvl * boost_share
    
            # Ensure total Canopy impact doesn't exceed Move TVL
            boosted_tvl = min(boosted_tvl, available_tvl)
    
            # Record boosted TVL
            self.boosted_tvl_history.append(boosted_tvl)
    
            # Update previous boosted TVL for growth rate calculation
            self.previous_boosted_tvl = boosted_tvl
    
            return boosted_tvl
    
        def _calculate_boost_share(self, month: int) -> float:
            """Calculate boost share using a sigmoid growth function."""
            normalized_time = (month / self.config.max_months) * 12 - 6  # Example normalization
            sigmoid = 1 / (1 + math.exp(-self.config.boost_growth_rate * normalized_time))
            return self.config.initial_boost_share * sigmoid
    
        def get_total_canopy_impact(self, month: int, canopy_tvl: float) -> float:
            """Calculate the total canopy impact for the given month."""
            if month < len(self.boosted_tvl_history):
                boosted_tvl = self.boosted_tvl_history[month]
                total_impact = canopy_tvl + boosted_tvl
                return total_impact
            else:
                return canopy_tvl
    
        def get_annual_boosted_growth_rate(self, month: int) -> float:
            """Calculate the annual boosted TVL growth rate for the given month."""
            if month == 0:
                return 0.0  # No growth in the first month
            if month >= len(self.boosted_tvl_history):
                current_boosted_tvl = self.previous_boosted_tvl
            else:
                current_boosted_tvl = self.boosted_tvl_history[month]
    
            previous_boosted_tvl = self.boosted_tvl_history[month - 1] if month - 1 < len(self.boosted_tvl_history) else self.previous_boosted_tvl
    
            if previous_boosted_tvl == 0:
                return 0.0  # Avoid division by zero
    
            growth_rate = (current_boosted_tvl - previous_boosted_tvl) / previous_boosted_tvl
            return growth_rate * 12  # Annualize the monthly growth rate 
    ```

### 8. Run Simulation

**Status**: ✅ Completed

**Key Components**:

1. **Run Simulation Script**

    ```python:run_simulation.py
    from src.Simulations.simulate import main
    
    if __name__ == "__main__":
        main() 
    ```

### 9. Initial Contributions Data

**Status**: ✅ Completed

**Key Components**:

1. **Initial Contributions**

    ```python:src/Data/initial_contributions.py
    from typing import List, Dict
    
    INITIAL_CONTRIBUTIONS = {
        'ProtocolLocked': [
            {
                'amount_usd': 50_000_000,
                'start_month': 3,
                'revenue_rate': 0.005
            },
            {
                'amount_usd': 1_500_000,
                'start_month': 0,
                'revenue_rate': 0.04
            }
        ],
        'Contracted': [
            {
                'amount_usd': 200_000_000,
                'start_month': 0,
                'revenue_rate': 0.01,
                'duration_months': 12
            },
            {
                'amount_usd': 200_000_000,
                'start_month': 0,
                'revenue_rate': 0.045,
                'duration_months': 12
            }
        ],
        'Organic': [
            {
                'amount_usd': 16_000_000,
                'start_month': 0,
                'revenue_rate': 0.03,
                'decay_rate': 0.01
            }
        ],
        'Boosted': [
            {
                'amount_usd': 10_000_000,
                'start_month': 6,
                'revenue_rate': 0.01,
                'expected_boost_rate': 0.05
            }
        ]
    }
    ```

### 10. TVL Contribtuions Tests (`test_TVLContributions.py`)

**Status**: ✅ Completed

**Implementation Details**:

- Contains comprehensive unit tests for the `TVLContribution` class and related functionalities.
- Located in `Tests/test_TVLContributions.py`.

**Key Components**:

1. **TVLContribution Unit Tests**

    ```python:Tests/test_TVLContributions.py
    import unittest
    from src.Functions.TVLContributions import TVLContribution
    from src.Functions.TVL import TVLModel, TVLModelConfig
    from src.Functions.TVLLoader import TVLLoader
    
    class TestTVLContributions(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            """Set up test fixtures."""
            cls.tvl_model = TVLModel(TVLModelConfig(
                initial_move_tvl=1_000_000_000,
                initial_canopy_tvl=500_000_000,
                move_growth_rates=[0.10, 0.08, 0.06],
                min_market_share=0.05,
                market_share_decay_rate=0.01,
                max_months=60
            ))
            cls.loader = TVLLoader(cls.tvl_model)
    
        def create_protocol_locked_tvl(self) -> TVLContribution:
            """Factory method for creating protocol locked TVL."""
            return TVLContribution(
                id=1,
                tvl_type='ProtocolLocked',
                amount_usd=5_000_000,
                start_month=0,
                revenue_rate=0.05
            )
    
        def create_contracted_tvl(self) -> TVLContribution:
            """Factory method for creating contracted TVL."""
            return TVLContribution(
                id=2,
                tvl_type='Contracted',
                amount_usd=2_000_000,
                start_month=0,
                revenue_rate=0.04,
                end_month=12,
                exit_condition=self.tvl_model.contract_end_condition
            )
    
        def create_organic_tvl(self) -> TVLContribution:
            """Factory method for creating organic TVL."""
            return TVLContribution(
                id=3,
                tvl_type='Organic',
                amount_usd=1_000_000,
                start_month=0,
                revenue_rate=0.03,
                decay_rate=0.15,
                exit_condition=lambda c, m: c.amount_usd < 1000
            )
    
        def create_boosted_tvl(self) -> TVLContribution:
            """Factory method for creating boosted TVL."""
            return TVLContribution(
                id=4,
                tvl_type='Boosted',
                amount_usd=3_000_000,
                start_month=0,
                revenue_rate=0.06,
                expected_boost_rate=0.05,
                exit_condition=lambda c, m: c.expected_boost_rate < 0.04
            )
    
        def test_protocol_locked_tvl(self):
            contrib = self.create_protocol_locked_tvl()
            self.assertTrue(contrib.active)
            revenue = contrib.calculate_revenue(1)
            expected_revenue = 5_000_000 * ((1 + 0.05) ** (1 / 12) - 1)
            self.assertAlmostEqual(revenue, expected_revenue, places=2)
            contrib.check_exit(100)
            self.assertTrue(contrib.active)
        
        def test_contracted_tvl_exit(self):
            contrib = self.create_contracted_tvl()
            self.assertTrue(contrib.active)
            contrib.check_exit(12)
            self.assertFalse(contrib.active)
    
        def test_organic_tvl_decay(self):
            contrib = self.create_organic_tvl()
            self.assertTrue(contrib.active)
            for month in range(1, 51):
                contrib.update_amount(month)
                if not contrib.active:
                    break
            self.assertFalse(contrib.active)
            self.assertLess(contrib.amount_usd, 1000)
    
        def test_boosted_tvl_exit(self):
            contrib = self.create_boosted_tvl()
            self.assertTrue(contrib.active)
            for month in range(1, 13):
                contrib.expected_boost_rate *= 0.95
                contrib.check_exit(month)
                if not contrib.active:
                    break
            self.assertFalse(contrib.active)
            self.assertLess(contrib.expected_boost_rate, 0.04)
    
        def test_calculate_revenue(self):
            contrib = TVLContribution(
                id=5,
                tvl_type='ProtocolLocked',
                amount_usd=1_000_000,
                start_month=0,
                revenue_rate=0.12
            )
            revenue = contrib.calculate_revenue(0)
            expected_revenue = 1_000_000 * ((1 + 0.12) ** (1 / 12) - 1)
            self.assertAlmostEqual(revenue, expected_revenue, places=2)
    
        def test_update_amount_organic(self):
            contrib = TVLContribution(
                id=6,
                tvl_type='Organic',
                amount_usd=500_000,
                start_month=0,
                decay_rate=0.02
            )
            contrib.update_amount(1)
            expected_amount = 500_000 * (1 - 0.02)
            self.assertAlmostEqual(contrib.amount_usd, expected_amount, places=2)
    
    if __name__ == '__main__':
        unittest.main()
    ```

## Next Steps

With the TVL, Revenue, LEAF Pairs models, and associated testing and data components successfully implemented and integrated into the simulation framework, the next steps involve tackling the pending models to complete the CanopyDFF implementation roadmap:

### 1. Implement AEGIS Model

- **Objective**: Manage LEAF and USDC balances, handle redemptions, and model market-driven changes.
- **Actions**:
  - Develop the `AEGIS.py` module with necessary classes and methods.
  - Integrate AEGIS functionalities into the main simulation.
  - Ensure seamless interaction between AEGIS and existing models (TVL, Revenue, LEAF Pairs).
  - Develop and execute comprehensive tests to validate AEGIS behaviors.
  - Document the AEGIS model thoroughly in `Docs/AEGIS.md`.

### 2. Implement OAK Distribution Model

- **Objective**: Manage the distribution and redemption of OAK tokens, model risk-adjusted returns.
- **Actions**:
  - Develop the `OAK.py` module with distribution logic and redemption mechanisms.
  - Integrate OAK Distribution into the simulation framework.
  - Coordinate OAK interactions with other financial models to ensure accuracy.
  - Conduct thorough testing to validate distribution and redemption processes.
  - Document the OAK Distribution model comprehensively in `Docs/OAK.md`.

### 3. Enhance Simulation Capabilities

- **Objective**: Expand the simulation to incorporate AEGIS and OAK models, improve visualization and reporting.
- **Actions**:
  - Update `src/Simulations/simulate.py` to include new models and their interactions.
  - Enhance visualization tools to reflect data from AEGIS and OAK distributions.
  - Implement interactive dashboards for dynamic exploration of simulation results.

### 4. Finalize Documentation and Testing

- **Objective**: Ensure all models are well-documented and thoroughly tested.
- **Actions**:
  - Complete documentation for AEGIS and OAK models in their respective markdown files.
  - Develop comprehensive test suites covering all functionalities.
  - Perform peer reviews to maintain code quality and consistency.
  - Integrate automated testing pipelines to streamline the testing process.

### 5. Comprehensive Code Review and Optimization

- **Objective**: Improve code quality, maintainability, and performance.
- **Actions**:
  - Conduct regular code reviews focusing on readability, efficiency, and adherence to best practices.
  - Optimize performance-critical sections of the code, especially within simulation loops and calculations.
  - Refactor code where necessary to enhance modularity and reduce complexity.

### 6. Deployment and Monitoring

- **Objective**: Prepare the simulation for deployment and ensure its reliability in production environments.
- **Actions**:
  - Set up deployment pipelines to streamline the deployment process.
  - Implement monitoring tools to track simulation performance and detect anomalies.
  - Establish logging mechanisms to capture detailed information about simulation runs, aiding in debugging and analysis.

By following this structured approach, the CanopyDFF project will achieve a robust and comprehensive implementation, ensuring accurate financial projections and effective tokenomics management. Regularly updating the `implementation_order.md` document to reflect ongoing progress and changes will maintain clarity and direction throughout the project's lifecycle.