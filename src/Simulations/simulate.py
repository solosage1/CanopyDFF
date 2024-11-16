import matplotlib.pyplot as plt # type: ignore
from ..Functions.TVL import TVLModel, TVLModelConfig

def main():
    # Initialize model with configuration
    config = TVLModelConfig(
        initial_move_tvl=800_000_000,          # $800M
        initial_canopy_tvl=350_000_000,       # $350M
        move_growth_rates=[1.5, 1, 0.75, 0.5, 0.4],  # Annual growth rates for 5 years
        min_market_share=0.10,                 # 10%
        market_share_decay_rate=0.02,          # Decay rate
        initial_boost_share=0.10,              # 10%
        boost_growth_rate=1.0                   # Growth rate for boost
    )

    model = TVLModel(config)
    months = list(range(61))  # 0 to 60
    move_tvls = []
    canopy_tvls = []
    boosted_tvls = []
    total_canopy_impact = []
    annual_boosted_growth_rates = []

    # Simulate TVL for 60 months
    for month in months:
        move_tvl, canopy_tvl, boosted_tvl = model.get_tvls(month)
        move_tvls.append(move_tvl)
        canopy_tvls.append(canopy_tvl)
        boosted_tvls.append(boosted_tvl)
        total_canopy_impact.append(canopy_tvl + boosted_tvl)

        # Calculate annual boosted TVL growth rate
        if month >= 12:
            # Compare boosted TVL with the same month in the previous year
            boosted_tvl_previous_year = boosted_tvls[month - 12]
            if boosted_tvl_previous_year > 0:
                annual_growth = ((boosted_tvl - boosted_tvl_previous_year) / boosted_tvl_previous_year) * 100
            else:
                annual_growth = 0.0
            annual_boosted_growth_rates.append(annual_growth)
        else:
            annual_boosted_growth_rates.append(0.0)  # Not enough data for annual growth

    # Display results in a table
    print("{:<10} {:>20} {:>20} {:>25} {:>30}".format(
        "Month", "Move TVL (USD)", "Canopy TVL (USD)", "Boosted TVL (USD)", "Annual Boosted Growth (%)"
    ))
    print("-" * 100)
    for month, move, canopy, boosted, growth in zip(months, move_tvls, canopy_tvls, boosted_tvls, annual_boosted_growth_rates):
        print("{:<10} {:>20,.2f} {:>20,.2f} {:>25,.2f} {:>30,.2f}".format(
            month, move, canopy, boosted, growth
        ))

    # Plot TVL over time
    plt.figure(figsize=(14, 7))
    # Convert to billions for display
    move_tvls_billions = [x / 1_000_000_000 for x in move_tvls]
    canopy_tvls_billions = [x / 1_000_000_000 for x in canopy_tvls]
    boosted_tvls_billions = [x / 1_000_000_000 for x in boosted_tvls]
    total_impact_b = [x / 1_000_000_000 for x in total_canopy_impact]

    plt.plot(months, move_tvls_billions, label='Move TVL', color='blue', linewidth=2)
    plt.plot(months, canopy_tvls_billions, label='Canopy TVL', color='green', linewidth=2)
    plt.plot(months, boosted_tvls_billions, label='Boosted by Canopy TVL', color='orange', linewidth=2)
    plt.plot(months, total_impact_b, label='Total Canopy Impact', color='purple', linestyle='--', linewidth=2)

    plt.title('Move TVL, Canopy TVL, Boosted TVL, and Total Canopy Impact Over 60 Months')
    plt.xlabel('Month')
    plt.ylabel('TVL (Billions USD)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot Annual Boosted TVL Growth Rate
    plt.figure(figsize=(14, 7))
    plt.plot(months, annual_boosted_growth_rates, label='Annual Boosted TVL Growth Rate', color='red', linewidth=2, linestyle='--')
    plt.title('Annual Boosted TVL Growth Rate Over 60 Months')
    plt.xlabel('Month')
    plt.ylabel('Growth Rate (%)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 