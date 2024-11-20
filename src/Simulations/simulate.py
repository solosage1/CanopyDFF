import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.Revenue import RevenueModel
from src.Functions.TVLContributions import TVLContributionHistory, TVLContribution
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Functions.AEGIS import AEGISConfig, AEGISModel
from src.Functions.LeafPrice import LEAFPriceModel, LEAFPriceConfig
from src.Data.deal import Deal, initialize_deals, get_active_deals
from typing import Dict, List, Optional
import numpy as np  # type: ignore
from collections import defaultdict
from src.Functions.OAK import OAKModel, OAKDistributionConfig

def calculate_leaf_price(month: int, total_liquidity: float) -> float:
    """Placeholder function to calculate LEAF price."""
    # Implement your LEAF price model here.
    return 1.0  # Placeholder value

def initialize_tvl_contributions(tvl_model: TVLModel, config: Dict) -> None:
    """Initialize all TVL contributions based on simulation config."""
    # Initialize deals first
    all_deals = initialize_deals()
    # Get active deals for month 0 (initialization)
    active_deals = get_active_deals(all_deals, 0)
    
    for deal in active_deals:
        tvl_model.add_contribution(TVLContribution(
            amount_usd=deal.tvl_amount,
            tvl_type=deal.tvl_category,
            start_month=deal.start_month,
            end_month=deal.start_month + deal.tvl_duration_months,
            revenue_rate=deal.tvl_revenue_rate,
            counterparty=deal.counterparty,
            category=deal.tvl_category
        ))

def print_monthly_summary(month: int, monthly_revenue: Dict[str, float], cumulative_revenue: float) -> None:
    """Print a summary of monthly revenue by TVL type."""
    # Convert to millions for display
    print(f"{month:3d}    {monthly_revenue['ProtocolLocked']/1e6:12.2f} "
          f"{monthly_revenue['Contracted']/1e6:12.2f} {monthly_revenue['Organic']/1e6:12.2f} "
          f"{monthly_revenue['Boosted']/1e6:12.2f} {sum(monthly_revenue.values())/1e6:15.2f} "
          f"{cumulative_revenue/1e6:20.2f}")

def track_liquidity_metrics(
    month: int,
    current_leaf_price: float,
    aegis_model: AEGISModel,
    leaf_pairs_model: LEAFPairsModel
) -> Dict[str, float]:
    """Track liquidity metrics based on AEGIS and LEAF Pairs models."""
    total_leaf = aegis_model.leaf_balance
    total_usdc = aegis_model.usdc_balance
    
    # Add LEAF pair balances from active deals
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

def create_oak_deal_from_tvl(
    tvl_type: str,
    amount_usd: float,
    revenue_rate: float,
    start_month: int,
    duration_months: int,
    counterparty: str,
    oak_model: 'OAKModel',
    aegis_usdc: float,
    aegis_leaf: float,
    current_leaf_price: float
) -> Optional[Deal]:
    """Create a new OAK deal based on TVL contribution."""
    # Define OAK amount based on some logic, e.g., based on revenue rate or amount_usd
    oak_amount = amount_usd * revenue_rate  # Example logic
    if oak_amount <= 0:
        return None  # No deal to create

    # Create a new Deal instance
    new_deal = Deal(
        deal_id=f"{counterparty[:10]}_{start_month:03d}",
        counterparty=counterparty,
        start_month=start_month,
        oak_amount=oak_amount,
        oak_vesting_months=12,  # Example vesting period
        oak_irr_threshold=15.0,  # Example IRR threshold
        tvl_amount=amount_usd,
        tvl_revenue_rate=revenue_rate,
        tvl_duration_months=duration_months,
        tvl_category=tvl_type
    )
    return new_deal

def main():
    """Main simulation function."""
    # Initialize configuration
    config = {
        'initial_move_tvl': 1_000_000_000,
        'initial_canopy_tvl': 500_000_000,
        'move_growth_rates': [0.10, 0.08, 0.06],
        'min_market_share': 0.05,
        'market_share_decay_rate': 0.01,
        'max_months': 60,
        'activation_months': {
            'LEAF_PAIRS_START_MONTH': 1,
            'AEGIS_START_MONTH': 3,
            'OAK_START_MONTH': 4,
            'MARKET_START_MONTH': 5,
            'PRICE_START_MONTH': 5,
            'DISTRIBUTION_START_MONTH': 5,
            'BOOST_START_MONTH': 6
        }
    }

    # Initialize models
    tvl_model = TVLModel(TVLModelConfig())
    revenue_model = RevenueModel()
    
    # Initialize LEAF pairs with deals
    all_deals = initialize_deals()  # Get all deals
    leaf_pairs_model = LEAFPairsModel(LEAFPairsConfig(), deals=all_deals)
    
    # Initialize AEGIS with required parameters
    aegis_config = AEGISConfig(
        initial_leaf_balance=1_000_000_000,
        initial_usdc_balance=500_000,
        leaf_price_decay_rate=0.005,
        max_months=config['max_months']
    )
    aegis_model = AEGISModel(aegis_config)

    # Initialize OAK model
    oak_config = OAKDistributionConfig(
        total_oak_supply=500_000,  # From OAK.md documentation
        deals=all_deals           # Use the same deals list
    )
    oak_model = OAKModel(oak_config)

    # Initialize LEAF price model
    leaf_price_config = LEAFPriceConfig(
        min_price=0.10,             # Minimum price floor
        max_price=10.0,             # Maximum price ceiling
        price_impact_threshold=0.10  # 10% max price impact per trade
    )
    leaf_price_model = LEAFPriceModel(leaf_price_config)

    # Initialize variables
    metrics_history = []
    leaf_prices = {}
    oak_states = []
    cumulative_revenue = 0.0
    months = list(range(1, config['max_months'] + 1))

    for month in months:
        print(f"Simulating month {month}...")
        
        # Get active deals for this month
        active_deals = get_active_deals(all_deals, month)
        
        # Create incentive deals for new contracted TVL
        # Assuming active_contributions are TVL contributions active this month
        active_contributions = [contrib for contrib in tvl_model.contributions if contrib.active and contrib.start_month <= month < contrib.end_month]
        
        for contribution in active_contributions:
            incentive_deal = create_oak_deal_from_tvl(
                tvl_type=contribution.tvl_type,
                amount_usd=contribution.amount_usd,
                revenue_rate=contribution.revenue_rate,
                start_month=contribution.start_month,
                duration_months=contribution.end_month - contribution.start_month,
                counterparty=contribution.counterparty,
                oak_model=oak_model,
                aegis_usdc=aegis_model.usdc_balance,
                aegis_leaf=aegis_model.leaf_balance,
                current_leaf_price=leaf_price_model.current_price
            )
            
            if incentive_deal:
                oak_model.config['deals'].append(incentive_deal)
                print(f"\nNew TVL Incentive Deal:")
                print(f"- Counterparty: {contribution.counterparty}")
                print(f"- TVL Amount: ${contribution.amount_usd:,.2f}")
                print(f"- Revenue Rate: {contribution.revenue_rate:.1%}")
                print(f"- OAK Amount: {incentive_deal.oak_amount:,.2f}")
                all_deals.append(incentive_deal)  # Add to all_deals for further processing
        
        # Process monthly distributions first
        oak_distributions = oak_model.process_monthly_distributions(month)
        if oak_distributions:
            print(f"\nOAK Distributions for month {month}:")
            for counterparty, amount in oak_distributions.items():
                print(f"- {counterparty}: {amount:,.2f} OAK")
        
        # Get current market conditions
        aegis_usdc = aegis_model.usdc_balance_history.get(month, aegis_model.usdc_balance)
        aegis_leaf = aegis_model.leaf_balance_history.get(month, aegis_model.leaf_balance)
        current_leaf_price = leaf_price_model.current_price
        
        # Process step and record state
        oak_redemption, supply_before, supply_after, usdc_redemption, leaf_redemption = oak_model.step(
            current_month=month,
            aegis_usdc=aegis_usdc,
            aegis_leaf=aegis_leaf,
            current_leaf_price=current_leaf_price,
            aegis_model=aegis_model
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
        if month >= config['activation_months']['AEGIS_START_MONTH']:
            # Skip redemption processing since OAK model handles it
            # Only step the model to update state
            aegis_model.step(month)
        
        # Update LEAF pairs if active
        if month >= config['activation_months']['LEAF_PAIRS_START_MONTH']:
            leaf_pairs_model.update_deals(month, current_leaf_price)
        
        # Update LEAF price if active
        if month >= config['activation_months']['PRICE_START_MONTH']:
            # Collect total trade amounts impacting LEAF price in this month
            simulated_trades = [10_000, -5_000, 15_000]  # Example trades in USD

            for trade_amount_usd in simulated_trades:
                try:
                    new_price = leaf_price_model.update_price(
                        month=month,
                        deals=active_deals,  # Pass the active deals list
                        trade_amount_usd=trade_amount_usd
                    )
                    current_leaf_price = new_price
                except ValueError as e:
                    print(f"Trade of {trade_amount_usd} USD could not be executed: {e}")

            # Finalize the month's LEAF price
            leaf_price_model.finalize_month_price(month)
        else:
            # LEAF price remains at initial price before PRICE_START_MONTH
            current_leaf_price = leaf_price_model.current_price
        
        # Update AEGIS history
        aegis_model.leaf_balance_history[month] = aegis_model.leaf_balance
        aegis_model.usdc_balance_history[month] = aegis_model.usdc_balance
        
        # Track metrics
        metrics = track_liquidity_metrics(month, current_leaf_price, aegis_model, leaf_pairs_model)
        metrics_history.append(metrics)
        
        # Track LEAF price
        leaf_prices[month] = current_leaf_price
        
        # Calculate monthly revenue
        monthly_revenue = revenue_model.calculate_revenue_from_contributions(tvl_model.contributions, month)
        revenue_model.cumulative_revenue += sum(monthly_revenue.values())
        cumulative_revenue += revenue_model.cumulative_revenue
        
        # Print monthly summary
        print_monthly_summary(month, monthly_revenue, revenue_model.cumulative_revenue)
        print(f"LEAF Price at month {month}: ${current_leaf_price:.4f}")  # Log price every month

        # Debug logging for TVL values
        print(f"\nTVL State for Month {month}:")
        tvl_state = tvl_model.get_tvl_by_type(active_deals, month)
        print(f"- ProtocolLocked: ${tvl_state.get('ProtocolLocked', 0):,.2f}")
        print(f"- Contracted: ${tvl_state.get('Contracted', 0):,.2f}")
        print(f"- Organic: ${tvl_state.get('Organic', 0):,.2f}")
        print(f"- Boosted: ${tvl_state.get('Boosted', 0):,.2f}")
        
        # Record TVL state properly
        tvl_model.tvl_by_category_history[month] = tvl_state

    # After simulation loop, create all visualizations
    plt.figure(figsize=(20, 20))  # Made taller to accommodate all charts
    
    # TVL Composition Over Time (1st plot)
    plt.subplot(4, 2, 1)
    
    tvl_by_type = defaultdict(list)
    for month in months:
        tvl_state = tvl_model.tvl_by_type_history.get(month, {})
        for category in ['ProtocolLocked', 'Contracted', 'Organic', 'Boosted']:
            tvl_by_type[category].append(tvl_state.get(category, 0))

    # Plot each TVL component
    for category in ['ProtocolLocked', 'Contracted', 'Organic', 'Boosted']:
        plt.plot(months, tvl_by_type[category], label=category)

    plt.title('TVL Composition Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Revenue Over Time (2nd plot)
    plt.subplot(4, 2, 2)
    cumulative_revenue_values = [sum(m['total_usdc'] + m['total_leaf'] for m in metrics_history[:i+1])
                           for i in range(len(metrics_history))]
    plt.plot(months, cumulative_revenue_values, label='Cumulative Revenue', color='#8e44ad')
    plt.title('Cumulative Revenue Over Time')
    plt.xlabel('Month')
    plt.ylabel('Revenue (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # LEAF Price Over Time (3rd plot)
    plt.subplot(4, 2, 3)
    leaf_price_values = [leaf_prices[m] for m in months]
    plt.plot(months, leaf_price_values, label='LEAF Price', color='#e67e22')
    plt.title('LEAF Price Over Time')
    plt.xlabel('Month')
    plt.ylabel('LEAF Price (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # AEGIS USDC Balance Over Time (4th plot)
    plt.subplot(4, 2, 4)
    usdc_balances = [aegis_model.usdc_balance_history.get(m, 0) for m in months]
    plt.plot(months, usdc_balances, label='AEGIS USDC Balance', color='#1abc9c')
    plt.title('AEGIS USDC Balance Over Time')
    plt.xlabel('Month')
    plt.ylabel('USDC Balance (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # AEGIS LEAF Balance Over Time (5th plot)
    plt.subplot(4, 2, 5)
    leaf_balances = [aegis_model.leaf_balance_history.get(m, 0) for m in months]
    plt.plot(months, leaf_balances, label='AEGIS LEAF Balance', color='#d35400')
    plt.title('AEGIS LEAF Balance Over Time')
    plt.xlabel('Month')
    plt.ylabel('LEAF Balance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # LEAF Pairs Activity Over Time (6th plot)
    plt.subplot(4, 2, 6)
    active_leaf_deals = [leaf_pairs_model.get_active_deals(m) for m in months]
    leaf_pairs_counts = [len(deals) for deals in active_leaf_deals]
    plt.plot(months, leaf_pairs_counts, label='Active LEAF Pairs', color='#2c3e50')
    plt.title('Active LEAF Pairs Over Time')
    plt.xlabel('Month')
    plt.ylabel('Number of Active LEAF Pairs')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # OAK Token Status (7th plot)
    plt.subplot(4, 2, 7)
    
    # Get allocated OAK from the config's deals
    allocated = [sum(deal.oak_distributed_amount for deal in oak_model.config.deals 
                    if deal.start_month <= m)
                 for m in months]
    
    # Get distributed and redeemed from history
    distributed = [oak_model.oak_supply_history.get(m, 0) for m in months]
    redeemed = [sum(oak_model.redemption_history.get(m, {}).values()) for m in months]
    
    plt.plot(months, allocated, label='Allocated', linestyle='--')
    plt.plot(months, distributed, label='Distributed')
    plt.plot(months, redeemed, label='Redeemed')
    plt.title('OAK Token Status')
    plt.xlabel('Month')
    plt.ylabel('OAK Tokens')
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

    # Calculate cumulative values for plotting
    cumulative_revenue_values = [sum(m['total_usdc'] + m['total_leaf'] for m in metrics_history[:i+1])
                           for i in range(len(metrics_history))]

    # Print final metrics
    print("\nFinal Metrics:")
    print(f"Total USDC Liquidity: ${metrics_history[-1]['total_usdc']:,.2f}")
    print(f"Total LEAF Liquidity: {metrics_history[-1]['total_leaf']:,.2f}")
    print(f"Final LEAF Price: ${current_leaf_price:.4f}")
    print(f"Total Value: ${cumulative_revenue_values[-1]:,.2f}")

if __name__ == "__main__":
    main() 