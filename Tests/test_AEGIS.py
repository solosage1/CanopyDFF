import unittest
from src.Functions.AEGIS import AEGISConfig, AEGISModel

class TestAEGISModel(unittest.TestCase):
    def setUp(self):
        self.config = AEGISConfig(
            initial_leaf_balance=1_000_000_000,
            initial_usdc_balance=500_000,
            leaf_price_decay_rate=0.005,
            max_months=60
        )
        self.aegis_model = AEGISModel(self.config)

    def test_initial_state(self):
        state = self.aegis_model.get_state()
        self.assertEqual(state['leaf_balance'], 1_000_000_000)
        self.assertEqual(state['usdc_balance'], 500_000)
        self.assertEqual(state['leaf_price'], 1.0)

    def test_redemption(self):
        """Test redemption with specific month and rate"""
        initial_leaf = self.aegis_model.leaf_balance
        initial_usdc = self.aegis_model.usdc_balance
        test_month = 1
        test_rate = 0.02  # 2% redemption
        
        # Execute redemption
        leaf_redeemed, usdc_redeemed = self.aegis_model.handle_redemptions(test_month, test_rate)
        
        # Calculate expected values
        expected_leaf_redeemed = initial_leaf * test_rate
        expected_usdc_redeemed = initial_usdc * test_rate
        expected_leaf_balance = initial_leaf - expected_leaf_redeemed
        expected_usdc_balance = initial_usdc - expected_usdc_redeemed
        
        print(f"\nTesting redemption:")
        print(f"Month: {test_month}")
        print(f"Initial LEAF: {initial_leaf:,.2f}")
        print(f"Initial USDC: {initial_usdc:,.2f}")
        print(f"Redemption rate: {test_rate:.1%}")
        print(f"LEAF redeemed: {leaf_redeemed:,.2f}")
        print(f"USDC redeemed: {usdc_redeemed:,.2f}")
        print(f"Expected LEAF balance: {expected_leaf_balance:,.2f}")
        print(f"Actual LEAF balance: {self.aegis_model.leaf_balance:,.2f}")
        print(f"Expected USDC balance: {expected_usdc_balance:,.2f}")
        print(f"Actual USDC balance: {self.aegis_model.usdc_balance:,.2f}")
        
        # Test balances
        self.assertAlmostEqual(self.aegis_model.leaf_balance, expected_leaf_balance)
        self.assertAlmostEqual(self.aegis_model.usdc_balance, expected_usdc_balance)
        
        # Test that redeemed amounts match expected
        self.assertAlmostEqual(leaf_redeemed, expected_leaf_redeemed)
        self.assertAlmostEqual(usdc_redeemed, expected_usdc_redeemed)
        
        # Test that we can't redeem twice in same month
        with self.assertRaises(ValueError):
            self.aegis_model.handle_redemptions(test_month, test_rate)
        
        # Test that we can redeem in a different month
        next_month = test_month + 1
        self.aegis_model.handle_redemptions(next_month, test_rate)

    def test_market_decay(self):
        self.aegis_model.apply_market_decay()
        expected_leaf_price = 1.0 * (1 - 0.005)
        self.assertAlmostEqual(self.aegis_model.leaf_price, expected_leaf_price)

    def test_step(self):
        """Test monthly step updates"""
        month = 1
        self.aegis_model.step(month)
        
        # Check that histories are updated
        self.assertEqual(len(self.aegis_model.leaf_balance_history), 1)
        self.assertEqual(len(self.aegis_model.usdc_balance_history), 1)
        self.assertEqual(len(self.aegis_model.leaf_price_history), 1)
        
        # Check that price decay was applied
        expected_price = 1.0 * (1 - self.config.leaf_price_decay_rate)
        self.assertAlmostEqual(self.aegis_model.leaf_price, expected_price)

    def test_usdc_insufficient(self):
        """Test redemption with low USDC balance"""
        # Set USDC balance low
        self.aegis_model.usdc_balance = 10_000
        month = 1
        redemption_rate = 0.02
        
        # Execute redemption
        leaf_redeemed, usdc_redeemed = self.aegis_model.handle_redemptions(month, redemption_rate)
        
        # Verify proportional redemption
        self.assertEqual(usdc_redeemed, 10_000 * redemption_rate)
        self.assertEqual(leaf_redeemed, 1_000_000_000 * redemption_rate)

    def test_get_liquidity_within_percentage_basic(self):
        """Test basic functionality of get_liquidity_within_percentage"""
        leaf_amount, usdc_amount = self.aegis_model.get_liquidity_within_percentage(
            percentage=5,  # 5% price range
            current_price=1.0  # $1 per LEAF
        )
        
        # Amounts should be positive and not exceed balances
        self.assertGreater(leaf_amount, 0)
        self.assertGreater(usdc_amount, 0)
        self.assertLessEqual(leaf_amount, self.aegis_model.leaf_balance)
        self.assertLessEqual(usdc_amount, self.aegis_model.usdc_balance)

    def test_get_liquidity_within_percentage_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        # Test negative percentage
        with self.assertRaises(ValueError):
            self.aegis_model.get_liquidity_within_percentage(-5, 1.0)
        
        # Test percentage > 100
        with self.assertRaises(ValueError):
            self.aegis_model.get_liquidity_within_percentage(101, 1.0)

    def test_get_liquidity_within_percentage_price_changes(self):
        """Test liquidity calculations at different price points"""
        print("\nTesting liquidity at different price points:")
        print("--------------------------------------------")
        
        # Test at current price = $1
        leaf_1, usdc_1 = self.aegis_model.get_liquidity_within_percentage(5, 1.0)
        print(f"\nAt price $1.00:")
        print(f"LEAF within range: {leaf_1:,.2f} ({(leaf_1/self.aegis_model.leaf_balance)*100:.2f}% of total)")
        print(f"USDC within range: {usdc_1:,.2f} ({(usdc_1/self.aegis_model.usdc_balance)*100:.2f}% of total)")
        
        # Test at higher price = $2
        leaf_2, usdc_2 = self.aegis_model.get_liquidity_within_percentage(5, 2.0)
        print(f"\nAt price $2.00:")
        print(f"LEAF within range: {leaf_2:,.2f} ({(leaf_2/self.aegis_model.leaf_balance)*100:.2f}% of total)")
        print(f"USDC within range: {usdc_2:,.2f} ({(usdc_2/self.aegis_model.usdc_balance)*100:.2f}% of total)")
        
        # Test at lower price = $0.5
        leaf_3, usdc_3 = self.aegis_model.get_liquidity_within_percentage(5, 0.5)
        print(f"\nAt price $0.50:")
        print(f"LEAF within range: {leaf_3:,.2f} ({(leaf_3/self.aegis_model.leaf_balance)*100:.2f}% of total)")
        print(f"USDC within range: {usdc_3:,.2f} ({(usdc_3/self.aegis_model.usdc_balance)*100:.2f}% of total)")
        
        print("\nComparing amounts:")
        print(f"LEAF at $2.00 vs $1.00: {leaf_2/leaf_1:.3f}x")
        print(f"LEAF at $0.50 vs $1.00: {leaf_3/leaf_1:.3f}x")
        print(f"USDC at $2.00 vs $1.00: {usdc_2/usdc_1:.3f}x")
        print(f"USDC at $0.50 vs $1.00: {usdc_3/usdc_1:.3f}x")
        
        # Higher price should result in less LEAF liquidity within range
        self.assertLess(leaf_2, leaf_1)
        # Lower price should result in more LEAF liquidity within range
        self.assertGreater(leaf_3, leaf_1)

    def test_get_liquidity_within_percentage_range_sizes(self):
        """Test liquidity calculations with different percentage ranges"""
        print("\nTesting different percentage ranges:")
        print("------------------------------------")
        
        # Get liquidity for 5% range
        leaf_5, usdc_5 = self.aegis_model.get_liquidity_within_percentage(5, 1.0)
        print(f"\nAt 5% range:")
        print(f"LEAF within range: {leaf_5:,.2f} ({(leaf_5/self.aegis_model.leaf_balance)*100:.2f}% of total)")
        print(f"USDC within range: {usdc_5:,.2f} ({(usdc_5/self.aegis_model.usdc_balance)*100:.2f}% of total)")
        
        # Get liquidity for 10% range
        leaf_10, usdc_10 = self.aegis_model.get_liquidity_within_percentage(10, 1.0)
        print(f"\nAt 10% range:")
        print(f"LEAF within range: {leaf_10:,.2f} ({(leaf_10/self.aegis_model.leaf_balance)*100:.2f}% of total)")
        print(f"USDC within range: {usdc_10:,.2f} ({(usdc_10/self.aegis_model.usdc_balance)*100:.2f}% of total)")
        
        print("\nComparing ranges:")
        print(f"LEAF at 10% vs 5%: {leaf_10/leaf_5:.3f}x")
        print(f"USDC at 10% vs 5%: {usdc_10/usdc_5:.3f}x")
        
        # Larger range should include more liquidity
        self.assertGreater(leaf_10, leaf_5)
        self.assertGreater(usdc_10, usdc_5)

    def test_get_liquidity_within_percentage_usdc_concentration(self):
        """Test that USDC liquidity is properly concentrated"""
        print("\nTesting USDC concentration:")
        print("---------------------------")
        
        leaf_amount, usdc_amount = self.aegis_model.get_liquidity_within_percentage(5, 1.0)
        
        # Calculate the proportion of total amounts that are within range
        leaf_proportion = leaf_amount / self.aegis_model.leaf_balance
        usdc_proportion = usdc_amount / self.aegis_model.usdc_balance
        
        print(f"\nAt 5% range:")
        print(f"LEAF proportion: {leaf_proportion:.6f}")
        print(f"USDC proportion: {usdc_proportion:.6f}")
        print(f"USDC/LEAF proportion ratio: {usdc_proportion/leaf_proportion:.2f}x")
        print(f"Expected max USDC proportion: {min(1.0, leaf_proportion * 5):.6f}")
        
        # USDC proportion should be up to 5x the LEAF proportion
        self.assertLessEqual(usdc_proportion, min(1.0, leaf_proportion * 5))
        self.assertGreater(usdc_proportion, leaf_proportion)

    def test_get_liquidity_within_percentage_empty_balances(self):
        """Test behavior with zero balances"""
        # Set balances to 0
        self.aegis_model.leaf_balance = 0
        self.aegis_model.usdc_balance = 0
        
        leaf_amount, usdc_amount = self.aegis_model.get_liquidity_within_percentage(5, 1.0)
        
        # Should return 0 for both
        self.assertEqual(leaf_amount, 0)
        self.assertEqual(usdc_amount, 0)

if __name__ == '__main__':
    unittest.main() 