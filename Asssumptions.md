`````markdown:Asssumptions.md
# Assumptions Document

```markdown

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
- **Total LEAF Minted**: 1,000,000,000 LEAF
- **Global Redemption Window**:
  - **Start Month**: 3
  - **End Month**: 48

- **Initial Distribution Deals**:
  1. **Private Sale**
     - **OAK Amount**: 50,000 OAK (10% of 500,000)
     - **Start Month**: 3
     - **Lock Period**: 12 months
     - **IRR Threshold**: 25% annually
  2. **Initial Liquidity Deals**
     - **OAK Amount**: 50,000 OAK (10% of 500,000)
     - **Start Month**: 15
     - **Lock Period**: 12 months
     - **IRR Threshold**: 25% annually
  3. **Year 2 Liquidity Deals**
     - **OAK Amount**: 50,000 OAK (10% of 500,000)
     - **Start Month**: 27
     - **Lock Period**: 12 months
     - **IRR Threshold**: 15% annually
  4. **Year 3 Liquidity Deals**
     - **OAK Amount**: 50,000 OAK (10% of 500,000)
     - **Start Month**: 39
     - **Lock Period**: 12 months
     - **IRR Threshold**: 10% annually
  5. **Founding Partners**
     - **OAK Amount**: 150,000 OAK (30% of 500,000)
     - **Start Month**: 3
     - **Lock Period**: 24 months
     - **IRR Threshold**: 20% annually
  6. **Initial TVL Rewards**
     - **OAK Amount**: 75,000 OAK (15% of 500,000)
     - **Start Month**: 15
     - **Lock Period**: 12 months
     - **IRR Threshold**: 35% annually
  7. **Year 2 TVL Reward**
     - **OAK Amount**: 50,000 OAK (10% of 500,000)
     - **Start Month**: 27
     - **Lock Period**: 12 months
     - **IRR Threshold**: 25% annually
  8. **Year 3 TVL Deals**
     - **OAK Amount**: 25,000 OAK (5% of 500,000)
     - **Start Month**: 39
     - **Lock Period**: 12 months
     - **IRR Threshold**: 15% annually
  
- **Redemption Mechanics**:
  - **Dual Exponential Decay Function**:
    - **Decay Constants**:
      - \( k_1 = 0.1 \): Controls redemption scaling for IRR between threshold and 1%.
      - \( k_2 = 0.5 \): Controls redemption scaling for IRR below threshold but above 1%.
    - **Redemption Logic**:
      - Partial redemptions occur as IRR approaches the threshold based on the dual exponential decay function.
      - Full redemption is triggered only when risk-adjusted IRR falls below 1%.
  - **Proportional Redistribution**: Upon redemption, redistribute unredeemed AEGIS LP proportionally to remaining OAK holders.
  
- **Validation Rules**:
  - Ensure total OAK allocated across all deals does not exceed 500,000 OAK.
  - Validate that all deal parameters (amounts, dates, thresholds) are within logical and permissible ranges.
  - Prevent duplicate counterparty entries.
  - Validate redemption periods relative to vesting periods.

---

## LEAF Pairs Model

### Starting Conditions

- **Initial Liquidity Deals**:
  1. **Protocol A**
     - **Amount (USD)**: $1,000,000
     - **LEAF Tokens**: 200,000 LEAF ($5 each)
     - **Start Month**: 0
     - **Duration**: 12 months
     - **LEAF Percentage Target**: 50%
     - **Concentration**: 0.3
     - **Correlation**: 0.0 (Uncorrelated, e.g., USDC pair)
  
  2. **Protocol B**
     - **Amount (USD)**: $2,000,000
     - **LEAF Tokens**: 100,000 LEAF ($20 each)
     - **Start Month**: 3
     - **Duration**: 24 months
     - **LEAF Percentage Target**: 25%
     - **Concentration**: 0.2
     - **Correlation**: 0.8 (Highly correlated to BTC)

- **Initial Balance History**: Maintains LEAF and other token balances starting from deal inception.

### Recommended Settings

- **Concentration Mechanics**:
  - **Above Target**:
    - **Buying LEAF**: Use specific concentration level per deal.
    - **Selling LEAF**: Default to Uniswap V2 concentration level (0.1).
  
  - **Below Target**:
    - **Buying LEAF**: Default to Uniswap V2 concentration level (0.1).
    - **Selling LEAF**: Use specific concentration level per deal.
  
  - **Weighted Impact**: Distribute market changes based on weighted liquidity to each deal.

- **Validation Rules**:
  - **LEAF Percentage**: Must be between 0% and 50%.
  - **Concentration**: Must be between 0 and 1.
  - **Duration Months**: Must be positive.
  - **Amount USD**: Must be positive.

- **State Management**:
  - Only allow updates to the latest month to maintain consistency.
  - Prevent negative balances through rigorous validation.

---

## Influenced TVL Model

### Starting Conditions

- **Initial Influenced TVL Share**: 10%
- **Target Influenced TVL Share (5 Years)**: 50%
- **Growth Pattern**: Sigmoid curve (slow start, accelerated middle, plateau)
- **Configuration Parameters**:
  - **Initial Influence Share**: 10% (0.10)
  - **Target Influence Share**: 50% (0.50)
  - **Growth Rate**: 1.0
  - **Maximum Months**: 60 (5 years)

### Recommended Settings

- **Sigmoid Function Parameters**:
  - **Normalized Time**: \( t = \left(\frac{\text{month}}{\text{max\_months}} \times 12\right) - 6 \)
  - **Base Sigmoid**: \( S(t) = \frac{1}{1 + e^{-\text{growth\_rate} \times t}} \)
  - **Scaled Influence**: \( \text{influence\_share} = \text{initial\_share} + \text{range} \times S(t) \)
  
- **Influenced TVL Calculation**:
  - Ensure that influenced TVL does not exceed the target share.
  - Maintain separation from direct TVL to accurately represent influenced TVL.

- **Model Extensions**:
  - Incorporate market condition modifiers.
  - Include competitive response factors.
  - Add geographic distribution modeling.
  - Implement protocol-specific influence rates.
  - Add confidence intervals for influence estimations.

---

## Revenue Model

### Starting Conditions

- **Initial TVL Composition**:
  - **Volatile TVL Share**: 10% (0.10)
  - **Stable TVL Share**: 90% (0.90)

- **Initial Revenue Rates (Annual)**:
  - **Volatile Revenue Rate**: 5% (0.05)
  - **Stable Revenue Rate**: 1% (0.01)

- **Target Revenue Rates (5 Years, Annual)**:
  - **Volatile Revenue Rate**: 1% (0.01)
  - **Stable Revenue Rate**: 0.1% (0.001)

- **Growth and Decay Parameters**:
  - **Revenue Rate Decay**: 0.03
  - **Volatile Share Growth**: 0.02
  - **Target Volatile Share**: 20% (0.20)

### Recommended Settings

- **Revenue Calculation**:
  - **Monthly Revenue Rates**: Annual rates converted to monthly by dividing by 12.
  - **Exponential Decay**: Apply exponential decay to model declining revenue rates over time.
  
- **Volatile Share Calculation**:
  - **Growth Rate**: Adjust `volatile_share_growth` to control the speed at which volatile TVL share approaches the target.
  - **Bounded Growth**: Ensure that the volatile share does not exceed the target volatile share.

- **Revenue Model Extensions**:
  - Add market shock scenarios to simulate sudden changes.
  - Include competitive pressure modeling to adjust revenue rates dynamically.
  - Add seasonal adjustment factors to account for periodic fluctuations.
  - Implement correlation with TVL growth for more integrated revenue projections.
  - Add risk-adjusted scenarios to reflect uncertainty in revenue streams.

- **Validation Rules**:
  - **Share Percentages**: Ensure volatile and stable shares sum to 100%.
  - **Revenue Rates**: Validate that revenue rates remain within logical and non-negative bounds.
  - **TVL Constraints**: Prevent TVL inputs that could lead to negative revenue calculations.

---

## General Recommendations

1. **Parameter Synchronization**:
   - Ensure that parameters across different models (OAK Distribution, LEAF Pairs, Influenced TVL, Revenue) are harmonized to reflect consistent economic assumptions.

2. **Scalability**:
   - Design models to allow easy scaling of parameters such as the number of deals, growth rates, and redemption windows without significant code changes.

3. **Monitoring and Alerts**:
   - Implement monitoring systems to track deviations from assumptions and trigger alerts when key metrics (e.g., IRR thresholds, influenced TVL shares) approach critical limits.

4. **Documentation and Transparency**:
   - Maintain comprehensive documentation for each model to facilitate audits, onboarding of new team members, and external reviews.

5. **Flexibility for Extensions**:
   - Design models with extensibility in mind, allowing for future enhancements such as partial redemptions, dynamic thresholds, and integration with external financial data sources.

6. **Risk Management**:
   - Incorporate robust risk management strategies to handle unexpected market conditions, ensuring the resilience of the OAK distribution and revenue generation mechanisms.

7. **Testing and Validation**:
   - Conduct thorough testing, including unit tests, integration tests, and scenario analyses, to validate the accuracy and reliability of each model under various conditions.

---

By adhering to these starting conditions and recommended settings, the Canopy ecosystem can ensure a stable, fair, and scalable distribution of OAK tokens, effective management of LEAF pairs, realistic modeling of influenced TVL, and accurate revenue projections. Regular reviews and updates to this assumptions document are advised to accommodate evolving market dynamics and strategic objectives.
