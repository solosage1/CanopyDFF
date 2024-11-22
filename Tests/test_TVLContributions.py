import unittest
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.Functions.TVLContributions import TVLContribution
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
            leaf_pair_amount=1_000_000,
            tvl_amount=5_000_000,
            tvl_revenue_rate=0.05,
            tvl_duration_months=12,
            tvl_type="ProtocolLocked"
        )
        
    def test_contribution_initialization(self):
        """Test basic TVL contribution creation."""
        contribution = TVLContribution(
            id=1,
            counterparty="TestProtocol",
            amount_usd=5_000_000,
            revenue_rate=0.05,
            start_month=1,
            end_month=13,
            tvl_type="ProtocolLocked"
        )
        
        self.assertEqual(contribution.amount_usd, 5_000_000)
        self.assertEqual(contribution.revenue_rate, 0.05)
        self.assertEqual(contribution.tvl_type, "ProtocolLocked")
        self.assertTrue(contribution.active)
        
    def test_get_current_amount(self):
        """Test amount calculation based on month."""
        contribution = TVLContribution(
            id=1,
            counterparty="Test",
            amount_usd=1_000_000,
            revenue_rate=0.04,
            start_month=1,
            end_month=13,
            tvl_type="Contracted"
        )
        
        # Before start
        self.assertEqual(contribution.get_current_amount(0), 0)
        
        # During active period
        self.assertEqual(contribution.get_current_amount(1), 1_000_000)
        
        # After end
        self.assertEqual(contribution.get_current_amount(13), 0)

if __name__ == '__main__':
    unittest.main()
