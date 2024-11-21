from typing import List
from dataclasses import dataclass
import logging

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
    oak_revenue_multiple: float = 1.0
    redeemed: bool = False
    
    # TVL Parameters
    tvl_amount: float = 0.0
    tvl_revenue_rate: float = 0.0
    tvl_duration_months: int = 0
    tvl_type: str = "none"      # "ProtocolLocked", "Contracted", "Organic", or "Boosted"
    tvl_accumulated_revenue: float = 0.0
    tvl_active: bool = True
    
    # LEAF Pair Parameters
    leaf_pair_amount: float = 0.0
    target_ratio: float = 0.0        # Renamed from leaf_percentage, defaulted to 0%
    leaf_tokens: float = 0.0         # New field for explicit LEAF token amount
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
    
    def add_deal(**kwargs):
        """Helper function to add a deal with logging."""
        # Generate deal_id if not provided
        if 'deal_id' not in kwargs:
            counterparty = kwargs.get('counterparty', 'Unknown')
            start_month = kwargs.get('start_month', 0)
            kwargs['deal_id'] = f"{counterparty[:10]}_{start_month:03d}"
        
        deal = Deal(**kwargs)
        
        # Log TVL deal OAK allocations
        if deal.tvl_amount > 0 and deal.oak_amount > 0:
            logging.info("\nTVL Deal OAK Allocation:")
            logging.info(f"- Counterparty: {deal.counterparty}")
            logging.info(f"- TVL Amount: ${deal.tvl_amount:,.2f}")
            logging.info(f"- Annual Revenue Rate: {deal.tvl_revenue_rate:.1%}")
            logging.info(f"- Expected Annual Revenue: ${deal.tvl_amount * deal.tvl_revenue_rate:,.2f}")
            logging.info(f"- OAK Amount: {deal.oak_amount:,.2f}")
            logging.info(f"- Revenue Multiple: {deal.oak_revenue_multiple:.1f}x")
            logging.info(f"- IRR Threshold: {deal.oak_irr_threshold:.1%}")
        
        deals.append(deal)
    
    # Initial Contracted TVL (~100M)
    initial_contracts = [
        {
            "counterparty": "Sigma Capital",
            "start_month": 1,
            "tvl_amount": 60_000_000,
            "tvl_revenue_rate": 0.035,  # 3.5% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Tau Lending",
            "start_month": 1,
            "tvl_amount": 40_000_000,
            "tvl_revenue_rate": 0.008,  # 0.8% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        }
    ]
    
    # Growth Phase Contracts (Ramping to ~500M)
    growth_contracts = [
        {
            "counterparty": "Upsilon Ventures",
            "start_month": 4,
            "tvl_amount": 100_000_000,
            "tvl_revenue_rate": 0.042,  # 4.2% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Phi Finance",
            "start_month": 6,
            "tvl_amount": 150_000_000,
            "tvl_revenue_rate": 0.015,  # 1.5% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Chi Trading",
            "start_month": 8,
            "tvl_amount": 150_000_000,
            "tvl_revenue_rate": 0.038,  # 3.8% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        }
    ]
    
    # Renewal Contracts (Maintaining ~300M)
    renewal_contracts = [
        {
            "counterparty": "Sigma Capital",
            "start_month": 13,
            "tvl_amount": 45_000_000,  # 75% renewal
            "tvl_revenue_rate": 0.032,  # 3.2% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Tau Lending",
            "start_month": 13,
            "tvl_amount": 30_000_000,  # 75% renewal
            "tvl_revenue_rate": 0.007,  # 0.7% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Upsilon Ventures",
            "start_month": 16,
            "tvl_amount": 75_000_000,  # 75% renewal
            "tvl_revenue_rate": 0.040,  # 4.0% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Phi Finance",
            "start_month": 18,
            "tvl_amount": 100_000_000,  # ~67% renewal
            "tvl_revenue_rate": 0.012,  # 1.2% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        },
        {
            "counterparty": "Chi Trading",
            "start_month": 20,
            "tvl_amount": 50_000_000,  # ~33% renewal
            "tvl_revenue_rate": 0.035,  # 3.5% annually
            "tvl_duration_months": 12,
            "tvl_type": "Contracted"
        }
    ]
    
    # Add all contracts
    for contract in initial_contracts + growth_contracts + renewal_contracts:
        add_deal(**contract)
    
    # 2. Team and Investor OAK Deals
    add_deal(
        counterparty="Team",
        start_month=3,
        oak_amount=175_000,
        oak_vesting_months=12,
        oak_irr_threshold=25.0
    )
    add_deal(
        counterparty="Seed Investors",
        start_month=3,
        oak_amount=25_000,
        oak_vesting_months=12,
        oak_irr_threshold=65.0
    )
    add_deal(
        counterparty="Advisors",
        start_month=3,
        oak_amount=25_000,
        oak_vesting_months=12,
        oak_irr_threshold=45.0
    )
    
    # 3. LEAF Pair + TVL Deal
    add_deal(
        counterparty="Move",
        start_month=1,
        leaf_pair_amount=1_500_000,
        leaf_tokens=0.0,
        target_ratio=0.35,
        leaf_base_concentration=0.5,
        leaf_max_concentration=0.8,
        leaf_duration_months=60,
        tvl_amount=1_500_000,
        tvl_revenue_rate=0.10,
        tvl_duration_months=60,
        tvl_type="ProtocolLocked"
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
        if deal.tvl_type != "none":
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