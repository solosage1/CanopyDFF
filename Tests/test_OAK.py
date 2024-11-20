import unittest
import sys
import os
import logging
from collections import defaultdict
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# Clear existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
logger.addHandler(logging.StreamHandler())

from src.Functions.OAK import OAKDistributionConfig, OAKModel
from src.Functions.AEGIS import AEGISConfig, AEGISModel
from src.Data.deal import Deal

class TestOAKModel(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        logger.info("\n=== Setting up new test case ===")
        
        # Create test deals
        self.test_deals = [
            Deal(
                deal_id="test_001",
                counterparty="Counterparty_A",
                start_month=1,
                oak_amount=100_000,
                oak_vesting_months=6,
                oak_irr_threshold=75.0
            ),
            Deal(
                deal_id="test_002",
                counterparty="Counterparty_B",
                start_month=1,
                oak_amount=200_000,
                oak_vesting_months=12,
                oak_irr_threshold=65.0
            ),
            Deal(
                deal_id="test_003",
                counterparty="Counterparty_C",
                start_month=3,
                oak_amount=150_000,
                oak_vesting_months=6,
                oak_irr_threshold=70.0
            )
        ]
        
        # Initialize config
        self.config = OAKDistributionConfig(
            total_oak_supply=1_000_000,
            redemption_start_month=12,
            redemption_end_month=48,
            deals=self.test_deals
        )
        
        # Initialize AEGIS model for testing
        self.aegis_config = AEGISConfig(
            initial_leaf_balance=1_000_000,
            initial_usdc_balance=500_000,
            leaf_price_decay_rate=0.005,
            max_months=60
        )
        self.aegis_model = AEGISModel(self.aegis_config)
        
        # Initialize OAK model
        self.model = OAKModel(self.config)

    def test_initial_state(self):
        """Test initial state of OAK model."""
        logger.info("\n=== Testing Initial State ===")
        
        state = self.model.get_state()
        self.assertEqual(state['remaining_oak_supply'], self.config.total_oak_supply)
        self.assertEqual(len(state['redemption_history']), 0)
        self.assertEqual(len(state['distribution_history']), 0)
        
        for deal in self.model.config.deals:
            self.assertEqual(deal.oak_distributed_amount, 0)

    def test_monthly_distributions(self):
        """Test monthly distribution process."""
        logger.info("\n=== Testing Monthly Distributions ===")
        
        # Test first month distributions
        month_1_dist = self.model.process_monthly_distributions(1)
        self.assertEqual(len(month_1_dist), 2)  # Two deals start in month 1
        
        # Test month 3 distributions
        month_3_dist = self.model.process_monthly_distributions(3)
        self.assertEqual(len(month_3_dist), 1)  # One deal starts in month 3

    def test_redemption_mechanics(self):
        """Test redemption process."""
        logger.info("\n=== Testing Redemption Mechanics ===")
        
        # Process distributions first
        for month in range(1, 13):
            self.model.process_monthly_distributions(month)
        
        # Test redemption at month 13
        redemption_amount, supply_before, supply_after, usdc_red, leaf_red = self.model.step(
            current_month=13,
            aegis_usdc=self.aegis_config.initial_usdc_balance,
            aegis_leaf=self.aegis_config.initial_leaf_balance,
            current_leaf_price=0.5,
            aegis_model=self.aegis_model
        )
        
        self.assertGreaterEqual(supply_before, supply_after)
        self.assertGreaterEqual(supply_before, redemption_amount)

    def test_irr_calculation(self):
        """Test IRR calculation logic."""
        logger.info("\n=== Testing IRR Calculation ===")
        
        irr = self.model.calculate_expected_irr(
            current_value=100,
            future_value=200,
            years_to_end=2.0
        )
        
        self.assertIsInstance(irr, float)
        self.assertGreater(irr, 0)

    def test_value_tracking(self):
        """Test value tracking through distributions and redemptions."""
        logger.info("\n=== Testing Value Tracking ===")
        
        initial_supply = self.model.remaining_oak_supply
        
        # Process several months
        for month in range(1, 15):
            self.model.step(
                current_month=month,
                aegis_usdc=self.aegis_config.initial_usdc_balance,
                aegis_leaf=self.aegis_config.initial_leaf_balance,
                current_leaf_price=1.0,
                aegis_model=self.aegis_model
            )
        
        final_supply = self.model.remaining_oak_supply
        self.assertLessEqual(final_supply, initial_supply)

    def test_aegis_integration(self):
        """Test integration with AEGIS model."""
        logger.info("\n=== Testing AEGIS Integration ===")
        
        initial_usdc = self.aegis_model.usdc_balance
        initial_leaf = self.aegis_model.leaf_balance
        
        # Process a redemption month
        self.model.step(
            current_month=13,
            aegis_usdc=initial_usdc,
            aegis_leaf=initial_leaf,
            current_leaf_price=1.0,
            aegis_model=self.aegis_model
        )
        
        # Verify AEGIS balances were updated
        self.assertLessEqual(self.aegis_model.usdc_balance, initial_usdc)
        self.assertLessEqual(self.aegis_model.leaf_balance, initial_leaf)

    def test_state_history(self):
        """Test historical state tracking."""
        logger.info("\n=== Testing State History ===")
        
        # Process several months
        for month in range(1, 5):
            self.model.step(
                current_month=month,
                aegis_usdc=self.aegis_config.initial_usdc_balance,
                aegis_leaf=self.aegis_config.initial_leaf_balance,
                current_leaf_price=1.0,
                aegis_model=self.aegis_model
            )
        
        state = self.model.get_state()
        self.assertIn('oak_supply_history', state)
        self.assertIn('redemption_history', state)
        self.assertIn('distribution_history', state)

if __name__ == '__main__':
    unittest.main() 