import unittest
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.Functions.AEGIS import AEGISConfig, AEGISModel
from src.Data.deal import Deal, initialize_deals

class TestAEGISModel(unittest.TestCase):
    def setUp(self):
        """Initialize test environment."""
        self.config = AEGISConfig(
            initial_leaf_balance=1_000_000_000,
            initial_usdc_balance=500_000,
            leaf_price_decay_rate=0.005,
            max_months=60,
            oak_to_usdc_rate=1.0,
            oak_to_leaf_rate=1.0
        )
        self.aegis_model = AEGISModel(self.config)
        self.test_deals = initialize_deals()

    def test_initial_state(self):
        """Test initial state of AEGIS model."""
        state = self.aegis_model.get_state()
        self.assertEqual(state['leaf_balance'], 1_000_000_000)
        self.assertEqual(state['usdc_balance'], 500_000)
        self.assertEqual(state['leaf_price'], 1.0)
        self.assertEqual(state['oak_to_usdc_rate'], 1.0)
        self.assertEqual(state['oak_to_leaf_rate'], 1.0)
        
        # Test initial history
        self.assertEqual(self.aegis_model.leaf_balance_history[0], 1_000_000_000)
        self.assertEqual(self.aegis_model.usdc_balance_history[0], 500_000)
        self.assertEqual(self.aegis_model.leaf_price_history[0], 1.0)

    def test_redemption_mechanics(self):
        """Test redemption process with various scenarios."""
        # Test basic redemption
        month = 1
        redemption_rate = 0.02
        leaf_redeemed, usdc_redeemed = self.aegis_model.handle_redemptions(month, redemption_rate)
        
        expected_leaf = self.config.initial_leaf_balance * redemption_rate
        expected_usdc = self.config.initial_usdc_balance * redemption_rate
        
        self.assertAlmostEqual(leaf_redeemed, expected_leaf)
        self.assertAlmostEqual(usdc_redeemed, expected_usdc)
        
        # Test double redemption prevention
        with self.assertRaises(ValueError):
            self.aegis_model.handle_redemptions(month, redemption_rate)
            
        # Test redemption history tracking
        self.assertEqual(self.aegis_model.redemption_history[month], redemption_rate)

    def test_market_decay(self):
        """Test price decay mechanics."""
        initial_price = self.aegis_model.leaf_price
        
        # Test single decay step
        self.aegis_model.apply_market_decay()
        expected_price = initial_price * (1 - self.config.leaf_price_decay_rate)
        self.assertAlmostEqual(self.aegis_model.leaf_price, expected_price)
        
        # Test multiple decay steps
        for _ in range(3):
            self.aegis_model.apply_market_decay()
        expected_price *= (1 - self.config.leaf_price_decay_rate) ** 3
        self.assertAlmostEqual(self.aegis_model.leaf_price, expected_price)

    def test_monthly_step(self):
        """Test monthly update process."""
        initial_price = self.aegis_model.leaf_price
        
        # Test multiple months
        for month in range(1, 4):
            self.aegis_model.step(month)
            
            # Verify history updates
            self.assertEqual(self.aegis_model.leaf_balance_history[month], 
                           self.aegis_model.leaf_balance)
            self.assertEqual(self.aegis_model.usdc_balance_history[month], 
                           self.aegis_model.usdc_balance)
            self.assertEqual(len(self.aegis_model.leaf_price_history), month + 1)
            
            # Verify price decay
            expected_price = initial_price * (1 - self.config.leaf_price_decay_rate) ** month
            self.assertAlmostEqual(self.aegis_model.leaf_price, expected_price)

    def test_liquidity_calculation(self):
        """Test liquidity calculation within price ranges."""
        # Test normal case
        leaf_amount, usdc_amount = self.aegis_model.get_liquidity_within_percentage(5, 1.0)
        self.assertGreater(leaf_amount, 0)
        self.assertGreater(usdc_amount, 0)
        self.assertLessEqual(leaf_amount, self.aegis_model.leaf_balance)
        self.assertLessEqual(usdc_amount, self.aegis_model.usdc_balance)
        
        # Test invalid inputs
        with self.assertRaises(ValueError):
            self.aegis_model.get_liquidity_within_percentage(-5, 1.0)
        with self.assertRaises(ValueError):
            self.aegis_model.get_liquidity_within_percentage(101, 1.0)
            
        # Test zero balance case
        self.aegis_model.leaf_balance = 0
        leaf_amount, usdc_amount = self.aegis_model.get_liquidity_within_percentage(5, 1.0)
        self.assertEqual(leaf_amount, 0)
        self.assertEqual(usdc_amount, 0)

    def test_balance_updates(self):
        """Test balance update mechanics."""
        initial_leaf = self.aegis_model.leaf_balance
        initial_usdc = self.aegis_model.usdc_balance
        
        # Test positive changes
        self.aegis_model.update_balances(usdc_change=1000, leaf_change=2000)
        self.assertEqual(self.aegis_model.usdc_balance, initial_usdc + 1000)
        self.assertEqual(self.aegis_model.leaf_balance, initial_leaf + 2000)
        
        # Test negative changes
        self.aegis_model.update_balances(usdc_change=-500, leaf_change=-1000)
        self.assertEqual(self.aegis_model.usdc_balance, initial_usdc + 500)
        self.assertEqual(self.aegis_model.leaf_balance, initial_leaf + 1000)
        
        # Test negative balance prevention
        self.aegis_model.update_balances(
            usdc_change=-self.aegis_model.usdc_balance * 2,
            leaf_change=-self.aegis_model.leaf_balance * 2
        )
        self.assertEqual(self.aegis_model.usdc_balance, 0)
        self.assertEqual(self.aegis_model.leaf_balance, 0)

    def test_integration_with_deals(self):
        """Test AEGIS interaction with Deal structure."""
        # Find a deal with LEAF pairs
        leaf_pair_deal = next(
            deal for deal in self.test_deals 
            if deal.leaf_pair_amount > 0
        )
        
        # Test balance updates from deal
        initial_leaf = self.aegis_model.leaf_balance
        initial_usdc = self.aegis_model.usdc_balance
        
        self.aegis_model.update_balances(
            leaf_change=leaf_pair_deal.leaf_pair_amount,
            usdc_change=leaf_pair_deal.leaf_pair_amount  # Assuming 1:1 ratio
        )
        
        self.assertEqual(
            self.aegis_model.leaf_balance, 
            initial_leaf + leaf_pair_deal.leaf_pair_amount
        )
        self.assertEqual(
            self.aegis_model.usdc_balance, 
            initial_usdc + leaf_pair_deal.leaf_pair_amount
        )

if __name__ == '__main__':
    unittest.main() 