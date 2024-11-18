import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.Revenue import RevenueModel, RevenueModelConfig
from src.Functions.TVLContributions import TVLContribution, TVLContributionHistory
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Data.leaf_deal import initialize_deals
from typing import Dict, List
from src.Functions.AEGIS import AEGISConfig, AEGISModel
import numpy as np # type: ignore

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
    plt.ylabel('Price in USDC')
    plt.legend()

    # Balances Over Time
    plt.subplot(2, 1, 2)
    plt.plot(months, aegis_model.leaf_balance_history, label='LEAF Balance')
    plt.plot(months, aegis_model.usdc_balance_history, label='USDC Balance')
    plt.title('AEGIS Balances Over Time')
    plt.xlabel('Month')
    plt.ylabel('Balance')
    plt.legend()

    plt.tight_layout()
    plt.show()

def track_liquidity_metrics(
    month: int,
    price: float,
    aegis_model: AEGISModel,
    leaf_pairs_model: LEAFPairsModel
) -> Dict:
    # Get AEGIS liquidity within 10% of price
    aegis_leaf, aegis_usdc = aegis_model.get_liquidity_within_percentage(10, price)
    
    # Get LEAFPairs liquidity within 10% of price
    leaf_pairs_leaf = 0
    leaf_pairs_other = 0
    active_deals = leaf_pairs_model.get_active_deals(month)
    
    # Get total liquidity across all active deals
    if active_deals:  # Only process if there are active deals
        leaf, other = leaf_pairs_model.get_liquidity_within_percentage(10, price)
        leaf_pairs_leaf = leaf
        leaf_pairs_other = other
    
    return {
        'month': month,
        'price': price,
        'aegis_leaf': aegis_leaf,
        'aegis_usdc': aegis_usdc,
        'leaf_pairs_leaf': leaf_pairs_leaf,
        'leaf_pairs_other': leaf_pairs_other,
        'aegis_total_usd': (aegis_leaf * price) + aegis_usdc,
        'leaf_pairs_total_usd': (leaf_pairs_leaf * price) + leaf_pairs_other
    }

def plot_liquidity_metrics(metrics_history: List[Dict]):
    months = [m['month'] for m in metrics_history]
    
    plt.figure(figsize=(15, 10))
    
    # Plot 1: LEAF Liquidity Comparison
    plt.subplot(2, 2, 1)
    plt.plot(months, [m['aegis_leaf'] for m in metrics_history], label='AEGIS LEAF')
    plt.plot(months, [m['leaf_pairs_leaf'] for m in metrics_history], label='LEAFPairs LEAF')
    plt.title('LEAF Liquidity Within 10% Range')
    plt.xlabel('Month')
    plt.ylabel('LEAF Amount')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Stablecoin Liquidity Comparison
    plt.subplot(2, 2, 2)
    plt.plot(months, [m['aegis_usdc'] for m in metrics_history], label='AEGIS USDC')
    plt.plot(months, [m['leaf_pairs_other'] for m in metrics_history], label='LEAFPairs Other')
    plt.title('Stablecoin Liquidity Within 10% Range')
    plt.xlabel('Month')
    plt.ylabel('USD Amount')
    plt.legend()
    plt.grid(True)
    
    # Plot 3: Total USD Value Comparison
    plt.subplot(2, 2, 3)
    plt.plot(months, [m['aegis_total_usd'] for m in metrics_history], label='AEGIS Total')
    plt.plot(months, [m['leaf_pairs_total_usd'] for m in metrics_history], label='LEAFPairs Total')
    plt.title('Total USD Value Within 10% Range')
    plt.xlabel('Month')
    plt.ylabel('USD Value')
    plt.legend()
    plt.grid(True)
    
    # Plot 4: Combined Liquidity Ratio
    plt.subplot(2, 2, 4)
    ratios = [(m['aegis_total_usd'] + m['leaf_pairs_total_usd']) / (m['aegis_total_usd'] or 1) for m in metrics_history]
    plt.plot(months, ratios)
    plt.title('Combined/AEGIS Liquidity Ratio')
    plt.xlabel('Month')
    plt.ylabel('Ratio')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

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

    # Define activation months for different features
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
    leaf_prices = []
    metrics_history = []
    history_tracker = TVLContributionHistory()

    # Print header
    print("Month          Protocol     Contracted        Organic        Boosted       Total Rev (M)       Cumulative Rev (M)")
    print("-" * 113)

    # Simulation loop
    for month in months:
        # Record state before updates
        history_tracker.record_state(month, tvl_model.contributions)
        
        # Update TVL and calculate metrics
        tvl_model.step()
        total_tvl = tvl_model.get_total_tvl()
        total_tvl_by_month.append(total_tvl)
        
        # Calculate revenue
        monthly_revenue = revenue_model.calculate_revenue(month)
        revenue_by_month.append(monthly_revenue)
        cumulative_revenues.append(revenue_model.cumulative_revenue)

        # Calculate LEAF price for this month
        leaf_price = calculate_leaf_price(month, total_tvl)
        leaf_prices.append(leaf_price)

        # Update AEGIS model if active
        if month >= activation_months['AEGIS_START_MONTH']:
            aegis_model.handle_redemptions(month, 0.02)  # 2% monthly redemption
            aegis_model.step(month)
            
        # Always update history arrays at the correct index
        aegis_model.leaf_balance_history[month] = aegis_model.leaf_balance
        aegis_model.usdc_balance_history[month] = aegis_model.usdc_balance
        aegis_model.leaf_price_history[month] = leaf_price

        # Update LEAF pairs if active
        if month >= activation_months['LEAF_PAIRS_START_MONTH']:
            leaf_pairs_model.update_deals(month, leaf_price)

        # Track liquidity metrics
        metrics = track_liquidity_metrics(month, leaf_price, aegis_model, leaf_pairs_model)
        metrics_history.append(metrics)

        # Print monthly summary
        print_monthly_summary(month, monthly_revenue, revenue_model.cumulative_revenue)

    # After simulation loop, create all visualizations
    plt.figure(figsize=(15, 10))
    
    # Original TVL Plot
    plt.subplot(3, 2, 1)
    plt.plot(months, total_tvl_by_month)
    plt.title('Total TVL Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (USD)')
    plt.grid(True)

    # Original Revenue Plot
    plt.subplot(3, 2, 2)
    protocol_locked = [rev['ProtocolLocked'] for rev in revenue_by_month]
    contracted = [rev['Contracted'] for rev in revenue_by_month]
    organic = [rev['Organic'] for rev in revenue_by_month]
    boosted = [rev['Boosted'] for rev in revenue_by_month]
    
    plt.plot(months, protocol_locked, label='Protocol Locked')
    plt.plot(months, contracted, label='Contracted')
    plt.plot(months, organic, label='Organic')
    plt.plot(months, boosted, label='Boosted')
    plt.title('Monthly Revenue by Type')
    plt.xlabel('Month')
    plt.ylabel('Revenue (USD)')
    plt.legend()
    plt.grid(True)

    # Original Cumulative Revenue Plot
    plt.subplot(3, 2, 3)
    plt.plot(months, cumulative_revenues)
    plt.title('Cumulative Revenue')
    plt.xlabel('Month')
    plt.ylabel('Revenue (USD)')
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
    plt.plot(months, aegis_model.leaf_balance_history[:len(months)], label='LEAF Balance')
    plt.plot(months, aegis_model.usdc_balance_history[:len(months)], label='USDC Balance')
    plt.title('AEGIS Balance History')
    plt.xlabel('Month')
    plt.ylabel('Balance')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # Now show the new liquidity metrics plots
    plot_liquidity_metrics(metrics_history)

    # Additional TVL composition analysis
    plt.figure(figsize=(15, 5))
    
    # TVL Composition
    plt.subplot(1, 2, 1)
    tvl_types = ['ProtocolLocked', 'Contracted', 'Organic', 'Boosted']
    bottom = np.zeros(len(months))
    
    for tvl_type in tvl_types:
        values = [sum(c['amount_usd'] for c in history_tracker.get_history(m) 
                 if c['tvl_type'] == tvl_type and c['active']) 
                 for m in months]
        plt.bar(months, values, bottom=bottom, label=tvl_type)
        bottom += np.array(values)
    
    plt.title('TVL Composition Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (USD)')
    plt.legend()
    
    # TVL Growth Rates
    plt.subplot(1, 2, 2)
    growth_rates = [(total_tvl_by_month[i] - total_tvl_by_month[i-1])/total_tvl_by_month[i-1] 
                   if i > 0 and total_tvl_by_month[i-1] != 0 else 0 
                   for i in range(len(months))]
    plt.plot(months, growth_rates)
    plt.title('Monthly TVL Growth Rate')
    plt.xlabel('Month')
    plt.ylabel('Growth Rate')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 