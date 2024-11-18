import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.Revenue import RevenueModel, RevenueModelConfig
from src.Functions.TVLContributions import TVLContributionHistory
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Data.leaf_deal import initialize_deals
from typing import Dict, List
from src.Functions.AEGIS import AEGISConfig, AEGISModel
import numpy as np  # type: ignore
from src.Functions.OAK import OAKDistributionConfig, OAKModel
from src.Data.oak_deals import get_oak_distribution_deals
from src.Functions.LeafPrice import LEAFPriceModel, LEAFPriceConfig

def calculate_leaf_price(month: int, total_liquidity: float) -> float:
    """
    Placeholder function to calculate LEAF price.
    """
    # Implement your LEAF price model here.
    return 1.0  # Placeholder value

def initialize_tvl_contributions(tvl_model: TVLModel, config: Dict) -> None:
    """Initialize all TVL contributions based on simulation config."""
    # Load initial contributions from data file
    tvl_model.loader.load_initial_contributions()

def print_monthly_summary(month: int, monthly_revenue: Dict[str, float], cumulative_revenue: float) -> None:
    """Print a summary of monthly revenue by TVL type."""
    # Convert to millions for display
    print(f"{month:3d}    {monthly_revenue['ProtocolLocked']/1e6:12.2f} {monthly_revenue['Contracted']/1e6:12.2f} "
          f"{monthly_revenue['Organic']/1e6:12.2f} {monthly_revenue['Boosted']/1e6:12.2f} "
          f"{sum(monthly_revenue.values())/1e6:15.2f} {cumulative_revenue/1e6:20.2f}")

def plot_aegis_data(months: List[int], aegis_model: AEGISModel):
    """Plot AEGIS model data."""
    plt.figure(figsize=(10, 6))

    # LEAF Price Over Time
    plt.subplot(2, 1, 1)
    plt.plot(months, aegis_model.leaf_price_history, label='LEAF Price')
    plt.title('LEAF Price Over Time (AEGIS Model)')
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.legend()

    # Balances Over Time
    plt.subplot(2, 1, 2)
    leaf_balance_millions = [b/1e6 for b in aegis_model.leaf_balance_history]
    usdc_balance_millions = [b/1e6 for b in aegis_model.usdc_balance_history]
    plt.plot(months, leaf_balance_millions, label='LEAF Balance')
    plt.plot(months, usdc_balance_millions, label='USDC Balance')
    plt.title('AEGIS Balances Over Time')
    plt.xlabel('Month')
    plt.ylabel('Balance (Millions USD)')
    plt.legend()

    plt.tight_layout()
    plt.show()

def track_liquidity_metrics(
    month: int,
    price: float,
    aegis_model: AEGISModel,
    leaf_pairs_model: LEAFPairsModel
) -> Dict:
    """Track liquidity metrics based on AEGIS and LEAF Pairs models."""
    # Get AEGIS liquidity within 10% of price
    aegis_leaf, aegis_usdc = aegis_model.get_liquidity_within_percentage(10, price)
    
    # Get LEAFPairs liquidity within 10% of price
    leaf_pairs_leaf = 0
    leaf_pairs_other = 0
    active_deals = leaf_pairs_model.get_active_deals(month)
    
    # Get total liquidity across all active deals
    if active_deals:  # Only process if there are active deals
        leaf, other = leaf_pairs_model.get_liquidity_within_percentage(10, price)
        leaf_pairs_leaf += leaf
        leaf_pairs_other += other
    
    total_leaf = aegis_leaf + leaf_pairs_leaf
    total_usdc = aegis_usdc + leaf_pairs_other
    
    return {
        'month': month,
        'total_leaf': total_leaf,
        'total_usdc': total_usdc
    }

def plot_liquidity_metrics(metrics_history: List[Dict]):
    """Plot liquidity metrics over time."""
    months = [metric['month'] for metric in metrics_history]
    total_leaf = [metric['total_leaf'] for metric in metrics_history]
    total_usdc = [metric['total_usdc'] for metric in metrics_history]

    plt.figure(figsize=(12, 6))
    plt.plot(months, total_leaf, label='Total LEAF Liquidity')
    plt.plot(months, total_usdc, label='Total USDC Liquidity')
    plt.title('Liquidity Metrics Over Time')
    plt.xlabel('Month')
    plt.ylabel('Liquidity')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_oak_distributions(oak_states: List[Dict]):
    """Plot OAK distribution metrics."""
    plt.figure(figsize=(15, 10))
    
    # OAK Supply Over Time
    plt.subplot(2, 2, 1)
    months = list(range(len(oak_states)))
    supplies = [state['remaining_oak_supply']/1e6 for state in oak_states]
    plt.plot(months, supplies)
    plt.title('Remaining OAK Supply')
    plt.xlabel('Month')
    plt.ylabel('OAK Tokens (Millions)')
    plt.grid(True)
    
    # Monthly Redemptions
    plt.subplot(2, 2, 2)
    monthly_redemptions = []
    for month in months:
        total = sum(oak_states[month]['redemption_history'].get(month, {}).values())/1e6
        monthly_redemptions.append(total)
    plt.bar(months, monthly_redemptions)
    plt.title('Monthly OAK Redemptions')
    plt.xlabel('Month')
    plt.ylabel('OAK Tokens Redeemed (Millions)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def simulate_months(months: int):
    """
    Placeholder function for simulating OAK distributions and redemptions.
    """
    # This function can be expanded based on specific simulation requirements.
    pass  # Implement simulation logic as needed

def estimate_leaf_price(
    leaf_price_model: LEAFPriceModel,
    current_price: float,
    leaf_liquidity: float,
    usd_liquidity: float,
    trade_amount_usd: float = 0.0
) -> float:
    """
    Helper function to estimate LEAF price using the LEAFPriceModel.
    
    Args:
        leaf_price_model: Initialized LEAFPriceModel instance
        current_price: Current LEAF token price
        leaf_liquidity: Amount of LEAF tokens available within 10% of current price
        usd_liquidity: USD value of paired liquidity within 10% of current price
        trade_amount_usd: USD value of LEAF to be bought (positive) or sold (negative)
    
    Returns:
        float: Estimated LEAF price
    """
    return leaf_price_model.get_leaf_price(
        current_price=current_price,
        leaf_liquidity=leaf_liquidity,
        usd_liquidity=usd_liquidity,
        trade_amount_usd=trade_amount_usd
    )

def main():
    # Initialize configuration
    config = {
        'initial_move_tvl': 1_000_000_000,
        'initial_canopy_tvl': 500_000_000,
        'move_growth_rates': [0.10, 0.08, 0.06],
        'min_market_share': 0.05,
        'market_share_decay_rate': 0.01,
        'max_months': 60
    }

    # Activation months for different features
    activation_months = {
        'LEAF_PAIRS_START_MONTH': 1,
        'BOOST_START_MONTH': 6,
        'AEGIS_START_MONTH': 3,
        'OAK_START_MONTH': 4,
        'MARKET_START_MONTH': 5,
        'PRICE_START_MONTH': 5,
        'DISTRIBUTION_START_MONTH': 5
    }

    # Initialize models
    tvl_model = TVLModel(TVLModelConfig(**config))
    revenue_model = RevenueModel(RevenueModelConfig(), tvl_model=tvl_model)
    leaf_pairs_model = LEAFPairsModel(LEAFPairsConfig(), initialize_deals())
    
    # Initialize AEGIS model
    aegis_config = AEGISConfig(
        initial_leaf_balance=1_000_000_000,
        initial_usdc_balance=500_000,
        leaf_price_decay_rate=0.005,
        max_months=config['max_months']
    )
    aegis_model = AEGISModel(aegis_config)

    # Initialize OAK model with redemption period parameters
    oak_config = OAKDistributionConfig(
        total_oak_supply=500_000,
        redemption_start_month=12,  # When redemptions can begin
        redemption_end_month=48,    # When max redemptions are allowed
        deals=get_oak_distribution_deals()
    )
    oak_model = OAKModel(oak_config)
    oak_states = []

    # Initialize history arrays with correct length
    aegis_model.leaf_balance_history = [aegis_config.initial_leaf_balance] * config['max_months']
    aegis_model.usdc_balance_history = [aegis_config.initial_usdc_balance] * config['max_months']
    aegis_model.leaf_price_history = [1.0] * config['max_months']

    # Initialize contributions from data file
    initialize_tvl_contributions(tvl_model, config)

    # Tracking variables
    months = list(range(config['max_months']))
    total_tvl_by_month = []
    revenue_by_month = []
    cumulative_revenues = []
    leaf_prices = [1.0] * config['max_months']  # Initialize with correct length
    metrics_history = []
    history_tracker = TVLContributionHistory()

    # Print header
    print("Month          Protocol     Contracted        Organic        Boosted       Total Rev (M)       Cumulative Rev (M)")
    print("-" * 113)

    # Initialize LEAF price model
    leaf_price_config = LEAFPriceConfig(
        min_price=0.01,
        max_price=100.0,
        price_impact_threshold=0.10
    )
    leaf_price_model = LEAFPriceModel(leaf_price_config)
    leaf_price_model.initialize_price(initial_price=1.0)
    current_leaf_price = 1.0  # Starting price

    # Simulation loop
    for month in months:
        print(f"\n--- Month {month + 1} ---")
        
        # Record state before updates - use contributions directly
        history_tracker.record_state(month, tvl_model.contributions)
        
        # Update TVL
        tvl_model.step()
        total_tvl = tvl_model.get_total_tvl()
        total_tvl_by_month.append(total_tvl)
        
        # Calculate revenue
        monthly_revenue = revenue_model.calculate_revenue(month)
        revenue_by_month.append(monthly_revenue)
        cumulative_revenues.append(revenue_model.cumulative_revenue)
        
        # Update OAK if active
        if month >= activation_months['OAK_START_MONTH']:
            # Get current AEGIS holdings and LEAF price
            aegis_usdc = aegis_model.usdc_balance_history[month]
            aegis_leaf = aegis_model.leaf_balance_history[month]
            current_leaf_price = leaf_price_model.get_current_price(month)
            
            # Process OAK redemptions with updated IRR calculation
            oak_redemption, supply_before, supply_after, usdc_redemption, leaf_redemption = oak_model.step(
                current_month=month,
                aegis_usdc=aegis_usdc,
                aegis_leaf=aegis_leaf,
                current_leaf_price=current_leaf_price
            )
            
            # Update AEGIS balances based on redemptions
            aegis_model.update_balances(
                usdc_change=-usdc_redemption,
                leaf_change=-leaf_redemption
            )
            
            oak_states.append(oak_model.get_state())
            
            if oak_redemption > 0:
                print(f"OAK Redemptions: {oak_redemption:,.2f} OAK")
                print(f"USDC Redeemed: {usdc_redemption:,.2f}")
                print(f"LEAF Redeemed: {leaf_redemption:,.2f}")
                print(f"LEAF Price: ${current_leaf_price:.2f}")
                print(f"Total Value Redeemed: ${(usdc_redemption + leaf_redemption * current_leaf_price):,.2f}")
        
        # Update AEGIS if active
        if month >= activation_months['AEGIS_START_MONTH']:
            # Get OAK redemptions from the previous step
            if oak_states:
                last_state = oak_states[-1]
                oak_redemption_amount = last_state.get('redemption_amount', 0)
            else:
                oak_redemption_amount = 0

            redemption_rate = oak_redemption_amount / oak_config.total_oak_supply if oak_config.total_oak_supply > 0 else 0
            
            # Handle redemptions with calculated rate
            aegis_model.handle_redemptions(month, redemption_rate)
            aegis_model.step(month)
        
        # Update LEAF pairs if active
        if month >= activation_months['LEAF_PAIRS_START_MONTH']:
            leaf_pairs_model.update_deals(month, current_leaf_price)
        
        # Update LEAF price if active
        if month >= activation_months['PRICE_START_MONTH']:
            # Collect total trade amounts impacting LEAF price in this month
            # For this example, we'll simulate trade amounts (this should come from actual trade data)
            simulated_trades = [10_000, -5_000, 15_000]  # Example trades in USD

            for trade_amount_usd in simulated_trades:
                # Get current liquidity metrics
                metrics = track_liquidity_metrics(month, current_leaf_price, aegis_model, leaf_pairs_model)
                total_leaf_liquidity = metrics['total_leaf']
                total_usdc_liquidity = metrics['total_usdc']

                # Update LEAF price based on trade
                try:
                    new_price = leaf_price_model.update_price(
                        month=month,
                        leaf_liquidity=total_leaf_liquidity,
                        usd_liquidity=total_usdc_liquidity,
                        trade_amount_usd=trade_amount_usd
                    )
                    current_leaf_price = new_price
                except ValueError as e:
                    print(f"Trade of {trade_amount_usd} USD could not be executed: {e}")

            # Finalize the month's LEAF price
            leaf_price_model.finalize_month_price(month)
        else:
            # LEAF price remains at initial price before PRICE_START_MONTH
            current_leaf_price = leaf_price_model.get_current_price(month)
        
        # Update AEGIS history
        aegis_model.leaf_balance_history[month] = aegis_model.leaf_balance
        aegis_model.usdc_balance_history[month] = aegis_model.usdc_balance
        
        # Track metrics
        metrics = track_liquidity_metrics(month, current_leaf_price, aegis_model, leaf_pairs_model)
        metrics_history.append(metrics)
        
        # Track LEAF price
        leaf_prices[month] = current_leaf_price
        
        # Print monthly summary
        print_monthly_summary(month, monthly_revenue, revenue_model.cumulative_revenue)

        if month % 12 == 0:  # Log every 12 months
            print(f"LEAF Price at month {month}: ${current_leaf_price:.4f}")

    # After simulation loop, create all visualizations

    # Plotting TVL Over Time
    plt.figure(figsize=(15, 10))
    
    # Original TVL Plot
    plt.subplot(3, 2, 1)
    tvl_billions = [tvl/1e9 for tvl in total_tvl_by_month]
    plt.plot(months, tvl_billions)
    plt.title('Total TVL Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (Billions USD)')
    plt.grid(True)

    # Original Revenue Plot
    plt.subplot(3, 2, 2)
    protocol_locked = [rev['ProtocolLocked']/1e6 for rev in revenue_by_month]
    contracted = [rev['Contracted']/1e6 for rev in revenue_by_month]
    organic = [rev['Organic']/1e6 for rev in revenue_by_month]
    boosted = [rev['Boosted']/1e6 for rev in revenue_by_month]
    
    plt.plot(months, protocol_locked, label='Protocol Locked')
    plt.plot(months, contracted, label='Contracted')
    plt.plot(months, organic, label='Organic')
    plt.plot(months, boosted, label='Boosted')
    plt.title('Monthly Revenue by Type')
    plt.xlabel('Month')
    plt.ylabel('Revenue (Millions USD)')
    plt.legend()
    plt.grid(True)

    # Original Cumulative Revenue Plot
    plt.subplot(3, 2, 3)
    cumulative_millions = [rev/1e6 for rev in cumulative_revenues]
    plt.plot(months, cumulative_millions)
    plt.title('Cumulative Revenue')
    plt.xlabel('Month')
    plt.ylabel('Revenue (Millions USD)')
    plt.grid(True)

    # LEAF Price Plot
    plt.subplot(3, 2, 4)
    plt.plot(months, leaf_prices)
    plt.title('LEAF Price Over Time')
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.grid(True)

    # AEGIS Balance History
    plt.subplot(3, 2, 5)
    leaf_balance_millions = [b/1e6 for b in aegis_model.leaf_balance_history[:len(months)]]
    usdc_balance_millions = [b/1e6 for b in aegis_model.usdc_balance_history[:len(months)]]
    plt.plot(months, leaf_balance_millions, label='LEAF Balance')
    plt.plot(months, usdc_balance_millions, label='USDC Balance')
    plt.title('AEGIS Balance History')
    plt.xlabel('Month')
    plt.ylabel('Balance (Millions USD)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # Show the new liquidity metrics plots
    plot_liquidity_metrics(metrics_history)

    # Additional TVL composition analysis
    plt.figure(figsize=(15, 5))
    
    # TVL Composition
    plt.subplot(1, 2, 1)
    tvl_types = ['ProtocolLocked', 'Contracted', 'Organic', 'Boosted']
    bottom = np.zeros(len(months))
    
    for tvl_type in tvl_types:
        values = [sum(c['amount_usd'] for c in history_tracker.get_history(m) 
                 if c['tvl_type'] == tvl_type and c['active'])/1e9  # Convert to billions
                 for m in months]
        plt.bar(months, values, bottom=bottom, label=tvl_type)
        bottom += np.array(values)
    
    plt.title('TVL Composition Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (Billions USD)')
    plt.legend()
    
    # TVL Growth Rates
    plt.subplot(1, 2, 2)
    growth_rates = [(total_tvl_by_month[i] - total_tvl_by_month[i-1])/total_tvl_by_month[i-1] 
                   if i > 0 and total_tvl_by_month[i-1] != 0 else 0 
                   for i in range(len(months))]
    plt.plot(months, growth_rates)
    plt.title('Monthly TVL Growth Rate')
    plt.xlabel('Month')
    plt.ylabel('Growth Rate (%)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

    # Create OAK distribution subplot
    plot_oak_distributions(oak_states)

if __name__ == "__main__":
    main() 