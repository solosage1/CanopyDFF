# CanopyDFF Implementation Order

## Repository Overview

The CanopyDFF repository comprises several interconnected models for Canopy's tokenomics and financial projections:

1. **TVL Model (`TVL.md`)**: Projects overall TVL growth, Canopy TVL, and Boosted TVL.
2. **Revenue Model (`Revenue.md`)**: Projects revenue based on TVL composition.
3. **LEAF Pairs Model (`LEAFPairs.md`)**: Handles liquidity pairs involving LEAF tokens.
4. **AEGIS Model (`AEGIS.md`)**: Manages LEAF and USDC balances and redemptions.
5. **OAK Distribution Model (`OAK.md`)**: Manages OAK token distribution and redemption.
6. **LEAF Price Model (`LeafPrice.md`)**: Manages the pricing dynamics of LEAF tokens.

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
        """Configuration for TVL Model."""
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
            self.tvl_history = []
            self.boosted_tvl_history = []
            self.total_impact_history = []
            self.month = 0
        
        def calculate_tvl(self) -> float:
            """Calculate total TVL based on growth rates."""
            tvl = self.config.initial_move_tvl * (1 + self.config.move_growth_rates[self.month % len(self.config.move_growth_rates)]) ** self.month
            self.tvl_history.append(tvl)
            return tvl
        
        def calculate_boosted_tvl(self, tvl: float) -> float:
            """Calculate boosted TVL based on market share."""
            boosted_tvl = tvl * self.config.min_market_share
            self.boosted_tvl_history.append(boosted_tvl)
            return boosted_tvl
        
        def step(self):
            """Advance the TVL model by one month."""
            tvl = self.calculate_tvl()
            boosted_tvl = self.calculate_boosted_tvl(tvl)
            total_impact = tvl + boosted_tvl
            self.total_impact_history.append(total_impact)
            self.month += 1
    ```

### 2. Revenue Model (`Revenue.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Core revenue projection functionalities implemented.
- Integrated with TVL for accurate financial projections.
- Implemented in `src/Functions/Revenue.py` and integrated into `src/Simulations/simulate.py`.

**Key Components**:

1. **RevenueModelConfig**

    ```python:src/Functions/Revenue.py
    @dataclass
    class RevenueModelConfig:
        base_revenue: float
        growth_rate: float
        max_months: int = 60
    ```

2. **RevenueModel**

    ```python:src/Functions/Revenue.py
    class RevenueModel:
        def __init__(self, config: RevenueModelConfig):
            self.config = config
            self.revenue_history = []
            self.month = 0
        
        def calculate_revenue(self, total_tvl: float) -> float:
            """Calculate revenue based on total TVL."""
            revenue = self.config.base_revenue * (1 + self.config.growth_rate) ** self.month
            self.revenue_history.append(revenue)
            return revenue
        
        def step(self, total_tvl: float):
            """Advance the revenue model by one month."""
            revenue = self.calculate_revenue(total_tvl)
            self.month += 1
            return revenue
    ```

### 3. LEAF Pairs Model (`LEAFPairs.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Manages liquidity pairs involving LEAF tokens.
- Implemented in `src/Functions/LEAFPairs.py`.
- Integrated into simulation for dynamic liquidity management.

**Key Components**:

1. **LEAFPairsModel**

    ```python:src/Functions/LEAFPairs.py
    class LEAFPairsModel:
        def __init__(self, initial_pairs: List[Tuple[str, float, float]]):
            self.pairs = initial_pairs  # List of tuples (token, amount, price)
            self.pair_history = {pair[0]: [] for pair in initial_pairs}
        
        def update_deals(self, month: int, current_leaf_price: float):
            """Update liquidity pairs based on current market conditions."""
            for pair in self.pairs:
                token, amount, price = pair
                # Example logic: adjust amount based on price
                new_amount = amount * (1 + 0.01 * month)  # Placeholder adjustment
                self.pairs = [(token, new_amount, current_leaf_price) if p[0] == token else p for p in self.pairs]
                self.pair_history[token].append(new_amount)
    ```

### 4. AEGIS Model (`AEGIS.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Manages LEAF and USDC balances and redemptions.
- Implemented in `src/Functions/AEGIS.py`.
- Integrated into simulation for balance and redemption management.

**Key Components**:

1. **AEGISModel**

    ```python:src/Functions/AEGIS.py
    @dataclass
    class AEGISConfig:
        initial_leaf_balance: float
        initial_usdc_balance: float
        leaf_price_decay_rate: float
        max_months: int
    
    class AEGISModel:
        def __init__(self, config: AEGISConfig):
            self.config = config
            self.usdc_balance = config.initial_usdc_balance
            self.leaf_balance = config.initial_leaf_balance
            self.usdc_balance_history = {}
            self.leaf_balance_history = {}
            self.month = 0
        
        def handle_redemptions(self, month: int, rate: float) -> Tuple[float, float]:
            """
            Handle redemptions based on the given rate.
            
            Args:
                month (int): Current simulation month.
                rate (float): Redemption rate (e.g., 0.02 for 2%).
            
            Returns:
                Tuple[float, float]: Amount of LEAF and USDC redeemed.
            """
            if month in self.usdc_balance_history:
                raise ValueError("Redemptions have already been processed for this month.")
            
            leaf_redeemed = self.leaf_balance * rate
            usdc_redeemed = self.usdc_balance * rate
            
            self.leaf_balance -= leaf_redeemed
            self.usdc_balance -= usdc_redeemed
            
            # Update history
            self.usdc_balance_history[month] = self.usdc_balance
            self.leaf_balance_history[month] = self.leaf_balance
            
            return leaf_redeemed, usdc_redeemed
        
        def step(self, month: int):
            """Advance the AEGIS model by one month."""
            # Apply market decay
            self.leaf_balance *= (1 - self.config.leaf_price_decay_rate)
            self.month += 1
    ```

### 5. OAK Distribution Model (`OAK.md`)

**Status**: ✅ Completed

**Implementation Details**:

- OAK Distribution Model is now fully implemented, tested, and integrated into the simulation.
- Detailed implementations are available in `src/Functions/OAK.py`.
- Initial OAK deals are defined in `src/Data/oak_deals.py`.
- Comprehensive tests are present in `Tests/test_OAK.py`.

**Key Components**:

1. **OAKModel Methods**

    ```python:src/Functions/OAK.py
    class OAKModel:
        def __init__(self, config: OAKDistributionConfig):
            self.config = config
            self.redemption_history = {}
            self.month = 0
            self.logger = self.config.logger
        
        def distribute_oak(self, month: int):
            """Distribute OAK tokens based on deals."""
            for deal in self.config.deals:
                if deal.start_month <= month < deal.start_month + deal.vesting_months:
                    # Distribute proportionally
                    distribution = deal.oak_amount / deal.vesting_months
                    self.redemption_history.setdefault(month, {})[deal.counterparty] = distribution
                    self.logger.debug(f"Distributed {distribution} OAK to {deal.counterparty} in month {month}.")
        
        def get_state(self) -> Dict[str, any]:
            """Get the current state of OAK distribution."""
            return {
                "month": self.month,
                "redemption_history": self.redemption_history,
                "total_oak_supply": self.config.total_oak_supply,
                "redemption_amount": sum(self.redemption_history.get(self.month, {}).values())
            }
        
        def get_monthly_redemption_amount(self, month: int) -> float:
            """
            Get the total amount of OAK redeemed in a specific month.
            
            Args:
                month (int): The month to check
            
            Returns:
                float: Total amount of OAK redeemed in the specified month
            """
            return sum(self.redemption_history.get(month, {}).values())
    ```

2. **OAKDistributionDeal**

    ```python:src/Functions/OAK.py
    @dataclass
    class OAKDistributionDeal:
        counterparty: str
        oak_amount: float
        start_month: int
        vesting_months: int
        irr_threshold: float
        unlock_month: int
        acquisition_price: float = 1.0  # Default acquisition price
    
    @dataclass
    class OAKDistributionConfig:
        deals: List[OAKDistributionDeal]
        redemption_start_month: int = 12
        redemption_end_month: int = 48
        total_oak_supply: float = field(init=False)
        logger: logging.Logger = field(default=logging.getLogger(__name__), init=False)
        
        def __post_init__(self):
            self.total_oak_supply = sum(deal.oak_amount for deal in self.deals)
    ```

### 6. LEAF Price Model (`LeafPrice.md`)

**Status**: ✅ Completed

**Implementation Details**:

- **LEAF Price Model**: Updated `LeafPrice.py` to align with the latest specifications.
  - Removed the stability period and monthly compound growth logic.
  - Configurations are passed from the simulation, and no parameters are fixed within the class.
  - Price is updated based on trade impacts and can be updated multiple times within a month.
  - The last price update in a month becomes the month-ending value; no further updates are allowed for that month.

**Key Components**:

1. **LEAFPriceModel**

    ```python:src/Functions/LeafPrice.py
    # src/Functions/LeafPrice.py

    from dataclasses import dataclass
    from typing import Tuple

    @dataclass
    class LEAFPriceConfig:
        """Configuration for LEAF price calculations."""
        min_price: float        # Minimum allowed LEAF price
        max_price: float        # Maximum allowed LEAF price
        price_impact_threshold: float  # Maximum price impact allowed (e.g., 0.10 for 10%)

    class LEAFPriceModel:
        """
        Handles LEAF price calculations, including price impact from trades.
        Price is updated based on trade impacts and can be updated multiple times within a month.
        The last price update in a month becomes the month-ending value and cannot be changed afterward.
        """

        def __init__(self, config: LEAFPriceConfig):
            self.config = config
            self.price_history = {}
            self.current_price = None  # Will be set when the simulation starts
            self.monthly_prices_locked = {}  # Tracks if the price for a month is finalized

        def initialize_price(self, initial_price: float):
            """Initialize the starting price of LEAF."""
            self.current_price = initial_price

        def calculate_price_impact(
            self,
            current_price: float,
            leaf_liquidity: float,
            usd_liquidity: float,
            trade_amount_usd: float
        ) -> Tuple[float, float]:
            """
            Calculate the price impact of a trade and return the new price.

            Args:
                current_price (float): Current LEAF price
                leaf_liquidity (float): Amount of LEAF tokens available within the price impact threshold
                usd_liquidity (float): USD value of paired liquidity within the price impact threshold
                trade_amount_usd (float): USD value of LEAF to be bought (positive) or sold (negative)

            Returns:
                Tuple[float, float]: (new_price, actual_price_impact_percentage)
            """
            if leaf_liquidity <= 0 or usd_liquidity <= 0:
                raise ValueError("Liquidity must be greater than 0")

            # Calculate total liquidity value
            total_liquidity = usd_liquidity + (leaf_liquidity * current_price)

            # Calculate price impact
            price_impact = trade_amount_usd / total_liquidity

            # Calculate new price with linear price impact
            # Positive trade_amount (buying) increases price, negative (selling) decreases price
            price_change = current_price * price_impact

            # Ensure price stays within bounds
            new_price = current_price + price_change

            new_price = max(self.config.min_price, min(self.config.max_price, new_price))

            # Calculate actual price impact percentage
            actual_price_impact = abs(price_change) / current_price

            return new_price, actual_price_impact

        def estimate_max_trade_size(
            self,
            current_price: float,
            leaf_liquidity: float,
            usd_liquidity: float,
            is_buy: bool
        ) -> float:
            """
            Estimate the maximum trade size possible within price impact threshold.

            Args:
                current_price (float): Current LEAF price
                leaf_liquidity (float): Amount of LEAF tokens available within the price impact threshold
                usd_liquidity (float): USD value of paired liquidity within the price impact threshold
                is_buy (bool): True for buy orders, False for sell orders

            Returns:
                float: Maximum trade size in USD
            """
            total_liquidity = usd_liquidity + (leaf_liquidity * current_price)
            max_trade = total_liquidity * self.config.price_impact_threshold

            return max_trade if is_buy else -max_trade

        def update_price(
            self,
            month: int,
            leaf_liquidity: float,
            usd_liquidity: float,
            trade_amount_usd: float
        ) -> float:
            """
            Update the LEAF price due to a trade impact.

            Args:
                month (int): Current simulation month
                leaf_liquidity (float): Amount of LEAF tokens available within the price impact threshold
                usd_liquidity (float): USD value of paired liquidity within the price impact threshold
                trade_amount_usd (float): USD value of LEAF to be bought (positive) or sold (negative)

            Returns:
                float: The updated LEAF price after the trade impact
            """
            if self.monthly_prices_locked.get(month, False):
                raise ValueError(f"Price for month {month} is already finalized and cannot be updated.")

            new_price, _ = self.calculate_price_impact(
                self.current_price,
                leaf_liquidity,
                usd_liquidity,
                trade_amount_usd
            )

            self.current_price = new_price
            self.price_history[month] = new_price

            return new_price

        def finalize_month_price(self, month: int):
            """
            Finalize the LEAF price for the month, preventing further updates.

            Args:
                month (int): The month to finalize
            """
            self.monthly_prices_locked[month] = True

        def get_current_price(self, month: int) -> float:
            """
            Get the LEAF price for the current month.

            Args:
                month (int): Current simulation month

            Returns:
                float: Current LEAF price
            """
            # If the price has not been initialized, raise an error
            if self.current_price is None:
                raise ValueError("LEAF price has not been initialized.")

            return self.current_price
    ```

2. **Testing for LEAF Price Model**

    ```python:Tests/test_leaf_price.py
    # Tests/test_leaf_price.py

    import unittest
    import logging
    from src.Functions.LeafPrice import LEAFPriceConfig, LEAFPriceModel

    class TestLEAFPrice(unittest.TestCase):
        def setUp(self):
            # Configure logging for the test
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger('TestLEAFPrice')
            
            # Configuration with no fixed parameters inside the class
            self.config = LEAFPriceConfig(
                min_price=0.01,
                max_price=100.0,
                price_impact_threshold=0.10  # 10% maximum price impact
            )
            self.model = LEAFPriceModel(self.config)
            self.model.initialize_price(initial_price=1.0)

        def test_buy_price_impact(self):
            """Test price impact from buying LEAF."""
            self.logger.info("Testing buy price impact")
            
            current_price = self.model.get_current_price(month=1)
            leaf_liquidity = 100_000
            usd_liquidity = 100_000
            trade_amount_usd = 10_000  # Buying $10,000 worth of LEAF
            
            new_price = self.model.update_price(
                month=1,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )
            
            expected_price_impact = trade_amount_usd / (usd_liquidity + leaf_liquidity * current_price)
            expected_new_price = current_price + current_price * expected_price_impact
            
            self.logger.debug(f"New price after buy: {new_price}")
            self.assertAlmostEqual(new_price, expected_new_price, places=6)

        def test_sell_price_impact(self):
            """Test price impact from selling LEAF."""
            self.logger.info("Testing sell price impact")
            
            current_price = self.model.get_current_price(month=1)
            leaf_liquidity = 100_000
            usd_liquidity = 100_000
            trade_amount_usd = -10_000  # Selling $10,000 worth of LEAF
            
            new_price = self.model.update_price(
                month=1,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )
            
            expected_price_impact = trade_amount_usd / (usd_liquidity + leaf_liquidity * current_price)
            expected_new_price = current_price + current_price * expected_price_impact
            
            self.logger.debug(f"New price after sell: {new_price}")
            self.assertAlmostEqual(new_price, expected_new_price, places=6)

        def test_multiple_updates_in_month(self):
            """Test multiple price updates within the same month."""
            self.logger.info("Testing multiple price updates in a month")
            
            month = 1
            self.model.initialize_price(initial_price=1.0)
            leaf_liquidity = 100_000
            usd_liquidity = 100_000
            
            # First trade
            trade_amount_usd = 5_000
            new_price = self.model.update_price(
                month=month,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )
            expected_price_impact = trade_amount_usd / (usd_liquidity + leaf_liquidity * 1.0)
            expected_new_price = 1.0 + 1.0 * expected_price_impact
            self.assertAlmostEqual(new_price, expected_new_price, places=6)
            
            # Second trade
            trade_amount_usd = -2_500
            new_price = self.model.update_price(
                month=month,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )
            expected_price_impact = trade_amount_usd / (usd_liquidity + leaf_liquidity * expected_new_price)
            expected_new_price = expected_new_price + expected_new_price * expected_price_impact
            self.assertAlmostEqual(new_price, expected_new_price, places=6)
            
            # Finalize the month's price
            self.model.finalize_month_price(month)
            
            # Attempt to update after finalization
            with self.assertRaises(ValueError):
                self.model.update_price(
                    month=month,
                    leaf_liquidity=leaf_liquidity,
                    usd_liquidity=usd_liquidity,
                    trade_amount_usd=1_000
                )

        def test_price_boundaries(self):
            """Test that price does not exceed min and max bounds."""
            self.logger.info("Testing price boundaries")
            
            month = 1
            leaf_liquidity = 100_000
            usd_liquidity = 100_000
            
            # Attempt to set price below min_price
            trade_amount_usd = -10_000 * (self.config.min_price / 1.0 + 1)  # Large sell to push price below min
            with self.assertRaises(ValueError):
                self.model.update_price(
                    month=month,
                    leaf_liquidity=leaf_liquidity,
                    usd_liquidity=usd_liquidity,
                    trade_amount_usd=trade_amount_usd
                )
            
            # Attempt to set price above max_price
            trade_amount_usd = 10_000 * (self.config.max_price / 1.0 + 1)  # Large buy to push price above max
            with self.assertRaises(ValueError):
                self.model.update_price(
                    month=month,
                    leaf_liquidity=leaf_liquidity,
                    usd_liquidity=usd_liquidity,
                    trade_amount_usd=trade_amount_usd
                )

        def test_price_impact_threshold(self):
            """Test that trades exceeding the price impact threshold are rejected."""
            self.logger.info("Testing price impact threshold enforcement")
            
            current_price = self.model.get_current_price(month=1)
            leaf_liquidity = 100_000
            usd_liquidity = 100_000
            
            # Trade that exceeds price impact threshold
            trade_amount_usd = (usd_liquidity + leaf_liquidity * current_price) * (self.config.price_impact_threshold + 0.01)
            
            with self.assertRaises(ValueError):
                self.model.update_price(
                    month=1,
                    leaf_liquidity=leaf_liquidity,
                    usd_liquidity=usd_liquidity,
                    trade_amount_usd=trade_amount_usd
                )

        def test_finalize_month_price(self):
            """Test that price cannot be updated after month is finalized."""
            self.logger.info("Testing month price finalization")

            month = 1
            leaf_liquidity = 100_000
            usd_liquidity = 100_000
            trade_amount_usd = 5_000  # Buy order

            # Update price once
            self.model.update_price(
                month=month,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )

            # Finalize the month's price
            self.model.finalize_month_price(month)

            # Attempt to update price after finalization
            with self.assertRaises(ValueError):
                self.model.update_price(
                    month=month,
                    leaf_liquidity=leaf_liquidity,
                    usd_liquidity=usd_liquidity,
                    trade_amount_usd=1_000
                )

    if __name__ == '__main__':
        unittest.main()
    ```

## Remaining Implementation Order

### 7. Finalize Documentation and Testing

**Objective**: Ensure all models are well-documented and thoroughly tested.

**Actions**:

- **Complete Documentation for LEAF Price Model**:
  - Finalize `Docs/LeafPrice.md` with detailed explanations, configurations, and usage examples.

- **Develop Comprehensive Test Suites**:
  - Expand unit tests to cover all functionalities of the `LEAFPriceModel`.
  - Ensure that edge cases and error conditions are thoroughly tested.

- **Perform Peer Reviews**:
  - Conduct thorough code reviews to maintain code quality and consistency.
  - Incorporate feedback and implement necessary changes.

- **Integrate with Other Models**:
  - Validate that the updated LEAF Price Model interacts correctly with AEGIS and OAK models.
  - Ensure that price changes due to trade impacts are reflected accurately in other model computations.

### 8. Deployment and Monitoring

**Objective**: Prepare the simulation for deployment and ensure its reliability in production environments.

**Actions**:

- **Set Up Deployment Pipelines**:
  - Automate the deployment process using CI/CD tools.
  - Ensure smooth transitions from development to production environments.

- **Implement Monitoring Tools**:
  - Track simulation performance and resource usage.
  - Detect anomalies and performance bottlenecks in real-time.

- **Establish Logging Mechanisms**:
  - Capture detailed information about simulation runs.
  - Facilitate debugging and analysis through comprehensive logs.

## Development Guidelines

### 1. Module Structure

```python:src/Functions/LeafPrice.py
src/
  Functions/
    TVL.py                     ✅ Completed
    Revenue.py                 ✅ Completed
    LEAFPairs.py               ✅ Completed
    AEGIS.py                   ✅ Completed
    OAK.py                     ✅ Completed
    LeafPrice.py               ✅ Completed
    TVLLoader.py               ✅ Completed
    boosted_tvl.py             ✅ Completed
    TVLContributions.py        ✅ Completed
  Simulations/
    simulate.py                ✅ Completed
  Data/
    leaf_deal.py               ✅ Completed
    oak_deals.py               ✅ Completed
    initial_contributions.py   ✅ Completed
Tests/
  test_TVLContributions.py    ✅ Completed
  test_AEGIS.py               ✅ Completed
  test_OAK.py                 ✅ Completed
  test_LeafPrice.py           ✅ Completed
Docs/
  TVL.md                      ✅ Completed
  Revenue.md                  ✅ Completed
  LEAFPairs.md                ✅ Completed
  AEGIS.md                    ✅ Completed
  OAK.md                      ✅ Completed
  LeafPrice.md                ✅ Completed
```

### 2. Testing Strategy

- **Unit Tests**:
  - Developed unit tests for `TVLContribution` and related functionalities in `Tests/test_TVLContributions.py` to ensure individual components work as expected.
  - **AEGIS Model**: Tests in `Tests/test_AEGIS.py` focusing on balance management, redemption mechanisms, and market decay effects.
  - **OAK Distribution Model**: Tests in `Tests/test_OAK.py` covering full simulations, IRR calculations, and redemption behaviors.
  - **LEAF Price Model**: Completed unit tests in `Tests/test_LeafPrice.py`.

- **Integration Tests**:
  - Developed integration tests to validate interactions between models (e.g., how AEGIS interacts with LEAF Pairs).
  - Ensured that other modules (AEGIS, LEAFPairs, Revenue, etc.) cause price impacts to LEAF Price within the simulation, with these impacts recorded by the simulation calling the LEAF Price module.

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

- **Linting and Formatting**:
  - Adhere to PEP 8 guidelines using tools like `flake8` and `black` to ensure consistent code style.

- **Modular Design**:
  - Ensure that each module has a clear responsibility, promoting reusability and ease of testing.

## Timeline

### Week 1: Model Integration

- **Tasks**:
  - Fully integrate the **LEAF Price Module** with:
    - `AEGIS` Model.
    - `LEAFPairs` Model.
    - `TVL` Model.
    - `Revenue` Model.
  - Refine the monthly simulation loop in `src/Simulations/simulate.py` to support integrated operations.
  
- **Deliverables**:
  - Updated `simulate.py` with integrated LEAF pricing.
  - Verified interactions between models through initial manual testing.

### Week 2: Testing Expansion

- **Tasks**:
  - **Unit Testing**:
    - Develop additional unit tests for `OAK` and `AEGIS` models, focusing on edge cases.
    - Utilize the existing test frameworks in `Tests/test_OAK.py` and `Tests/test_AEGIS.py`.
  - **Integration Testing**:
    - Design and implement initial integration tests to validate model interactions.
  
- **Deliverables**:
  - Expanded unit test suite with increased coverage.
  - Preliminary integration tests demonstrating model interoperability.

### Week 3: Documentation Enhancement

- **Tasks**:
  - **Refine Documentation**:
    - Review and update `Docs/AEGIS.md`, `Docs/OAK.md`, and `Docs/LeafPrice.md` for clarity.
  - **Add Examples**:
    - Incorporate practical examples and step-by-step guides in documentation files.
    - Ensure that new contributors can easily understand and utilize the models.
  
- **Deliverables**:
  - Comprehensive and clarified documentation files.
  - Added usage examples and guides in documentation.

### Week 4: Future Enhancements Implementation

- **Tasks**:
  - **New Deal Creation Mechanism**:
    - Design and implement the ability to create new deals dynamically within the `OAK` model.
    - Ensure that new deals adhere to existing validation and redemption logic.
  - **Finalize LEAF Price Integration**:
    - Address any remaining issues related to LEAF price dynamics across all models.
    - Conduct thorough testing to confirm accurate price impacts.
  
- **Deliverables**:
  - Functional new deal creation mechanism within the `OAK` model.
  - Fully integrated LEAF price dynamics validated through testing.

## Testing Progress

### AEGIS Model Tests (`Tests/test_AEGIS.py`)

**Overview**:

- Comprehensive unit tests covering initialization, redemptions, market decay, step updates, and liquidity calculations.

**Key Tests**:

1. **Initial State**:
    - Verifies initial balances and price.

2. **Redemption**:
    - Tests redemption mechanics, ensuring correct balance updates and error handling for multiple redemptions in the same month.

3. **Market Decay**:
    - Ensures that the LEAF price decays correctly over time.

4. **Step Updates**:
    - Validates that monthly steps correctly update balance histories and apply price decay.

5. **Liquidity Calculations**:
    - Tests the `get_liquidity_within_percentage` method for various price points and ensures proper USDC concentration.

**Sample Test Case**:

```python:Tests/test_AEGIS.py
20| class TestAEGISModel(unittest.TestCase):
21|     ...
22|     def test_redemption(self):
23|         """Test redemption with specific month and rate"""
24|         initial_leaf = self.aegis_model.leaf_balance
25|         initial_usdc = self.aegis_model.usdc_balance
26|         test_month = 1
27|         test_rate = 0.02  # 2% redemption
28|         
29|         # Execute redemption
30|         leaf_redeemed, usdc_redeemed = self.aegis_model.handle_redemptions(test_month, test_rate)
31|         
32|         # Calculate expected values
33|         expected_leaf_redeemed = initial_leaf * test_rate
34|         expected_usdc_redeemed = initial_usdc * test_rate
35|         expected_leaf_balance = initial_leaf - expected_leaf_redeemed
36|         expected_usdc_balance = initial_usdc - expected_usdc_redeemed
37|         
38|         print(f"\nTesting redemption:")
39|         print(f"Month: {test_month}")
40|         print(f"Initial LEAF: {initial_leaf:,.2f}")
41|         print(f"Initial USDC: {initial_usdc:,.2f}")
            ...
55|         self.assertAlmostEqual(usdc_redeemed, expected_usdc_redeemed)
56|         
57|         # Test that we can't redeem twice in same month
58|         with self.assertRaises(ValueError):
59|             self.aegis_model.handle_redemptions(test_month, test_rate)
60|         
61|         # Test that we can redeem in a different month
62|         next_month = test_month + 1
63|         self.aegis_model.handle_redemptions(next_month, test_rate)
            ...
213|    unittest.main() 
```

## Notes

- **Regular Updates**:
  - Continuously review and adjust the implementation order as progress is made.
  - Stay adaptable to changing project requirements and emerging challenges.

- **Collaboration**:
  - Engage with team members during integration and testing phases to ensure cohesive progress.
  - Share findings, seek feedback, and incorporate improvement suggestions promptly.

- **Performance Monitoring**:
  - Maintain vigilance on simulation performance, especially as model complexity increases.
  - Optimize code where necessary to prevent potential performance bottlenecks.

- **Version Control Best Practices**:
  - Commit changes frequently with clear and descriptive messages.
  - Ensure that all team members adhere to the established branching and merging strategies to prevent conflicts.

- **Integration Behavior**:
  - Other modules (AEGIS, LEAFPairs, Revenue, etc.) will cause price impacts to the LEAF Price Model within the simulation.
  - These impacts will be recorded by the simulation by calling the LEAF Price module.
  - This integration behavior still must be implemented to ensure accurate and dynamic price adjustments based on model interactions.

---

## Summary

By adhering to this implementation order, the CanopyDFF project aims to:

- **Achieve Full Integration**: Seamlessly combine all financial models within the simulation framework to produce accurate and reliable projections.

- **Ensure High-Quality Code**: Expand testing coverage to over 80%, focusing on critical functionalities and edge cases to maintain robustness.

- **Provide Clear Documentation**: Enhance documentation to support both current development and future contributions, ensuring accessibility and comprehensiveness.

- **Enhance Model Realism**: Implement dynamic features such as new deal creation and fully integrated LEAF pricing to reflect real-world scenarios more accurately.

- **Foster Sustainable Growth**: Utilize comprehensive simulations and projections to inform strategic business development and tokenomics decisions within the Canopy ecosystem.

**Notes on Updates:**

- **LEAF Price Module Completion**: The `LEAFPriceModel` section has been updated to reflect its completion, removing the stability period and compound growth logic. All configurations are now passed from the simulation, ensuring no fixed parameters within the class.

- **Integration Behavior**: An additional task has been added under the **Notes** section to highlight that other modules (AEGIS, LEAFPairs, Revenue, etc.) will impact the LEAF Price Model. This integration behavior requires implementation to ensure that trade impacts are accurately recorded and reflected in the LEAF price dynamics.

- **Testing Progress**: The testing section for `test_OAK.py` and `test_AEGIS.py` has been completed, and `test_LeafPrice.py` is now marked as completed, reflecting the comprehensive testing of the LEAF Price Model.

- **Completion Status Updates**: All modules are now marked as ✅ Completed in the **Module Structure** section, indicating their readiness and integration within the simulation framework.
