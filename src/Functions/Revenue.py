from dataclasses import dataclass
from typing import Dict, List, Optional
from src.Data.deal import Deal, get_active_deals
from src.Functions.TVLContributions import TVLContribution

class RevenueModel:
    """Model for calculating protocol revenue from TVL contributions."""
    
    def __init__(self):
        self.cumulative_revenue = 0.0
        self.revenue_history: Dict[int, Dict[str, float]] = {}
        
    def calculate_revenue_from_deals(self, deals: List[Deal], month: int) -> Dict[str, float]:
        """
        Calculate monthly revenue from active deals.
        
        Args:
            deals: List of all deals
            month: Current month
            
        Returns:
            Dictionary of revenue by category (ProtocolLocked, Contracted, Organic, Boosted)
        """
        revenue_by_category = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        active_deals = get_active_deals(deals, month)
        
        for deal in active_deals:
            if deal.tvl_category == "none":
                continue
                
            # Calculate revenue based on TVL amount and revenue rate
            monthly_revenue = deal.tvl_amount * deal.tvl_revenue_rate / 12
            
            # Determine revenue category based on deal type
            if deal.linear_ramp_months > 0:
                # For ramped deals, calculate the ramp progress
                ramp_progress = min(1.0, (month - deal.start_month) / deal.linear_ramp_months)
                monthly_revenue *= ramp_progress
                revenue_by_category['Contracted'] += monthly_revenue
            elif deal.oak_amount > 0:
                # Deals with OAK incentives are considered Boosted
                revenue_by_category['Boosted'] += monthly_revenue
            elif deal.leaf_pair_amount > 0:
                # LEAF pair deals are considered Protocol Locked
                revenue_by_category['ProtocolLocked'] += monthly_revenue
            else:
                # All other TVL is considered Organic
                revenue_by_category['Organic'] += monthly_revenue
        
        # Store revenue history
        self.revenue_history[month] = revenue_by_category.copy()
        
        return revenue_by_category
    
    def calculate_revenue_from_contributions(self, contributions: List[TVLContribution], month: int) -> Dict[str, float]:
        """
        Calculate monthly revenue from TVL contributions (legacy support).
        
        Args:
            contributions: List of TVL contributions
            month: Current month
            
        Returns:
            Dictionary of revenue by category
        """
        revenue_by_category = {
            'ProtocolLocked': 0.0,
            'Contracted': 0.0,
            'Organic': 0.0,
            'Boosted': 0.0
        }
        
        active_contributions = [
            contrib for contrib in contributions 
            if contrib.active and contrib.start_month <= month < contrib.end_month
        ]
        
        for contribution in active_contributions:
            monthly_revenue = contribution.amount_usd * contribution.revenue_rate / 12
            revenue_by_category[contribution.tvl_type] += monthly_revenue
        
        # Store revenue history
        self.revenue_history[month] = revenue_by_category.copy()
        
        return revenue_by_category
    
    def get_monthly_revenue(self, month: int) -> Optional[Dict[str, float]]:
        """Get revenue breakdown for a specific month."""
        return self.revenue_history.get(month)
    
    def get_total_revenue(self, month: int) -> float:
        """Get total revenue for a specific month."""
        monthly_revenue = self.get_monthly_revenue(month)
        if monthly_revenue:
            return sum(monthly_revenue.values())
        return 0.0
    
    def get_cumulative_revenue(self, through_month: int) -> float:
        """Get cumulative revenue through specified month."""
        return sum(
            sum(monthly_revenue.values())
            for month, monthly_revenue in self.revenue_history.items()
            if month <= through_month
        )
    
    def get_state(self) -> Dict:
        """Get current state of revenue model."""
        return {
            'cumulative_revenue': self.cumulative_revenue,
            'revenue_history': self.revenue_history.copy()
        }