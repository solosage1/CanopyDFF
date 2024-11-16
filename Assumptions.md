# Assumptions Document

This document outlines the starting conditions and recommended settings for the Canopy ecosystem models. These assumptions are crucial for understanding the foundational parameters and configurations that drive each component.

## Table of Contents

1. [TVL Model](#tvl-model)
   - [Starting Conditions](#starting-conditions)
   - [Growth Assumptions](#growth-assumptions)
   - [Implementation Details](#implementation-details)
2. [OAK Distribution Model](#oak-distribution-model)
3. [LEAF Pairs Model](#leaf-pairs-model)
4. [Influenced TVL Model](#influenced-tvl-model)
5. [Revenue Model](#revenue-model)
6. [General Recommendations](#general-recommendations)

---

## TVL Model

### Starting Conditions

- **Move Blockchain Total TVL**: $800M initial
- **Canopy TVL**: $300M initial
- **Initial Market Share**: 37.5% (derived from initial TVLs)
- **Minimum Market Share**: 10% floor
- **Market Share Decay Rate**: 0.04 annually

### Growth Assumptions

#### Move Blockchain Growth
- **Year 1**: 200% annual growth
- **Year 2**: 150% annual growth
- **Year 3**: 100% annual growth
- **Year 4**: 75% annual growth
- **Year 5**: 50% annual growth

#### Market Share Dynamics
- Exponential decay from initial 37.5% share
- Floor at 10% minimum share
- Yearly decay rate of 0.04
- Smooth decline as competitors enter the market

### Implementation Details

#### Growth Calculation
- Monthly compounding of annual growth rates
- Continuous growth within each year
- Maintains final year's cumulative growth for any periods beyond 5 years

#### Market Share Calculation
- Exponential decay function with floor
- Yearly decay rate converted to monthly basis
- Prevents share from falling below minimum threshold

#### Configuration Parameters
```python
TVLModelConfig(
    initial_move_tvl=800_000_000,    # $800M
    initial_canopy_tvl=300_000_000,  # $300M
    move_growth_rates=[2.0, 1.5, 1.0, 0.75, 0.5],  # Annual growth rates
    min_market_share=0.10,           # 10% floor
    market_share_decay_rate=0.04     # Annual decay rate
)
```

#### Model Limitations
- Does not account for:
  - Market shocks or black swan events
  - Seasonal variations in TVL
  - Competitive actions beyond general market share decay
  - Geographic variations
  - Regulatory impacts

---

## OAK Distribution Model

### Starting Conditions

- **Total OAK Minted**: 500,000 OAK tokens (hard cap).
- **Total LEAF Minted**: 1,000,000,000 LEAF tokens.
- **Global Redemption Window**:
  - **Start Month**: 3
  - **End Month**: 48

### Recommended Settings

- **Redemption Mechanics**:
  - **Redemption Percentage**: Define a strategic percentage for monthly redemptions to maintain liquidity and token value.
  - **IRR Thresholds**: Set risk-adjusted Internal Rate of Return (IRR) thresholds to guide redemption processes.
  
- **Supply Tracking**:
  - Continuously monitor the total OAK supply, ensuring it does not exceed the hard cap.
  - Implement mechanisms to burn redeemed tokens, reducing the total supply accordingly.

- **Sample Usage Parameters**:
  - **Initial OAK Supply**: 500,000 OAK
  - **Redemption Start Month**: 3
  - **Redemption End Month**: 48
  - **Redemption Percentage Range**: 5% to 15% monthly

---

## LEAF Pairs Model

### Starting Conditions

- **Total LEAF Minted**: 1,000,000,000 LEAF tokens.
- **Initial Liquidity Allocation**:
  - **Initial Leaf**: 900,000,000 LEAF tokens.
  - **Initial LEAF Price**: $1.00 per LEAF.
  - **Initial USDC Balance**: $900,000,000 USDC.
- **Liquidity Deals**: Define initial liquidity deals with specific protocols, allocating LEAF and USDC accordingly.

### Recommended Settings

- **Liquidity Management**:
  - **Concentration Level**: Set between 0 to 1 to control the degree of impact on liquidity pairs.
  - **Correlation Factors**: Adjust correlation with paired assets to manage risk and responsiveness to market changes.

- **Market Impact Handling**:
  - **LEAF Trading Activity**: Implement parameters to adjust LEAF and USDC balances based on buying and selling activities.
    - **Selling LEAF**: Decrease LEAF balance, increase USDC balance.
    - **Buying LEAF**: Increase LEAF balance, decrease USDC balance.
  
- **Proportional Redemptions**:
  - Ensure redemptions are handled proportionally based on current LEAF and USDC holdings.
  
- **Historical Tracking**:
  - Maintain detailed logs of monthly LEAF and USDC balances for auditing and performance analysis.
  
- **Sample Configuration Parameters**:
  - **Market Change Logic**: Reflects LEAF trading accurately in balance updates.
  - **Redemption Percentage**: Typically between 5% to 15% to balance liquidity needs.

---

## Influenced TVL Model

### Starting Conditions

- **Initial Non-Canopy TVL Influence**: 10%
- **Target Non-Canopy TVL Influence (5 years)**: 50%
- **Growth Pattern**: Sigmoid curve (slow start, accelerated middle, plateau)
- **Maximum Projection Duration**: 60 months (5 years)

### Recommended Settings

- **Growth Rate Parameter**: Set to 1.0 for a balanced growth curve.
- **Sigmoid Function Parameters**:
  - **Normalized Time Calculation**: `t = (month/max_months * 12) - 6`
  - **Base Sigmoid Function**: `S(t) = 1 / (1 + e^(-growth_rate * t))`
  
- **Configuration Flexibility**:
  - Allow adjustable parameters for `initial_influence_share`, `target_influence_share`, `growth_rate`, and `max_months` to model different growth scenarios.
  
- **Market Share Dynamics**:
  - **Network Effects**: Incorporate factors that accelerate influence growth during the middle phase of the sigmoid curve.
  
- **Integration with TVL Model**:
  - Ensure synchronization with the TVL model to accurately reflect influenced TVL in overall projections.
  
- **Sample Configuration Parameters**:
  - **Initial Influence Share**: 10%
  - **Target Influence Share**: 50%
  - **Growth Rate**: 1.0
  - **Max Months**: 60

---

## Revenue Model

### Starting Conditions

- **Volatile TVL Share**: 
  - **Initial**: 10%
  - **Target (5 years)**: 20%
- **Stable TVL Share**: 
  - **Initial**: 90%
  - **Target (5 years)**: 80%
- **Revenue Rates (Annual)**:
  - **Initial Volatile Revenue Rate**: 5%
  - **Target Volatile Revenue Rate (5 years)**: 1%
  - **Initial Stable Revenue Rate**: 1%
  - **Target Stable Revenue Rate (5 years)**: 0.1%
- **Decay and Growth Parameters**:
  - **Revenue Rate Decay**: 0.03
  - **Volatile Share Growth**: 0.02

### Recommended Settings

- **Revenue Calculation**:
  - Implement exponential decay functions for revenue rates:
    - **Volatile Revenue Rate**: Decreases from 5% to 1% over 5 years.
    - **Stable Revenue Rate**: Decreases from 1% to 0.1% over 5 years.
  
- **Composition Tracking**:
  - Model the shift from stable to volatile TVL over time using sigmoid growth.
  
- **Rate Decay Implementation**:
  - **Volatile Rate Decay**: Faster decay for volatile TVL to reflect higher initial rewards.
  - **Stable Rate Decay**: Slower decay for stable TVL to ensure consistent returns.
  
- **Monthly Revenue Calculation**:
  - Convert annual revenue rates to monthly rates for accurate monthly projections.
  
- **Scenario Incorporations**:
  - **Market Shocks**: Model sudden changes in revenue rates due to unexpected market events.
  - **Competitive Pressures**: Adjust revenue rates based on market competition.
  
- **Sample Configuration Parameters**:
  - **Initial Volatile Share**: 10%
  - **Target Volatile Share**: 20%
  - **Initial Volatile Rate**: 5% annually
  - **Target Volatile Rate**: 1% annually
  - **Initial Stable Rate**: 1% annually
  - **Target Stable Rate**: 0.1% annually
  - **Revenue Rate Decay**: 0.03
  - **Volatile Share Growth**: 0.02

---

## General Recommendations

1. **Parameter Synchronization**:
   - Ensure TVL model parameters align with other models
   - Validate growth assumptions against market conditions
   - Regular calibration of decay rates based on competitive landscape

2. **Monitoring and Validation**:
   - Track actual vs. projected TVL growth
   - Monitor market share dynamics
   - Regular review of minimum share assumptions

3. **Risk Management**:
   - Stress test models with various growth scenarios
   - Plan for potential market share compression
   - Monitor competitive pressures and adjust decay rates

4. **Model Extensions**:
   - Consider adding seasonal variations
   - Implement market shock scenarios
   - Add geographic distribution of TVL
   - Include regulatory impact scenarios

5. **Documentation and Maintenance**:
   - Keep growth rate assumptions updated
   - Document market share decay rationale
   - Regular review of minimum share floor

6. **Testing and Validation**:
   - Unit tests for all calculations
   - Integration tests across models
   - Scenario analysis for different market conditions
   - Regular backtesting against actual data

7. **Reporting and Visualization**:
   - Monthly TVL tracking
   - Market share trend analysis
   - Growth rate validation
   - Competitive position monitoring

---

By adhering to these assumptions and recommendations, the Canopy ecosystem models provide a realistic framework for projecting TVL growth and market share evolution. Regular reviews and updates to this document are advised to maintain alignment with market conditions and strategic objectives. 