# Monthly Simulation Loop Documentation

## Overview

The simulation operates on a month-by-month basis, meticulously tracking the interactions between the **AEGIS**, **LEAF Pairs**, **TVL (Total Value Locked)**, and **OAK token** systems. This comprehensive simulation framework is implemented in:

```python:src/Simulations/simulate.py
```

The simulation loop orchestrates the progression of each month, updating models, processing contributions, handling liquidity, and tracking key metrics to provide insightful projections into the ecosystem's dynamics.

## Monthly Update Sequence

Each month within the simulation undergoes a structured series of updates to ensure accurate modeling of the ecosystem's behavior. Below is a detailed, step-by-step breakdown of the simulation process for a given month:

1. **Start Month**

   - **Increment Month Counter & Calculate LEAF Price**

     ```python
     for month in range(1, simulation_months + 1):
         current_leaf_price = calculate_leaf_price(month, total_liquidity)
     ```

     - **Iteration:** The simulation iterates through each month, starting from month 1 up to the configured number of simulation months.
     - **LEAF Price Calculation:** The LEAF price is computed based on the current month and the total liquidity in the system. This price influences various aspects of the simulation, including token distributions and redemptions.

2. **TVL (Total Value Locked) Model Updates**

   - **Process TVL Contributions**

     ```python
     tvl_loader.process_month(month)
     
     # Get active deals for this month
     active_deals = set(deal.deal_id for deal in get_active_deals(deals, month))
     ```

     - **TVL Contributions Processing:** New TVL contributions for the current month are processed, ensuring that all financial inputs are accounted for.
     - **Active Deals Retrieval:** The simulation identifies and tracks active deals pertinent to the current month, which are essential for calculating liquidity and token distributions.

3. **Calculate Total Liquidity from LEAF Pairs**

   - **Determine Current Liquidity**

     ```python
     total_liquidity = leaf_pairs_model.get_usd_liquidity()
     ```

     - **Liquidity Calculation:** The total liquidity provided by LEAF Pairs is calculated in USD. This metric is crucial for assessing the health and stability of the ecosystem.

4. **Update LEAF Price Based on Liquidity**

   - **Recalculate LEAF Price**

     ```python
     current_leaf_price = calculate_leaf_price(month, total_liquidity)
     ```

     - **Dynamic Pricing:** Leveraging the updated liquidity, the LEAF price is recalculated to reflect current market dynamics. This adaptive pricing model ensures that token valuations remain realistic and responsive to changes in liquidity.

5. **LEAF Pairs Updates**

   - **Update Deals with New Price**

     ```python
     deal_deficits, total_leaf_needed = leaf_pairs_model.calculate_leaf_needed(current_leaf_price)
     ```

     - **Deficit Calculation:** The simulation determines the LEAF tokens required to meet the target percentages of active deals based on the newly calculated LEAF price.
     - **Liquidity Adjustment:** Identifies any deficits in LEAF tokens that need to be addressed to maintain optimal liquidity levels within the deals.

   - **Acquire LEAF from AEGIS if Necessary**

     ```python
     if total_leaf_needed > 0:
         leaf_sold, usdc_received = aegis_model.sell_leaf(total_leaf_needed, current_leaf_price)
         # Distribute the purchased LEAF to the deals
         leaf_pairs_model.distribute_purchased_leaf(leaf_sold, deal_deficits)
     ```

     - **LEAF Acquisition:** If additional LEAF tokens are required (`total_leaf_needed > 0`), the simulation initiates the sale of LEAF tokens from the AEGIS model.
     - **Distribution:** The acquired LEAF tokens are then distributed to the active deals to fulfill their liquidity needs, ensuring that all pairs remain well-funded and operational.

6. **Process Model Steps**

   - **Update AEGIS and LEAF Pairs Models**

     ```python
     aegis_model.step(month)
     leaf_pairs_model.step(month)
     ```

     - **AEGIS Model Update:** The AEGIS model updates its state, adjusting LEAF and USDC balances, and recalculates any price impacts resulting from recent transactions.
     - **LEAF Pairs Model Update:** Advances the state of LEAF Pairs, handling deal-specific logic such as updating deal statuses, managing liquidity pools, and ensuring compliance with distribution parameters.

7. **OAK Token Updates**

   - **Process Distributions and Redemptions**

     ```python
     oak_model.step(
         month,
         aegis_model.usdc_balance,
         aegis_model.leaf_balance,
         current_leaf_price,
         aegis_model
     )
     ```

     - **Token Distribution:** The OAK model handles the distribution of new OAK tokens based on the current state of the ecosystem and predefined distribution rules.
     - **Redemptions Processing:** Manages any OAK token redemptions, ensuring that the supply adjusts appropriately in response to user actions and market conditions.

8. **Track Monthly Metrics**

   - **Collect and Store Metrics**

     ```python
     metrics = track_liquidity_metrics(
         month=month,
         current_leaf_price=current_leaf_price,
         aegis_model=aegis_model,
         leaf_pairs_model=leaf_pairs_model,
         tvl_model=tvl_model,
         oak_model=oak_model,
         deals=deals,
         previous_state=previous_state
     )
     
     # Update metrics with active deals and current price
     metrics['active_deals'] = active_deals
     metrics['leaf_price'] = current_leaf_price
     metrics_history.append(metrics)
     ```

     - **Liquidity Metrics:** Aggregates and records metrics such as total LEAF and USDC liquidity, TVL breakdowns by category, OAK token metrics, and the Internal Rate of Return (IRR).
     - **Historical Tracking:** Appends the collected metrics to the `metrics_history` for longitudinal analysis and visualization, enabling the simulation to provide comprehensive insights over time.

9. **Calculate Monthly Revenue**

   - **Determine Revenue and Update Totals**

     ```python
     monthly_revenue = tvl_model.calculate_monthly_revenue(tvl_model.contributions, month)
     cumulative_revenue += sum(monthly_revenue.values())
     cumulative_revenue_values.append(cumulative_revenue)
     ```

     - **Revenue Calculation:** Computes the revenue generated from each TVL category for the current month, providing clarity on the financial performance of different segments.
     - **Cumulative Tracking:** Updates the total revenue accumulated over the simulation period, facilitating an understanding of long-term financial growth and sustainability.

10. **Print Monthly Summary**

    - **Display Revenue and System Status**

      ```python
      print_monthly_summary(month, monthly_revenue, cumulative_revenue)
      ```

      - **Console Output:** Generates a succinct summary of the month's financials, including both monthly and cumulative revenues across different categories, offering immediate visibility into the simulation's progression.

11. **End Month Processing**

    - **Record State Histories**

      ```python
      previous_state = metrics
      ```

      - **State Preservation:** Updates the `previous_state` with the current month's metrics to maintain data integrity and provide a reference point for future iterations, ensuring that historical data remains accurate and accessible.

## Core Components

1. **Initialization**
   - **Logging Setup:** Configures the logging system with log rotation, ensuring that only the latest three log files are retained to manage storage efficiently.
   - **TVL Contributions:** Loaded via `TVLLoader`, initializing various TVL categories to accurately represent financial inputs into the ecosystem.
   - **Model Initialization:** Sets up the AEGIS, LEAF Pairs, and OAK models with their respective configurations, establishing the foundational elements of the simulation.
   - **Metrics Tracking:** Initializes structures to track metrics and revenue over time, enabling comprehensive data collection and analysis.

2. **LEAF Price Model**
   - **Current Implementation:** Utilizes a placeholder price of \$1.00 for LEAF tokens, serving as a foundational assumption in the simulation.
   - **Future Plans:** Aims to implement a dynamic pricing model that reflects real-time market conditions, enhancing the simulation's accuracy and responsiveness.

3. **Liquidity Tracking**
   - **Function Definition:**

     ```python
     def track_liquidity_metrics(month, current_leaf_price, aegis_model, leaf_pairs_model, tvl_model, oak_model):
         # Get AEGIS state
         aegis_state = aegis_model.get_state()
         total_leaf = aegis_state['leaf_balance']
         total_usdc = aegis_state['usdc_balance']
         
         # Add LEAF pair balances
         active_deals = leaf_pairs_model.get_active_deals(month)
         for deal in active_deals:
             total_leaf += deal.leaf_balance
             total_usdc += deal.other_balance
             
         return {
             'month': month,
             'total_leaf': total_leaf,
             'total_usdc': total_usdc,
             'total_value': total_usdc + (total_leaf * current_leaf_price)
         }
     ```

     - **Liquidity Aggregation:** Summarizes total LEAF and USDC liquidity by combining balances from the AEGIS model and active LEAF Pairs.
     - **TVL Calculation:** Computes the Total Value Locked (TVL) by factoring in the current LEAF price, providing a comprehensive financial snapshot of the ecosystem.

## Visualization Components

1. **TVL Composition Plot**
   - **Details:**
     - Displays the breakdown of TVL across **Protocol-locked**, **Contracted**, **Organic**, and **Boosted** categories.
     - Values are visualized in billions of USD, offering a clear view of liquidity distribution.

2. **AEGIS Metrics**
   - **Details:**
     - Tracks LEAF and USDC balances over time, illustrating the growth or depletion of these reserves.
     - Shows the history of LEAF prices, highlighting trends and fluctuations within the simulation period.

3. **LEAF Pairs Activity**
   - **Details:**
     - Indicates the number of active LEAF pairs each month, reflecting the engagement and utilization of the LEAF token.
     - Visualizes the total liquidity provided by LEAF Pairs, emphasizing their role in the ecosystem's financial health.

4. **OAK Token Metrics**
   - **Details:**
     - Displays the allocation, distribution, and redemption of OAK tokens, tracking their circulation within the system.
     - Monitors monthly redemption amounts, providing insights into user behavior and token utility.

## Data Collection

1. **Metrics History**
   - **Includes:**
     - Monthly TVL by category, offering granular insights into different liquidity segments.
     - Total LEAF and USDC liquidity, capturing the overall financial reserves.
     - Current LEAF price, serving as a pivotal factor in financial calculations.
     - Total system value, representing the aggregate worth of the ecosystem.

2. **Revenue Tracking**
   - **Includes:**
     - Monthly revenue by TVL category, detailing the income generated from different liquidity sources.
     - Cumulative revenue over the simulation period, illustrating long-term financial growth.
     - Revenue figures are presented in millions of USD, ensuring clarity and scalability in financial reporting.

## Current Implementation Status

1. **Working Components**
   - **Monthly Update Sequence:** Robustly handles the cyclical process of updating models and processing data each month.
   - **Logging System with Rotation:** Efficiently manages log files, retaining only the most recent entries to optimize storage.
   - **Basic TVL Tracking:** Accurately monitors and records Total Value Locked across various categories.
   - **LEAF Pairs Liquidity Tracking:** Maintains detailed records of liquidity provided by LEAF Pairs, ensuring accurate financial modeling.
   - **AEGIS Balance Tracking:** Keeps precise tabs on LEAF and USDC balances within the AEGIS model.
   - **OAK Token Distribution/Redemption:** Effectively manages the allocation and redemption of OAK tokens, maintaining token supply integrity.
   - **Visualization of All Metrics:** Generates comprehensive plots and visualizations to present key metrics and trends.

2. **Pending Implementation**
   - **Dynamic LEAF Pricing Model:** Developing a responsive pricing mechanism that adjusts based on real-time market conditions.
   - **Market Impact on Liquidity:** Incorporating factors that account for external market influences on liquidity levels.
   - **Advanced TVL Growth Modeling:** Enhancing TVL projections with more sophisticated growth algorithms and scenarios.
   - **Revenue Rate Adjustments:** Adjusting revenue rates dynamically in response to evolving market and ecosystem conditions.
   - **Enhanced Error Handling and Recovery:** Implementing robust mechanisms to handle and recover from unexpected errors, ensuring simulation integrity.

## Output Format

1. **Console Output**
   - **Details:**
     - Provides monthly summaries of revenue, offering quick snapshots of financial performance.
     - Displays a final metrics summary upon simulation completion, encapsulating overall results.
     - Outputs system status updates, keeping users informed of the simulation's progression and any critical events.

2. **Visual Output**
   - **Details:**
     - **TVL Composition:** Visualizes how Total Value Locked is distributed across different categories over time.
     - **Revenue Trends:** Illustrates the trajectory of both monthly and cumulative revenues throughout the simulation.
     - **AEGIS Metrics:** Shows the evolution of LEAF and USDC balances, as well as LEAF price fluctuations.
     - **LEAF Pairs Activity:** Displays the number of active LEAF pairs and their associated liquidity contributions.
     - **OAK Token Status:** Monitors the distribution and redemption activities of OAK tokens.
     - **Monthly Redemptions:** Tracks the frequency and volume of OAK token redemptions each month.

3. **Logging Output**
   - **Details:**
     - **System Events:** Logs detailed events occurring within the simulation, providing a chronological record of activities.
     - **Error Tracking:** Captures and records any errors encountered, facilitating debugging and system reliability.
     - **Performance Metrics:** Monitors and logs the performance aspects of the simulation, ensuring efficiency and responsiveness.
     - **Log Management:** Logs are stored in rotating log files, maintaining only the recent history to optimize storage and retrieval.

## Future Enhancements Needed

- **Implementation of Dynamic LEAF Pricing:** Develop a pricing model that responds to market forces and liquidity changes in real-time.
- **Integration of Market Impact Calculations:** Incorporate external market factors that influence liquidity and token prices.
- **Advanced TVL Modeling:** Enhance TVL projections with more nuanced growth patterns and economic scenarios.
- **Revenue Rate Adjustments Based on Market Conditions:** Modify revenue generation rates in response to evolving ecosystem dynamics and market trends.
- **Enhanced Error Handling and Recovery Mechanisms:** Strengthen the simulation's resilience by implementing comprehensive error detection and recovery strategies.

## Additional Details from `simulate.py`

The `simulate.py` script is the backbone of the simulation, orchestrating the monthly update sequence and managing all core components. Below is an in-depth look at how the script aligns with and supports the documentation:

- **Logging Setup:**

  ```python
  def setup_logging():
      """Setup logging configuration with log rotation."""
      try:
          current_dir = os.getcwd()
          logs_dir = os.path.join(current_dir, 'logs')
          os.makedirs(logs_dir, exist_ok=True)
          
          # Clean up old logs first
          log_files = sorted(Path(logs_dir).glob('simulation_*.log'), 
                            key=lambda x: x.stat().st_mtime, reverse=True)
          for log_file in log_files[3:]:  # Keep only 3 most recent
              log_file.unlink()
          
          # Setup new log file
          log_file = os.path.join(logs_dir, f'simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
          
          # Simpler logging config
          logging.basicConfig(
              level=logging.DEBUG,
              format='%(message)s',  # Simplified format
              handlers=[
                  logging.FileHandler(log_file),
                  logging.StreamHandler()
              ],
              force=True  # Force reconfiguration
          )
          
          # Suppress matplotlib debug messages
          logging.getLogger('matplotlib').setLevel(logging.WARNING)
          
          return log_file
          
      except Exception as e:
          print(f"❌ Logging setup error: {e}")
          return None
  ```

  - **Functionality:** Configures the logging system to record simulation events, errors, and performance metrics. Ensures log files are rotated, maintaining only the most recent three to prevent storage overload.
  - **Error Handling:** Catches and reports any issues encountered during the logging setup, safeguarding against potential disruptions in the logging process.

- **Initialization of Models:**

  ```python
  def main():
      # Initialize models with proper configuration
      tvl_model = TVLModel(tvl_config)
      tvl_loader = initialize_tvl_contributions(tvl_model, simulation_config)
      
      aegis_config = AEGISConfig(
          initial_leaf_balance=config['initial_leaf_supply'],
          initial_usdc_balance=config['initial_usdc'],
          max_months=simulation_months,
          oak_to_usdc_rate=1.0,
          oak_to_leaf_rate=1.0
      )
      aegis_model = AEGISModel(aegis_config)
  
      leaf_pairs_config = LEAFPairsConfig()
      leaf_pairs_model = LEAFPairsModel(leaf_pairs_config, initialize_deals())
  
      oak_config = OAKDistributionConfig(deals=deals)
      oak_model = OAKModel(oak_config, aegis_model)
  
      # Initialize revenue model with TVL model
      revenue_config = RevenueModelConfig()
      revenue_model = RevenueModel(revenue_config, tvl_model)
  
      # Initialize metrics tracking
      metrics_history = []
      cumulative_revenue = 0.0
      cumulative_revenue_values = []
      current_leaf_price = 1.0  # Initialize LEAF price
      ...
  ```

  - **Model Configuration:** Sets up all necessary models (AEGIS, LEAF Pairs, OAK, Revenue) with their respective configurations, ensuring each component operates with the correct parameters.
  - **Dependency Management:** Establishes dependencies between models, such as passing the AEGIS model instance to the OAK model, facilitating coordinated updates and interactions.

- **Main Simulation Loop:**

  ```python
  for month in range(1, simulation_months + 1):
      # Process TVL first
      tvl_loader.process_month(month)
      
      # Get active deals for this month
      active_deals = set(deal.deal_id for deal in get_active_deals(deals, month))
      
      # Calculate total liquidity from LEAF pairs
      total_liquidity = leaf_pairs_model.get_usd_liquidity()
      
      # Update LEAF price based on liquidity
      current_leaf_price = calculate_leaf_price(month, total_liquidity)
      
      # Update LEAF pairs with new price
      deal_deficits, total_leaf_needed = leaf_pairs_model.calculate_leaf_needed(current_leaf_price)
      
      # If LEAF pairs need LEAF, get it from AEGIS
      if total_leaf_needed > 0:
          leaf_sold, usdc_received = aegis_model.sell_leaf(total_leaf_needed, current_leaf_price)
          # Distribute the purchased LEAF to the deals
          leaf_pairs_model.distribute_purchased_leaf(leaf_sold, deal_deficits)
      
      # Process model steps
      aegis_model.step(month)
      leaf_pairs_model.step(month)
      
      # Process OAK updates
      oak_model.step(
          month,
          aegis_model.usdc_balance,
          aegis_model.leaf_balance,
          current_leaf_price,
          aegis_model
      )
      
      # Get metrics
      metrics = track_liquidity_metrics(
          month=month,
          current_leaf_price=current_leaf_price,
          aegis_model=aegis_model,
          leaf_pairs_model=leaf_pairs_model,
          tvl_model=tvl_model,
          oak_model=oak_model,
          deals=deals,
          previous_state=previous_state
      )
      
      # Update metrics with active deals and current price
      metrics['active_deals'] = active_deals
      metrics['leaf_price'] = current_leaf_price
      metrics_history.append(metrics)
      
      # Calculate revenue
      monthly_revenue = tvl_model.calculate_monthly_revenue(tvl_model.contributions, month)
      cumulative_revenue += sum(monthly_revenue.values())
      cumulative_revenue_values.append(cumulative_revenue)
      
      print_monthly_summary(month, monthly_revenue, cumulative_revenue)
      
      # Update previous state
      previous_state = metrics
  ```

  - **Sequential Processing:** Ensures that each step of the simulation is executed in the correct order, maintaining data integrity and logical consistency.
  - **Model Interactions:** Facilitates interactions between different models (e.g., LEAF Pairs and AEGIS) to reflect the interconnected nature of the ecosystem.
  - **Metrics Collection:** Continuously gathers and updates metrics, enabling real-time tracking and post-simulation analysis.

- **Plotting Results:**

  ```python
  plot_simulation_results(
      months=list(range(1, simulation_months + 1)),
      metrics_history=metrics_history,
      cumulative_revenue_values=cumulative_revenue_values,
      aegis_model=aegis_model,
      oak_model=oak_model
  )
  ```

  - **Visualization Execution:** Calls the plotting function to generate comprehensive visual representations of the simulation's outcomes, facilitating easier interpretation and analysis of the data.

## Conclusion

This updated documentation provides an exhaustive overview of the simulation's monthly processing logic, intricately aligned with the current implementation in `simulate.py`. By detailing each step and elucidating the interactions between various models, the documentation offers a clear and thorough understanding of how the simulation operates. The integration of comprehensive logging, dynamic pricing, and robust metrics tracking ensures that the simulation not only models the ecosystem accurately but also provides valuable insights into its potential future states.