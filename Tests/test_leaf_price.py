import unittest
import logging
from src.Functions.LeafPrice import LEAFPriceConfig, LEAFPriceModel
from src.Data.deal import Deal

class TestLEAFPrice(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('TestLEAFPrice')
        
        self.config = LEAFPriceConfig(
            min_price=0.01,
            max_price=100.0,
            price_impact_threshold=0.10,
            initial_price=1.0
        )
        self.model = LEAFPriceModel(self.config)
        
        # Create test deal for liquidity
        self.test_deal = Deal(
            deal_id="test_001",
            counterparty="Test",
            start_month=1,
            leaf_pair_amount=200_000,  # Total liquidity of $200k
            leaf_tokens=100_000,       # 100k LEAF tokens
            target_ratio=0.5,
            leaf_base_concentration=0.5,
            leaf_max_concentration=1.0,
            leaf_duration_months=12
        )
        self.test_deal.leaf_balance = 100_000    # Set initial balances
        self.test_deal.other_balance = 100_000

    def test_buy_price_impact(self):
        """Test price impact from buying LEAF."""
        self.logger.info("Testing buy price impact")
        
        current_price = self.model.get_price(month=1)
        trade_amount_usd = 10_000  # Buying $10,000 worth of LEAF
        
        new_price = self.model.update_price(
            month=1,
            deals=[self.test_deal],
            trade_amount_usd=trade_amount_usd
        )
        
        # Calculate expected impact using total liquidity
        total_liquidity = self.test_deal.other_balance + (self.test_deal.leaf_balance * current_price)
        expected_price_impact = trade_amount_usd / total_liquidity
        expected_new_price = current_price + current_price * expected_price_impact
        
        self.logger.debug(f"New price after buy: {new_price}")
        self.assertAlmostEqual(new_price, expected_new_price, places=6)

    def test_sell_price_impact(self):
        """Test price impact from selling LEAF."""
        self.logger.info("Testing sell price impact")
        
        current_price = self.model.get_price(month=1)
        trade_amount_usd = -10_000  # Selling $10,000 worth of LEAF
        
        new_price = self.model.update_price(
            month=1,
            deals=[self.test_deal],
            trade_amount_usd=trade_amount_usd
        )
        
        total_liquidity = self.test_deal.other_balance + (self.test_deal.leaf_balance * current_price)
        expected_price_impact = trade_amount_usd / total_liquidity
        expected_new_price = current_price + current_price * expected_price_impact
        
        self.logger.debug(f"New price after sell: {new_price}")
        self.assertAlmostEqual(new_price, expected_new_price, places=6)

    def test_multiple_updates_in_month(self):
        """Test multiple price updates within the same month."""
        self.logger.info("Testing multiple price updates in a month")
        
        month = 1
        trades = [5_000, -2_000, 3_000]  # Series of trades
        
        for trade_amount_usd in trades:
            new_price = self.model.update_price(
                month=month,
                deals=[self.test_deal],
                trade_amount_usd=trade_amount_usd
            )
        
        # Finalize month's price
        self.model.finalize_month_price(month)
        
        # Ensure no further updates are allowed
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=month,
                deals=[self.test_deal],
                trade_amount_usd=1_000
            )

    def test_price_bounds(self):
        """Test price bounds enforcement."""
        self.logger.info("Testing price bounds enforcement")
        
        current_price = self.model.get_price(month=1)
        
        # Large buy to exceed max price
        trade_amount_usd = self.test_deal.other_balance * 10
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=1,
                deals=[self.test_deal],
                trade_amount_usd=trade_amount_usd
            )
        
        # Large sell to drop below min price
        trade_amount_usd = -self.test_deal.other_balance * 10
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=1,
                deals=[self.test_deal],
                trade_amount_usd=trade_amount_usd
            )

    def test_price_impact_threshold(self):
        """Test that trades exceeding the price impact threshold are rejected."""
        self.logger.info("Testing price impact threshold enforcement")
        
        current_price = self.model.get_price(month=1)
        total_liquidity = self.test_deal.other_balance + (self.test_deal.leaf_balance * current_price)
        
        # Trade that exceeds price impact threshold
        trade_amount_usd = total_liquidity * (self.config.price_impact_threshold + 0.01)
        
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=1,
                deals=[self.test_deal],
                trade_amount_usd=trade_amount_usd
            )

    def test_finalize_month_price(self):
        """Test that price cannot be updated after month is finalized."""
        self.logger.info("Testing month price finalization")
        
        month = 1
        trade_amount_usd = 5_000  # Buy order
        
        # Update price once
        self.model.update_price(
            month=month,
            deals=[self.test_deal],
            trade_amount_usd=trade_amount_usd
        )
        
        # Finalize the month's price
        self.model.finalize_month_price(month)
        
        # Attempt to update price after finalization
        with self.assertRaises(ValueError):
            self.model.update_price(
                month=month,
                deals=[self.test_deal],
                trade_amount_usd=1_000
            )

if __name__ == '__main__':
    unittest.main() 