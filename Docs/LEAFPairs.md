# LEAF Pairs Model

## Purpose

The LEAF Pairs Model manages liquidity pairs involving LEAF tokens. It handles the distribution, maintenance, and tracking of liquidity in various trading pairs, ensuring optimal liquidity provision and market stability. This model supports both single-sided and balanced pairs, with dynamic concentration adjustments based on target ratios.

## Python Implementation

```python:Functions/LEAFPairs.md
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict
import math

@dataclass
class LEAFPairDeal:
    counterparty: str           # Name of the counterparty
    amount_usd: float           # Total liquidity value in USD
    num_leaf_tokens: float      # Number of LEAF tokens added
    start_month: int            # Start month (as number of months since launch)
    duration_months: int        # Duration of the deal in months
    leaf_percentage: float      # Target percentage of liquidity in LEAF (0-50%)
    concentration: float        # Concentration level for above-target LEAF buying
    correlation: float          # Correlation coefficient to BTC

    # Balance tracking
    leaf_balance: float = None      # Current LEAF balance (number of tokens)
    other_balance: float = None     # Current other token balance in USD

    UNISWAP_V2_CONCENTRATION = 0.1  # Base concentration for below-target selling

    def __post_init__(self):
        if self.leaf_balance is None:
            self.leaf_balance = self.num_leaf_tokens
        if self.other_balance is None:
            self.other_balance = self.amount_usd - (self.num_leaf_tokens * self.get_leaf_price())

    def get_leaf_price(self) -> float:
        """Assumes initial LEAF price based on allocation."""
        return (self.amount_usd / self.num_leaf_tokens) if self.num_leaf_tokens else 0

    def get_effective_concentration(self, is_buying_leaf: bool) -> float:
        """
        Calculate effective concentration based on whether LEAF is being bought or sold.
        
        Args:
            is_buying_leaf: True if buying LEAF, False if selling LEAF.
        
        Returns:
            Effective concentration value.
        """
        if is_buying_leaf:
            return self.concentration
        else:
            return self.UNISWAP_V2_CONCENTRATION

    def calculate_weighted_liquidity(self, is_buying_leaf: bool, leaf_price: float) -> float:
        """
        Calculate the weighted liquidity based on current LEAF price and concentration.
        
        Args:
            is_buying_leaf: True if buying LEAF, False if selling LEAF.
            leaf_price: Current LEAF price in USD.
        
        Returns:
            Weighted liquidity in USD.
        """
        total_liquidity = (self.leaf_balance * leaf_price) + self.other_balance
        effective_concentration = self.get_effective_concentration(is_buying_leaf)
        return total_liquidity * effective_concentration
```

```python:Functions/LEAFPairs.md
class LEAFPairsConfig:
    deals: List[LEAFPairDeal]

    def __init__(self, deals: List[LEAFPairDeal]):
        self.deals = deals
    
    def add_deal(self, deal: LEAFPairDeal):
        existing_deals = [d.counterparty for d in self.deals]
        if deal.counterparty in existing_deals:
            raise ValueError(f"Deal with counterparty {deal.counterparty} already exists.")
        self.deals.append(deal)

@dataclass
class LEAFPairsModel:
    def __init__(self, config: LEAFPairsConfig):
        self.config = config
        self.current_month = min(deal.start_month for deal in config.deals)
        self.balance_history = defaultdict(
            list
        )  # month -> List[(counterparty, leaf_balance, other_balance)]
        self._validate_deals()
        self._record_state(self.current_month)

    def process_market_change(
        self,
        month: int,
        leaf_price: float,
        total_market_change: float,
    ) -> Dict[str, Tuple[float, float]]:
        """
        Process market changes across all active deals.

        Args:
            month: Month number since start.
            leaf_price: Current LEAF price in USD.
            total_market_change: Net token change from LEAF trading
                                 (positive = sold LEAF, negative = bought LEAF).

        Returns:
            Dict of counterparty -> (new_leaf_balance, new_other_balance).
        """
        if month < self.current_month:
            raise ValueError("Cannot process market changes for past months.")
        if month > self.current_month + 1:
            raise ValueError("Cannot skip months when processing market changes.")

        for deal in self.config.deals:
            if self._is_deal_active(deal, month):
                is_buying_leaf = total_market_change < 0
                weighted_liquidity = deal.calculate_weighted_liquidity(is_buying_leaf, leaf_price)
                liquidity_change = (total_market_change * (weighted_liquidity / self._total_weighted_liquidity(month, leaf_price)))
                if is_buying_leaf:
                    deal.leaf_balance += liquidity_change / leaf_price
                    deal.other_balance -= liquidity_change
                else:
                    deal.leaf_balance -= liquidity_change / leaf_price
                    deal.other_balance += liquidity_change

                if deal.other_balance < 0:
                    raise ValueError(
                        f"Insufficient other token balance for deal with {deal.counterparty}."
                    )

        results = {
            deal.counterparty: (deal.leaf_balance, deal.other_balance)
            for deal in self.config.deals
            if self._is_deal_active(deal, month)
        }

        self._record_state(month)
        self.current_month = month

        return results

    def get_ratio_deviations(
        self, month: int, leaf_price: float
    ) -> Dict[str, float]:
        """
        Calculate how far each deal is from its target ratio.

        Args:
            month: Month number to check.
            leaf_price: Current LEAF price in USD.

        Returns:
            Dict of counterparty -> ratio deviation (positive means above target).
        """
        if month > self.current_month:
            raise ValueError("Cannot get ratio deviations for future months.")

        return {
            deal.counterparty: (deal.leaf_balance * leaf_price / (deal.leaf_balance * leaf_price + deal.other_balance)) - (deal.leaf_percentage / 100)
            for deal in self.get_active_deals(month)
        }

    def get_liquidity_metrics(
        self, month: int, leaf_price: float
    ) -> Dict[str, Dict[str, float]]:
        """
        Get liquidity metrics for each deal.

        Args:
            month: Month number to check.
            leaf_price: Current LEAF price in USD.

        Returns:
            Dict of counterparty -> metrics dict.
        """
        return {
            deal.counterparty: {
                "leaf_balance_tokens": deal.leaf_balance,
                "leaf_balance_usd": deal.leaf_balance * leaf_price,
                "other_balance_usd": deal.other_balance,
                "current_leaf_ratio": (deal.leaf_balance * leaf_price) / (deal.leaf_balance * leaf_price + deal.other_balance) if (deal.leaf_balance * leaf_price + deal.other_balance) > 0 else 0,
            }
            for deal in self.get_active_deals(month)
        }

    def get_leaf_liquidity(self, month: int, leaf_price: float) -> float:
        """
        Calculate total LEAF liquidity for a given month.

        Args:
            month: Month number to check.
            leaf_price: Current LEAF price in USD.

        Returns:
            Total LEAF liquidity in USD.
        """
        return sum(
            deal.leaf_balance * leaf_price for deal in self.get_active_deals(month)
        )

    def get_deals_end_in_month(
        self, month: int, leaf_price: float
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get liquidity of deals that end in a specific month.

        Args:
            month: The month in which deals end.
            leaf_price: Current LEAF price in USD to calculate USD value.

        Returns:
            Dict of counterparty -> (leaf_balance_tokens, leaf_balance_usd).
        """
        if month <= 0:
            raise ValueError("Month must be a positive integer.")
        if (month - 1) < self.current_month:
            raise ValueError(
                "Cannot retrieve end-of-deal balances for months not yet processed."
            )

        deals_ending = [
            deal for deal in self.config.deals if (deal.start_month + deal.duration_months) == month
        ]
        if not deals_ending:
            return {}

        end_balances = {}
        for deal in deals_ending:
            # Ensure the previous month's state is recorded
            if (month - 1) not in self.balance_history:
                raise ValueError(
                    f"State for month {month - 1} is not recorded yet."
                )
            # Find the balance for this deal in the previous month
            previous_state = self.balance_history[month - 1]
            deal_state = next(
                (
                    (cp, leaf, other)
                    for cp, leaf, other in previous_state
                    if cp == deal.counterparty
                ),
                None,
            )
            if deal_state is None:
                raise ValueError(
                    f"No state found for deal {deal.counterparty} in month {month - 1}."
                )
            _, leaf_balance, _ = deal_state
            leaf_balance_usd = leaf_balance * leaf_price
            end_balances[deal.counterparty] = (leaf_balance, leaf_balance_usd)

        return end_balances

    def add_new_deal(self, deal: LEAFPairDeal):
        """
        Add a new liquidity pair deal to the configuration.

        Args:
            deal: LEAFPairDeal instance to add.
        """
        self.config.add_deal(deal)
        self._validate_deals()
        self._record_state(self.current_month)

    def get_active_deals(self, month: int) -> List[LEAFPairDeal]:
        """
        Retrieve all active deals for a given month.

        Args:
            month: Month number to check.

        Returns:
            List of active LEAFPairDeal instances.
        """
        return [
            deal for deal in self.config.deals if self._is_deal_active(deal, month)
        ]

    def _is_deal_active(self, deal: LEAFPairDeal, month: int) -> bool:
        """
        Check if a deal is active during a given month.

        Args:
            deal: LEAFPairDeal instance.
            month: Month number to check.

        Returns:
            True if active, False otherwise.
        """
        return deal.start_month <= month < (deal.start_month + deal.duration_months)

    def _validate_deals(self) -> None:
        """
        Validate all deals in the configuration.
        """
        for deal in self.config.deals:
            if not (0 <= deal.leaf_percentage <= 50):
                raise ValueError(
                    f"Invalid leaf_percentage for deal with {deal.counterparty}. Must be between 0 and 50."
                )
            if not (0 <= deal.concentration <= 1):
                raise ValueError(
                    f"Invalid concentration for deal with {deal.counterparty}. Must be between 0 and 1."
                )
            if deal.duration_months <= 0:
                raise ValueError(
                    f"Invalid duration_months for deal with {deal.counterparty}. Must be positive."
                )
            if deal.amount_usd <= 0:
                raise ValueError(
                    f"Invalid amount_usd for deal with {deal.counterparty}. Must be positive."
                )
            if deal.num_leaf_tokens < 0:
                raise ValueError(
                    f"Invalid num_leaf_tokens for deal with {deal.counterparty}. Must be non-negative."
                )
            # Additional validations can be added here

    def _record_state(self, month: int) -> None:
        """Record current state for all active deals."""
        self.balance_history[month] = [
            (deal.counterparty, deal.leaf_balance, deal.other_balance)
            for deal in self.get_active_deals(month)
        ]

    def _total_weighted_liquidity(self, month: int, leaf_price: float) -> float:
        """Calculate the total weighted liquidity for market change distribution."""
        return sum(
            deal.calculate_weighted_liquidity(
                is_buying_leaf=(deal.leaf_percentage < (deal.leaf_balance * leaf_price) / (deal.leaf_balance * leaf_price + deal.other_balance)),
                leaf_price=leaf_price
            )
            for deal in self.get_active_deals(month)
        )
```

```python:Functions/LEAFPairs.md
# Sample Usage

```python:Functions/LEAFPairs.md
# Create initial deals
deals = [
    LEAFPairDeal(
        counterparty="Protocol A",
        amount_usd=1_000_000,
        num_leaf_tokens=200_000,      # 200k LEAF tokens at $5 each
        start_month=0,
        duration_months=12,
        leaf_percentage=50,            # 50% LEAF target
        concentration=0.3,             # Higher concentration for rebalancing
        correlation=0.0                # Uncorrelated (e.g., USDC pair)
    ),
    LEAFPairDeal(
        counterparty="Protocol B",
        amount_usd=2_000_000,
        num_leaf_tokens=100_000,      # 100k LEAF tokens at $20 each
        start_month=3,
        duration_months=24,
        leaf_percentage=25,            # 25% LEAF target
        concentration=0.2,             # Medium concentration
        correlation=0.8                # Highly correlated to BTC
    )
]

# Initialize model
config = LEAFPairsConfig(deals=deals)
model = LEAFPairsModel(config)

# Process market changes
results = model.process_market_change(
    month=1,
    leaf_price=5.0,               # Current LEAF price in USD
    total_market_change=50_000    # Selling LEAF
)

print("Market Change Results:")
for counterparty, balances in results.items():
    print(f"{counterparty}: Leaf Balance = {balances[0]}, Other Balance = {balances[1]}")

# Check ratio deviations
deviations = model.get_ratio_deviations(month=1, leaf_price=5.0)
print("\nRatio Deviations:")
for counterparty, deviation in deviations.items():
    status = "above" if deviation > 0 else "below" if deviation < 0 else "at"
    print(f"{counterparty}: {status} target by {abs(deviation)*100:.2f}%")

# Get liquidity metrics
metrics = model.get_liquidity_metrics(month=1, leaf_price=5.0)
print("\nLiquidity Metrics:")
for counterparty, metric in metrics.items():
    print(f"{counterparty}: {metric}")

# Get deals ending in month 12
deals_end_month_12 = model.get_deals_end_in_month(month=12, leaf_price=5.0)
print("\nDeals Ending in Month 12:")
for counterparty, (tokens, usd_value) in deals_end_month_12.items():
    print(f"{counterparty}: {tokens} LEAF tokens, ${usd_value:.2f} USD")
```

## Implementation Details

1. **Deal Structure**:
   - **Target LEAF Percentage**: Defines the desired ratio of LEAF tokens in the liquidity pair.
   - **Dynamic Concentration**: Adjusts based on whether the current LEAF ratio is above or below the target.
   - **Balance Tracking**: Maintains LEAF token counts and other token balances in USD.
   - **State History**: Records balances for each month to allow state restoration.

2. **Concentration Mechanics**:
   - **Above Target**:
     - **Buying LEAF**: Uses the deal's specific concentration level for LEAF buying.
     - **Selling LEAF**: Defaults to Uniswap V2 concentration level (0.1) for LEAF selling.
   - **Below Target**:
     - **Buying LEAF**: Defaults to Uniswap V2 concentration level (0.1) for LEAF buying.
     - **Selling LEAF**: Uses the deal's specific concentration level for LEAF selling.
   - **Weighted Impact**: Distributes market changes across deals based on weighted liquidity.

3. **State Management**:
   - **Tracking Balances**: Keeps track of LEAF and other token balances over time.
   - **Current Month Updates**: Allows updates only to the latest month to maintain consistency.
   - **Ratio History**: Maintains how each deal deviates from its target ratio over time.

4. **Validation Rules**:
   - Ensures that all input parameters are within valid ranges (e.g., percentages between 0-50% for LEAF).
   - Prevents processing of past or skipped months.
   - Validates that balance updates do not result in negative balances.

## Model Capabilities

1. **Process Market Changes**:
   - Distributes LEAF buying or selling across active deals based on concentration and target ratios.

2. **Track Ratio Deviations**:
   - Monitors how each deal's current LEAF ratio deviates from its target.

3. **Maintain Balance History**:
   - Keeps a historical record of balances for each deal by month.

4. **Add New Deals**:
   - Allows adding new liquidity pair deals dynamically.

5. **Retrieve Liquidity Metrics**:
   - Provides detailed metrics on LEAF and other token balances for each deal.

6. **Ensure Consistent State**:
   - Only permits updates to the latest month to avoid inconsistencies.

## Integration Notes

1. **Price Impact Model**:
   - **Integration**: Provides concentration-weighted liquidity metrics to support dynamic price impacts.
   - **Functionality**: Adjusts liquidity distribution based on LEAF price fluctuations.

2. **Risk Management**:
   - **Integration**: Utilizes ratio deviations to monitor and manage risks associated with liquidity pair imbalances.
   - **Functionality**: Alerts or actions can be triggered based on significant deviations from target ratios.

3. **Performance Analysis**:
   - **Integration**: Uses historical state data to analyze performance over time.
   - **Functionality**: Facilitates rebalancing strategies and optimization of liquidity pair deals.

4. **Volume Model**:
   - **Integration**: Can leverage liquidity metrics to assess trading volumes and liquidity provisioning efficiency.
   - **Functionality**: Enhances understanding of market participation and liquidity dynamics.

5. **TVL Model**:
   - **Integration**: Uses total value locked metrics to gauge the overall health and scale of liquidity pair deals.
   - **Functionality**: Provides insights into capital allocation and investment performance.

## Recommended Extensions

1. **Add Price Impact Tracking**:
   - Enhance the model to track how trading activities influence LEAF price over time.

2. **Include Volume-Based Metrics**:
   - Incorporate metrics that evaluate trading volumes and their effects on liquidity pairs.

3. **Add Trading Limits**:
   - Implement constraints to prevent excessive buying or selling that could destabilize the liquidity pairs.

4. **Track Historical Trading Activity**:
   - Maintain a detailed log of all trading activities for auditing and performance review purposes.

5. **Add Minimum Balance Requirements**:
   - Ensure that deals maintain a minimum balance to sustain liquidity and operational stability.

6. **Include Fee Calculations**:
   - Integrate fee structures to account for transactional costs associated with LEAF trading.

7. **Add Detailed Reporting Capabilities**:
   - Develop comprehensive reporting tools to visualize and analyze liquidity pair performance and metrics.