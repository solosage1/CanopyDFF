import unittest
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.Functions.LEAFPairs import LEAFPairsConfig, LEAFPairsModel
from src.Data.deal import Deal
from src.Functions.UniswapV2Math import UniswapV2Math

class TestLEAFPairs(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = LEAFPairsConfig()
        
        # Create test deals with LEAF pair parameters
        self.leaf_heavy_deal = Deal(
            deal_id="test_001",
            counterparty="LeafHeavy",
            start_month=1,
            leaf_pair_amount=1_000_000,
            leaf_tokens=250_000,  # Explicit LEAF token amount
            target_ratio=0.25,    # Target for future purchases
            leaf_base_concentration=0.5,
            leaf_max_concentration=1.0,
            leaf_duration_months=12
        )
        
        self.leaf_light_deal = Deal(
            deal_id="test_002",
            counterparty="LeafLight",
            start_month=1,
            leaf_pair_amount=2_000_000,
            leaf_tokens=600_000,  # Explicit LEAF token amount
            target_ratio=0.30,    # Target for future purchases
            leaf_base_concentration=0.4,
            leaf_max_concentration=0.8,
            leaf_duration_months=12
        )
        
        # Initialize model with test deals
        self.model = LEAFPairsModel(self.config, [self.leaf_heavy_deal, self.leaf_light_deal])
        self.model.month = 1  # Set current month to 1 so deals are active

    def test_deal_initialization(self):
        """Test that deals are properly initialized with correct balances."""
        for deal in self.model.deals:
            # Check that balances are initialized to explicit values
            self.assertEqual(deal.leaf_balance, deal.leaf_tokens)
            self.assertEqual(deal.other_balance, deal.leaf_pair_amount - (deal.leaf_tokens * 1.0))
            
            # Check that total value matches leaf_pair_amount
            total_value = deal.leaf_balance + deal.other_balance  # At $1 LEAF price
            self.assertAlmostEqual(total_value, deal.leaf_pair_amount, places=2)
            
            # Check LEAF percentage is correct
            leaf_ratio = deal.leaf_balance / deal.leaf_pair_amount
            self.assertAlmostEqual(leaf_ratio, deal.target_ratio, places=2)  # Changed from leaf_percentage

    def test_get_active_deals(self):
        """Test active deal filtering."""
        # Month 1: Both deals should be active
        active_month_1 = self.model.get_active_deals(1)
        self.assertEqual(len(active_month_1), 2)
        
        # Month 13: No deals should be active
        active_month_13 = self.model.get_active_deals(13)
        self.assertEqual(len(active_month_13), 0)
        
        # Month 0: No deals should be active
        active_month_0 = self.model.get_active_deals(0)
        self.assertEqual(len(active_month_0), 0)

    def test_get_total_liquidity(self):
        """Test total liquidity calculation at different price points."""
        test_prices = [0.5, 1.0, 2.0]
        
        for price in test_prices:
            total_liquidity = self.model.get_total_liquidity(1, price)
            
            # Calculate expected liquidity
            expected_liquidity = sum(
                (deal.leaf_balance * price + deal.other_balance)
                for deal in self.model.deals
            )
            
            self.assertAlmostEqual(total_liquidity, expected_liquidity, places=2)
            print(f"\nAt LEAF price ${price:.2f}:")
            print(f"Total liquidity: ${total_liquidity:,.2f}")

    def test_liquidity_within_percentage(self):
        """Test liquidity calculation within percentage range."""
        current_price = 1.0  # Use constant price for test
        percentage = 5.0  # 5% range
        
        leaf_amount, other_amount = self.model.get_liquidity_within_percentage(
            percentage, current_price
        )
        
        print(f"\nLiquidity within {percentage}% range at ${current_price:.2f}:")
        print(f"LEAF amount: {leaf_amount:,.2f}")
        print(f"Other amount: ${other_amount:,.2f}")
        print(f"Total value: ${(leaf_amount * current_price) + other_amount:,.2f}")
        
        self.assertGreater(leaf_amount, 0)
        self.assertGreater(other_amount, 0)

    def test_add_new_deal(self):
        """Test adding a new deal to the model."""
        new_deal = Deal(
            deal_id="test_003",
            counterparty="NewPair",
            start_month=2,
            leaf_pair_amount=500_000,
            leaf_tokens=100_000,     # Explicit LEAF token amount
            target_ratio=0.20,       # Target for future purchases
            leaf_base_concentration=0.6,
            leaf_max_concentration=0.9,
            leaf_duration_months=12
        )
        
        initial_deal_count = len(self.model.deals)
        self.model.add_deal(new_deal)
        
        self.assertEqual(len(self.model.deals), initial_deal_count + 1)
        self.assertIn(new_deal, self.model.deals)

    def test_invalid_deal_validation(self):
        """Test validation of invalid deals."""
        # Test invalid target ratio
        with self.assertRaises(ValueError):
            invalid_deal = Deal(
                deal_id="test_004",
                counterparty="Invalid",
                start_month=1,
                leaf_pair_amount=100_000,
                leaf_tokens=60_000,      # Explicit LEAF token amount
                target_ratio=0.6,        # Invalid ratio (>50%)
                leaf_base_concentration=0.5,
                leaf_max_concentration=0.8,
                leaf_duration_months=12
            )
            self.model.add_deal(invalid_deal)
        
        # Test duplicate counterparty
        with self.assertRaises(ValueError):
            duplicate_deal = Deal(
                deal_id="test_005",
                counterparty="LeafHeavy",  # Duplicate counterparty
                start_month=1,
                leaf_pair_amount=100_000,
                leaf_tokens=30_000,      # Explicit LEAF token amount
                target_ratio=0.3,        # Target for future purchases
                leaf_base_concentration=0.5,
                leaf_max_concentration=0.8,
                leaf_duration_months=12
            )
            self.model.add_deal(duplicate_deal)

    def test_state_recording(self):
        """Test that deal states are properly recorded."""
        self.model.update_deals(1, 1.0)  # Update at month 1, price $1.0
        
        self.assertIn(1, self.model.balance_history)
        state = self.model.balance_history[1]
        
        self.assertEqual(len(state), 2)  # Should have records for both deals
        for counterparty, leaf_balance, other_balance in state:
            self.assertGreater(leaf_balance, 0)
            self.assertGreater(other_balance, 0)

if __name__ == '__main__':
    unittest.main() 