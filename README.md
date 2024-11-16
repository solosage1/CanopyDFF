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
4. [Usage](#usage)
   - [Running Simulations](#running-simulations)
   - [Modifying Parameters](#modifying-parameters)
5. [Documentation](#documentation)
6. [Getting Started](#getting-started)
7. [Contributing](#contributing)
8. [License](#license)

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

    ```python
    TVLModelConfig(
        initial_move_tvl=800_000_000,    # $800M
        initial_canopy_tvl=350_000_000,  # $350M
        move_growth_rates=[1.5, 1, 0.75, 0.5, 0.4],
        min_market_share=0.10,
        market_share_decay_rate=0.02,
        initial_boost_share=0.10,
        boost_growth_rate=1.0
    )
    ```

### Revenue Model

The Revenue Model (`src/Functions/Revenue.py`) projects revenue based on the composition of TVL. Key features include:

- **Revenue Calculations**:
  - Differentiates between volatile and stable revenue streams.
  - Adjusts revenue rates over time based on growth parameters.

- **Dynamic Share Management**:
  - Adjusts the volatile share of TVL dynamically to reach target shares over a specified duration.

- **Configuration Flexibility**:

    ```python
    RevenueModelConfig(
        initial_volatile_share=0.10,     # 10% volatile at start
        target_volatile_share=0.20,      # Target 20% volatile share
        volatile_share_growth=0.02,      # Growth rate for volatile TVL share
        initial_volatile_rate=0.05,      # 5% annual revenue rate for volatile
        target_volatile_rate=0.02,       # 2% annual revenue rate for volatile
        initial_stable_rate=0.01,        # 1% annual revenue rate for stable
        target_stable_rate=0.005,        # 0.5% annual revenue rate for stable
        share_growth_duration=24         # Duration over which shares and rates change (in months)
    )
    ```

### LEAF Pairs Model

The LEAF Pairs Model (`src/Functions/LEAFPairs.py`) manages liquidity pairs involving LEAF tokens. Key features include:

- **Deal Management**:
  - Initializes and manages multiple LEAF pairing deals.
  - Tracks LEAF and counter asset balances over time.

- **Liquidity Calculation**:
  - Calculates total liquidity contributed by active LEAF pairs based on LEAF prices.

- **Configuration Flexibility**:

    ```python
    LEAFPairsConfig(
        # Define configurations as needed
    )
    ```

### AEGIS Model

The AEGIS Model (`src/Functions/AEGIS.py`) manages LEAF and USDC balances and redemptions. It handles:

- **Balance Tracking**:
  - Monitors LEAF and USDC balances for liquidity providers.

- **Redemption Mechanics**:
  - Implements redemption processes based on predefined rules and market conditions.

- **Integration with Other Models**:
  - Coordinates with TVL and Revenue models to reflect changes in balances and revenues.

### OAK Distribution Model

The OAK Distribution Model (`src/Functions/OAK.py`) manages OAK token distribution and redemption. Key features include:

- **Token Distribution**:
  - Implements mechanisms for distributing OAK tokens to stakeholders.

- **Redemption Processes**:
  - Allows users to redeem OAK tokens for underlying assets based on specific rules.

- **Supply Management**:
  - Tracks total OAK supply and ensures distributions do not exceed predefined caps.

---

## Usage

### Running Simulations

To run the comprehensive simulation encompassing all models:

1. **Activate Python Virtual Environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install Required Packages**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Simulation**:

    ```bash
    python3 run_simulation.py
    ```

    The simulation will execute the TVL, Revenue, LEAF Pairs, AEGIS, and OAK models over a 60-month period, generating comprehensive visualizations and detailed tables of key metrics.

### Modifying Parameters

To customize simulation parameters:

1. **Edit Configuration**:

    Open `src/Simulations/simulate.py` and adjust the configurations for each model as needed. For example:

    ```python
    tvl_config = TVLModelConfig(
        initial_move_tvl=800_000_000,         # $800M
        initial_canopy_tvl=350_000_000,       # $350M
        move_growth_rates=[1.5, 1, 0.75, 0.5, 0.4],  # Annual growth rates for 5 years
        min_market_share=0.10,                # 10%
        market_share_decay_rate=0.02,         # Decay rate
        initial_boost_share=0.10,             # 10%
        boost_growth_rate=1.0                 # Growth rate for boost
    )
    ```

2. **Adjust Activation Months**:

    Define or modify the activation months for various components:

    ```python
    activation_months = {
        'LEAF_PAIRS_START_MONTH': 1,
        'AEGIS_START_MONTH': 3,
        'OAK_START_MONTH': 4,
        'MARKET_START_MONTH': 5,
        'PRICE_START_MONTH': 5,
        'DISTRIBUTION_START_MONTH': 5,
    }
    ```

3. **Update Assumptions**:

    Ensure that `Assumptions.md` aligns with your parameter changes for consistency and accurate documentation.

4. **Re-run Simulations**:

    After making changes, re-run the simulation to observe the impact of your adjustments.

---

## Documentation

Comprehensive documentation is available to provide detailed insights into each model and component:

- **[Assumptions.md](./Assumptions.md)**: Detailed model assumptions and configurations.
- **[TVL.md](./Docs/TVL.md)**: Technical specification for the TVL model.
- **[Revenue.md](./Docs/Revenue.md)**: Technical specification for the Revenue model.
- **[LEAFPairs.md](./Docs/LEAFPairs.md)**: Technical specification for the LEAF Pairs model.
- **[AEGIS.md](./Docs/AEGIS.md)**: Technical specification for the AEGIS LP model.
- **[OAK.md](./Docs/OAK.md)**: Technical specification for the OAK Distribution model.
- **[src/Functions/TVL.py](./src/Functions/TVL.py)**: Implementation of the TVL model.
- **[src/Functions/Revenue.py](./src/Functions/Revenue.py)**: Implementation of the Revenue model.
- **[src/Functions/LEAFPairs.py](./src/Functions/LEAFPairs.py)**: Implementation of the LEAF Pairs model.
- **[src/Functions/AEGIS.py](./src/Functions/AEGIS.py)**: Implementation of the AEGIS model.
- **[src/Functions/OAK.py](./src/Functions/OAK.py)**: Implementation of the OAK Distribution model.
- **[src/Simulations/simulate.py](./src/Simulations/simulate.py)**: Simulation and visualization code.

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
