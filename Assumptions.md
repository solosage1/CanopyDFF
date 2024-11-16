# Updated Assumptions Document

This document outlines the starting conditions, recommended settings, and implementation details for the Canopy ecosystem models, incorporating the information from the updated timeline and code files. These assumptions are crucial for understanding the foundational parameters and configurations that drive each component.

---

## Overview of Timeline Events

### Month 0: Initial Deployment

- **Active Components:**
  - **TVL Model:** Active from Month 0 onwards.

### Month 1: LEAF Incentives Start

- **Events:**
  - **LEAF Pairings Active:** LEAF pairs are activated, allowing participants to lock liquidity and start earning LEAF tokens.
- **Impact:**
  - **Increase in TVL:** The introduction of LEAF pairings is expected to increase the total value locked (TVL) in the network.
  - **Market Participants:** Liquidity providers and protocols can deposit capital paired with LEAF, preparing for future trading.

### Month 2: LEAF Trading (Underlying LP)

- **Events:**
  - **LEAF Token Trading Activated:** LEAF tokens are added to an underlying liquidity pool, becoming tradable.
- **Impact:**
  - **Market Confidence:** Stable or increasing LEAF token price is expected to drive confidence and encourage more deposits.
  - **No Selling Pressure:** As no LEAF tokens are distributed initially, there's minimal selling pressure.

### Month 3: OAK Token Becomes Tradable

- **Events:**
  - **OAK Token Trading Activated:** OAK tokens become tradable on exchanges.
- **Impact:**
  - **Increased Market Activity:** Trading of OAK tokens is expected to increase market activity and further build confidence.

### Month 4: OAK Redemption Start

- **Events:**
  - **OAK Redemption Activated:** Users can redeem OAK tokens for underlying assets.
- **Impact:**
  - **Minimal Redemptions Expected:** Due to stable LEAF prices and high internal rates of return, few redemptions are expected.

### Month 5: Market and Distribution Achievements

- **Events:**
  - **Full Activation of Market Mechanisms:** All market mechanisms, including Canopy Boost, are fully active.
- **Impact:**
  - **Incentive Alignment:** Distribution strategies align incentives among users and stakeholders, supporting network growth.
  - **Sustainable Growth:** The ecosystem reaches maturity, attracting larger investors and supporting long-term sustainability.

---

## TVL Model

### Starting Conditions

- **Move Blockchain Total TVL:** $800 million initial.
- **Canopy TVL:** $350 million initial.
- **Initial Market Share:** 43.75% (Canopy TVL / Move Blockchain TVL).
- **Minimum Market Share:** 10% floor.
- **Market Share Decay Rate:** 0.02 annually.

### Growth Assumptions

#### Move Blockchain Growth Rates

- **Year 1:** 150% annual growth.
- **Year 2:** 100% annual growth.
- **Year 3:** 75% annual growth.
- **Year 4:** 50% annual growth.
- **Year 5:** 40% annual growth.

#### Market Share Dynamics

- **Exponential Decay:** Canopy's market share decays exponentially from the initial 43.75% towards the minimum 10% floor.
- **Decay Rate:** 0.02 annually.

### Implementation Details

- **Configuration Parameters:**

  ```python
  TVLModelConfig(
      initial_move_tvl=800_000_000,           # $800 million
      initial_canopy_tvl=350_000_000,         # $350 million
      move_growth_rates=[1.5, 1.0, 0.75, 0.5, 0.4],  # Annual growth rates over 5 years
      min_market_share=0.10,                  # 10% floor
      market_share_decay_rate=0.02            # Annual decay rate
  )
  ```

- **Move TVL Calculation:**
  - **Monthly Growth Rates:** Convert annual growth rates to monthly rates per year.
  - **Month-to-Month Calculation:** Apply the appropriate monthly growth rate based on the year.

- **Canopy TVL Calculation:**
  - **Market Share Decay:** Canopy's market share decays exponentially towards the minimum floor.
  - **Monthly Calculation:** Calculate Canopy's TVL as a percentage of Move's TVL each month.

### Model Limitations

- Does not account for:
  - Market shocks or black swan events.
  - Seasonal variations in TVL.
  - Competitive actions beyond general market share decay.
  - Geographic variations.
  - Regulatory impacts.

---

## Revenue Model

### Revenue Model Starting Conditions

- **TVL Composition:**
  - **Initial Volatile TVL Share:** 10%
  - **Target Volatile TVL Share:** 20%
  - **Volatile Share Growth Duration:** 24 months

- **Revenue Rates (Annual):**
  - **Initial Volatile Revenue Rate:** 5%
  - **Target Volatile Revenue Rate:** 2%
  - **Initial Stable Revenue Rate:** 1%
  - **Target Stable Revenue Rate:** 0.5%

### Recommended Settings

- **Volatile TVL Share Growth:**
  - **Linear Growth:** Volatile TVL share increases linearly from 10% to 20% over 24 months.

- **Revenue Rate Decay:**
  - **Linear Decay:** Revenue rates decay linearly from initial values to target values over 24 months.

- **Monthly Revenue Calculation:**
  - **Convert Annual Rates to Monthly Rates:** Divide annual rates by 12 to get monthly rates.
  - **Calculate Revenues:**
    - **Volatile Revenue:** `Volatile TVL` * `Volatile Rate (monthly)`
    - **Stable Revenue:** `Stable TVL` * `Stable Rate (monthly)`
    - **Total Revenue:** Sum of volatile and stable revenues.

### Revenue Model Implementation Details

- **Configuration Parameters:**

  ```python
  RevenueModelConfig(
      initial_volatile_share=0.10,       # 10% volatile at start
      target_volatile_share=0.20,        # Target 20% volatile share
      share_growth_duration=24,          # Duration to reach target share (months)
      initial_volatile_rate=0.05,        # 5% annual volatile rate
      target_volatile_rate=0.02,         # 2% annual volatile rate
      initial_stable_rate=0.01,          # 1% annual stable rate
      target_stable_rate=0.005           # 0.5% annual stable rate
  )
  ```

- **Volatile Share Calculation:**
  - **Monthly Progress:** `progress = min(month / share_growth_duration, 1.0)`
  - **Current Volatile Share:** `volatile_share = initial_volatile_share + (target_volatile_share - initial_volatile_share) * progress`

- **Revenue Rate Calculation:**
  - **Volatile Rate:**
    - `volatile_rate = initial_volatile_rate + (target_volatile_rate - initial_volatile_rate) * progress`
  - **Stable Rate:**
    - `stable_rate = initial_stable_rate + (target_stable_rate - initial_stable_rate) * progress`

- **Monthly Rates:**
  - **Convert Annual Rates to Monthly Rates:** `monthly_rate = annual_rate / 12`

### Revenue Model Limitations

- Does not account for:
  - Abrupt market changes affecting TVL composition.
  - Competitive pressures dynamically adjusting revenue rates.
  - Seasonal variations in revenue generation.
  - Network effects influencing revenue growth.
  - Regulatory impacts on revenue.

---

## LEAF Pairs Model

### LEAF Pairs Model Starting Conditions

- **Total LEAF Minted:** 1,000,000,000 LEAF tokens.

- **Initial Liquidity Deals:**
  - Initial LEAF Pair deals with specifics such as:
    - **Counterparty:** "Move"
    - **Amount USD:** $1,500,000
    - **LEAF Percentage:** 35%
    - **Start Month:** 1
    - **Duration Months:** 60 months
    - **Base Concentration:** 0.5
    - **Max Concentration:** 0.8
    - **Min Concentration:** 0.2

### LEAF Pairs Model Recommended Settings

- **Liquidity Management:**
  - **Concentration Levels:** Control the impact on liquidity pairs through concentration settings.

- **Market Impact Handling:**
  - **LEAF Trading Activity:**
    - Adjust LEAF and counter asset balances based on trading activities.
    - **Selling LEAF:** Decrease LEAF balance, increase counter asset balance.
    - **Buying LEAF:** Increase LEAF balance, decrease counter asset balance.

- **Proportional Redemptions:**
  - Ensure redemptions are proportional to current LEAF and counter asset holdings.

- **Historical Tracking:**
  - Maintain logs of monthly LEAF and other asset balances for analysis.

---

## OAK Distribution Model

### OAK Distribution Model Starting Conditions

- **Total OAK Minted:** 500,000 OAK tokens (hard cap).
- **Total LEAF Minted:** 1,000,000,000 LEAF tokens.
- **OAK Redemption Window:**
  - **Start Month:** 4
  - **End Month:** 48

### OAK Distribution Model Recommended Settings

- **Redemption Mechanics:**
  - **Redemption Percentage:** Define strategic percentages for monthly redemptions to maintain liquidity and token value.
  - **IRR Thresholds:** Set internal rate of return thresholds to guide redemption processes.

- **Supply Tracking:**
  - Monitor total OAK supply to ensure it does not exceed the hard cap.
  - Implement mechanisms to burn redeemed tokens, reducing total supply accordingly.

---

## General Recommendations

1. **Parameter Synchronization:**
   - Ensure that parameters across models (TVL, Revenue, LEAF Pairs, OAK Distribution) are consistent.
   - Align growth assumptions with market conditions and strategic objectives.

2. **Monitoring and Validation:**
   - Regularly track actual vs. projected metrics (e.g., TVL growth, revenue).
   - Adjust models based on real-world data and market feedback.

3. **Risk Management:**
   - Perform stress tests with various growth scenarios.
   - Prepare for potential market volatility and competitive pressures.

4. **Model Extensions:**
   - Consider incorporating market shocks or regulatory impacts into future model enhancements.
   - Explore adding seasonal variations or network effect factors.

5. **Documentation and Maintenance:**
   - Keep assumptions and parameters up to date.
   - Document any changes to models or configurations.

6. **Testing and Validation:**
   - Implement unit tests and integration tests for all calculations.
   - Conduct scenario analyses for different market conditions.

7. **Reporting and Visualization:**
   - Provide regular reports on key metrics.
   - Use visualizations to communicate trends and performance to stakeholders.

---

By incorporating the updated timeline and assumptions from the revised code files, this document provides a comprehensive framework for projecting the Canopy ecosystem's growth and economic dynamics. Regular reviews and updates are recommended to maintain alignment with evolving market conditions and strategic goals.
