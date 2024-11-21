import unittest
import sys
import os
import logging

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Functions.AEGIS import AEGISModel, AEGISConfig
from src.Functions.LEAFPairs import LEAFPairsModel, LEAFPairsConfig
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.TVLContributions import TVLContribution
from src.Data.deal import Deal
from typing import List, Dict, Tuple

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_deal(
    counterparty: str,
    leaf_amount: float,
    other_amount: float,
    leaf_percentage: float = 0.35,
) -> Deal:
    """Helper to create a test deal"""
    return Deal(
        deal_id=f"TEST_{counterparty}",
        counterparty=counterparty,
        start_month=1,
        leaf_pair_amount=leaf_amount + other_amount,
        leaf_percentage=leaf_percentage,
        leaf_base_concentration=0.5,
        leaf_max_concentration=0.8,
        leaf_duration_months=60,
        leaf_balance=leaf_amount,
        other_balance=other_amount,
        num_leaf_tokens=leaf_amount
    )

def calculate_leaf_needed():
    total_usdc = 1_500_000
    target_ratio = 0.35
    current_ratio = 0.0
    
    # Total value after rebalance = USDC + LEAF
    # target_ratio = LEAF / (USDC + LEAF)
    # 0.35 = LEAF / (1.5M + LEAF)
    # 0.35 * (1.5M + LEAF) = LEAF
    # 0.35 * 1.5M + 0.35 * LEAF = LEAF
    # 0.35 * 1.5M = LEAF - 0.35 * LEAF
    # 0.35 * 1.5M = 0.65 * LEAF
    # LEAF = (0.35 * 1.5M) / 0.65
    
    leaf_needed = (target_ratio * total_usdc) / (1 - target_ratio)
    return leaf_needed

class TestLiquidityDepth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Called once before all tests"""
        logger.info("=== Starting Liquidity Depth Test Suite ===")

    def setUp(self):
        """Set up test cases"""
        logger.info("\nSetting up new test case...")
        
        # Create AEGIS model
        aegis_config = AEGISConfig(
            initial_leaf_balance=1_000_000_000,
            initial_usdc_balance=100_000,
            leaf_price_decay_rate=0.0,
            max_months=12,
            oak_to_usdc_rate=1.0,
            oak_to_leaf_rate=1.0
        )
        self.aegis_model = AEGISModel(aegis_config)
        logger.info("AEGIS model initialized with 1B LEAF and 100M USDC")
        
        # Initialize deals starting at month 1
        deals = [
            Deal(
                deal_id="TEST_1",
                counterparty="Test1",
                start_month=1,
                tvl_amount=1_000_000,
                tvl_revenue_rate=0.04,
                tvl_duration_months=12,
                tvl_type="ProtocolLocked",
                leaf_pair_amount=1_000_000,
                leaf_percentage=0.35,
                leaf_base_concentration=0.5,
                leaf_max_concentration=0.8,
                leaf_duration_months=12
            ),
            Deal(
                deal_id="TEST_2",
                counterparty="Test2",
                start_month=1,
                tvl_amount=500_000,
                tvl_revenue_rate=0.04,
                tvl_duration_months=12,
                tvl_type="ProtocolLocked",
                leaf_pair_amount=500_000,
                leaf_percentage=0.35,
                leaf_base_concentration=0.5,
                leaf_max_concentration=0.8,
                leaf_duration_months=12
            )
        ]
        
        # Initialize models
        leaf_pairs_config = LEAFPairsConfig()
        self.leaf_pairs_model = LEAFPairsModel(leaf_pairs_config, deals)
        
        # Step forward to month 1
        self.leaf_pairs_model.month = 1
        self.leaf_pairs_model.update_deals(1, 1.0)  # Update for month 1 at $1.00
        
        # Add TVL contributions
        tvl_config = TVLModelConfig()
        self.tvl_model = TVLModel(tvl_config)
        for deal in deals:
            contribution = TVLContribution(
                id=len(self.tvl_model.contributions) + 1,
                counterparty=deal.counterparty,
                amount_usd=deal.tvl_amount,
                revenue_rate=deal.tvl_revenue_rate,
                start_month=deal.start_month,
                end_month=deal.start_month + deal.tvl_duration_months,
                tvl_type=deal.tvl_type
            )
            self.tvl_model.add_contribution(contribution)
            logger.info(f"Added TVL contribution: ${deal.tvl_amount:,.2f} from {deal.counterparty}")
        
        logger.info("LEAF Pairs model initialized with protocol-locked deals")

    def test_a_liquidity_depth_calculation(self):
        """Test liquidity depth calculations at various price ranges"""
        logger.info("\nTesting liquidity depth calculations...")
        current_price = 1.0
        test_ranges = [1, 2, 5, 10]

        # Test AEGIS liquidity
        logger.info("\nTesting AEGIS liquidity:")
        for pct in test_ranges:
            leaf, usdc = self.aegis_model.get_liquidity_within_percentage(pct, current_price)
            logger.info(f"  {pct}% range: {leaf:,.2f} LEAF, ${usdc:,.2f} USDC")
            
            # Verify AEGIS results
            self.assertGreaterEqual(leaf, 0, f"AEGIS LEAF liquidity should be non-negative at {pct}%")
            self.assertGreaterEqual(usdc, 0, f"AEGIS USDC liquidity should be non-negative at {pct}%")
            self.assertLessEqual(leaf, self.aegis_model.leaf_balance, f"AEGIS LEAF liquidity exceeds total at {pct}%")
            self.assertLessEqual(usdc, self.aegis_model.usdc_balance, f"AEGIS USDC liquidity exceeds total at {pct}%")
            
            # Verify increasing liquidity with wider ranges
            if pct > 1:
                prev_leaf, prev_usdc = self.aegis_model.get_liquidity_within_percentage(pct-1, current_price)
                self.assertGreaterEqual(leaf, prev_leaf, f"AEGIS LEAF liquidity should increase with range")
                self.assertGreaterEqual(usdc, prev_usdc, f"AEGIS USDC liquidity should increase with range")

        # Test LEAF Pairs liquidity
        logger.info("\nTesting LEAF Pairs liquidity:")
        for pct in test_ranges:
            leaf, usdc = self.leaf_pairs_model.get_liquidity_within_percentage(pct, current_price)
            logger.info(f"  {pct}% range: {leaf:,.2f} LEAF, ${usdc:,.2f} USDC")
            
            # Verify LEAF Pairs results
            self.assertGreaterEqual(leaf, 0, f"LEAF Pairs LEAF liquidity should be non-negative at {pct}%")
            self.assertGreaterEqual(usdc, 0, f"LEAF Pairs USDC liquidity should be non-negative at {pct}%")
            self.assertLessEqual(leaf, self.leaf_pairs_model.get_leaf_liquidity(), f"LEAF Pairs LEAF liquidity exceeds total at {pct}%")
            self.assertLessEqual(usdc, self.leaf_pairs_model.get_usd_liquidity(), f"LEAF Pairs USDC liquidity exceeds total at {pct}%")
            
            # Verify increasing liquidity with wider ranges
            if pct > 1:
                prev_leaf, prev_usdc = self.leaf_pairs_model.get_liquidity_within_percentage(pct-1, current_price)
                self.assertGreaterEqual(leaf, prev_leaf, f"LEAF Pairs LEAF liquidity should increase with range")
                self.assertGreaterEqual(usdc, prev_usdc, f"LEAF Pairs USDC liquidity should increase with range")

    def test_b_price_impact(self):
        """Test liquidity depth at different price points"""
        logger.info("\nTesting price impact...")
        test_prices = [0.8, 0.9, 1.0, 1.1, 1.2]
        pct_range = 5

        for price in test_prices:
            aegis_leaf, aegis_usdc = self.aegis_model.get_liquidity_within_percentage(pct_range, price)
            leaf_pairs_leaf, leaf_pairs_usdc = self.leaf_pairs_model.get_liquidity_within_percentage(pct_range, price)
            
            logger.info(f"\nPrice ${price:.2f}:")
            logger.info(f"  AEGIS: {aegis_leaf:,.2f} LEAF, ${aegis_usdc:,.2f} USDC")
            logger.info(f"  LEAF Pairs: {leaf_pairs_leaf:,.2f} LEAF, ${leaf_pairs_usdc:,.2f} USDC")
            
            # Calculate total USD value
            aegis_value = (aegis_leaf * price) + aegis_usdc
            leaf_pairs_value = (leaf_pairs_leaf * price) + leaf_pairs_usdc
            
            # Verify reasonable values
            self.assertGreaterEqual(aegis_value, 0, f"AEGIS total value out of range at price {price}")
            self.assertGreaterEqual(leaf_pairs_value, 0, f"LEAF Pairs total value out of range at price {price}")

    def test_c_combined_liquidity(self):
        """Test combined liquidity from both systems"""
        logger.info("\nTesting combined liquidity...")
        
        current_price = 1.0
        pct_range = 5

        aegis_leaf, aegis_usdc = self.aegis_model.get_liquidity_within_percentage(pct_range, current_price)
        leaf_pairs_leaf, leaf_pairs_usdc = self.leaf_pairs_model.get_liquidity_within_percentage(pct_range, current_price)
        
        combined_value = ((aegis_leaf + leaf_pairs_leaf) * current_price) + (aegis_usdc + leaf_pairs_usdc)
        
        logger.info(f"AEGIS: {aegis_leaf:,.2f} LEAF, ${aegis_usdc:,.2f} USDC")
        logger.info(f"LEAF Pairs: {leaf_pairs_leaf:,.2f} LEAF, ${leaf_pairs_usdc:,.2f} USDC")
        logger.info(f"Combined Value: ${combined_value:,.2f}")
        
        # Verify combined liquidity
        self.assertGreater(combined_value, 0, "Combined liquidity should be positive")
        
        # Update expected maximum based on actual liquidity provided
        expected_max = (1_000_000_000 * current_price) + 100_000_000  # AEGIS: 1B LEAF + 100M USDC
        expected_max += 1_500_000  # LEAF Pairs: $1.5M USDC
        self.assertLessEqual(combined_value, expected_max, 
            "Combined liquidity exceeds total possible value")
        
        # Verify it's greater than either individual system
        aegis_value = (aegis_leaf * current_price) + aegis_usdc
        leaf_pairs_value = (leaf_pairs_leaf * current_price) + leaf_pairs_usdc
        
        self.assertGreaterEqual(combined_value, aegis_value, 
            "Combined value should be >= AEGIS value")
        self.assertGreaterEqual(combined_value, leaf_pairs_value, 
            "Combined value should be >= LEAF Pairs value")

    def test_d_liquidity_imbalance(self):
        """Test liquidity balance across price ranges"""
        logger.info("\nTesting liquidity imbalance...")
        
        current_price = 1.0
        pct_range = 10
        lower_price = current_price * 0.9  # -10%
        upper_price = current_price * 1.1  # +10%

        # Get liquidity from both systems
        aegis_leaf, aegis_usdc = self.aegis_model.get_liquidity_within_percentage(pct_range, current_price)
        leaf_pairs_leaf, leaf_pairs_usdc = self.leaf_pairs_model.get_liquidity_within_percentage(pct_range, current_price)
        
        # Calculate total liquidity on each side
        total_leaf = aegis_leaf + leaf_pairs_leaf
        total_usdc = aegis_usdc + leaf_pairs_usdc
        
        # Calculate USD value on each side
        buy_side_value = total_usdc  # USDC available to buy LEAF
        sell_side_value = total_leaf * current_price  # LEAF available to sell
        
        logger.info(f"\nLiquidity within ±10% of ${current_price:.2f}:")
        logger.info(f"Buy side (USDC):  ${buy_side_value:,.2f}")
        logger.info(f"Sell side (LEAF): ${sell_side_value:,.2f}")
        
        # Calculate imbalance
        imbalance = abs(buy_side_value - sell_side_value)
        if buy_side_value > sell_side_value:
            logger.info(f"\nImbalanced towards buyers: ${imbalance:,.2f} more USDC than LEAF")
            logger.info(f"Need {imbalance/current_price:,.2f} more LEAF to balance")
        else:
            logger.info(f"\nImbalanced towards sellers: ${imbalance:,.2f} more LEAF than USDC")
            logger.info(f"Need ${imbalance:,.2f} more USDC to balance")
        
        # Calculate percentage imbalance
        total_value = buy_side_value + sell_side_value
        imbalance_pct = (imbalance / total_value) * 100 if total_value > 0 else 0
        logger.info(f"Imbalance is {imbalance_pct:.1f}% of total liquidity")

    @classmethod
    def tearDownClass(cls):
        """Called once after all tests"""
        logger.info("\n=== Completed Liquidity Depth Test Suite ===")

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLiquidityDepth)
    
    # Create a test runner with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    print("\nRunning Liquidity Depth Tests...")
    result = runner.run(suite)
