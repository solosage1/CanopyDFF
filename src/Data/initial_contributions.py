from typing import List, Dict

INITIAL_CONTRIBUTIONS = {
    'Contracted': [
        # Initial Month 0 ($100M)
        {
            'amount_usd': 20_000_000,  # $20M volatile
            'start_month': 0,
            'revenue_rate': 0.04,
            'duration_months': 12,
            'counterparty': 'AlphaTrading LLC',
            'category': 'volatile'
        },
        {
            'amount_usd': 80_000_000,  # $80M lending
            'start_month': 0,
            'revenue_rate': 0.005,
            'duration_months': 12,
            'counterparty': 'BetaLend Finance',
            'category': 'lending'
        }
    ]
}

# Ramp schedule for first 3 months
RAMP_SCHEDULE = [
    # Month 1 (+$100M)
    {
        'month': 1,
        'volatile': 43_000_000,
        'lending': 57_000_000
    },
    # Month 2 (+$100M)
    {
        'month': 2,
        'volatile': 44_000_000,
        'lending': 56_000_000
    },
    # Month 3 (+$100M)
    {
        'month': 3,
        'volatile': 43_000_000,
        'lending': 57_000_000
    }
]

# List of potential counterparties for monthly additions
COUNTERPARTIES = [
    'KappaFi Protocol', 'LambdaVest', 'MuTrading Co', 'NuLend Finance',
    'OmegaX Capital', 'PiVault Solutions', 'RhoFi Trading', 'SigmaLend',
    'TauVest Capital', 'UpsilonX Finance', 'PhiLending', 'ChiTrading LLC'
]
