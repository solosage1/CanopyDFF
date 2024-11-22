import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, List
from src.Functions.TVLLoader import TVLLoader
from src.Functions.TVLContributions import TVLContribution
from src.Data.deal import Deal

class TestTVLLoader(unittest.TestCase):
    def setUp(self):
        """Set up the TVLLoader instance with mocked TVLModel and configuration."""
        # Mock TVLModel with config
        self.mock_tvl_model = MagicMock()
        self.mock_tvl_model.config = MagicMock()
        self.mock_tvl_model.config.revenue_rates = {
            'Organic': 0.02,
            'Contracted': 0.025,
            'ProtocolLocked': 0.04
        }
        
        # Sample organic configuration
        self.organic_config = {
            'conversion_ratio': 0.2,
            'decay_rate': 0.05,
            'duration_months': 36
        }
        
        # Define sample deals
        self.sample_deals = [
            Deal(
                deal_id="DEAL_001",
                counterparty="Counterparty_A",
                start_month=1,
                tvl_amount=100_000_000,
                tvl_revenue_rate=0.025,
                tvl_duration_months=12,
                tvl_type="Contracted"
            ),
            Deal(
                deal_id="DEAL_002",
                counterparty="Counterparty_B",
                start_month=2,
                tvl_amount=50_000_000,
                tvl_revenue_rate=0.03,
                tvl_duration_months=24,
                tvl_type="Contracted"
            ),
            Deal(
                deal_id="DEAL_003",
                counterparty="Counterparty_C",
                start_month=3,
                tvl_amount=0,
                tvl_revenue_rate=0.02,
                tvl_duration_months=6,
                tvl_type="none"
            )
        ]
        
        # Create patcher
        patcher = patch('src.Functions.TVLLoader.initialize_deals', 
                       return_value=self.sample_deals)
        self.mock_initialize_deals = patcher.start()
        self.addCleanup(patcher.stop)
        
        # Initialize TVLLoader
        self.loader = TVLLoader(self.mock_tvl_model, self.organic_config)
        
        # Reset mock calls after initialization
        self.mock_tvl_model.add_contribution.reset_mock()
    
    def test_initialization_loads_initial_contributions(self):
        """Test that TVLLoader initializes and loads initial contributions correctly."""
        # Reset mock and create new loader
        self.mock_tvl_model.add_contribution.reset_mock()
        
        # Create new loader to trigger initialization
        loader = TVLLoader(self.mock_tvl_model, self.organic_config)
        
        # Get all calls to add_contribution
        calls = self.mock_tvl_model.add_contribution.call_args_list
        
        # Should have calls for both initial contributions and their organic counterparts
        self.assertEqual(len(calls), 4)  # 2 initial + 2 organic
        
        # Verify the types and amounts of contributions
        contributions = [call[0][0] for call in calls]
        contracted = [c for c in contributions if c.tvl_type == "Contracted"]
        organic = [c for c in contributions if c.tvl_type == "Organic"]
        
        self.assertEqual(len(contracted), 2)
        self.assertEqual(len(organic), 2)
        
        # Verify amounts
        self.assertEqual(contracted[0].amount_usd, 100_000_000)
        self.assertEqual(organic[0].amount_usd, 20_000_000)  # 20% of first contracted
        self.assertEqual(contracted[1].amount_usd, 50_000_000)
        self.assertEqual(organic[1].amount_usd, 10_000_000)  # 20% of second contracted
    
    def test_load_initial_contributions_ignores_invalid_deals(self):
        """Test that load_initial_contributions ignores deals with zero amount or 'none' type."""
        # Reset id_counter for this test
        self.loader.id_counter = 1
        
        contributions = self.loader.load_initial_contributions(self.sample_deals)
        
        # Check number of valid contributions
        self.assertEqual(len(contributions), 2)  # Only two valid deals
        
        # Check that the invalid deal was ignored
        invalid_deal_ids = [c.id for c in contributions if c.counterparty == "Counterparty_C"]
        self.assertEqual(len(invalid_deal_ids), 0)
        
        # Verify the valid contributions
        valid_counterparties = {c.counterparty for c in contributions}
        self.assertEqual(valid_counterparties, {"Counterparty_A", "Counterparty_B"})
    
    def test_add_monthly_contracted_tvl_before_month_4(self):
        """Test that no TVL is added for months <=3."""
        with patch.object(self.loader, 'add_new_contribution') as mock_add_new:
            self.loader.add_monthly_contracted_tvl(month=3)
            mock_add_new.assert_not_called()
    
    def test_add_monthly_contracted_tvl_after_month_3(self):
        """Test that monthly contracted TVL is added for months >3."""
        with patch.object(self.loader, 'add_new_contribution') as mock_add_new:
            self.loader.add_monthly_contracted_tvl(month=4)
            
            # Verify the correct config is passed
            expected_config = {
                'amount_usd': 20_000_000,
                'start_month': 4,
                'revenue_rate': 0.025,
                'duration_months': 6,
                'counterparty': "MonthlyContract_4"
            }
            mock_add_new.assert_called_once_with('Contracted', expected_config)
    
    def test_add_new_contribution_contract_type(self):
        """Test that adding a new 'Contracted' contribution also adds organic contribution."""
        # Reset mock and id_counter
        self.mock_tvl_model.add_contribution.reset_mock()
        self.loader.id_counter = 1
        
        config = {
            'amount_usd': 20_000_000,
            'start_month': 4,
            'revenue_rate': 0.025,
            'duration_months': 6,
            'counterparty': 'MonthlyContract_4'
        }
        
        contrib = self.loader.add_new_contribution('Contracted', config)
        
        # Verify the contribution attributes instead of the entire object
        calls = self.mock_tvl_model.add_contribution.call_args_list
        self.assertEqual(len(calls), 2)  # Should have 2 calls - contracted and organic
        
        # Verify contracted contribution
        contracted = calls[0][0][0]
        self.assertEqual(contracted.tvl_type, "Contracted")
        self.assertEqual(contracted.amount_usd, 20_000_000)
        
        # Verify organic contribution
        organic = calls[1][0][0]
        self.assertEqual(organic.tvl_type, "Organic")
        self.assertEqual(organic.amount_usd, 4_000_000)  # 20% of contracted
    
    def test_add_new_contribution_non_contracted_type(self):
        """Test that adding a non-'Contracted' contribution does not add organic contribution."""
        # Reset mock and id_counter
        self.mock_tvl_model.add_contribution.reset_mock()
        self.loader.id_counter = 1  # Reset ID counter
        
        with patch.object(self.loader, '_add_organic_contribution') as mock_add_org:
            contrib = self.loader.add_new_contribution('ProtocolLocked', {
                'amount_usd': 30_000_000,
                'start_month': 4,
                'revenue_rate': 0.04,
                'duration_months': 12,
                'counterparty': "ProtocolLocked_1"
            })
            
            # Verify only one call to add_contribution (no organic contribution)
            self.assertEqual(self.mock_tvl_model.add_contribution.call_count, 1)
            
            # Verify the contribution attributes
            actual_contrib = self.mock_tvl_model.add_contribution.call_args[0][0]
            self.assertEqual(actual_contrib.id, 1)
            self.assertEqual(actual_contrib.counterparty, "ProtocolLocked_1")
            self.assertEqual(actual_contrib.amount_usd, 30_000_000)
            self.assertEqual(actual_contrib.revenue_rate, 0.04)
            self.assertEqual(actual_contrib.start_month, 4)
            self.assertEqual(actual_contrib.end_month, 16)
            self.assertEqual(actual_contrib.tvl_type, "ProtocolLocked")
            self.assertTrue(actual_contrib.active)
            
            # Verify no organic contribution was added
            mock_add_org.assert_not_called()
    
    def test_process_month_calls_step_and_logging(self):
        """Test that process_month calls add_monthly_contracted_tvl, step, and logs correctly."""
        with patch.object(self.loader, 'add_monthly_contracted_tvl') as mock_add_mtv, \
             patch.object(self.loader.tvl_model, 'step') as mock_step, \
             patch('logging.debug') as mock_log:
            self.loader.process_month(month=5)
            
            mock_add_mtv.assert_called_once_with(5)
            mock_step.assert_called_once()
            # Check that logging.debug is called for TVL Breakdown
            self.assertTrue(mock_log.called)
    
    def test_create_contribution_correct_attributes(self):
        """Test that _create_contribution creates a TVLContribution with correct attributes."""
        # Reset id_counter for this test
        self.loader.id_counter = 1
        
        config = {
            'amount_usd': 25_000_000,
            'start_month': 5,
            'revenue_rate': 0.035,
            'duration_months': 10,
            'counterparty': "TestCounterparty"
        }
        contribution = self.loader._create_contribution('Boosted', config)
        
        self.assertEqual(contribution.id, 1)
        self.assertEqual(contribution.counterparty, "TestCounterparty")
        self.assertEqual(contribution.amount_usd, 25_000_000)
        self.assertEqual(contribution.revenue_rate, 0.035)
        self.assertEqual(contribution.start_month, 5)
        self.assertEqual(contribution.end_month, 15)
        self.assertEqual(contribution.tvl_type, 'Boosted')
        self.assertTrue(contribution.active)
    
    def test_add_organic_contribution_creates_correct_contribution(self):
        """Test that _add_organic_contribution creates and adds an organic TVLContribution correctly."""
        # Reset mock and id_counter
        self.mock_tvl_model.add_contribution.reset_mock()
        self.loader.id_counter = 1
        
        source_contribution = TVLContribution(
            id=1,
            counterparty="Counterparty_A",
            amount_usd=100_000_000,
            revenue_rate=0.025,
            start_month=1,
            end_month=13,
            tvl_type="Contracted",
            active=True
        )
        
        with patch.object(self.mock_tvl_model, 'add_contribution') as mock_add_contrib:
            self.loader._add_organic_contribution(source_contribution)
            
            # Get the actual contribution that was passed to add_contribution
            actual_contribution = mock_add_contrib.call_args[0][0]
            
            # Verify individual attributes instead of the entire object
            self.assertEqual(actual_contribution.counterparty, "Organic_Counterparty_A")
            self.assertEqual(actual_contribution.amount_usd, 20_000_000)
            self.assertEqual(actual_contribution.revenue_rate, 0.02)
            self.assertEqual(actual_contribution.start_month, 1)
            self.assertEqual(actual_contribution.end_month, 37)
            self.assertEqual(actual_contribution.tvl_type, "Organic")
            self.assertTrue(actual_contribution.active)
            self.assertEqual(actual_contribution.decay_rate, 0.05)

if __name__ == '__main__':
    unittest.main()