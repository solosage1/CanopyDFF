from src.Functions.OAK import OAKDistributionDeal

def get_oak_distribution_deals():
    """
    Returns a list of OAKDistributionDeal instances representing the initial OAK deals.
    """
    deals = [
        OAKDistributionDeal(
            counterparty="Team",
            oak_amount=175_000,
            start_month=0,
            vesting_months=12,
            irr_threshold=10.0
        ),
        OAKDistributionDeal(
            counterparty="EarlyInvestor2",
            oak_amount=25_000,
            start_month=0,
            vesting_months=12,
            irr_threshold=25.0
        ),
        OAKDistributionDeal(
            counterparty="StrategicPartner",
            oak_amount=250_000,
            start_month=0,
            vesting_months=18,
            irr_threshold=12.0
        ),
        OAKDistributionDeal(
            counterparty="TeamAndAdvisors",
            oak_amount=200_000,
            start_month=0,
            vesting_months=24,
            irr_threshold=15.0
        ),
    ]
    return deals 