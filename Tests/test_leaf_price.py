import unittest
import logging
from src.Functions.LeafPrice import LEAFPriceConfig, LEAFPriceModel

class TestLEAFPrice(unittest.TestCase):
    def setUp(self):
        # Configure logging for the test
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('TestLEAFPrice')
        
        # Configuration with no fixed parameters inside the class
        self.config = LEAFPriceConfig(
            min_price=0.01,
            max_price=100.0,
            price_impact_threshold=0.10  # 10% maximum price impact
        )
        self.model = LEAFPriceModel(self.config)
        self.model.initialize_price(initial_price=1.0)

    def test_buy_price_impact(self):
        """Test price impact from buying LEAF."""
        self.logger.info("Testing buy price impact")
        
        current_price = self.model.get_current_price(month=1)
        leaf_liquidity = 100_000
        usd_liquidity = 100_000
        trade_amount_usd = 10_000  # Buying $10,000 worth of LEAF
        
        new_price = self.model.update_price(
            month=1,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount_usd
        )
        
        expected_price_impact = trade_amount_usd / (usd_liquidity + leaf_liquidity * current_price)
        expected_new_price = current_price + current_price * expected_price_impact
        
        self.logger.debug(f"New price after buy: {new_price}")
        self.assertAlmostEqual(new_price, expected_new_price, places=6)

    def test_sell_price_impact(self):
        """Test price impact from selling LEAF."""
        self.logger.info("Testing sell price impact")
        
        current_price = self.model.get_current_price(month=1)
        leaf_liquidity = 100_000
        usd_liquidity = 100_000
        trade_amount_usd = -10_000  # Selling $10,000 worth of LEAF
        
        new_price = self.model.update_price(
            month=1,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount_usd
        )
        
        expected_price_impact = trade_amount_usd / (usd_liquidity + leaf_liquidity * current_price)
        expected_new_price = current_price + current_price * expected_price_impact
        
        self.logger.debug(f"New price after sell: {new_price}")
        self.assertAlmostEqual(new_price, expected_new_price, places=6)

    def test_multiple_updates_in_month(self):
        """Test multiple price updates within the same month."""
        self.logger.info("Testing multiple price updates in a month")
        
        month = 1
        self.model.initialize_price(initial_price=1.0)
        leaf_liquidity = 100_000
        usd_liquidity = 100_000
        
        # First trade
        trade_amount_usd = 5_000  # Buy order
        new_price = self.model.update_price(
            month=month,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount_usd
        )
        
        # Second trade
        trade_amount_usd = -2_000  # Sell order
        new_price = self.model.update_price(
            month=month,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount_usd
        )
        
        # Final trade of the month
        trade_amount_usd = 3_000  # Buy order
        new_price = self.model.update_price(
            month=month,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount_usd
        )
        
        # Finalize month's price
        self.model.finalize_month_price(month)
        
        # Ensure no further updates are allowed
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=month,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=1_000
            )

    def test_price_bounds(self):
        """Test price bounds enforcement."""
        self.logger.info("Testing price bounds enforcement")
        
        current_price = self.model.get_current_price(month=1)
        leaf_liquidity = 10_000
        usd_liquidity = 10_000
        
        # Large buy to exceed max price
        trade_amount_usd = usd_liquidity * 10  # Large enough to push price above max
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=1,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )

        # Large sell to drop below min price
        trade_amount_usd = -usd_liquidity * 10  # Large enough to push price below min
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=1,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )

    def test_price_impact_threshold(self):
        """Test that trades exceeding the price impact threshold are rejected."""
        self.logger.info("Testing price impact threshold enforcement")
        
        current_price = self.model.get_current_price(month=1)
        leaf_liquidity = 100_000
        usd_liquidity = 100_000
        
        # Trade that exceeds price impact threshold
        trade_amount_usd = (usd_liquidity + leaf_liquidity * current_price) * (self.config.price_impact_threshold + 0.01)
        
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=1,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=trade_amount_usd
            )

    def test_finalize_month_price(self):
        """Test that price cannot be updated after month is finalized."""
        self.logger.info("Testing month price finalization")

        month = 1
        leaf_liquidity = 100_000
        usd_liquidity = 100_000
        trade_amount_usd = 5_000  # Buy order

        # Update price once
        self.model.update_price(
            month=month,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount_usd
        )

        # Finalize the month's price
        self.model.finalize_month_price(month)

        # Attempt to update price after finalization
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=month,
                leaf_liquidity=leaf_liquidity,
                usd_liquidity=usd_liquidity,
                trade_amount_usd=1_000
            )

if __name__ == '__main__':
    unittest.main() 