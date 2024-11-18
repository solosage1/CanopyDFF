import unittest
import logging
from src.Functions.LeafPrice import LEAFPriceModel, LEAFPriceConfig

class TestLEAFPrice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up logging configuration for the test class"""
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        cls.logger = logging.getLogger(__name__)

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.config = LEAFPriceConfig(
            min_price=0.01,
            max_price=100.0,
            price_impact_threshold=0.10
        )
        self.model = LEAFPriceModel(self.config)
        self.logger.info("\n=== Starting New Test ===")

    def test_basic_price_calculation(self):
        """Test basic price calculation with no trade impact"""
        self.logger.info("Testing basic price calculation")
        
        # Test parameters
        current_price = 1.0
        leaf_liquidity = 100000
        usd_liquidity = 100000
        trade_amount = 0
        
        self.logger.debug(f"Input parameters:")
        self.logger.debug(f"Current price: ${current_price}")
        self.logger.debug(f"LEAF liquidity: {leaf_liquidity} LEAF")
        self.logger.debug(f"USD liquidity: ${usd_liquidity}")
        self.logger.debug(f"Trade amount: ${trade_amount}")

        new_price = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount
        )
        
        self.logger.info(f"New price calculated: ${new_price}")
        self.assertEqual(new_price, current_price)

    def test_buy_price_impact(self):
        """Test price impact from buying LEAF"""
        self.logger.info("Testing buy price impact")
        
        # Test parameters
        current_price = 1.0
        leaf_liquidity = 100000
        usd_liquidity = 100000
        trade_amount = 10000  # Buy $10k worth of LEAF
        
        self.logger.debug(f"Input parameters:")
        self.logger.debug(f"Current price: ${current_price}")
        self.logger.debug(f"LEAF liquidity: {leaf_liquidity} LEAF")
        self.logger.debug(f"USD liquidity: ${usd_liquidity}")
        self.logger.debug(f"Buy amount: ${trade_amount}")

        total_liquidity = usd_liquidity + (leaf_liquidity * current_price)
        self.logger.debug(f"Total liquidity: ${total_liquidity}")
        expected_price_impact = trade_amount / total_liquidity
        self.logger.debug(f"Expected price impact: {expected_price_impact:.2%}")

        new_price = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount
        )
        
        actual_price_impact = (new_price - current_price) / current_price
        self.logger.info(f"New price calculated: ${new_price}")
        self.logger.info(f"Actual price impact: {actual_price_impact:.2%}")
        
        self.assertGreater(new_price, current_price)
        self.assertLess(actual_price_impact, self.config.price_impact_threshold)

    def test_sell_price_impact(self):
        """Test price impact from selling LEAF"""
        self.logger.info("Testing sell price impact")
        
        # Test parameters
        current_price = 1.0
        leaf_liquidity = 100000
        usd_liquidity = 100000
        trade_amount = -10000  # Sell $10k worth of LEAF
        
        self.logger.debug(f"Input parameters:")
        self.logger.debug(f"Current price: ${current_price}")
        self.logger.debug(f"LEAF liquidity: {leaf_liquidity} LEAF")
        self.logger.debug(f"USD liquidity: ${usd_liquidity}")
        self.logger.debug(f"Sell amount: ${-trade_amount}")

        total_liquidity = usd_liquidity + (leaf_liquidity * current_price)
        self.logger.debug(f"Total liquidity: ${total_liquidity}")
        expected_price_impact = trade_amount / total_liquidity
        self.logger.debug(f"Expected price impact: {expected_price_impact:.2%}")

        new_price = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=trade_amount
        )
        
        actual_price_impact = (new_price - current_price) / current_price
        self.logger.info(f"New price calculated: ${new_price}")
        self.logger.info(f"Actual price impact: {actual_price_impact:.2%}")
        
        self.assertLess(new_price, current_price)
        self.assertGreater(actual_price_impact, -self.config.price_impact_threshold)

    def test_max_trade_size(self):
        """Test maximum trade size calculation"""
        self.logger.info("Testing maximum trade size calculation")
        
        # Test parameters
        current_price = 1.0
        leaf_liquidity = 100000
        usd_liquidity = 100000
        
        # Get maximum trade sizes
        max_buy = self.model.estimate_max_trade_size(
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            is_buy=True
        )
        max_sell = self.model.estimate_max_trade_size(
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            is_buy=False
        )
        
        self.logger.info(f"Maximum buy size: ${max_buy:,.2f}")
        self.logger.info(f"Maximum sell size: ${max_sell:,.2f}")
        
        # Test buy impact
        new_price_buy = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=max_buy * 0.99  # Use slightly less than max to avoid threshold
        )
        buy_impact = (new_price_buy - current_price) / current_price
        self.logger.debug(f"Price impact at max buy: {buy_impact:.2%}")
        self.assertAlmostEqual(buy_impact, self.config.price_impact_threshold * 0.99, places=4)
        
        # Test sell impact
        new_price_sell = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=max_sell * 0.99  # Use slightly less than max to avoid threshold
        )
        sell_impact = (new_price_sell - current_price) / current_price
        self.logger.debug(f"Price impact at max sell: {sell_impact:.2%}")
        self.assertAlmostEqual(sell_impact, -self.config.price_impact_threshold * 0.99, places=4)

    def test_price_bounds(self):
        """Test price bounds enforcement"""
        self.logger.info("Testing price bounds enforcement")
        
        # Test parameters
        current_price = 1.0
        leaf_liquidity = 10000
        usd_liquidity = 10000
        
        # Test actual min/max bounds
        min_price = self.config.min_price
        max_price = self.config.max_price
        
        # Test near bounds
        near_min_test = min_price * 1.1
        near_max_test = max_price * 0.9

        # Test upper bound
        large_buy = usd_liquidity * 2  # Should hit max price
        self.logger.debug(f"Testing large buy: ${large_buy:,.2f}")
        
        new_price = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=large_buy
        )
        self.logger.info(f"Price after large buy: ${new_price}")
        self.assertLessEqual(new_price, self.config.max_price)
        
        # Test lower bound
        large_sell = -usd_liquidity * 2  # Should hit min price
        self.logger.debug(f"Testing large sell: ${-large_sell:,.2f}")
        
        new_price = self.model.get_leaf_price(
            month=1,
            current_price=current_price,
            leaf_liquidity=leaf_liquidity,
            usd_liquidity=usd_liquidity,
            trade_amount_usd=large_sell
        )
        self.logger.info(f"Price after large sell: ${new_price}")
        self.assertGreaterEqual(new_price, self.config.min_price)

    def test_error_handling(self):
        """Test invalid inputs"""
        self.logger.info("Testing error handling")
        
        # Test zero liquidity
        with self.assertRaises(ValueError):
            self.model.calculate_price_impact(
                current_price=1.0,
                leaf_liquidity=0,  # Invalid value
                usd_liquidity=100000,
                trade_amount_usd=1000
            )
        
        # Test zero USD liquidity
        with self.assertRaises(ValueError):
            self.model.calculate_price_impact(
                current_price=1.0,
                leaf_liquidity=100000,
                usd_liquidity=0,  # Invalid value
                trade_amount_usd=1000
            )

if __name__ == '__main__':
    unittest.main() 