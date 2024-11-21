import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.Revenue import RevenueModel, RevenueModelConfig
from src.Functions.TVLLoader import TVLLoader
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Functions.AEGIS import AEGISConfig, AEGISModel
from src.Functions.LeafPrice import LEAFPriceModel, LEAFPriceConfig
from src.Data.deal import Deal, initialize_deals, get_active_deals
from typing import Dict, List, Optional
import numpy as np  # type: ignore
from collections import defaultdict
from src.Functions.OAK import OAKModel, OAKDistributionConfig
import logging
import os
from datetime import datetime
from pathlib import Path

def cleanup_old_logs(logs_dir: str, keep_count: int = 3):
    """Keep only the most recent log files."""
    # Get all log files sorted by modification time (newest first)
    log_files = sorted(
        Path(logs_dir).glob('simulation_*.log'),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Remove all but the most recent 'keep_count' files
    for log_file in log_files[keep_count:]:
        try:
            log_file.unlink()
            logging.debug(f"Removed old log file: {log_file}")
        except Exception as e:
            logging.warning(f"Failed to remove old log file {log_file}: {e}")

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

def calculate_leaf_price(month: int, total_liquidity: float) -> float:
    """Placeholder function to calculate LEAF price."""
    # Implement your LEAF price model here.
    return 1.0  # Placeholder value

def initialize_tvl_contributions(tvl_model: TVLModel, config: Dict) -> TVLLoader:
    """Initialize all TVL contributions based on simulation config."""
    organic_config = {
        'initial_tvl': 0,
        'monthly_growth_rate': 0.05,
        'max_tvl': 1_000_000_000,
        'conversion_ratio': 0.2,
        'decay_rate': 0.05,
        'duration_months': 36
    }
    
    # Initialize TVL loader with organic config
    loader = TVLLoader(tvl_model, organic_config)
    
    # Add Protocol Locked TVL from Move deal (already in initialize_deals)
    # No need to add it here as it's handled by the TVLLoader
    
    return loader

def print_monthly_summary(month: int, monthly_revenue: Dict[str, float], cumulative_revenue: float):
    """Print monthly simulation summary"""
    print(f"\nMonth {month} Summary:")
    print(f"Monthly Revenue by Category:")
    for category, amount in monthly_revenue.items():
        print(f"- {category}: ${amount:,.2f}")
    print(f"Cumulative Revenue: ${cumulative_revenue:,.2f}")

def track_liquidity_metrics(month: int, current_leaf_price: float, aegis_model: AEGISModel, 
                          leaf_pairs_model: LEAFPairsModel, tvl_model: TVLModel, 
                          oak_model: OAKModel, deals: List[Deal], previous_state: Dict) -> Dict:
    """Track all relevant metrics for the current month."""
    logger = logging.getLogger(__name__)
    
    # Get states from each model
    aegis_state = aegis_model.get_state()
    oak_state = oak_model.get_state()
    
    # Use OAK model's built-in methods
    distributed_oak = oak_model.get_total_distributed_oak()  # Use existing method
    redeemed_oak = oak_model.redeemed_oak
    remaining_oak = oak_model.total_oak_supply - redeemed_oak
    
    # Use the model's value calculation method
    value_per_oak = oak_model.calculate_value_per_oak(
        aegis_model.usdc_balance,
        aegis_model.leaf_balance,
        current_leaf_price
    )
    
    # Get TVL breakdown
    tvl_breakdown = tvl_model.get_current_tvl_by_type()
    total_tvl = tvl_model.get_current_tvl()
    
    # Calculate IRR once and store it
    current_value, irr = oak_model._calculate_monthly_metrics(
        month,
        value_per_oak,
        current_leaf_price
    ) if month >= oak_model.config.redemption_start_month else (0, 0)

    return {
        'month': month,
        'leaf_price': current_leaf_price,
        'total_value': total_tvl,
        'tvl_breakdown': tvl_breakdown,
        'distributed_oak': distributed_oak,
        'redeemed_oak': redeemed_oak,
        'remaining_oak': remaining_oak,
        'value_per_oak': value_per_oak,
        'irr': irr  # Store the IRR in metrics
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
):
    """Create and add an OAK deal based on TVL contribution."""
    # Implement the logic to create an OAK deal from TVL
    # This is a placeholder function and should be replaced with actual implementation
    pass

def plot_all_metrics(
    months: List[int],
    metrics_history: List[Dict],
    leaf_prices: Dict[int, float],
    aegis_model: AEGISModel,
    leaf_pairs_model: LEAFPairsModel,
    oak_model: OAKModel,
    current_leaf_price: float
) -> None:
    """Plot comprehensive metrics from the simulation."""
    plt.figure(figsize=(15, 15))
    
    # Plot 1: LEAF Price
    plt.subplot(3, 1, 1)
    plt.title('LEAF Price Over Time')
    price_values = [leaf_prices.get(m, 0) for m in months]
    plt.plot(months, price_values, label='LEAF Price', color='#2ecc71')
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Liquidity Composition
    plt.subplot(3, 1, 2)
    plt.title('Liquidity Composition Over Time')
    
    # Extract liquidity metrics
    total_leaf = [m['total_leaf'] / 1_000_000 for m in metrics_history]  # Convert to millions
    total_usdc = [m['total_usdc'] / 1_000_000 for m in metrics_history]
    
    plt.plot(months, total_leaf, label='Total LEAF', color='#3498db')
    plt.plot(months, total_usdc, label='Total USDC', color='#e74c3c')
    plt.xlabel('Month')
    plt.ylabel('Amount (Millions)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Total Value Locked
    plt.subplot(3, 1, 3)
    plt.title('Total Value Locked Over Time')
    total_value = [m['total_value'] / 1_000_000_000 for m in metrics_history]  # Convert to billions
    plt.plot(months, total_value, label='Total Value', color='#9b59b6')
    plt.xlabel('Month')
    plt.ylabel('TVL (Billions USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def run_simulation(simulation_months: int):
    # Initialize models
    deals = initialize_deals()
    
    aegis_config = AEGISConfig(
        initial_leaf_balance=1_000_000_000,  # 1 billion LEAF
        initial_usdc_balance=100_000,        # 100k USDC
        max_months=simulation_months
    )
    aegis_model = AEGISModel(aegis_config)
    
    oak_config = OAKDistributionConfig(
        total_oak_supply=500_000,
        redemption_start_month=12,
        redemption_end_month=48,
        deals=deals
    )
    oak_model = OAKModel(oak_config, aegis_model)  # Pass AEGIS model to OAK model
    
    # ... rest of simulation setup ...

def main():
    """Run the main simulation loop."""
    # Setup logging
    log_file = setup_logging()
    if not log_file:
        print("Failed to setup logging. Exiting.")
        return
    logger = logging.getLogger(__name__)
    
    # Initialize simulation parameters
    simulation_months = 60
    simulation_config = {'simulation_months': simulation_months}
    
    # Initialize deals
    deals = initialize_deals()

    # Setup logging


    # Initialize configuration
    simulation_months = 60
    config = {
        'simulation_months': simulation_months,
        'initial_leaf_supply': 1_000_000_000,
        'initial_usdc': 100_000_000
    }

    # Initialize models with proper configuration
    tvl_config = TVLModelConfig()
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
    
    previous_state = {
        'active_deals': set(),
        'tvl_breakdown': {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        },
        'total_tvl': 0.0,
        'leaf_price': current_leaf_price,
        'distributed_oak': 0.0,
        'redeemed_oak': 0.0,
        'remaining_oak': oak_model.total_oak_supply,
        'value_per_oak': 0.0
    }

    # Main simulation loop
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

    # Plot results
    plot_simulation_results(
        months=list(range(1, simulation_months + 1)),
        metrics_history=metrics_history,
        cumulative_revenue_values=cumulative_revenue_values,
        aegis_model=aegis_model,
        oak_model=oak_model
    )

def plot_simulation_results(months: List[int], metrics_history: List[Dict], cumulative_revenue_values: List[float], aegis_model: AEGISModel, oak_model: OAKModel):
    """Plot simulation results with multiple 2x2 subplots."""
    
    # First Grid (TVL, Revenue, LEAF Price, and OAK Value)
    plt.figure(figsize=(15, 15))
    
    # Plot 1: TVL Composition Over Time (Top Left)
    plt.subplot(2, 2, 1)
    plt.title('TVL Composition Over Time')
    protocol_locked = [m['tvl_breakdown'].get('ProtocolLocked', 0) / 1_000_000_000 for m in metrics_history]
    contracted = [m['tvl_breakdown'].get('Contracted', 0) / 1_000_000_000 for m in metrics_history]
    organic = [m['tvl_breakdown'].get('Organic', 0) / 1_000_000_000 for m in metrics_history]
    boosted = [m['tvl_breakdown'].get('Boosted', 0) / 1_000_000_000 for m in metrics_history]
    plt.stackplot(months, [protocol_locked, contracted, organic, boosted], 
                 labels=['Protocol Locked', 'Contracted', 'Organic', 'Boosted'], 
                 colors=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'])
    plt.xlabel('Month')
    plt.ylabel('TVL (Billions USD)')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Cumulative Revenue (Top Right)
    plt.subplot(2, 2, 2)
    plt.title('Cumulative Revenue Over Time')
    cumulative_millions = [v / 1_000_000 for v in cumulative_revenue_values]
    plt.plot(months, cumulative_millions, label='Cumulative Revenue', color='#27ae60', linewidth=2)
    plt.xlabel('Month')
    plt.ylabel('Revenue (Millions USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: LEAF Price Over Time (Bottom Left)
    plt.subplot(2, 2, 3)
    plt.title('LEAF Price Over Time')
    leaf_prices = [m['leaf_price'] for m in metrics_history]
    plt.plot(months, leaf_prices, label='LEAF Price', color='#f1c40f', linewidth=2)
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 4: OAK Distribution and Redemption (Bottom Right)
    plt.subplot(2, 2, 4)
    plt.title('OAK Token Metrics')
    
    # Create two y-axes for different scales
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    # Plot OAK amounts on left y-axis
    distributed = [m['distributed_oak'] for m in metrics_history]
    redeemed = [m['redeemed_oak'] for m in metrics_history]
    remaining = [m['remaining_oak'] for m in metrics_history]
    
    # Plot stacked area for OAK amounts
    ax1.stackplot(months, 
                 [redeemed, remaining],
                 labels=['Redeemed OAK', 'Unredeemed OAK'],
                 colors=['#e74c3c', '#2ecc71'],
                 alpha=0.5)
    ax1.plot(months, distributed, 'k--', label='Total Distributed', linewidth=2)
    ax1.set_ylabel('OAK Tokens')
    
    # Plot value per OAK on right y-axis
    values = [m['value_per_oak'] for m in metrics_history]
    ax2.plot(months, values, color='#3498db', label='Value per OAK', linewidth=2)
    ax2.set_ylabel('Value per OAK (USD)')
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Second Grid (AEGIS Composition, Total Value, and IRR Metrics)
    plt.figure(figsize=(15, 15))
    
    # Plot 5: AEGIS Composition Over Time (Top Left)
    plt.subplot(2, 2, 1)
    plt.title('AEGIS Composition Over Time')
    leaf_balances = [aegis_model.leaf_balance_history[m] for m in months]
    usdc_balances = [aegis_model.usdc_balance_history[m] for m in months]
    total_values = [leaf + usdc for leaf, usdc in zip(leaf_balances, usdc_balances)]
    leaf_percentages = [(leaf / total) * 100 if total > 0 else 0 for leaf, total in zip(leaf_balances, total_values)]
    usdc_percentages = [(usdc / total) * 100 if total > 0 else 0 for usdc, total in zip(usdc_balances, total_values)]
    plt.stackplot(months, [leaf_percentages, usdc_percentages], labels=['% LEAF', '% USDC'], colors=['#f1c40f', '#3498db'])
    plt.xlabel('Month')
    plt.ylabel('Composition (%)')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Plot 6: AEGIS Total Value Over Time (Top Right)
    plt.subplot(2, 2, 2)
    plt.title('AEGIS Total Value Over Time')
    total_values_millions = [total / 1_000_000 for total in total_values]
    plt.plot(months, total_values_millions, label='AEGIS Total Value', color='#8e44ad', linewidth=2)
    plt.xlabel('Month')
    plt.ylabel('Value (Millions USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 7: IRR Metrics Over Time (Bottom Left)
    plt.subplot(2, 2, 3)
    plt.title('OAK IRR Metrics')
    
    # Use stored IRR values instead of recalculating
    irr_values = [m['irr'] * 100 for m in metrics_history]  # Convert to percentage
    
    # Calculate weighted average threshold
    weighted_threshold = oak_model.calculate_weighted_avg_irr_threshold() * 100  # Convert to percentage
    threshold_line = [weighted_threshold] * len(months)
    
    # Plot both lines
    plt.plot(months, irr_values, label='Global IRR', color='#e67e22', linewidth=2)
    plt.plot(months, threshold_line, '--', label='Weighted Avg Threshold', 
            color='#c0392b', linewidth=2)
    
    plt.xlabel('Month')
    plt.ylabel('IRR (%)')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Optional: Set y-axis limits to better show the IRR range
    plt.ylim(bottom=0)  # Start at 0
    max_irr = max(max(irr_values), weighted_threshold)
    plt.ylim(top=max_irr * 1.1)  # Add 10% padding at top
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 