from src.Functions.OAK import OAKDistributionDeal

def get_oak_distribution_deals():
    """
    Returns a list of OAKDistributionDeal instances representing the initial OAK deals.
    """
    deals = [
        OAKDistributionDeal(
            counterparty="Team",
            oak_amount=175_000,
            start_month=3,
            vesting_months=12,
            irr_threshold=10.0
        ),
        OAKDistributionDeal(
            counterparty="Seed Investors",
            oak_amount=25_000,
            start_month=3,
            vesting_months=12,
            irr_threshold=25.0
        ),
        OAKDistributionDeal(
            counterparty="Advisors",
            oak_amount=25_000,
            start_month=3,
            vesting_months=12,
            irr_threshold=15.0
        ),
        OAKDistributionDeal(
            counterparty="Month 5 - Boost",
            oak_amount=10_000,
            start_month=5,
            vesting_months=0,
            irr_threshold=55.0
        ),
                OAKDistributionDeal(
            counterparty="Month 6 - Boost",
            oak_amount=10_000,
            start_month=6,
            vesting_months=0,
            irr_threshold=50.0
        ),
                OAKDistributionDeal(
            counterparty="Month 7 - Boost",
            oak_amount=10_000,
            start_month=7,
            vesting_months=0,
            irr_threshold=45.0
        ),
                OAKDistributionDeal(
            counterparty="Month 8 - Boost",
            oak_amount=10_000,
            start_month=8,
            vesting_months=0,
            irr_threshold=40.0
        ),
                OAKDistributionDeal(
            counterparty="Month 9 - Boost",
            oak_amount=10_000,
            start_month=9,
            vesting_months=0,
            irr_threshold=35.0
        ),
                OAKDistributionDeal(
            counterparty="Month 5 - Boost",
            oak_amount=10_000,
            start_month=10,
            vesting_months=0,
            irr_threshold=30.0
        ),
    ]
    return deals 