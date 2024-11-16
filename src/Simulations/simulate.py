import matplotlib.pyplot as plt  # type: ignore
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.boosted_tvl import BoostedTVLModel, BoostedTVLConfig
from src.Functions.Revenue import RevenueModel, RevenueModelConfig
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Data.leaf_deal import initialize_deals

def calculate_leaf_price(month: int, total_liquidity: float) -> float:
    """
    Placeholder function to calculate LEAF price.
    """
    # Implement your LEAF price model here.
    return 1.0  # Placeholder value

def main():
    # Define activation months for components
    activation_months = {
        'LEAF_PAIRS_START_MONTH': 1,
        'AEGIS_START_MONTH': 3,
        'OAK_START_MONTH': 4,
        'MARKET_START_MONTH': 5,
        'PRICE_START_MONTH': 5,
        'DISTRIBUTION_START_MONTH': 5,
    }

    # Initialize TVL model with configuration
    tvl_config = TVLModelConfig(
        initial_move_tvl=800_000_000,         # $800M
        initial_canopy_tvl=350_000_000,       # $350M
        move_growth_rates=[1.5, 1, 0.75, 0.5, 0.4],  # Annual growth rates for 5 years
        min_market_share=0.10,                # 10%
        market_share_decay_rate=0.02          # Decay rate
    )
    tvl_model = TVLModel(tvl_config)

    # Initialize Boosted TVL model
    boosted_tvl_config = BoostedTVLConfig(
        initial_boost_share=0.10,             # 10%
        boost_growth_rate=1.0,                # Growth rate for boost
        max_months=60
    )
    boosted_tvl_model = BoostedTVLModel(boosted_tvl_config)

    # Initialize Revenue Model with configuration
    revenue_config = RevenueModelConfig(
        initial_volatile_share=0.10,     # 10% volatile at start
        target_volatile_share=0.20,      # Target 20% volatile share
        volatile_share_growth=0.02,      # Not used in current implementation
        initial_volatile_rate=0.05,      # 5% annual revenue rate for volatile
        target_volatile_rate=0.02,       # 2% annual revenue rate for volatile
        initial_stable_rate=0.01,        # 1% annual revenue rate for stable
        target_stable_rate=0.005,        # 0.5% annual revenue rate for stable
        share_growth_duration=24         # Duration over which shares and rates change (in months)
    )
    revenue_model = RevenueModel(revenue_config)

    # Initialize LEAFPairs Model variables
    leaf_model = None
    leaf_config = LEAFPairsConfig()

    months = list(range(61))  # 0 to 60

    # Initialize data storage lists
    move_tvls = []
    canopy_tvls = []
    boosted_tvls = []
    total_tvls = []
    total_revenues = []
    stable_revenues = []
    volatile_revenues = []
    cumulative_revenues = []
    leaf_prices = []
    leaf_total_liquidities = []
    cumulative_revenue = 0.0

    # Initialize previous_leaf_price
    previous_leaf_price = 1.0  # Starting with a default LEAF price

    for month in months:
        # Get Move TVL and Canopy TVL
        move_tvl, canopy_tvl = tvl_model.get_tvls(month)
        move_tvls.append(move_tvl)
        canopy_tvls.append(canopy_tvl)

        # Determine if boosted TVL is active
        is_boost_active = (month >= activation_months.get('LEAF_PAIRS_START_MONTH', 0))

        # Get boosted TVL
        boosted_tvl = boosted_tvl_model.get_boosted_tvl(
            month, canopy_tvl, move_tvl, is_active=is_boost_active
        )
        boosted_tvls.append(boosted_tvl)

        # Total TVL contributing to revenue
        if is_boost_active:
            total_tvl = canopy_tvl + boosted_tvl
        else:
            total_tvl = canopy_tvl
        total_tvls.append(total_tvl)

        # Calculate revenue
        stable_rev, volatile_rev, total_rev = revenue_model.calculate_revenue(month, total_tvl)
        cumulative_revenue += total_rev
        total_revenues.append(total_rev)
        stable_revenues.append(stable_rev)
        volatile_revenues.append(volatile_rev)
        cumulative_revenues.append(cumulative_revenue)

        # LEAF Pair logic
        if month == activation_months['LEAF_PAIRS_START_MONTH']:
            initial_deals = initialize_deals()
            leaf_model = LEAFPairsModel(leaf_config, initial_deals)

        if leaf_model and month >= activation_months['LEAF_PAIRS_START_MONTH']:
            # Update LEAF pair deals
            total_liquidity = leaf_model.get_total_liquidity(month, leaf_price=previous_leaf_price)
            leaf_price = calculate_leaf_price(month, total_liquidity)
            leaf_prices.append(leaf_price)
            leaf_total_liquidities.append(total_liquidity)
            leaf_model.update_deals(month, leaf_price)
            previous_leaf_price = leaf_price  # Update for next iteration
        else:
            leaf_prices.append(None)
            leaf_total_liquidities.append(0.0)

        # Implement OAK logic when active
        if month >= activation_months.get('OAK_START_MONTH', 0):
            # Placeholder for OAK-related logic
            pass

        # Implement other components as per activation months

    # Output Revenue Table
    print(f"{'Month':<8}{'Stable Rev (M)':>20}{'Volatile Rev (M)':>20}{'Total Rev (M)':>20}{'Cumulative Rev (M)':>25}")
    print("-" * 93)
    for i, month in enumerate(months):
        print(f"{month:<8}{stable_revenues[i] / 1_000_000:>20,.2f}{volatile_revenues[i] / 1_000_000:>20,.2f}{total_revenues[i] / 1_000_000:>20,.2f}{cumulative_revenues[i] / 1_000_000:>25,.2f}")

    # Plotting and Visualization
    plt.figure(figsize=(12, 8))

    # Plot Move TVL, Canopy TVL, Boosted TVL
    plt.subplot(2, 2, 1)
    plt.plot(months, [tvl / 1_000_000_000 for tvl in move_tvls], label='Move TVL')
    plt.plot(months, [tvl / 1_000_000_000 for tvl in canopy_tvls], label='Canopy TVL')
    plt.plot(months, [tvl / 1_000_000_000 for tvl in boosted_tvls], label='Boosted TVL')
    plt.title('TVL Over Time')
    plt.xlabel('Month')
    plt.ylabel('TVL (in billions USD)')
    plt.legend()

    # Plot Revenue
    plt.subplot(2, 2, 2)
    plt.plot(months, [rev / 1_000_000 for rev in total_revenues], label='Total Revenue')
    plt.plot(months, [rev / 1_000_000 for rev in stable_revenues], label='Stable Revenue')
    plt.plot(months, [rev / 1_000_000 for rev in volatile_revenues], label='Volatile Revenue')
    plt.title('Monthly Revenue Over Time')
    plt.xlabel('Month')
    plt.ylabel('Monthly Revenue (in millions USD)')
    plt.legend()

    # Plot Cumulative Revenue
    plt.subplot(2, 2, 3)
    plt.plot(months, [rev / 1_000_000 for rev in cumulative_revenues], label='Cumulative Revenue')
    plt.title('Cumulative Revenue Over Time')
    plt.xlabel('Month')
    plt.ylabel('Cumulative Revenue (in millions USD)')
    plt.legend()

    # Plot LEAF Price if applicable
    plt.subplot(2, 2, 4)
    plt.plot(months, leaf_prices, label='LEAF Price')
    plt.title('LEAF Price Over Time')
    plt.xlabel('Month')
    plt.ylabel('LEAF Price (USD)')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 