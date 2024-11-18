import unittest
from src.Functions.TVLContributions import TVLContribution
from src.Functions.TVL import TVLModel, TVLModelConfig
from src.Functions.TVLLoader import TVLLoader

class TestTVLContributions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.tvl_model = TVLModel(TVLModelConfig(
            revenue_rates={
                'ProtocolLocked': 0.05,
                'Contracted': 0.04,
                'Organic': 0.03,
                'Boosted': 0.06
            }
        ))
        cls.loader = TVLLoader(cls.tvl_model)

    def create_protocol_locked_tvl(self) -> TVLContribution:
        """Factory method for creating protocol locked TVL."""
        return TVLContribution(
            id=1,
            tvl_type='ProtocolLocked',
            amount_usd=5_000_000,
            start_month=0,
            revenue_rate=0.05
        )

    def create_contracted_tvl(self) -> TVLContribution:
        """Factory method for creating contracted TVL."""
        return TVLContribution(
            id=2,
            tvl_type='Contracted',
            amount_usd=2_000_000,
            start_month=0,
            revenue_rate=0.04,
            end_month=12,
            exit_condition=self.tvl_model.contract_end_condition
        )

    def create_organic_tvl(self) -> TVLContribution:
        """Factory method for creating organic TVL."""
        return TVLContribution(
            id=3,
            tvl_type='Organic',
            amount_usd=1_000_000,
            start_month=0,
            revenue_rate=0.03,
            decay_rate=0.15,
            exit_condition=lambda c, m: c.amount_usd < 1000
        )

    def create_boosted_tvl(self) -> TVLContribution:
        """Factory method for creating boosted TVL."""
        return TVLContribution(
            id=4,
            tvl_type='Boosted',
            amount_usd=3_000_000,
            start_month=0,
            revenue_rate=0.06,
            expected_boost_rate=0.05,
            exit_condition=lambda c, m: c.expected_boost_rate < 0.04
        )

    def test_protocol_locked_tvl(self):
        contrib = self.create_protocol_locked_tvl()
        self.assertTrue(contrib.active)
        revenue = contrib.calculate_revenue(1)
        expected_revenue = 5_000_000 * ((1 + 0.05) ** (1 / 12) - 1)
        self.assertAlmostEqual(revenue, expected_revenue, places=2)
        contrib.check_exit(100)
        self.assertTrue(contrib.active)

    def test_contracted_tvl_exit(self):
        contrib = self.create_contracted_tvl()
        self.assertTrue(contrib.active)
        contrib.check_exit(12)
        self.assertFalse(contrib.active)

    def test_organic_tvl_decay(self):
        contrib = self.create_organic_tvl()
        self.assertTrue(contrib.active)
        for month in range(1, 51):
            contrib.update_amount(month)
            if not contrib.active:
                break
        self.assertFalse(contrib.active)
        self.assertLess(contrib.amount_usd, 1000)

    def test_boosted_tvl_exit(self):
        contrib = self.create_boosted_tvl()
        self.assertTrue(contrib.active)
        for month in range(1, 13):
            contrib.expected_boost_rate *= 0.95
            contrib.check_exit(month)
            if not contrib.active:
                break
        self.assertFalse(contrib.active)
        self.assertLess(contrib.expected_boost_rate, 0.04)

    def test_calculate_revenue(self):
        contrib = TVLContribution(
            id=5,
            tvl_type='ProtocolLocked',
            amount_usd=1_000_000,
            start_month=0,
            revenue_rate=0.12
        )
        revenue = contrib.calculate_revenue(0)
        expected_revenue = 1_000_000 * ((1 + 0.12) ** (1 / 12) - 1)
        self.assertAlmostEqual(revenue, expected_revenue, places=2)

    def test_update_amount_organic(self):
        contrib = TVLContribution(
            id=6,
            tvl_type='Organic',
            amount_usd=500_000,
            start_month=0,
            decay_rate=0.02
        )
        contrib.update_amount(1)
        expected_amount = 500_000 * (1 - 0.02)
        self.assertAlmostEqual(contrib.amount_usd, expected_amount, places=2)

if __name__ == '__main__':
    unittest.main()
