import unittest
from src.Functions.LEAFPairs import LEAFPairsConfig, LEAFPairsModel, LEAFPairDeal

class TestLEAFPairs(unittest.TestCase):
    def setUp(self):
        self.config = LEAFPairsConfig()
        
        # Create test deals
        self.deals = [
            LEAFPairDeal(
                counterparty="Deal1",
                amount_usd=1_000_000,
                num_leaf_tokens=250_000,
                start_month=1,
                duration_months=12,
                leaf_percentage=0.25,  # Target 25% LEAF
                base_concentration=0.5,  # 50% concentration
                max_concentration=1.0
            ),
            LEAFPairDeal(
                counterparty="Deal2",
                amount_usd=2_000_000,
                num_leaf_tokens=800_000,
                start_month=1,
                duration_months=12,
                leaf_percentage=0.3,  # Target 30% LEAF
                base_concentration=0.4,  # 40% concentration
                max_concentration=0.8
            )
        ]
        
        self.model = LEAFPairsModel(self.config, self.deals)
        self.model.month = 1  # Set month to 1 so deals are active

    def test_liquidity_calculation_leaf_heavy(self):
        """Test liquidity calculation when LEAF ratio is above target"""
        deal = self.deals[1]  # Deal2 is LEAF-heavy
        current_price = 1.0
        
        leaf_amount, other_amount = self.model.get_liquidity_within_percentage(5, current_price, deal_index=1)
        
        print("\nTesting LEAF-heavy position (Deal2):")
        print(f"Deal value: ${deal.amount_usd:,.2f}")
        print(f"Target LEAF ratio: {deal.leaf_percentage:.1%}")
        print(f"Current LEAF value: ${deal.leaf_balance * current_price:,.2f}")
        print(f"Current LEAF ratio: {(deal.leaf_balance * current_price/deal.amount_usd):,.1%}")
        print(f"LEAF within range: {leaf_amount:,.2f} (${leaf_amount * current_price:,.2f})")
        print(f"Other within range: {other_amount:,.2f} (${other_amount:,.2f})")
        print(f"Total USD within range: ${(leaf_amount * current_price) + other_amount:,.2f}")
        
        self.assertGreater(leaf_amount, 0)
        self.assertGreater(other_amount, 0)

    def test_liquidity_calculation_leaf_light(self):
        """Test liquidity calculation when LEAF ratio is below target"""
        deal = self.deals[0]  # Deal1 is LEAF-light
        current_price = 1.0
        
        leaf_amount, other_amount = self.model.get_liquidity_within_percentage(5, current_price, deal_index=0)
        
        print("\nTesting LEAF-light position (Deal1):")
        print(f"Deal value: ${deal.amount_usd:,.2f}")
        print(f"Target LEAF ratio: {deal.leaf_percentage:.1%}")
        print(f"Current LEAF value: ${deal.leaf_balance * current_price:,.2f}")
        print(f"Current LEAF ratio: {(deal.leaf_balance * current_price/deal.amount_usd):,.1%}")
        print(f"LEAF within range: {leaf_amount:,.2f} (${leaf_amount * current_price:,.2f})")
        print(f"Other within range: {other_amount:,.2f} (${other_amount:,.2f})")
        print(f"Total USD within range: ${(leaf_amount * current_price) + other_amount:,.2f}")
        
        self.assertGreater(leaf_amount, 0)
        self.assertGreater(other_amount, 0)

    def test_different_price_points(self):
        """Test liquidity at different price points"""
        print("\nTesting at different price points:")
        
        prices = [0.5, 1.0, 2.0]
        previous_leaf_usd = None
        previous_other_usd = None
        
        for price in prices:
            leaf, other = self.model.get_liquidity_within_percentage(5, price)
            leaf_usd = leaf * price
            other_usd = other
            
            print(f"\nAt price ${price:.2f}:")
            print(f"LEAF within range: {leaf:,.2f} (${leaf_usd:,.2f})")
            print(f"Other within range: {other:,.2f} (${other_usd:,.2f})")
            print(f"Total USD within range: ${leaf_usd + other_usd:,.2f}")
            
            if previous_leaf_usd is not None:
                print(f"LEAF USD ratio vs previous: {leaf_usd/previous_leaf_usd:.3f}x")
                print(f"Other USD ratio vs previous: {other_usd/previous_other_usd:.3f}x")
            
            previous_leaf_usd = leaf_usd
            previous_other_usd = other_usd
            
            self.assertGreater(leaf, 0)
            self.assertGreater(other, 0)

if __name__ == '__main__':
    unittest.main() 