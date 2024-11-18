# CanopyDFF Repository

## Overview

**CanopyDFF** is a comprehensive modeling toolkit designed to support Canopy's business development and tokenomics decisions. The project implements robust models for Total Value Locked (TVL) projections, revenue calculations, liquidity pair management, and token distribution mechanisms. This toolkit facilitates strategic planning by providing detailed simulations and visualizations of Canopy’s economic ecosystem over time.

## Table of Contents

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Components Overview](#components-overview)
   - [TVL Model](#tvl-model)
   - [Revenue Model](#revenue-model)
   - [LEAF Pairs Model](#leaf-pairs-model)
   - [AEGIS Model](#aegis-model)
   - [OAK Distribution Model](#oak-distribution-model)
4. [Simulation Activation Dates](#simulation-activation-dates)
5. [Usage](#usage)
   - [Running Simulations](#running-simulations)
   - [Modifying Parameters](#modifying-parameters)
6. [Documentation](#documentation)
7. [Getting Started](#getting-started)
8. [Contributing](#contributing)
9. [License](#license)

---

## Introduction

CanopyDFF is built to support strategic business development and informed tokenomics decisions within the Canopy ecosystem. The toolkit provides comprehensive models that project Total Value Locked (TVL), revenue streams, liquidity pair dynamics, and token distribution mechanisms. By simulating various scenarios, CanopyDFF enables stakeholders to make data-driven decisions to foster sustainable growth and market confidence.

---

## Project Structure

```plaintext
CanopyDFF/
├── src/
│   ├── Functions/
│   │   ├── __init__.py
│   │   ├── TVL.py
│   │   ├── Revenue.py
│   │   ├── LEAFPairs.py
│   │   ├── AEGIS.py
│   │   └── OAK.py
│   ├── Simulations/
│   │   ├── __init__.py
│   │   └── simulate.py
│   └── __init__.py
├── Docs/
│   ├── TVL.md
│   ├── Revenue.md
│   ├── LEAFPairs.md
│   ├── AEGIS.md
│   └── OAK.md
├── Data/
│   ├── leaf_deal.py
│   └── __init__.py
├── Assumptions.md
├── Implementation_Order.md
├── run_simulation.py
├── README.md
└── .gitignore
```

---

## Components Overview

### TVL Model

The TVL Model (`src/Functions/TVL.py`) projects Total Value Locked growth for both the Move blockchain and Canopy. Key features include:

- **Growth Projections**:
  - Implements yearly growth rates with monthly compounding.
  - Handles multi-year projections with different growth rates per year.
  - Maintains the final year's growth rate for extended projections.

- **Market Share Dynamics**:
  - Models Canopy's market share using exponential decay.
  - Implements a minimum market share floor.
  - Accounts for competitive pressure through a decay rate.

- **Configuration Flexibility**:
  - Allows adjustments to initial TVL, growth rates, market share parameters, and projection duration.

### Revenue Model

The Revenue Model (`src/Functions/Revenue.py`) calculates projected revenues based on the TVL composition. It considers different revenue streams such as protocol-locked, contracted, organic, and boosted TVL.

- **Revenue Streams**:
  - **Protocol-Locked**: Revenue from locked protocols.
  - **Contracted**: Revenue from contractual agreements.
  - **Organic**: Revenue from organic growth.
  - **Boosted**: Additional revenue from boosted incentives.

- **Features**:
  - Configurable revenue rates for each TVL type.
  - Supports dynamic adjustments over time.

### LEAF Pairs Model

The LEAF Pairs Model (`src/Functions/LEAFPairs.py`) manages liquidity pairs involving LEAF tokens.

- **Liquidity Management**:
  - Handles the creation and dissolution of LEAF-based liquidity pools.
  - Tracks liquidity contributions and withdrawals.

- **Token Dynamics**:
  - Manages the distribution of LEAF tokens as incentives for liquidity providers.

### AEGIS Model

The AEGIS Model (`src/Functions/AEGIS.py`) manages LEAF and USDC balances, including redemptions.

- **Balance Management**:
  - Tracks LEAF and USDC balances over time.
  - Handles redemption requests and updates balances accordingly.

- **Redemption Mechanisms**:
  - Implements rules and constraints for token redemptions.
  - Ensures sustainable balance management.

### OAK Distribution Model

The OAK Distribution Model (`src/Functions/OAK.py`) manages OAK token distribution and redemption.

- **Token Distribution**:
  - Controls the release schedule of OAK tokens.
  - Manages redemption processes for participants.

- **Supply Management**:
  - Tracks remaining OAK supply.
  - Implements mechanisms to adjust distribution based on market conditions.

---

## Simulation Activation Dates

In the CanopyDFF simulation, various components are activated at specific months to mimic realistic deployment and growth scenarios. Staggering the activation dates allows for a more accurate representation of how each component impacts the overall ecosystem, both economically and in market parameters.

### Activation Months

```python
activation_months = {
    'LEAF_PAIRS_START_MONTH': 1,
    'AEGIS_START_MONTH': 3,
    'OAK_START_MONTH': 4,
    'MARKET_START_MONTH': 5,
    'PRICE_START_MONTH': 5,
    'DISTRIBUTION_START_MONTH': 5,
    'BOOST_START_MONTH': 6,
}
```

#### LEAF_PAIRS_START_MONTH: Month 1

- **Purpose**: Activates the LEAF Pairs Model, allowing participants to create liquidity pools with LEAF tokens.
- **Benefit**: Early activation encourages liquidity provision, facilitating market depth and stability for LEAF token trading from the beginning.

#### AEGIS_START_MONTH: Month 3

- **Purpose**: Launches the AEGIS Model, introducing mechanisms for LEAF and USDC balance management, along with redemption features.
- **Benefit**: Delaying AEGIS activation allows initial liquidity to build up, ensuring sufficient LEAF and USDC reserves for effective balance management and stabilization mechanisms.

#### OAK_START_MONTH: Month 4

- **Purpose**: Initiates the OAK Distribution Model, starting the distribution and redemption of OAK tokens.
- **Benefit**: Timing the OAK distribution after initial liquidity and balance mechanisms are in place ensures that the token distribution occurs in a more mature market environment, enhancing token value and utility.

#### MARKET_START_MONTH: Month 5

- **Purpose**: Simulates the activation of broader market interactions, enabling external trading and market forces to impact the ecosystem.
- **Benefit**: Introducing the market after foundational components are established allows the ecosystem to better absorb market volatility and participant behaviors, promoting stability.

#### PRICE_START_MONTH: Month 5

- **Purpose**: Activates dynamic pricing mechanisms for the LEAF token, allowing the price to fluctuate based on trading activity and liquidity.
- **Benefit**: Implementing price dynamics after the market is active ensures that price changes reflect real market conditions, improving the accuracy of economic modeling and projections.

#### DISTRIBUTION_START_MONTH: Month 5

- **Purpose**: Begins the distribution of rewards and incentives to participants, such as staking rewards or liquidity mining incentives.
- **Benefit**: Delaying distribution until the market and pricing mechanisms are active maximizes participant engagement and aligns incentives with market performance.

#### BOOST_START_MONTH: Month 6

- **Purpose**: Activates the BOOST functionality, enhancing the TVL and revenue models by incorporating boosted yields or incentives.
- **Benefit**: Introducing BOOST after other components are operational magnifies its impact, leveraging existing liquidity and market participation to amplify growth and revenue generation.

### Benefits of Staggered Activation

- **Controlled Ecosystem Growth**: Staggering components ensures that the ecosystem grows in a controlled manner, allowing each component to build upon the foundations laid by the previous ones.

- **Risk Mitigation**: Delaying certain functionalities reduces the risk of market shocks by ensuring that sufficient liquidity and stability mechanisms are in place before exposing the ecosystem to greater volatility.

- **Enhanced Market Confidence**: Gradual activation builds trust among participants, as they can observe the system's performance over time, leading to increased engagement and investment.

- **Optimized Resource Allocation**: Staggered deployment allows the development team to focus on each component's successful implementation and monitoring, ensuring high-quality performance and quick response to any issues.

---

## Usage

### Running Simulations

To run the simulation and generate projections:

1. **Navigate to the Project Directory**

    ```bash
    cd CanopyDFF
    ```

2. **Execute the Simulation Script**

    ```bash
    python3 run_simulation.py
    ```

3. **View Outputs**

    - The simulation will output plots and data to the console, illustrating the projected TVL, revenues, LEAF prices, and other key metrics over time.

### Modifying Parameters

#### Adjust Simulation Parameters

Modify the simulation parameters to test different scenarios. Parameters can be adjusted in `src/Simulations/simulate.py`.

##### Example

```python
tvl_config = TVLModelConfig(
    initial_move_tvl=800_000_000,         # $800M
    initial_canopy_tvl=350_000_000,       # $350M
    move_growth_rates=[1.5, 1, 0.75, 0.5, 0.4],  # Annual growth rates for 5 years
    min_market_share=0.10,                # 10%
    market_share_decay_rate=0.02,         # Decay rate
    max_months=60                         # Projection duration in months
)
```

#### Modifying Activation Dates

To adjust the activation months of various components, edit the `activation_months` dictionary in `src/Simulations/simulate.py`:

```python
activation_months = {
    'LEAF_PAIRS_START_MONTH': 1,
    'AEGIS_START_MONTH': 3,
    'OAK_START_MONTH': 4,
    'MARKET_START_MONTH': 5,
    'PRICE_START_MONTH': 5,
    'DISTRIBUTION_START_MONTH': 5,
    'BOOST_START_MONTH': 6,
}
```

**Impact of Changing Activation Dates**:

- **Earlier Activation**: Activating components earlier can simulate a more aggressive rollout strategy, potentially leading to faster ecosystem growth but may increase risk due to less mature infrastructure.

- **Later Activation**: Delaying activation can model a more conservative approach, allowing for greater stability and liquidity accumulation before introducing more complex mechanics.

- **Custom Scenarios**: Adjust activation dates to create custom scenarios that align with different strategic goals or market conditions.

#### Update Assumptions

Ensure that `Assumptions.md` aligns with your parameter changes for consistency and accurate documentation.

#### Re-run Simulations

After making changes, re-run the simulation to observe the impact of your adjustments.

---

## Documentation

Detailed documentation for each component is available in the `Docs/` directory:

- `Docs/TVL.md`
- `Docs/Revenue.md`
- `Docs/LEAFPairs.md`
- `Docs/AEGIS.md`
- `Docs/OAK.md`

These documents provide in-depth explanations, usage examples, and implementation details.

---

## Getting Started

Follow these steps to set up and run the CanopyDFF toolkit:

1. **Clone the Repository**

    ```bash
    git clone [repository-url]
    cd CanopyDFF
    ```

2. **Set Up Environment**

    Create and activate a Python virtual environment, then install dependencies:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Run Simulation**

    Execute the simulation script to generate projections and visualizations:

    ```bash
    python3 run_simulation.py
    ```

4. **Modify Parameters**

    - Open `src/Simulations/simulate.py` to adjust:
      - Initial TVL values.
      - Growth rates.
      - Market share parameters.
      - Activation months.
      - Simulation duration.

    - Update configurations for other models as necessary.

5. **Review Outputs**

    - View generated plots for TVL, revenue, cumulative revenue, and LEAF prices.
    - Analyze detailed tables outputted to the console for monthly metrics.

---

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository**

2. **Create a Feature Branch**

    ```bash
    git checkout -b feature/YourFeature
    ```

3. **Commit Your Changes**

    ```bash
    git commit -m "Add Your Feature"
    ```

4. **Push to Your Fork**

    ```bash
    git push origin feature/YourFeature
    ```

5. **Create a Pull Request**

Please ensure all contributions include:

- Appropriate tests.
- Updated documentation.
- Clear commit messages following best practices.

---

## License

This project is licensed under the [BSD-3-Clause](LICENSE) License.
