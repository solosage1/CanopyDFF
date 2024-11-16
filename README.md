# CanopyDFF Repository

## Overview

**CanopyDFF** is a comprehensive modeling toolkit designed to drive Canopy's business development and tokenomics decisions. The project currently implements a robust TVL (Total Value Locked) model with plans to expand to other components including OAK distribution, LEAF pairs liquidity, influenced TVL, and revenue projections.

## Table of Contents

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Components Overview](#components-overview)
   - [TVL Model](#tvl-model)
4. [Usage](#usage)
5. [Documentation](#documentation)
6. [Getting Started](#getting-started)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction

CanopyDFF is built to support strategic business development and informed tokenomics decisions within the Canopy ecosystem. The current implementation focuses on TVL modeling, providing robust projections for both Move blockchain and Canopy TVL growth.

## Project Structure

```plaintext
CanopyDFF/
├── src/
│   ├── Functions/
│   │   ├── __init__.py
│   │   └── TVL.py
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
├── Assumptions.md
├── run_simulation.py
├── README.md
└── .gitignore
```

## Components Overview

### TVL Model

The TVL Model (`src/Functions/TVL.py`) projects Total Value Locked growth for both Move blockchain and Canopy. Key features include:

- **Growth Projections**:
  - Implements yearly growth rates with monthly compounding
  - Handles multi-year projections with different growth rates per year
  - Maintains final year's growth rate for extended projections

- **Market Share Dynamics**:
  - Models Canopy's market share using exponential decay
  - Implements minimum market share floor
  - Accounts for competitive pressure through decay rate

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

## Usage

To run the TVL simulation:

1. Ensure you're in a Python virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the simulation:

    ```bash
    python3 run_simulation.py
    ```

The simulation will generate:

- A line plot showing Move and Canopy TVL over 60 months
- A detailed table of monthly TVL values

## Documentation

Key documentation files:

- **[Assumptions.md](./Assumptions.md)**: Detailed model assumptions and configurations
- **[TVL.md](./Docs/TVL.md)**: Technical specification for the TVL model
- **[Revenue.md](./Docs/Revenue.md)**: Technical specification for the Revenue model
- **[LEAFPairs.md](./Docs/LEAFPairs.md)**: Technical specification for the LEAF Pairs model
- **[AEGIS.md](./Docs/AEGIS.md)**: Technical specification for the AEGIS LP model
- **[OAK.md](./Docs/OAK.md)**: Technical specification for the OAK Distribution model
- **[src/Functions/TVL.py](./src/Functions/TVL.py)**: Implementation of the TVL model
- **[src/Simulations/simulate.py](./src/Simulations/simulate.py)**: Simulation and visualization code

## Getting Started

1. **Clone the Repository**

    ```bash
    git clone [repository-url]
    cd CanopyDFF
    ```

2. **Set Up Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Run Simulation**

    ```bash
    python3 run_simulation.py
    ```

4. **Modify Parameters**
    Edit `src/Simulations/simulate.py` to adjust:
    - Initial TVL values
    - Growth rates
    - Market share parameters
    - Simulation duration

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your fork
5. Create a Pull Request

Please ensure all contributions include:

- Appropriate tests
- Updated documentation
- Clear commit messages

## License

This project is licensed under the [BSD-3-Clause](LICENSE) License.

```
