import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.Revenue import RevenueModel
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

    # Add revenue configuration
    revenue_config = {
        'protocol_locked_rate': 0.02,  # 2% fee on protocol-locked TVL
        'contracted_rate': 0.015,      # 1.5% fee on contracted TVL
        'organic_rate': 0.01,          # 1% fee on organic TVL
        'boosted_rate': 0.025          # 2.5% fee on boosted TVL
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
    revenue_model = RevenueModel(tvl_model=tvl_model)
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

    # Add this before the simulation loop
    monthly_revenue_by_type = {}  # Dictionary to store revenue by type for each month
    
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
        active_contributions = tvl_model.get_active_contributions(month)
        monthly_revenue = revenue_model.calculate_revenue_from_contributions(active_contributions, month)
        revenue_by_month.append(monthly_revenue)
        revenue_model.cumulative_revenue += sum(monthly_revenue.values())
        cumulative_revenues.append(revenue_model.cumulative_revenue)
        
        # Update OAK if active
        if month >= activation_months['OAK_START_MONTH']:
            # Process monthly distributions first
            oak_distributions = oak_model.process_monthly_distributions(month)
            if oak_distributions:
                print(f"\nOAK Distributions for month {month}:")
                for counterparty, amount in oak_distributions.items():
                    print(f"- {counterparty}: {amount:,.2f} OAK")
            
            # Get current market conditions
            aegis_usdc = aegis_model.usdc_balance_history[month]
            aegis_leaf = aegis_model.leaf_balance_history[month]
            current_leaf_price = leaf_price_model.get_current_price(month)
            
            # Process step and record state
            oak_redemption, supply_before, supply_after, usdc_redemption, leaf_redemption = oak_model.step(
                current_month=month,
                aegis_usdc=aegis_usdc,
                aegis_leaf=aegis_leaf,
                current_leaf_price=current_leaf_price
            )
            
            # Store state for visualization
            oak_states.append(oak_model.get_state())
            
            # Update AEGIS balances based on redemptions
            if oak_redemption > 0:
                aegis_model.update_balances(
                    usdc_change=-usdc_redemption,
                    leaf_change=-leaf_redemption
                )
                print(f"\nOAK Redemptions:")
                print(f"- Amount: {oak_redemption:,.2f} OAK")
                print(f"- USDC: ${usdc_redemption:,.2f}")
                print(f"- LEAF: {leaf_redemption:,.2f} @ ${current_leaf_price:.2f}")
                print(f"- Total Value: ${(usdc_redemption + leaf_redemption * current_leaf_price):,.2f}")
        
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
        print(f"LEAF Price at month {month}: ${current_leaf_price:.4f}")  # Log price every month

    # After simulation loop, create all visualizations
    plt.figure(figsize=(20, 20))  # Made taller to accommodate all charts
    
    # TVL Composition (1st plot)
    plt.subplot(4, 2, 1)
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
    plt.grid(True, alpha=0.3)

    # TVL Growth Rate (2nd plot)
    plt.subplot(4, 2, 2)
    growth_rates = [(total_tvl_by_month[i] - total_tvl_by_month[i-1])/total_tvl_by_month[i-1] * 100
                   if i > 0 and total_tvl_by_month[i-1] != 0 else 0 
                   for i in range(len(months))]
    plt.plot(months, growth_rates, color='#2ecc71')
    plt.title('Monthly TVL Growth Rate')
    plt.xlabel('Month')
    plt.ylabel('Growth Rate (%)')
    plt.grid(True, alpha=0.3)

    # Revenue Composition (3rd plot)
    plt.subplot(4, 2, 3)
    revenue_types = ['ProtocolLocked', 'Contracted', 'Organic', 'Boosted']
    bottom = np.zeros(len(months))
    for revenue_type in revenue_types:
        values = [revenue_by_month[m][revenue_type]/1e6 for m in months]  # Convert to millions
        plt.bar(months, values, bottom=bottom, label=revenue_type)
        bottom += np.array(values)
    plt.title('Monthly Revenue by Type')
    plt.xlabel('Month')
    plt.ylabel('Revenue (Millions USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Cumulative Revenue (4th plot)
    plt.subplot(4, 2, 4)
    plt.plot(months, cumulative_revenues, color='#3498db')
    plt.title('Cumulative Revenue')
    plt.xlabel('Month')
    plt.ylabel('Revenue (Millions USD)')
    plt.grid(True, alpha=0.3)

    # LEAF Price (5th plot)
    plt.subplot(4, 2, 5)
    plt.plot(months, [leaf_prices[m] for m in months], color='#3498db')
    plt.title('LEAF Price Over Time')
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.grid(True, alpha=0.3)

    # Liquidity Metrics (6th plot)
    plt.subplot(4, 2, 6)
    months_metrics = [metric['month'] for metric in metrics_history]
    total_leaf = [metric['total_leaf']/1e6 for metric in metrics_history]
    total_usdc = [metric['total_usdc']/1e6 for metric in metrics_history]
    plt.plot(months_metrics, total_leaf, label='LEAF', color='#3498db')
    plt.plot(months_metrics, total_usdc, label='USDC', color='#e74c3c')
    plt.title('Liquidity Over Time')
    plt.xlabel('Month')
    plt.ylabel('Amount (Millions)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # OAK Token Status (7th plot)
    plt.subplot(4, 2, 7)
    
    # Calculate allocated, distributed, and redeemed amounts
    allocated = [sum(deal.oak_amount for deal in oak_states[0]['deals'])] * len(oak_states)
    
    # Track running totals for distributions and redemptions
    distributed = []
    running_dist_total = 0
    for state in oak_states:
        month_dist = sum(state['distribution_history'].get(state['current_month'], {}).values())
        running_dist_total += month_dist
        distributed.append(running_dist_total)
    
    redeemed = []
    running_red_total = 0
    for state in oak_states:
        month_red = sum(state['redemption_history'].get(state['current_month'], {}).values())
        running_red_total += month_red
        redeemed.append(running_red_total)
    
    # Convert to millions for display
    allocated = [a/1e6 for a in allocated]
    distributed = [d/1e6 for d in distributed]
    redeemed = [r/1e6 for r in redeemed]
    
    # Create stacked area chart
    plt.fill_between(months[:len(oak_states)], 0, allocated, 
                     alpha=0.3, label='Allocated', color='#2ecc71')
    plt.fill_between(months[:len(oak_states)], 0, distributed, 
                     alpha=0.5, label='Distributed', color='#3498db')
    plt.fill_between(months[:len(oak_states)], 0, redeemed, 
                     alpha=0.7, label='Redeemed', color='#e74c3c')
    
    plt.title('OAK Token Status')
    plt.xlabel('Month')
    plt.ylabel('OAK Tokens (Millions)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Monthly OAK Redemptions (8th plot)
    plt.subplot(4, 2, 8)
    monthly_redemptions = [
        sum(state['redemption_history'].get(state['current_month'], {}).values())/1e6 
        for state in oak_states
    ]
    plt.bar(months[:len(oak_states)], monthly_redemptions, color='#e74c3c', alpha=0.7)
    plt.title('Monthly OAK Redemptions')
    plt.xlabel('Month')
    plt.ylabel('OAK Tokens (Millions)')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 