import unittest
import sys
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)
logger = logging.getLogger(__name__)
# Clear existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
logger.addHandler(logging.StreamHandler())

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Functions.OAK import OAKDistributionDeal, OAKDistributionConfig, OAKModel
from src.Simulations.simulate import create_oak_deal_from_tvl

class TestOAKModel(unittest.TestCase):
    def setUp(self):
        logger.info("\n=== Setting up new test case ===")
        # Create test deals with distribution schedules
        self.deal1 = OAKDistributionDeal(
            counterparty="Counterparty_A",
            oak_amount=100_000,
            start_month=1,
            vesting_months=6,
            irr_threshold=75.0
        )
        self.deal2 = OAKDistributionDeal(
            counterparty="Counterparty_B",
            oak_amount=200_000,
            start_month=1,
            vesting_months=12,
            irr_threshold=65.0
        )
        self.deal3 = OAKDistributionDeal(
            counterparty="Counterparty_C",
            oak_amount=200_000,
            start_month=12,
            vesting_months=6,
            irr_threshold=70.0
        )

        # Initialize configuration
        self.config = OAKDistributionConfig(
            total_oak_supply=500_000,
            redemption_start_month=12,
            redemption_end_month=48,
            deals=[self.deal1, self.deal2, self.deal3]
        )

        # Initialize model
        self.model = OAKModel(self.config)

    def test_initial_distribution_state(self):
        """Test initial distribution state of deals."""
        logger.info("\n=== Testing Initial Distribution State ===")
        
        for deal in self.model.config.deals:
            self.assertEqual(
                deal.distributed_amount, 
                0, 
                f"Initial distributed amount for {deal.counterparty} should be 0"
            )
            logger.info(f"{deal.counterparty}: {deal.distributed_amount} OAK distributed")
    
    def test_monthly_distribution(self):
        """Test cliff distribution at end of vesting."""
        logger.info("\n=== Testing Cliff Distribution ===")
        
        # Store original amounts
        original_amount_1 = self.deal1.oak_amount
        original_amount_2 = self.deal2.oak_amount
        
        # Test month 7 (deal1 vesting completion)
        distributions = self.model.process_monthly_distributions(7)
        self.assertAlmostEqual(
            distributions.get("Counterparty_A", 0),
            original_amount_1,  # Compare against stored original amount
            msg=f"Expected full amount ({original_amount_1} OAK) for Counterparty_A at vesting end"
        )
        
        # Test month 13 (deal2 vesting completion)
        distributions = self.model.process_monthly_distributions(13)
        self.assertAlmostEqual(
            distributions.get("Counterparty_B", 0),
            original_amount_2,  # Compare against stored original amount
            msg=f"Expected full amount ({original_amount_2} OAK) for Counterparty_B at vesting end"
        )
    
    def test_vesting_completion(self):
        """Test that distributions stop after vesting period."""
        logger.info("\n=== Testing Vesting Completion ===")
        
        # Store original amounts
        original_amount_1 = self.deal1.oak_amount
        original_amount_2 = self.deal2.oak_amount
        original_amount_3 = self.deal3.oak_amount
        
        total_distributed = defaultdict(float)
        
        # Process 24 months
        for month in range(1, 25):
            distributions = self.model.process_monthly_distributions(month)
            for counterparty, amount in distributions.items():
                total_distributed[counterparty] += amount
            logger.info(f"Month {month} distributions: {distributions}")
        
        # Check that each deal distributed the correct amount
        self.assertAlmostEqual(
            total_distributed["Counterparty_A"],
            original_amount_1,  # Compare against original amount
            msg="Deal 1 should be fully distributed"
        )
        
        self.assertAlmostEqual(
            total_distributed["Counterparty_B"],
            original_amount_2,  # Compare against original amount
            msg="Deal 2 should be fully distributed"
        )
        
        self.assertAlmostEqual(
            total_distributed["Counterparty_C"],
            original_amount_3,  # Compare against original amount
            msg="Deal 3 should be fully distributed"
        )
        
        # Verify no further distributions after vesting
        for month in range(25, 30):
            distributions = self.model.process_monthly_distributions(month)
            self.assertEqual(
                len(distributions), 
                0, 
                f"Unexpected distribution in month {month}: {distributions}"
            )
    
    def test_distribution_before_start(self):
        """Test that no distributions occur before start_month."""
        logger.info("\n=== Testing Distribution Before Start ===")
        
        # Test month 0 (before any deals start)
        distributions = self.model.process_monthly_distributions(0)
        self.assertEqual(
            len(distributions), 
            0,
            "No distributions should occur before any deals start"
        )
        logger.info(f"Month 0 distributions: {distributions}")
    
    def test_distribution_tracking(self):
        """Test that distributed amounts are properly tracked."""
        logger.info("\n=== Testing Distribution Tracking ===")
        
        # Store original amounts
        original_amount_1 = self.deal1.oak_amount
        original_amount_2 = self.deal2.oak_amount
        
        # Process 7 months (until deal1's vesting completion)
        for month in range(1, 8):
            distributions = self.model.process_monthly_distributions(month)
            logger.info(f"Month {month} distributions: {distributions}")
        
        # Check deal1 distributed amount
        self.assertAlmostEqual(
            self.deal1.distributed_amount,
            original_amount_1,  # Compare against stored original amount
            msg="Incorrect tracking of distributed amount for deal1"
        )
        
        # Process until deal2's vesting completion
        for month in range(8, 14):
            distributions = self.model.process_monthly_distributions(month)
            logger.info(f"Month {month} distributions: {distributions}")
        
        # Check deal2 distributed amount
        self.assertAlmostEqual(
            self.deal2.distributed_amount,
            original_amount_2,  # Compare against stored original amount
            msg="Incorrect tracking of distributed amount for deal2"
        )
    
    def test_ir_threshold(self):
        """Test that redemptions occur when IRR is below threshold."""
        logger.info("\n=== Testing IR Threshold ===")
        logger.info("Stepping to month 25 (after redemption start) with low IRR scenario")
        
        # Step to month 25 with low IRR scenario
        redemption_amount, supply_before, supply_after, usdc_redeemed, leaf_redeemed = self.model.step(
            current_month=25,
            aegis_usdc=5000,    # Further reduced USDC
            aegis_leaf=250,     # Further reduced LEAF
            current_leaf_price=0.1  # Low price to decrease value per OAK
        )
        
        state = self.model.get_state()
        logger.info(f"Month 25 state: {state}")
        self.assertGreater(redemption_amount, 0, "Expected redemptions due to low IRR")
    
    def test_irr_calculation(self):
        """Test IRR calculation based on redemption progress."""
        logger.info("\n=== Testing IRR Calculation ===")
        logger.info("Stepping to month 40 (later in redemption period) with low IRR scenario")
        
        # Step to month 40 with low IRR scenario
        redemption_amount, supply_before, supply_after, usdc_redeemed, leaf_redeemed = self.model.step(
            current_month=40,
            aegis_usdc=1000,    # Further reduced USDC
            aegis_leaf=100,     # Further reduced LEAF
            current_leaf_price=0.05  # Very low price
        )
        
        state = self.model.get_state()
        logger.info(f"Month 40 state: {state}")
        self.assertGreater(redemption_amount, 0, "Expected redemptions due to low IRR")
    
    def test_no_redemption_above_irr_threshold(self):
        """Test that no redemptions occur when IRR is above threshold."""
        logger.info("\n=== Testing No Redemption Above IRR Threshold ===")
        logger.info("Stepping to month 13 with high value assets")
        
        # Step to month 13 with high IRR scenario
        redemption_amount, supply_before, supply_after, usdc_redeemed, leaf_redeemed = self.model.step(
            current_month=13,
            aegis_usdc=100_000,      # Increased USDC
            aegis_leaf=50_000,       # Increased LEAF
            current_leaf_price=10.0  # High price to ensure high IRR
        )
        
        state = self.model.get_state()
        logger.info(f"Month 13 state: {state}")
        self.assertEqual(redemption_amount, 0, "Expected no redemptions when IRR is above threshold")
    
    def test_value_based_redemptions(self):
        """Test redemption behavior based on value differences."""
        logger.info("\n=== Testing Value-Based Redemptions ===")
        
        # Early in redemption period (month 15) - should not trigger redemption
        redemption_amount, total_oak, remaining_oak, _, _ = self.model.step(
            current_month=15,
            aegis_usdc=5000,    # Further reduced USDC
            aegis_leaf=250,     # Further reduced LEAF
            current_leaf_price=0.1  # Low price to decrease value per OAK
        )
        
        state = self.model.get_state()
        logger.info(f"Month 15 state: {state}")
        self.assertEqual(redemption_amount, 0, "Expected no redemptions due to high IRR early in redemption period")
        
        # Later in redemption period (month 40) - should trigger redemption
        redemption_amount, total_oak, remaining_oak, _, _ = self.model.step(
            current_month=40,
            aegis_usdc=1000,    # Further reduced USDC
            aegis_leaf=100,     # Further reduced LEAF
            current_leaf_price=0.05  # Very low price
        )
        
        redemption_progress = (40 - self.config.redemption_start_month) / (self.config.redemption_end_month - self.config.redemption_start_month)
        logger.info(f"\nMonth 40:")
        logger.info(f"Redemption progress: {redemption_progress:.2%}")
        logger.info(f"Redemption amount: {redemption_amount}")
        
        self.assertGreater(redemption_amount, 0, "Expected redemptions due to low IRR")

    def test_full_simulation(self):
        """Test running a full 48-month simulation."""
        logger.info("\n=== Testing Full 48-Month Simulation ===")
        
        for month in range(1, 49):
            leaf_price = 1.0  # Example leaf price; adjust as needed
            redemption_amount, supply_before, supply_after, usdc_redeemed, leaf_redeemed = self.model.step(
                current_month=month,
                aegis_usdc=5000,    # Example USDC; adjust as needed
                aegis_leaf=250,     # Example LEAF; adjust as needed
                current_leaf_price=leaf_price
            )
            logger.info(f"Month {month}: Redemption Amount={redemption_amount}, Supply Before={supply_before}, Supply After={supply_after}")
        
        # Add appropriate assertions based on expected outcomes
        # For demonstration, ensure that total redemption does not exceed supply
        self.assertLessEqual(self.model.get_monthly_redemption_amount(48), self.config.total_oak_supply, "Total redemptions should not exceed total supply")

    def test_get_best_case_irr(self):
        """Test the best case IRR calculation."""
        logger.info("\n=== Testing Best Case IRR Calculation ===")
        irr = self.model.get_best_case_irr(
            aegis_usdc=100_000,        # Example USDC
            aegis_leaf=50_000,         # Example LEAF
            current_leaf_price=5.0,     # Current LEAF price
            current_month=12            # Current month
        )
        logger.info(f"Calculated IRR: {irr:.2f}%")
        self.assertIsInstance(irr, float, "IRR should be a float value")
        # Add more assertions based on expected IRR value

    def test_tvl_incentive_deal_creation(self):
        """Test creation of OAK deals for TVL."""
        logger.info("\n=== Testing TVL Incentive Deal Creation ===")
        
        # Create test OAK model with initial state
        test_oak_model = OAKModel(OAKDistributionConfig(total_oak_supply=500_000))
        
        # Test with qualifying TVL
        incentive_deal = create_oak_deal_from_tvl(
            tvl_type="Contracted",
            amount_usd=10_000_000,
            revenue_rate=0.04,
            start_month=5,
            duration_months=12,
            counterparty="QualifyingLP",
            oak_model=test_oak_model,
            aegis_usdc=1_000_000,
            aegis_leaf=100_000,
            current_leaf_price=1.0
        )
        
        # Verify deal was created correctly
        self.assertIsNotNone(incentive_deal)
        self.assertEqual(
            incentive_deal.counterparty,
            "QualifyingLP_TVL_Incentive"
        )
        self.assertEqual(
            incentive_deal.oak_amount,
            400_000  # $10M * 0.04 = $400k worth of OAK at $1/OAK
        )

    def test_tvl_incentive_integration(self):
        """Test integration of TVL incentives with OAK model."""
        logger.info("\n=== Testing TVL Incentive Integration ===")
        
        # Create and add a TVL incentive deal
        incentive_deal = OAKDistributionDeal(
            counterparty="TestLP_TVL_Incentive",
            oak_amount=100_000,
            start_month=5,
            vesting_months=12,
            irr_threshold=15.0  # Lower threshold for TVL incentives
        )
        
        # Add to model's deals
        original_deal_count = len(self.model.config.deals)
        self.model.config.deals.append(incentive_deal)
        
        # Process distributions through vesting period
        for month in range(5, 18):
            distributions = self.model.process_monthly_distributions(month)
        
        # Move to later in redemption period where IRR thresholds are more lenient
        # and set conditions that should trigger redemption
        redemption_amount, _, _, _, _ = self.model.step(
            current_month=40,  # Later in redemption period
            aegis_usdc=1000,   # Lower USDC to decrease IRR
            aegis_leaf=100,    # Lower LEAF to decrease IRR
            current_leaf_price=0.05  # Low price to decrease IRR
        )
        
        # Calculate and log redemption progress
        redemption_progress = (40 - self.config.redemption_start_month) / (
            self.config.redemption_end_month - self.config.redemption_start_month
        )
        logger.info(f"\nRedemption progress: {redemption_progress:.2%}")
        logger.info(f"Redemption amount: {redemption_amount}")
        
        self.assertGreater(
            redemption_amount,
            0,
            "TVL incentive deals should be eligible for redemption"
        )

if __name__ == '__main__':
    unittest.main() 