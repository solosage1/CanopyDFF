# CanopyDFF Repository

## Overview

**CanopyDFF** is a comprehensive modeling toolkit designed to drive Canopy's business development and tokenomics decisions. The project encompasses several interconnected models that manage the distribution and redemption of OAK tokens, the dynamics of LEAF pairs liquidity, influenced TVL (Total Value Locked), and revenue projections. These models collectively ensure the economic stability, scalability, and fairness within the Canopy ecosystem.

## Table of Contents

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Components Overview](#components-overview)
   - [OAK Distribution Model](#oak-distribution-model)
   - [LEAF Pairs Model](#leaf-pairs-model)
   - [Influenced TVL Model](#influenced-tvl-model)
   - [Revenue Model](#revenue-model)
4. [Interaction Between Components](#interaction-between-components)
5. [Assumptions](#assumptions)
6. [Usage](#usage)
7. [Documentation](#documentation)
8. [Getting Started](#getting-started)
9. [Contributing](#contributing)
10. [License](#license)

## Introduction

CanopyDFF is built to support strategic business development and informed tokenomics decisions within the Canopy ecosystem. By leveraging robust financial models, the project ensures an efficient and fair distribution of OAK tokens, maintains liquidity through LEAF pairs, projects and manages TVL, and forecasts revenue streams. These models are designed to be flexible, scalable, and aligned with evolving market dynamics.

## Project Structure

```

CanopyDFF/
├── Functions/
│   ├── LEAFPairs.md
│   ├── OAK.md
│   ├── LEAFPrice.md
│   ├── OAKPrice.md
│   ├── TVL.md
│   ├── TVLGrowth.md
│   └── TVLGrowth.md
├── Asssumptions.md
├── README.md
├── .gitignore
└── README_content/
```

- **Functions/**: Contains detailed specifications and implementations of various models.
- **Asssumptions.md**: Outlines the foundational assumptions and settings for all models.
- **README.md**: This document.
- **.gitignore**: Specifies intentionally untracked files to ignore.

## Components Overview

### OAK Distribution Model

The [OAK Distribution Model](./Functions/OAK.md) manages the distribution and redemption of OAK tokens. Key functionalities include:

- **Deal Management**: Tracks multiple distribution deals, each with their own OAK allocation, vesting periods, and IRR (Internal Rate of Return) thresholds.
- **Redemption Mechanics**: Implements a dual exponential decay function to determine partial and full redemptions based on risk-adjusted IRR.
- **Supply Tracking**: Monitors the total OAK supply, adjusting for redemptions and ensuring economic stability.
- **Best Case IRR Calculation**: Estimates potential returns for AEGIS LP holders under current conditions.

### LEAF Pairs Model

The [LEAF Pairs Model](./Functions/LEAFPairs.md) manages liquidity pairs involving LEAF tokens. It handles:

- **Liquidity Management**: Adds, maintains, and retrieves liquidity pair metrics and historical balances.
- **Fee Calculations**: Integrates fee structures for transactional costs related to LEAF trading.
- **Reporting**: Provides detailed reports and visualizations of liquidity pair performance.

### Influenced TVL Model

The [Influenced TVL Model](./Functions/TVL.md) projects the Total Value Locked (TVL) influenced by the Canopy ecosystem. It includes:

- **Growth Projections**: Uses exponential and sigmoid functions to model TVL growth and market share decay.
- **Market Share Dynamics**: Simulates the Canopy's market share evolution in the Move blockchain ecosystem.
- **Integration**: Links with other models to align TVL with OAK distribution and revenue projections.

### Revenue Model

The [Revenue Model](./Functions/Revenue.md) forecasts revenue streams based on TVL and other economic indicators. Features include:

- **Revenue Calculation**: Models revenue using both volatile and stable TVL components with exponential decay.
- **Growth and Decay Parameters**: Adjusts revenue rates and TVL shares over time to reflect market stability and growth.
- **Extensions**: Incorporates scenarios like market shocks, competitive pressures, and risk-adjusted revenue streams.

## Interaction Between Components

All components within CanopyDFF interact to provide a cohesive modeling framework:

- **OAK Distribution & TVL Model**: The OAK Distribution Model relies on TVL projections to determine redemption mechanics and IRR thresholds.
- **LEAF Pairs & TVL Model**: Liquidity pairs managed by the LEAF Pairs Model directly influence the TVL dynamics.
- **Revenue Model**: Revenue projections depend on the TVL model and indirectly affect OAK supply through redemptions and tokenomics adjustments.

This interlinked structure ensures that changes in one component automatically reflect across the system, enabling dynamic and responsive tokenomics strategies.

## Assumptions

The [Asssumptions Document](./Asssumptions.md) details the starting conditions and recommended settings for each model, covering:

- **Token Supply**: Total minting caps for OAK and LEAF tokens.
- **Distribution Deals**: Breakdown of OAK allocation, lock periods, and IRR expectations.
- **TVL Projections**: Initial values, growth rates, and market share dynamics.
- **Revenue Parameters**: Initial and target revenue rates, growth and decay parameters.

These assumptions are critical for ensuring consistency and reliability across all models.

## Usage

To leverage CanopyDFF for driving Canopy's business development and tokenomics, follow these steps:

1. **Review Assumptions**: Understand the foundational assumptions in [Asssumptions.md](./Asssumptions.md).
2. **Explore Models**: Dive into each model's documentation within the [Functions](./Functions/) directory to understand their implementations.
3. **Run Models**: Utilize the provided Python implementations to simulate token distributions, TVL projections, and revenue forecasts.
4. **Analyze Outputs**: Use the reporting capabilities within each model to inform strategic decisions and tokenomics adjustments.

## Documentation

For detailed information and specific implementations, refer to the following documents:

- **[Asssumptions.md](./Asssumptions.md)**: Foundational assumptions and settings.
- **[OAK Distribution Model](./Functions/OAK.md)**: Details on OAK token distribution and redemption mechanics.
- **[LEAF Pairs Model](./Functions/LEAFPairs.md)**: Specifications for managing LEAF liquidity pairs.
- **[TVL Model](./Functions/TVL.md)**: Framework for projecting influenced Total Value Locked.
- **[LEAFPrice.md](./Functions/LEAFPrice.md)**: Placeholder for LEAF price calculations.
- **[OAKPrice.md](./Functions/OAKPrice.md)**: Placeholder for OAK price calculations.
- **[TVLGrowth.md](./Functions/TVLGrowth.md)**: Placeholder for incremental TVL growth calculations.

Each document provides comprehensive details, including model definitions, implementation nuances, sample usage code, and recommendations for extensions and enhancements.

## Getting Started

To get started with CanopyDFF:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/solosage1/CanopyDFF.git
   cd CanopyDFF
   ```

2. **Install Dependencies**

   Ensure you have Python 3.8+ installed. Install any required packages (if applicable).

   ```bash
   pip install -r requirements.txt
   ```

3. **Review Models**

   Browse through the [Functions](./Functions/) folder to understand each model's specifications and implementations.

4. **Run Sample Usage**

   Execute sample scripts provided in each model's documentation to see the models in action.

   ```bash
   python Functions/OAK.md
   ```

   *(Note: Adjust the command based on actual executable scripts if present.)*

5. **Modify and Extend**

   Customize models as per your requirements, adjusting parameters in the Asssumptions and model configurations.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Push to your fork and create a pull request detailing your changes.

Please ensure that any new features or bugfixes are accompanied by relevant tests and documentation updates.

## License

This project is licensed under the [BSD-3-Clause](LICENSE) License.
