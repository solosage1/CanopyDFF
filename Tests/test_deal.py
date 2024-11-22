import unittest
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.Data.deal import Deal, initialize_deals, get_active_deals, get_deal_by_counterparty, generate_deal_id

class TestDeal(unittest.TestCase):
    def setUp(self):
        """Initialize test deals."""
        self.test_deals = initialize_deals()
        
    def test_deal_initialization(self):
        """Test basic deal creation with all parameter types."""
        deal = Deal(
            deal_id="test_001",
            counterparty="Test Protocol",
            start_month=1,
            # OAK parameters
            oak_amount=100_000,
            oak_vesting_months=12,
            oak_irr_threshold=20.0,
            # TVL parameters
            tvl_amount=1_000_000,
            tvl_revenue_rate=0.04,
            tvl_duration_months=12,
            tvl_type="Contracted",
            # LEAF parameters
            leaf_pair_amount=500_000,
            target_ratio=0.3,
            leaf_base_concentration=0.5,
            leaf_max_concentration=0.8,
            leaf_duration_months=12,
            # Linear ramp
            linear_ramp_months=3
        )
        
        # Test deal identification
        self.assertEqual(deal.deal_id, "test_001")
        self.assertEqual(deal.counterparty, "Test Protocol")
        self.assertEqual(deal.start_month, 1)
        
        # Test OAK parameters
        self.assertEqual(deal.oak_amount, 100_000)
        self.assertEqual(deal.oak_vesting_months, 12)
        self.assertEqual(deal.oak_irr_threshold, 20.0)
        self.assertEqual(deal.oak_distributed_amount, 0.0)
        
        # Test TVL parameters
        self.assertEqual(deal.tvl_amount, 1_000_000)
        self.assertEqual(deal.tvl_revenue_rate, 0.04)
        self.assertEqual(deal.tvl_duration_months, 12)
        self.assertEqual(deal.tvl_type, "Contracted")
        self.assertTrue(deal.tvl_active)
        
        # Test LEAF parameters
        self.assertEqual(deal.leaf_pair_amount, 500_000)
        self.assertEqual(deal.target_ratio, 0.3)
        self.assertEqual(deal.leaf_base_concentration, 0.5)
        self.assertEqual(deal.leaf_max_concentration, 0.8)
        
        # Test linear ramp
        self.assertEqual(deal.linear_ramp_months, 3)

    def test_generate_deal_id(self):
        """Test deal ID generation."""
        # Test basic ID generation
        deal_id = generate_deal_id("Test Protocol", 1)
        self.assertEqual(deal_id, "TestProtoc_001")
        
        # Test with special characters
        deal_id = generate_deal_id("Test & Protocol!", 2)
        self.assertEqual(deal_id, "TestProtoc_002")
        
        # Test with numbers in name
        deal_id = generate_deal_id("Test123", 3)
        self.assertEqual(deal_id, "Test123_003")

    def test_initialize_deals(self):
        """Test the initialization of all protocol deals."""
        deals = self.test_deals
        
        # Test initial TVL deals
        sigma_deals = get_deal_by_counterparty(deals, "Sigma Capital")
        self.assertEqual(len(sigma_deals), 2)  # Initial + Renewal deal
        
        # Test total TVL amount for initial Sigma deal
        initial_sigma = [d for d in sigma_deals if d.start_month == 1][0]
        self.assertEqual(initial_sigma.tvl_amount, 60_000_000)
        
        # Test boost deals
        boost_deals = [d for d in deals if "Boost" in d.counterparty]
        self.assertEqual(len(boost_deals), 6)  # Should have 6 boost deals
        
        # Test ramp deals
        ramp_deals = [d for d in deals if d.linear_ramp_months > 0]
        self.assertEqual(len(ramp_deals), 0)  # No deals have linear_ramp_months set

    def test_get_active_deals(self):
        """Test active deal filtering for different months."""
        deals = self.test_deals
        
        # Month 0: Only initial deals should be active
        month_0_deals = get_active_deals(deals, 0)
        self.assertEqual(
            len([d for d in deals if d.tvl_type == "Contracted" and d.start_month == 1]), 
            2  # Sigma Capital and Tau Lending
        )
        
        # Month 1: Should include Move deal
        month_1_deals = get_active_deals(deals, 1)
        self.assertTrue(
            any(d.counterparty == "Move" for d in month_1_deals)
        )
        
        # Month 5: Should include boost deals
        month_5_deals = get_active_deals(deals, 5)
        self.assertTrue(
            any("Boost" in d.counterparty for d in month_5_deals)
        )

    def test_get_deal_by_counterparty(self):
        """Test counterparty filtering."""
        deals = self.test_deals
        
        # Test existing counterparty
        move_deals = get_deal_by_counterparty(deals, "Move")
        self.assertEqual(len(move_deals), 1)
        self.assertEqual(move_deals[0].leaf_pair_amount, 1_500_000)
        
        # Test non-existent counterparty
        nonexistent_deals = get_deal_by_counterparty(deals, "NonExistent")
        self.assertEqual(len(nonexistent_deals), 0)
        
        # Test case sensitivity
        case_deals = get_deal_by_counterparty(deals, "MOVE")
        self.assertEqual(len(case_deals), 0)

    def test_deal_categories(self):
        """Test TVL type validation and filtering."""
        deals = self.test_deals
        
        # Test contracted deals
        contracted_deals = [d for d in deals if d.tvl_type == "Contracted"]
        self.assertTrue(len(contracted_deals) > 0)
        
        # Test protocol locked deals
        locked_deals = [d for d in deals if d.tvl_type == "ProtocolLocked"]
        self.assertTrue(len(locked_deals) > 0)
        
        # Verify no invalid types
        valid_types = ["none", "Contracted", "ProtocolLocked", "Organic", "Boosted"]
        invalid_deals = [d for d in deals if d.tvl_type not in valid_types]
        self.assertEqual(len(invalid_deals), 0)

if __name__ == '__main__':
    unittest.main() 