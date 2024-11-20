from dataclasses import dataclass
from typing import Dict, List, Optional
from src.Data.deal import Deal

@dataclass
class TVLContribution:
    """Legacy class for backward compatibility."""
    counterparty: str
    amount_usd: float
    revenue_rate: float
    start_month: int
    end_month: int
    tvl_type: str  # 'ProtocolLocked', 'Contracted', 'Organic', or 'Boosted'
    category: str  # 'volatile' or 'lending'
    active: bool = True

class TVLContributionHistory:
    """Handles conversion between Deal and TVLContribution objects."""
    
    @staticmethod
    def deal_to_contribution(deal: Deal) -> Optional[TVLContribution]:
        """Convert a Deal to a TVLContribution."""
        if deal.tvl_amount <= 0 or deal.tvl_category == "none":
            return None
            
        # Determine TVL type based on deal attributes
        tvl_type = "Organic"  # default
        if deal.leaf_pair_amount > 0:
            tvl_type = "ProtocolLocked"
        elif deal.linear_ramp_months > 0:
            tvl_type = "Contracted"
        elif deal.oak_amount > 0:
            tvl_type = "Boosted"
            
        return TVLContribution(
            counterparty=deal.counterparty,
            amount_usd=deal.tvl_amount,
            revenue_rate=deal.tvl_revenue_rate,
            start_month=deal.start_month,
            end_month=deal.start_month + deal.tvl_duration_months,
            tvl_type=tvl_type,
            category=deal.tvl_category,
            active=deal.tvl_active
        )

    @staticmethod
    def get_contributions_from_deals(deals: List[Deal]) -> List[TVLContribution]:
        """Convert a list of Deals to TVLContributions."""
        contributions = []
        for deal in deals:
            contribution = TVLContributionHistory.deal_to_contribution(deal)
            if contribution:
                contributions.append(contribution)
        return contributions

    @staticmethod
    def get_active_contributions(deals: List[Deal], month: int) -> List[TVLContribution]:
        """Get active TVL contributions for a given month from deals."""
        contributions = TVLContributionHistory.get_contributions_from_deals(deals)
        return [
            c for c in contributions 
            if c.active and c.start_month <= month < c.end_month
        ]

    @staticmethod
    def get_tvl_by_type(deals: List[Deal], month: int) -> Dict[str, float]:
        """Get TVL amounts grouped by type."""
        active_deals = [d for d in deals if d.start_month <= month < (d.start_month + d.tvl_duration_months)]
        
        tvl_by_type = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        for deal in active_deals:
            if deal.tvl_amount > 0 and deal.tvl_type in tvl_by_type:
                tvl_by_type[deal.tvl_type] += deal.tvl_amount
            
        return tvl_by_type

    @staticmethod
    def get_tvl_by_category(deals: List[Deal], month: int) -> Dict[str, float]:
        """Get TVL amounts grouped by category (volatile/lending)."""
        contributions = TVLContributionHistory.get_active_contributions(deals, month)
        tvl_by_category = {
            'volatile': 0.0,
            'lending': 0.0
        }
        
        for contribution in contributions:
            if contribution.category in tvl_by_category:
                tvl_by_category[contribution.category] += contribution.amount_usd
            
        return tvl_by_category