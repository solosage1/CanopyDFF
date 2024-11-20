import unittest
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.Functions.TVLContributions import TVLContribution, TVLContributionHistory
from src.Data.deal import Deal, initialize_deals

class TestTVLContributions(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_deals = initialize_deals()
        
        # Create test deals for specific scenarios
        self.protocol_locked_deal = Deal(
            deal_id="test_001",
            counterparty="TestProtocol",
            start_month=1,
            leaf_pair_amount=1_000_000,  # Makes it ProtocolLocked
            tvl_amount=5_000_000,
            tvl_revenue_rate=0.05,
            tvl_duration_months=12,
            tvl_category="volatile"
        )
        
        self.contracted_deal = Deal(
            deal_id="test_002",
            counterparty="TestContract",
            start_month=1,
            tvl_amount=2_000_000,
            tvl_revenue_rate=0.04,
            tvl_duration_months=12,
            tvl_category="lending",
            linear_ramp_months=3  # Makes it Contracted
        )
        
        self.boosted_deal = Deal(
            deal_id="test_003",
            counterparty="TestBoost",
            start_month=1,
            oak_amount=10_000,  # Makes it Boosted
            tvl_amount=3_000_000,
            tvl_revenue_rate=0.06,
            tvl_duration_months=12,
            tvl_category="volatile"
        )
        
        self.organic_deal = Deal(
            deal_id="test_004",
            counterparty="TestOrganic",
            start_month=1,
            tvl_amount=1_000_000,
            tvl_revenue_rate=0.03,
            tvl_duration_months=12,
            tvl_category="lending"
        )

    def test_deal_to_contribution_protocol_locked(self):
        """Test conversion of ProtocolLocked deal to TVLContribution."""
        contribution = TVLContributionHistory.deal_to_contribution(self.protocol_locked_deal)
        self.assertIsNotNone(contribution)
        self.assertEqual(contribution.tvl_type, "ProtocolLocked")
        self.assertEqual(contribution.amount_usd, 5_000_000)
        self.assertEqual(contribution.revenue_rate, 0.05)
        self.assertEqual(contribution.category, "volatile")

    def test_deal_to_contribution_contracted(self):
        """Test conversion of Contracted deal to TVLContribution."""
        contribution = TVLContributionHistory.deal_to_contribution(self.contracted_deal)
        self.assertIsNotNone(contribution)
        self.assertEqual(contribution.tvl_type, "Contracted")
        self.assertEqual(contribution.amount_usd, 2_000_000)
        self.assertEqual(contribution.category, "lending")

    def test_deal_to_contribution_boosted(self):
        """Test conversion of Boosted deal to TVLContribution."""
        contribution = TVLContributionHistory.deal_to_contribution(self.boosted_deal)
        self.assertIsNotNone(contribution)
        self.assertEqual(contribution.tvl_type, "Boosted")
        self.assertEqual(contribution.amount_usd, 3_000_000)
        self.assertEqual(contribution.category, "volatile")

    def test_deal_to_contribution_organic(self):
        """Test conversion of Organic deal to TVLContribution."""
        contribution = TVLContributionHistory.deal_to_contribution(self.organic_deal)
        self.assertIsNotNone(contribution)
        self.assertEqual(contribution.tvl_type, "Organic")
        self.assertEqual(contribution.amount_usd, 1_000_000)
        self.assertEqual(contribution.category, "lending")

    def test_get_contributions_from_deals(self):
        """Test conversion of multiple deals to TVLContributions."""
        test_deals = [
            self.protocol_locked_deal,
            self.contracted_deal,
            self.boosted_deal,
            self.organic_deal
        ]
        contributions = TVLContributionHistory.get_contributions_from_deals(test_deals)
        self.assertEqual(len(contributions), 4)
        
        # Verify all TVL types are represented
        tvl_types = {c.tvl_type for c in contributions}
        self.assertEqual(
            tvl_types, 
            {"ProtocolLocked", "Contracted", "Boosted", "Organic"}
        )

    def test_get_active_contributions(self):
        """Test filtering of active contributions."""
        test_deals = [
            self.protocol_locked_deal,
            self.contracted_deal,
            self.boosted_deal,
            self.organic_deal
        ]
        
        # Test month 1 (all should be active)
        month_1_contributions = TVLContributionHistory.get_active_contributions(test_deals, 1)
        self.assertEqual(len(month_1_contributions), 4)
        
        # Test month 13 (all should be inactive due to duration)
        month_13_contributions = TVLContributionHistory.get_active_contributions(test_deals, 13)
        self.assertEqual(len(month_13_contributions), 0)

    def test_get_tvl_by_type(self):
        """Test TVL aggregation by type."""
        test_deals = [
            self.protocol_locked_deal,
            self.contracted_deal,
            self.boosted_deal,
            self.organic_deal
        ]
        
        tvl_by_type = TVLContributionHistory.get_tvl_by_type(test_deals, 1)
        
        self.assertEqual(tvl_by_type["ProtocolLocked"], 5_000_000)
        self.assertEqual(tvl_by_type["Contracted"], 2_000_000)
        self.assertEqual(tvl_by_type["Boosted"], 3_000_000)
        self.assertEqual(tvl_by_type["Organic"], 1_000_000)

    def test_get_tvl_by_category(self):
        """Test TVL aggregation by category."""
        test_deals = [
            self.protocol_locked_deal,
            self.contracted_deal,
            self.boosted_deal,
            self.organic_deal
        ]
        
        tvl_by_category = TVLContributionHistory.get_tvl_by_category(test_deals, 1)
        
        # Protocol Locked (5M) + Boosted (3M) = 8M volatile
        self.assertEqual(tvl_by_category["volatile"], 8_000_000)
        # Contracted (2M) + Organic (1M) = 3M lending
        self.assertEqual(tvl_by_category["lending"], 3_000_000)

    def test_invalid_deal_conversion(self):
        """Test handling of invalid deals."""
        # Deal with no TVL
        invalid_deal = Deal(
            deal_id="test_005",
            counterparty="TestInvalid",
            start_month=1
        )
        contribution = TVLContributionHistory.deal_to_contribution(invalid_deal)
        self.assertIsNone(contribution)
        
        # Deal with zero TVL
        zero_tvl_deal = Deal(
            deal_id="test_006",
            counterparty="TestZero",
            start_month=1,
            tvl_amount=0,
            tvl_category="volatile"
        )
        contribution = TVLContributionHistory.deal_to_contribution(zero_tvl_deal)
        self.assertIsNone(contribution)

if __name__ == '__main__':
    unittest.main()
