# Assumptions Document

This document outlines the starting conditions and recommended settings for the Canopy OAK Distribution Model, LEAF Pairs Model, Influenced TVL Model, and Revenue Model. These assumptions are crucial for understanding the foundational parameters and configurations that drive each component of the Canopy ecosystem.

## Table of Contents

1. [OAK Distribution Model](#oak-distribution-model)
   - [Starting Conditions](#starting-conditions)
   - [Recommended Settings](#recommended-settings)
2. [LEAF Pairs Model](#leaf-pairs-model)
   - [Starting Conditions](#starting-conditions-1)
   - [Recommended Settings](#recommended-settings-1)
3. [Influenced TVL Model](#influenced-tvl-model)
   - [Starting Conditions](#starting-conditions-2)
   - [Recommended Settings](#recommended-settings-2)
4. [Revenue Model](#revenue-model)
   - [Starting Conditions](#starting-conditions-3)
   - [Recommended Settings](#recommended-settings-3)
5. [General Recommendations](#general-recommendations)

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

- **IRR Calculations**:
  - Utilize dual exponential decay functions for best case IRR calculations:
    - **Below 1% IRR**: Apply a faster decay rate.
    - **Above 1% IRR**: Apply a slower decay rate.
  
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
   - Ensure that parameters across different models (OAK Distribution, LEAF Pairs, Influenced TVL, Revenue) are harmonized to reflect consistent economic assumptions.
   - Example: The growth rate in the Influenced TVL Model should align with revenue projections in the Revenue Model.

2. **Scalability**:
   - Design models to allow easy scaling of parameters such as the number of liquidity deals, growth rates, and redemption windows without significant code changes.
   - Utilize configuration files or environment variables to adjust parameters dynamically.

3. **Monitoring and Alerts**:
   - Implement monitoring systems to track deviations from assumptions and trigger alerts when key metrics (e.g., IRR thresholds, influenced TVL shares) approach critical limits.
   - Use visualization tools to regularly review model performances against assumptions.

4. **Documentation and Transparency**:
   - Maintain comprehensive documentation for each model to facilitate audits, onboarding of new team members, and external reviews.
   - Update this assumptions document regularly to reflect changes in strategic directions or market conditions.

5. **Flexibility for Extensions**:
   - Design models with extensibility in mind, allowing for future enhancements such as partial redemptions, dynamic thresholds, and integration with external financial data sources.
   - Modularize code to enable independent updates and scalability.

6. **Risk Management**:
   - Incorporate robust risk management strategies to handle unexpected market conditions, ensuring the resilience of the OAK distribution and revenue generation mechanisms.
   - Implement contingency plans for extreme scenarios like market crashes or regulatory changes.

7. **Testing and Validation**:
   - Conduct thorough testing, including unit tests, integration tests, and scenario analyses, to validate the accuracy and reliability of each model under various conditions.
   - Utilize sensitivity analysis to understand the impact of different parameter variations on model outcomes.

---

By adhering to these starting conditions and recommended settings, the Canopy ecosystem can ensure a stable, fair, and scalable distribution of OAK tokens, effective management of LEAF pairs, realistic modeling of influenced TVL, and accurate revenue projections. Regular reviews and updates to this assumptions document are advised to accommodate evolving market dynamics and strategic objectives. 