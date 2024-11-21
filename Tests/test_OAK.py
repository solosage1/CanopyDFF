import unittest
import sys
import os
import logging
from collections import defaultdict
from pathlib import Path
from typing import Tuple

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Configure logging at the root level
logging.basicConfig(
    level=logging.DEBUG,  # Capture all levels DEBUG and above
    format='%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)

# Get the root logger
logger = logging.getLogger()

from src.Functions.OAK import OAKDistributionConfig, OAKModel
from src.Functions.AEGIS import AEGISConfig, AEGISModel
from src.Data.deal import Deal

class TestOAKModel(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # No need to configure logging here since it's done globally above
        
        self.aegis_config = AEGISConfig(
            initial_leaf_balance=1_000_000_000,
            initial_usdc_balance=100_000,
            max_months=60,
            oak_to_usdc_rate=1.0,
            oak_to_leaf_rate=1.0
        )
        self.aegis_model = AEGISModel(self.aegis_config)
        
        # Create test deals with lower IRR thresholds
        self.test_deals = [
            Deal(
                deal_id="test_001",
                counterparty="Counterparty_A",
                start_month=1,
                oak_amount=100_000,
                oak_vesting_months=6,
                oak_irr_threshold=95.0
            ),
            Deal(
                deal_id="test_002",
                counterparty="Counterparty_B",
                start_month=1,
                oak_amount=200_000,
                oak_vesting_months=12,
                oak_irr_threshold=85.0
            ),
            Deal(
                deal_id="test_003",
                counterparty="Counterparty_C",
                start_month=3,
                oak_amount=150_000,
                oak_vesting_months=9,
                oak_irr_threshold=100.0
            )
        ]
        
        self.oak_config = OAKDistributionConfig(
            total_oak_supply=500_000,
            redemption_start_month=12,
            redemption_end_month=48,
            deals=self.test_deals
        )
        
        self.model = OAKModel(self.oak_config, self.aegis_model)

    def test_oak_vesting_and_redemption(self):
        """Test OAK vesting and redemption mechanics."""
        for month in range(1, 21):
            self.model.step(
                month,
                self.aegis_config.initial_usdc_balance,
                self.aegis_config.initial_leaf_balance,
                1.0,
                self.aegis_model
            )
            
            # Verify distributions at cliff vesting points
            if month == 6:  # Counterparty_A vests
                self.assertEqual(len(self.model.distribution_history[month]), 1)
                self.assertEqual(
                    self.model.distribution_history[month]["Counterparty_A"], 
                    100_000  # Full amount
                )
            elif month == 11:  # Counterparty_C vests
                self.assertEqual(len(self.model.distribution_history[month]), 1)
                self.assertEqual(
                    self.model.distribution_history[month]["Counterparty_C"], 
                    150_000  # Full amount
                )
            elif month == 12:  # Counterparty_B vests
                self.assertEqual(len(self.model.distribution_history[month]), 1)
                self.assertEqual(
                    self.model.distribution_history[month]["Counterparty_B"], 
                    200_000  # Full amount
                )
            
            # Verify state tracking
            state = self.model.get_state()
            self.assertEqual(state["current_month"], month)

    def test_weighted_avg_irr_threshold(self):
        """Test weighted average IRR threshold calculation."""
        # Test with no distributions
        self.assertEqual(self.model.calculate_weighted_avg_irr_threshold(), 0.0)
        
        # Run simulation until all distributions complete
        for month in range(1, 13):
            self.model.step(
                month,
                self.aegis_config.initial_usdc_balance,
                self.aegis_config.initial_leaf_balance,
                1.0,
                self.aegis_model
            )
        
        # Calculate expected weighted average
        total_oak = 450_000  # Sum of all deal amounts
        expected_weighted_avg = max(0.0, 
            (100_000 * 95.0 + 200_000 * 85.0 + 150_000 * 100.0) / total_oak
        )
        
        calculated_avg = self.model.calculate_weighted_avg_irr_threshold()
        self.assertAlmostEqual(calculated_avg, expected_weighted_avg, places=2)