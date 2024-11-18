from typing import List, Dict

INITIAL_CONTRIBUTIONS = {
    'ProtocolLocked': [
        {
            'amount_usd': 50_000_000,
            'start_month': 3,
            'revenue_rate': 0.005
        },
        {
            'amount_usd': 1_500_000,
            'start_month': 0,
            'revenue_rate': 0.04
        }
    ],
    'Contracted': [
        {
            'amount_usd': 200_000_000,
            'start_month': 0,
            'revenue_rate': 0.01,
            'duration_months': 12
        },
        {
            'amount_usd': 200_000_000,
            'start_month': 0,
            'revenue_rate': 0.045,
            'duration_months': 12
        }
    ],
    'Organic': [
        {
            'amount_usd': 16_000_000,
            'start_month': 0,
            'revenue_rate': 0.03,
            'decay_rate': 0.01
        }
    ],
    'Boosted': [
        {
            'amount_usd': 10_000_000,
            'start_month': 6,
            'revenue_rate': 0.01,
            'expected_boost_rate': 0.05
        }
    ]
}
