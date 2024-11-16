# CanopyDFF Implementation Order

## Repository Overview

The CanopyDFF repository comprises several interconnected models for Canopy's tokenomics and financial projections:

1. **TVL Model (`TVL.md`)**: Projects overall TVL growth, Canopy TVL, and Boosted TVL
2. **Revenue Model (`Revenue.md`)**: Projects revenue based on TVL composition
3. **LEAF Pairs Model (`LEAFPairs.md`)**: Handles liquidity pairs involving LEAF tokens
4. **AEGIS Model (`AEGIS.md`)**: Manages LEAF and USDC balances and redemptions
5. **OAK Distribution Model (`OAK.md`)**: Manages OAK token distribution and redemption

## Completed Implementations

### 1. TVL Model (`TVL.md`)

**Status**: ✅ Completed

**Implementation Details**:

- Combined TVL, Boosted TVL, and Total Impact into single unified model
- Core implementation in `src/Functions/TVL.py`
- Simulation and visualization in `src/Simulations/simulate.py`

**Key Components**:

1. **TVLModelConfig**:

```python:src/Functions/TVL.py
startLine: 6
endLine: 13
```

2. **BoostedTVLModel**:

```python:src/Functions/TVL.py
startLine: 15
endLine: 39
```

3. **TVLModel**:

```python:src/Functions/TVL.py
startLine: 41
endLine: 84
```

4. **Simulation**:

```python:src/Simulations/simulate.py
startLine: 4
endLine: 83
```

**Documentation**: Full specification in `Docs/TVL.md`

## Remaining Implementation Order

### 2. Revenue Model (`Revenue.md`)

**Reasoning**: With TVL projections in place, the Revenue Model can accurately project revenue streams.

**Implementation Plan**:

- Create `src/Functions/Revenue.py`
- Define revenue calculation methods based on TVL composition
- Implement fee structure and revenue distribution logic
- Add simulation and visualization capabilities

### 3. LEAF Pairs Model (`LEAFPairs.md`)

**Reasoning**: Requires TVL and Revenue models to properly model liquidity dynamics.

**Implementation Plan**:

- Create `src/Functions/LEAFPairs.py`
- Implement liquidity pair management
- Model LEAF token price impacts
- Add simulation capabilities for different market scenarios

### 4. AEGIS Model (`AEGIS.md`)

**Reasoning**: Depends on LEAF Pairs model for balance management.

**Implementation Plan**:

- Create `src/Functions/AEGIS.py`
- Implement LEAF/USDC balance tracking
- Add redemption mechanics
- Model market-driven changes

### 5. OAK Distribution Model (`OAK.md`)

**Reasoning**: Most complex model requiring all other components.

**Implementation Plan**:

- Create `src/Functions/OAK.py`
- Implement distribution logic
- Add redemption calculations
- Model risk-adjusted returns

## Development Guidelines

1. **Module Structure**:

```
src/
  Functions/
    TVL.py         ✅ Completed
    Revenue.py     🔄 Next
    LEAFPairs.py   🔜 Pending
    AEGIS.py       🔜 Pending
    OAK.py         🔜 Pending
  Simulations/
    simulate.py    ✅ Completed
```

2. **Testing Strategy**:

- Unit tests for each model
- Integration tests between dependent models
- Scenario testing for edge cases

3. **Documentation Requirements**:

- Comprehensive docstrings
- Updated markdown specs
- Implementation notes
- Usage examples

4. **Code Quality**:

- Type hints
- Error handling
- Input validation
- Performance optimization

## Additional Recommendations

1. **Configuration Management**:

- Centralize parameters in config files
- Document assumption changes
- Version control for different scenarios

2. **Visualization**:

- Consistent plotting styles
- Interactive dashboards
- Export capabilities

3. **Validation**:

- Cross-check calculations
- Peer review process
- Regular calibration

4. **Maintenance**:

- Regular code reviews
- Performance monitoring
- Documentation updates
