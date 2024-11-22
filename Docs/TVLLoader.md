```markdown
# TVLLoader Documentation

## Overview

The `TVLLoader` class is a pivotal component within the simulation framework, responsible for managing and processing **Total Value Locked (TVL)** contributions each month. It interacts closely with the **TVLModel**, ensuring that TVL contributions are accurately initialized, updated, and tracked throughout the simulation period. Additionally, `TVLLoader` handles the integration of organic TVL growth based on existing contributions and manages the addition of new contracted TVL deals over time.

## File Location

- **File Path:** `src/Functions/TVLLoader.py`

## Class: TVLLoader

```python:src/Functions/TVLLoader.py
class TVLLoader:
    ...
```

### Purpose

- **Initialization:** Sets up initial TVL contributions based on predefined deals and organic growth configurations.
- **Monthly Processing:** Manages monthly TVL updates, including adding new contracted TVL after a specified month and handling organic contributions.
- **Contribution Management:** Creates and adds new TVL contributions, ensuring that the TVLModel is always up-to-date with the latest financial inputs.

### Initialization

```python:src/Functions/TVLLoader.py
def __init__(self, tvl_model: 'TVLModel', organic_config: Dict):
    """Initialize the TVLLoader with the TVLModel."""
    self.tvl_model = tvl_model
    self.id_counter = 1
    self.deals = initialize_deals()
    
    # Use configuration from simulation
    self.organic_ratio = organic_config['conversion_ratio']
    self.organic_decay_rate = organic_config['decay_rate']
    self.organic_duration = organic_config['duration_months']
    
    # Load initial contributions
    initial_contributions = self.load_initial_contributions(self.deals)
    for contribution in initial_contributions:
        self.tvl_model.add_contribution(contribution)
        # Add organic contribution for initial TVL
        if contribution.tvl_type == "Contracted":
            self._add_organic_contribution(contribution)
```

#### Parameters

- `tvl_model` (`TVLModel`): The TVL model instance that manages TVL contributions and calculations.
- `organic_config` (`Dict`): Configuration dictionary containing settings for organic TVL growth, including:
  - `conversion_ratio`: The percentage of a contracted TVL contribution that should spawn an organic contribution.
  - `decay_rate`: The monthly decay rate applied to organic TVL contributions.
  - `duration_months`: The lifespan (in months) of an organic TVL contribution.

#### Functionality

1. **Model Association:** Links the `TVLLoader` with a specific `TVLModel` instance.
2. **Deal Initialization:** Initializes TVL deals using the `initialize_deals()` function, which sets up predefined TVL contributions.
3. **Organic Configuration:** Sets up parameters for organic TVL growth based on the provided configuration.
4. **Initial Contributions Loading:** Loads initial TVL contributions from the initialized deals and adds them to the `TVLModel`. For each contracted contribution, it also initiates an organic contribution based on the configured ratio.

### Method: `process_month`

```python:src/Functions/TVLLoader.py
def process_month(self, month: int) -> None:
    """Process TVL changes for the current month."""
    # Add monthly contracted TVL after month 3
    self.add_monthly_contracted_tvl(month)
    
    # Step the TVL model
    self.tvl_model.step()
    
    # Log monthly TVL state
    tvl_state = self.tvl_model.get_current_tvl_by_type()
    logging.debug(f"\nMonth {month} TVL Breakdown:")
    for tvl_type, amount in tvl_state.items():
        logging.debug(f"- {tvl_type}: ${amount:,.2f}")
```

#### Parameters

- `month` (`int`): The current month number in the simulation (1-based index).

#### Functionality

1. **Adding New Contracted TVL:** Invokes `add_monthly_contracted_tvl(month)` to introduce new contracted TVL contributions starting from month 4 onward.
2. **TVL Model Update:** Calls the `step()` method of the `TVLModel` to advance the state of TVL contributions based on new inputs and decay rates.
3. **Logging:** Retrieves the current TVL breakdown by type and logs the detailed state for debugging and analysis purposes.

### Method: `load_initial_contributions`

```python:src/Functions/TVLLoader.py
def load_initial_contributions(self, deals: List[Deal]) -> List[TVLContribution]:
    """Load initial TVL contributions from deals."""
    contributions = []
    contribution_count = 0
    
    for deal in deals:
        if deal.tvl_amount > 0 and deal.tvl_type != 'none':
            end_month = deal.start_month + deal.tvl_duration_months
            contribution = TVLContribution(
                id=self.id_counter,
                counterparty=deal.counterparty,
                amount_usd=deal.tvl_amount,
                revenue_rate=deal.tvl_revenue_rate,
                start_month=deal.start_month,
                end_month=end_month,
                tvl_type=deal.tvl_type,
                active=True
            )
            contributions.append(contribution)
            self.id_counter += 1
            contribution_count += 1
    
    logging.debug(f"Loaded {contribution_count} initial TVL contributions")
    return contributions
```

#### Parameters

- `deals` (`List[Deal]`): A list of `Deal` objects representing predefined TVL contributions.

#### Functionality

- **Contribution Creation:** Iterates through each deal and creates a corresponding `TVLContribution` if the deal has a positive TVL amount and a valid TVL type.
- **ID Assignment:** Assigns a unique identifier to each contribution using `self.id_counter`.
- **Logging:** Logs the number of initial TVL contributions loaded for transparency.
- **Return Value:** Returns a list of initialized `TVLContribution` instances.

### Method: `_add_organic_contribution`

```python:src/Functions/TVLLoader.py
def _add_organic_contribution(self, source_contribution: TVLContribution) -> None:
    """Create an organic TVL contribution based on a percentage of the source."""
    organic_amount = source_contribution.amount_usd * self.organic_ratio
    
    end_month = source_contribution.start_month + self.organic_duration
    
    organic_contribution = TVLContribution(
        id=self.id_counter,
        tvl_type="Organic",
        counterparty=f"Organic_{source_contribution.counterparty}",
        amount_usd=organic_amount,
        start_month=source_contribution.start_month,
        end_month=end_month,
        revenue_rate=self.tvl_model.config.revenue_rates['Organic'],
        active=True,
        decay_rate=self.organic_decay_rate
    )
    
    self.id_counter += 1
    self.tvl_model.add_contribution(organic_contribution)
    logging.debug(
        f"Added organic contribution:"
        f"\n  ID: {organic_contribution.id}"
        f"\n  Amount: ${organic_amount:,.2f}"
        f"\n  Based on: {source_contribution.counterparty}"
        f"\n  Decay Rate: {self.organic_decay_rate:.1%}/month"
        f"\n  Duration: {self.organic_duration} months"
    )
```

#### Parameters

- `source_contribution` (`TVLContribution`): The original TVL contribution based on which an organic contribution is generated.

#### Functionality

- **Organic Amount Calculation:** Determines the amount of organic TVL to be added by applying the `organic_ratio` to the source contribution's USD amount.
- **Contribution Creation:** Constructs a new `TVLContribution` instance representing the organic growth, linking it to the original counterparty.
- **Revenue Rate & Decay:** Sets the revenue rate based on the TVLModel's configuration for "Organic" TVL and applies the configured decay rate.
- **Logging:** Provides detailed logs about the newly added organic contribution for traceability.

### Method: `add_monthly_contracted_tvl`

```python:src/Functions/TVLLoader.py
def add_monthly_contracted_tvl(self, month: int) -> None:
    """Add new monthly contracted TVL after month 3."""
    if month <= 3:
        logging.debug(f"No monthly TVL additions for month {month}")
        return
    
    # Create new deals for monthly TVL additions
    new_deal = Deal(
        deal_id=f"CONTRACT_{month:03d}",
        counterparty=f"MonthlyContract_{month}",
        start_month=month,
        tvl_amount=20_000_000,  # Combined amount
        tvl_revenue_rate=0.025,  # Average rate
        tvl_duration_months=6,
        tvl_type="Contracted"
    )
    
    # Add deal to the deals list
    self.deals.append(new_deal)
    logging.debug(f"Added new deal: {new_deal.deal_id} with TVL amount ${new_deal.tvl_amount}")
    
    # Create and add corresponding TVL contribution
    config = {
        'amount_usd': new_deal.tvl_amount,
        'start_month': new_deal.start_month,
        'revenue_rate': new_deal.tvl_revenue_rate,
        'duration_months': new_deal.tvl_duration_months,
        'counterparty': new_deal.counterparty
    }
    self.add_new_contribution('Contracted', config)
```

#### Parameters

- `month` (`int`): The current month number in the simulation.

#### Functionality

1. **Early Months Check:** Ensures that new contracted TVL contributions are only added from month 4 onward. For months 1 to 3, no additions are made, and a debug log is recorded.
2. **Deal Creation:** Constructs a new `Deal` instance representing a monthly contracted TVL addition with predefined parameters:
   - `tvl_amount`: \$20,000,000
   - `revenue_rate`: 2.5% monthly
   - `duration_months`: 6 months
3. **Deal Management:** Appends the new deal to the existing list of deals.
4. **Contribution Addition:** Prepares a configuration dictionary based on the new deal and calls `add_new_contribution` to create and add the corresponding TVL contribution.
5. **Logging:** Records the addition of the new deal for monitoring purposes.

### Method: `add_new_contribution`

```python:src/Functions/TVLLoader.py
def add_new_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
    """Add a new contribution during simulation."""
    contrib = self._create_contribution(tvl_type, config)
    self.tvl_model.add_contribution(contrib)
    
    # Add organic growth for contracted TVL
    if tvl_type == "Contracted":
        self._add_organic_contribution(contrib)
        
    logging.debug(f"Added new TVL Contribution ID {contrib.id} of type {tvl_type}")
    return contrib
```

#### Parameters

- `tvl_type` (`str`): The type of TVL contribution ("Contracted", "Organic", etc.).
- `config` (`Dict`): Configuration dictionary containing details for the contribution, such as:
  - `amount_usd`: The amount in USD for the contribution.
  - `start_month`: The month when the contribution starts.
  - `revenue_rate`: The monthly revenue rate for the contribution.
  - `duration_months`: The duration of the contribution in months.
  - `counterparty`: The counterparty associated with the contribution.

#### Functionality

1. **Contribution Creation:** Uses the `_create_contribution` helper method to instantiate a new `TVLContribution` based on the provided type and configuration.
2. **Model Update:** Adds the newly created contribution to the `TVLModel`.
3. **Organic Growth Handling:** If the contribution type is "Contracted", it triggers the creation of an organic contribution linked to this contribution.
4. **Logging:** Logs the addition of the new TVL contribution for transparency and debugging.
5. **Return Value:** Returns the newly created `TVLContribution` instance.

### Method: `_create_contribution`

```python:src/Functions/TVLLoader.py
def _create_contribution(self, tvl_type: str, config: Dict) -> TVLContribution:
    """Create a TVL contribution based on type and config."""
    end_month = config['start_month'] + config['duration_months']
    
    contribution = TVLContribution(
        id=self.id_counter,
        counterparty=config['counterparty'],
        amount_usd=config['amount_usd'],
        revenue_rate=config.get('revenue_rate', 0.0),
        start_month=config['start_month'],
        end_month=end_month,
        tvl_type=tvl_type,
        active=True
    )
    self.id_counter += 1
    return contribution
```

#### Parameters

- `tvl_type` (`str`): The type of TVL contribution.
- `config` (`Dict`): Configuration dictionary containing details for the contribution.

#### Functionality

- **End Month Calculation:** Determines the `end_month` by adding the `duration_months` to the `start_month`.
- **Contribution Instantiation:** Creates a new `TVLContribution` instance with the provided details.
- **ID Assignment:** Assigns a unique identifier to the contribution using `self.id_counter`.
- **ID Counter Increment:** Increments the ID counter for future contributions.
- **Return Value:** Returns the newly created `TVLContribution` instance.

## Example Usage

```python:src/Functions/TVLLoader.py:path/to/file.py
from src.Functions.TVLLoader import TVLLoader
from src.Functions.TVL import TVLModel, TVLModelConfig

# Initialize TVLModel with configuration
tvl_config = TVLModelConfig(
    revenue_rates={'Organic': 0.03, 'Contracted': 0.025},
    # ... other configurations
)
tvl_model = TVLModel(tvl_config)

# Define organic growth configuration
organic_config = {
    'conversion_ratio': 0.2,      # 20% of contracted TVL generates organic TVL
    'decay_rate': 0.05,           # 5% monthly decay for organic TVL
    'duration_months': 36         # Organic TVL lasts for 36 months
}

# Initialize TVLLoader
tvl_loader = TVLLoader(tvl_model, organic_config)

# Process TVL for a specific month
current_month = 4
tvl_loader.process_month(current_month)
```

## Interaction with Other Components

- **TVLModel:** `TVLLoader` directly interacts with `TVLModel` to add and update TVL contributions. It relies on `TVLModel` to manage the state and calculations related to TVL.
- **Deals Management:** Uses `initialize_deals()`, `get_active_deals()`, and `Deal` objects from `src.Data.deal` to manage and initialize TVL contributions based on predefined deals.
- **Logging:** Utilizes Python’s `logging` module to record detailed debug information, facilitating monitoring and debugging of TVL processes.

## Logging Details

- **Initialization Logs:** Logs the number of initial TVL contributions loaded during the initialization phase.
- **Monthly TVL Breakdown:** After processing each month, logs the breakdown of TVL by type, providing insights into the distribution of locked value.
- **Organic Contributions:** Logs detailed information whenever an organic TVL contribution is added, including the source contribution, amount, decay rate, and duration.
- **New Deal Additions:** Logs the addition of new contracted TVL deals each month, detailing the deal ID and TVL amount.
- **Contribution Additions:** Logs the addition of new TVL contributions, specifying their ID and type.

## Error Handling

- The current implementation assumes that all input configurations are valid and does not include explicit error handling within the `TVLLoader` class. It is advisable to implement additional validations and exception handling mechanisms to ensure robustness, especially when dealing with dynamic or user-provided configurations.

## Future Enhancements

- **Dynamic Contribution Adjustments:** Implement mechanisms to adjust TVL contributions dynamically based on external factors or simulation outcomes.
- **Enhanced Organic Growth Models:** Develop more sophisticated models for organic TVL growth, potentially incorporating factors like market conditions or user behavior.
- **Integration with Other Models:** Strengthen the integration between `TVLLoader` and other models (e.g., AEGIS, LEAF Pairs) to enable more complex interactions and dependencies.
- **Comprehensive Error Handling:** Introduce robust error detection and recovery strategies to handle unexpected scenarios gracefully.

## Additional Notes

- **Atomic Operations:** Ensure that operations involving multiple steps (e.g., adding a new deal and its corresponding contribution) are handled atomically to maintain data consistency.
- **Scalability:** Consider optimizing the `TVLLoader` methods for scalability, especially when dealing with a large number of TVL contributions and extended simulation periods.
- **Configuration Management:** Externalize configurations where possible to facilitate easier adjustments and experimentation with different simulation parameters.

## Related Documentation

- **Simulation Loop:** For an overarching view of how `TVLLoader` fits into the simulation, refer to the [Simulation Loop Documentation](simulation_loop.md).
- **AEGIS Module:** Understand how `TVLLoader` interacts with the AEGIS system by reviewing the [AEGIS Documentation](Docs/AEGIS.md).
- **TVL and Revenue Models:** Learn more about the TVL and Revenue models in [TVL_Revenue Documentation](Docs/TVL_Revenue.md).

## Conclusion

The `TVLLoader` class is integral to managing and processing TVL contributions within the simulation framework. By initializing contributions based on predefined deals, handling organic growth, and introducing new contracted TVL over time, it ensures that the TVLModel remains accurate and reflective of the evolving ecosystem. Comprehensive logging facilitates transparency and debugging, while future enhancements aim to bolster its robustness and functionality.
