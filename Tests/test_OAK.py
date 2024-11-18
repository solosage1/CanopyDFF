import unittest
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Functions.OAK import OAKDistributionDeal, OAKDistributionConfig, OAKModel

class TestOAKModel(unittest.TestCase):
    def setUp(self):
        logger.info("\n=== Setting up new test case ===")
        # Create test deals
        self.deal1 = OAKDistributionDeal(
            counterparty="Counterparty_A",
            oak_amount=100_000,
            start_month=1,
            vesting_months=6,
            irr_threshold=10.0,
            unlock_month=24
        )
        self.deal2 = OAKDistributionDeal(
            counterparty="Counterparty_B",
            oak_amount=200_000,
            start_month=1,
            vesting_months=12,
            irr_threshold=8.0,
            unlock_month=36
        )
        self.deal3 = OAKDistributionDeal(
            counterparty="Counterparty_C",
            oak_amount=200_000,
            start_month=12,
            vesting_months=6,
            irr_threshold=12.0,
            unlock_month=48
        )

        logger.info("Created deals:")
        logger.info(f"Deal 1: {self.deal1}")
        logger.info(f"Deal 2: {self.deal2}")
        logger.info(f"Deal 3: {self.deal3}")

        self.config = OAKDistributionConfig(
            total_oak_supply=500_000,
            deals=[self.deal1, self.deal2, self.deal3]
        )
        logger.info(f"Created OAKDistributionConfig with total supply: {self.config.total_oak_supply}")

        self.model = OAKModel(self.config)
        logger.info("Initialized OAKModel")

    def test_initial_state(self):
        logger.info("\n=== Testing Initial State ===")
        state = self.model.get_state()
        logger.info(f"Initial state: {state}")
        self.assertEqual(state['month'], 0)
        self.assertEqual(state['remaining_oak_supply'], 500_000)
        self.assertEqual(len(state['oak_supply_history']), 0)
        self.assertEqual(len(state['redemption_history']), 0)
        logger.info("Initial state validation successful")

    def test_redemptions_before_vesting(self):
        logger.info("\n=== Testing Redemptions Before Vesting ===")
        logger.info("Stepping to month 1 with IRR of 9.0")
        self.model.step(current_month=1, current_irr=9.0)
        state = self.model.get_state()
        logger.info(f"State after step: {state}")
        self.assertEqual(state['remaining_oak_supply'], 500_000)
        self.assertEqual(state['redemption_history'].get(1, {}), {})
        logger.info("Verified no redemptions occurred before vesting period")

    def test_redemptions_after_vesting(self):
        logger.info("\n=== Testing Redemptions After Vesting ===")
        logger.info("Stepping to month 7 with IRR of 9.0 (after vesting for deal1)")
        
        redemption_amount, supply_before, supply_after = self.model.step(
            current_month=7,
            current_irr=9.0
        )
        
        state = self.model.get_state()
        logger.info(f"State after step: {state}")
        logger.info(f"Redemption amount: {redemption_amount}")
        logger.info(f"Supply before: {supply_before} -> Supply after: {supply_after}")
        
        redemption = state['redemption_history'][7]
        logger.info(f"Month 7 redemptions: {redemption}")
        
        self.assertIn('Counterparty_A', redemption)
        self.assertNotIn('Counterparty_B', redemption)
        self.assertNotIn('Counterparty_C', redemption)
        self.assertEqual(supply_after, state['remaining_oak_supply'])
        self.assertEqual(supply_before - redemption_amount, supply_after)
        logger.info(f"Verified Counterparty_A redemption. Remaining supply: {supply_after}")

    def test_ir_threshold(self):
        logger.info("\n=== Testing IR Threshold ===")
        logger.info("Stepping to month 13 with IRR of 1.0 (after vesting for deal1 and deal2)")
        self.model.step(current_month=13, current_irr=1.0)
        state = self.model.get_state()
        logger.info(f"State after step: {state}")
        redemption = state['redemption_history'][13]
        logger.info(f"Month 13 redemptions: {redemption}")
        
        self.assertIn('Counterparty_A', redemption)
        self.assertIn('Counterparty_B', redemption)
        self.assertLess(self.deal1.oak_amount, 1e-6)
        self.assertLess(self.deal2.oak_amount, 1e-6)
        self.assertLess(state['remaining_oak_supply'], 500_000)
        logger.info(f"Verified both deals redeemed. Remaining amounts - Deal1: {self.deal1.oak_amount}, Deal2: {self.deal2.oak_amount}")

    def test_no_redemption_above_irr_threshold(self):
        logger.info("\n=== Testing No Redemption Above IRR Threshold ===")
        logger.info("Stepping to month 13 with high IRR of 15.0")
        self.model.step(current_month=13, current_irr=15.0)
        state = self.model.get_state()
        logger.info(f"State after step: {state}")
        self.assertEqual(state['redemption_history'].get(13, {}), {})
        self.assertEqual(state['remaining_oak_supply'], 500_000)
        logger.info("Verified no redemptions occurred due to high IRR")

    def test_get_best_case_irr(self):
        logger.info("\n=== Testing Best Case IRR Calculation ===")
        irr = self.model.get_best_case_irr(
            acquisition_price=1.0,
            current_leaf_price=2.0,
            current_month=0
        )
        logger.info(f"Calculated best case IRR: {irr}%")
        self.assertGreater(irr, 0)
        logger.info("Verified IRR is positive")

    def test_full_simulation(self):
        logger.info("\n=== Testing Full 48-Month Simulation ===")
        for month in range(1, 49):
            current_irr = 7.0
            logger.info(f"\nMonth {month} - Processing with IRR: {current_irr}")
            self.model.step(current_month=month, current_irr=current_irr)
            state = self.model.get_state()
            logger.info(f"Month {month} redemptions: {state['redemption_history'].get(month, {})}")
            logger.info(f"Remaining supply: {state['remaining_oak_supply']}")
        
        state = self.model.get_state()
        total_redeemed = sum(
            sum(counterparty_redemptions.values())
            for counterparty_redemptions in self.model.redemption_history.values()
        )
        
        total_redeemed = round(total_redeemed, 8)
        expected_redeemed = round(self.config.total_oak_supply - state['remaining_oak_supply'], 8)
        
        logger.info(f"\nSimulation complete:")
        logger.info(f"Total redeemed: {total_redeemed}")
        logger.info(f"Expected redeemed: {expected_redeemed}")
        logger.info(f"Final remaining supply: {state['remaining_oak_supply']}")
        
        self.assertLess(state['remaining_oak_supply'], 500_000)
        self.assertEqual(expected_redeemed, total_redeemed)
        logger.info("Verified simulation results match expectations")

if __name__ == '__main__':
    unittest.main() 