from typing import List
from dataclasses import dataclass

@dataclass
class Deal:
    """Unified deal structure for all protocol deals."""
    # Deal Identification
    deal_id: str
    counterparty: str
    start_month: int
    
    # OAK Parameters
    oak_amount: float = 0.0
    oak_vesting_months: int = 0
    oak_irr_threshold: float = 0.0
    oak_distributed_amount: float = 0.0
    
    # TVL Parameters
    tvl_amount: float = 0.0
    tvl_revenue_rate: float = 0.0
    tvl_duration_months: int = 0
    tvl_category: str = "none"  # "none", "volatile", or "lending"
    tvl_accumulated_revenue: float = 0.0
    tvl_active: bool = True
    
    # LEAF Pair Parameters
    leaf_pair_amount: float = 0.0
    leaf_percentage: float = 0.0
    leaf_base_concentration: float = 0.0
    leaf_max_concentration: float = 0.0
    leaf_duration_months: int = 0
    leaf_balance: float = 0.0
    other_balance: float = 0.0
    num_leaf_tokens: float = 0.0
    
    # Linear Ramp Parameters
    linear_ramp_months: int = 0

def generate_deal_id(counterparty: str, sequence: int) -> str:
    """Generate a unique deal ID based on counterparty and sequence number."""
    base = ''.join(filter(str.isalnum, counterparty))[:10]  # Take first 10 alphanumerics
    return f"{base}_{sequence:03d}"

def initialize_deals() -> List[Deal]:
    """Initialize all protocol deals."""
    deals = []
    deal_sequence = {}
    
    def add_deal(counterparty: str, start_month: int, **kwargs):
        """Helper function to add a deal with a unique deal_id."""
        seq = deal_sequence.get(counterparty, 1)
        deal_id = generate_deal_id(counterparty, seq)
        deal_sequence[counterparty] = seq + 1
        deal = Deal(deal_id=deal_id, counterparty=counterparty, start_month=start_month, **kwargs)
        deals.append(deal)
    
    # 1. Initial TVL + OAK Incentive Deals
    add_deal(
        counterparty="AlphaTrading LLC",
        start_month=0,
        tvl_amount=20_000_000,
        tvl_revenue_rate=0.04,
        tvl_duration_months=12,
        tvl_category="volatile",
        oak_amount=800_000,
        oak_vesting_months=12,
        oak_irr_threshold=15.0
    )
    add_deal(
        counterparty="BetaLend Finance",
        start_month=0,
        tvl_amount=80_000_000,
        tvl_revenue_rate=0.005,
        tvl_duration_months=12,
        tvl_category="lending",
        oak_amount=400_000,
        oak_vesting_months=12,
        oak_irr_threshold=15.0
    )
    
    # 2. Team and Investor OAK Deals
    add_deal(
        counterparty="Team",
        start_month=3,
        oak_amount=175_000,
        oak_vesting_months=12,
        oak_irr_threshold=10.0
    )
    add_deal(
        counterparty="Seed Investors",
        start_month=3,
        oak_amount=25_000,
        oak_vesting_months=12,
        oak_irr_threshold=25.0
    )
    add_deal(
        counterparty="Advisors",
        start_month=3,
        oak_amount=25_000,
        oak_vesting_months=12,
        oak_irr_threshold=15.0
    )
    
    # 3. LEAF Pair + TVL Deal
    add_deal(
        counterparty="Move",
        start_month=1,
        leaf_pair_amount=1_500_000,
        leaf_percentage=0.35,
        leaf_base_concentration=0.5,
        leaf_max_concentration=0.8,
        leaf_duration_months=60,
        tvl_amount=1_500_000,
        tvl_revenue_rate=0.02,
        tvl_duration_months=60,
        tvl_category="volatile"
    )
    
    # 4. Monthly Boost Deals
    boost_months = [5, 6, 7, 8, 9, 10]
    boost_thresholds = [55.0, 50.0, 45.0, 40.0, 35.0, 30.0]
    for month, threshold in zip(boost_months, boost_thresholds):
        add_deal(
            counterparty=f"Month {month} - Boost",
            start_month=month,
            oak_amount=10_000,
            oak_vesting_months=0,
            oak_irr_threshold=threshold
        )
    
    # 5. Ramp Schedule TVL Deals
    ramp_schedule = [
        {
            "counterparty": "KappaFi Protocol",
            "start_month": 1,
            "tvl_amount": 43_000_000,
            "tvl_revenue_rate": 0.04,
            "tvl_duration_months": 12,
            "tvl_category": "volatile",
            "linear_ramp_months": 3
        },
        {
            "counterparty": "LambdaVest",
            "start_month": 1,
            "tvl_amount": 57_000_000,
            "tvl_revenue_rate": 0.005,
            "tvl_duration_months": 12,
            "tvl_category": "lending",
            "linear_ramp_months": 3
        },
        {
            "counterparty": "MuTrading Co",
            "start_month": 2,
            "tvl_amount": 44_000_000,
            "tvl_revenue_rate": 0.04,
            "tvl_duration_months": 12,
            "tvl_category": "volatile",
            "linear_ramp_months": 3
        },
        {
            "counterparty": "NuLend Finance",
            "start_month": 2,
            "tvl_amount": 56_000_000,
            "tvl_revenue_rate": 0.005,
            "tvl_duration_months": 12,
            "tvl_category": "lending",
            "linear_ramp_months": 3
        },
        {
            "counterparty": "OmegaX Capital",
            "start_month": 3,
            "tvl_amount": 43_000_000,
            "tvl_revenue_rate": 0.04,
            "tvl_duration_months": 12,
            "tvl_category": "volatile",
            "linear_ramp_months": 3
        },
        {
            "counterparty": "PiVault Solutions",
            "start_month": 3,
            "tvl_amount": 57_000_000,
            "tvl_revenue_rate": 0.005,
            "tvl_duration_months": 12,
            "tvl_category": "lending",
            "linear_ramp_months": 3
        }
    ]
    
    for ramp in ramp_schedule:
        add_deal(**ramp)
    
    return deals

def get_deal_by_counterparty(deals: List[Deal], counterparty: str) -> List[Deal]:
    """Helper function to find all deals by a specific counterparty."""
    return [deal for deal in deals if deal.counterparty == counterparty]

def get_active_deals(deals: List[Deal], month: int) -> List[Deal]:
    """Retrieve all deals that are active in a given month."""
    active_deals = []
    for deal in deals:
        is_active = False
        
        # Check OAK Distribution Activity
        if deal.oak_amount > deal.oak_distributed_amount and month >= deal.start_month:
            is_active = True
        
        # Check TVL Activity
        if deal.tvl_category != "none":
            if deal.start_month <= month < (deal.start_month + deal.tvl_duration_months):
                is_active = True
        
        # Check LEAF Pair Activity
        if deal.leaf_pair_amount > 0:
            if deal.start_month <= month < (deal.start_month + deal.leaf_duration_months):
                is_active = True
        
        # Check Linear Ramp Activity
        if deal.linear_ramp_months > 0:
            if deal.start_month <= month < (deal.start_month + deal.linear_ramp_months):
                is_active = True
        
        if is_active:
            active_deals.append(deal)
    
    return active_deals 