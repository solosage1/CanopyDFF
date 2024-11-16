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

1. **TVLModelConfig**:

    ```python:src/Functions/TVL.py
    startLine: 6
    endLine: 13
    ```

2. **TVLModel**:

    ```python:src/Functions/TVL.py
    startLine: 15
    endLine: 84
    ```

**Documentation**: Full specification in `Docs/TVL.md`.

### 2. Revenue Model (`Revenue.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Implemented revenue calculation based on TVL composition.
- Core implementation in `src/Functions/Revenue.py`.
- Integrated revenue calculations into simulation in `src/Simulations/simulate.py`.

**Key Components**:

1. **RevenueModelConfig**:

    ```python:src/Functions/Revenue.py
    startLine: 5
    endLine: 14
    ```

2. **RevenueModel**:

    ```python:src/Functions/Revenue.py
    startLine: 16
    endLine: 64
    ```

3. **Simulation Integration**:

    - Updated `src/Simulations/simulate.py` to include revenue calculations and visualizations.

    ```python:src/Simulations/simulate.py
    startLine: 100
    endLine: 320
    ```

**Documentation**: Full specification in `Docs/Revenue.md`.

### 3. LEAF Pairs Model (`LEAFPairs.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Handles liquidity pairs involving LEAF tokens, including deal initialization and liquidity calculations.
- Core implementation in `src/Functions/LEAFPairs.py`.
- Integrated LEAF Pairs logic into simulation in `src/Simulations/simulate.py`.
- Debugged and resolved issues related to LEAF price calculations.

**Key Components**:

1. **LEAFPairDeal**:

    ```python:src/Functions/LEAFPairs.py
    startLine: 5
    endLine: 20
    ```

2. **LEAFPairsModel**:

    ```python:src/Functions/LEAFPairs.py
    startLine: 22
    endLine: 84
    ```

3. **Simulation Integration**:

    - Updated `src/Simulations/simulate.py` to include LEAF Pairs management and fixed bugs.

    ```python:src/Simulations/simulate.py
    startLine: 85
    endLine: 320
    ```

**Documentation**: Full specification in `Docs/LEAFPairs.md`.

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
    TVL.py         ✅ Completed
    Revenue.py     ✅ Completed
    LEAFPairs.py   ✅ Completed
    AEGIS.py       🔜 Pending
    OAK.py         🔜 Pending
  Simulations/
    simulate.py    ✅ Completed
Docs/
  TVL.md
  Revenue.md
  LEAFPairs.md
  AEGIS.md        🔜 Pending
  OAK.md          🔜 Pending
```

### 2. Testing Strategy

- **Unit Tests**:
  - Develop unit tests for each model to ensure individual functionalities work as expected.
  
- **Integration Tests**:
  - Test interactions between dependent models (e.g., how AEGIS interacts with LEAF Pairs).

- **Scenario Testing**:
  - Implement scenario analyses for edge cases and varying market conditions.

### 3. Documentation Requirements

- **Comprehensive Docstrings**:
  - Ensure all classes, methods, and functions have clear and descriptive docstrings.
  
- **Updated Markdown Specifications**:
  - Maintain up-to-date documentation in the `Docs/` directory for each model.
  
- **Implementation Notes**:
  - Document any assumptions, design choices, and dependencies.

- **Usage Examples**:
  - Provide examples to demonstrate how each model and function should be used.

### 4. Code Quality

- **Type Hints**:
  - Utilize type hints for all functions and methods to enhance readability and maintainability.

- **Error Handling**:
  - Implement robust error handling to manage unexpected inputs and states.

- **Input Validation**:
  - Validate all inputs to functions and methods to ensure data integrity.

- **Performance Optimization**:
  - Optimize code for performance, especially within simulation loops and calculations.

## Additional Recommendations

### 1. Configuration Management

- **Centralize Parameters**:
  - Store all configurable parameters in centralized config files to simplify adjustments and maintenance.

- **Document Assumption Changes**:
  - Track and document any changes to assumptions in a version-controlled manner.

- **Version Control for Scenarios**:
  - Manage different simulation scenarios through version control to facilitate testing and comparisons.

### 2. Visualization

- **Consistent Plotting Styles**:
  - Maintain uniform styles and color schemes across all visualizations for clarity.

- **Interactive Dashboards**:
  - Consider developing interactive dashboards to allow dynamic exploration of simulation results.

- **Export Capabilities**:
  - Enable exporting of plots and data for reporting and further analysis.

### 3. Validation

- **Cross-Check Calculations**:
  - Regularly verify that all calculations align with the documented assumptions and specifications.

- **Peer Review Process**:
  - Implement a peer review process for all code changes to catch potential issues early.

- **Regular Calibration**:
  - Adjust models based on real-world data and feedback to enhance accuracy.

### 4. Maintenance

- **Regular Code Reviews**:
  - Schedule periodic code reviews to ensure code quality and adherence to best practices.

- **Performance Monitoring**:
  - Monitor the performance of simulations and models, optimizing as necessary.

- **Documentation Updates**:
  - Keep all documentation up to date with the latest changes and implementations.

## Conclusion

This updated Implementation Order document provides a clear roadmap for advancing the CanopyDFF project. By following the outlined steps and adhering to development guidelines, the team can ensure a structured and efficient implementation process. Regular reviews and updates to this document are recommended to accommodate any changes in project scope or requirements.

---
