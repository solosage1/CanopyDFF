import unittest
import sys
import os
from pathlib import Path
import time
from datetime import datetime
import logging
from typing import Dict, List, Tuple
import importlib

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

class TestResult:
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.total_time = 0.0
        self.failure_messages: List[str] = []

class TestRunner:
    def __init__(self):
        self.setup_logging()
        self.results: Dict[str, TestResult] = {}
        
    def setup_logging(self):
        """Configure logging for test results"""
        logs_dir = Path(project_root) / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f'test_results_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def discover_tests(self) -> List[Path]:
        """Find all test files in the Tests directory"""
        test_dir = Path(__file__).parent
        return [
            f for f in test_dir.glob("test_*.py")
            if f.name != "run_all_tests.py"
        ]
    
    def run_test_file(self, test_path: Path) -> TestResult:
        """Run a single test file and return results"""
        result = TestResult(test_path.name)
        
        # Create test loader and runner
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner(stream=None, verbosity=0)
        
        # Load and run tests
        start_time = time.time()
        try:
            # Import the test module
            module_name = f"Tests.{test_path.stem}"
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            
            # Load tests from the module
            suite = loader.loadTestsFromModule(module)
            test_result = runner.run(suite)
            
            # Collect results
            result.passed = test_result.testsRun - len(test_result.failures) - len(test_result.errors)
            result.failed = len(test_result.failures)
            result.errors = len(test_result.errors)
            result.skipped = len(test_result.skipped)
            
            # Collect failure messages
            for failure in test_result.failures + test_result.errors:
                result.failure_messages.append(f"{failure[0]}: {failure[1]}")
                
        except Exception as e:
            result.errors += 1
            result.failure_messages.append(f"Error loading test file: {str(e)}")
            
        result.total_time = time.time() - start_time
        return result
    
    def run_all_tests(self):
        """Run all test files and generate report"""
        test_files = self.discover_tests()
        total_start_time = time.time()
        
        logging.info("\n=== Running All Tests ===\n")
        
        for test_file in test_files:
            logging.info(f"Running {test_file.name}...")
            self.results[test_file.name] = self.run_test_file(test_file)
        
        self.generate_report(time.time() - total_start_time)
    
    def generate_report(self, total_time: float):
        """Generate and print consolidated test report"""
        logging.info("\n=== Test Results Summary ===\n")
        
        # Calculate totals
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0
        
        # Print individual file results
        for test_file, result in self.results.items():
            total = result.passed + result.failed + result.errors + result.skipped
            if total == 0:
                logging.info(f"{test_file}: No tests ran")
                continue
            
            total_tests += total
            total_passed += result.passed
            total_failed += result.failed
            total_errors += result.errors
            total_skipped += result.skipped
            
            # Calculate pass percentage safely
            pass_percentage = (result.passed / total * 100) if total > 0 else 0
            
            logging.info(f"{test_file}:")
            logging.info(f"  Passed: {result.passed}/{total} ({pass_percentage:.1f}%)")
            logging.info(f"  Failed: {result.failed}")
            logging.info(f"  Errors: {result.errors}")
            logging.info(f"  Skipped: {result.skipped}")
            logging.info(f"  Time: {result.total_time:.2f}s")
            
            if result.failure_messages:
                logging.info("\n  Failure Details:")
                for msg in result.failure_messages:
                    logging.info(f"    - {msg}")
            logging.info("")
        
        if total_tests == 0:
            logging.info("No tests were executed!")
            return
        
        # Print summary
        logging.info("=== Overall Summary ===")
        logging.info(f"Total Test Files: {len(self.results)}")
        logging.info(f"Total Tests: {total_tests}")
        if total_tests > 0:
            logging.info(f"Total Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)")
        logging.info(f"Total Failed: {total_failed}")
        logging.info(f"Total Errors: {total_errors}")
        logging.info(f"Total Skipped: {total_skipped}")
        logging.info(f"Total Time: {total_time:.2f}s")
        
        # Print final status
        if total_tests == 0:
            logging.info("\n⚠️ No tests were executed!")
        elif total_failed == 0 and total_errors == 0:
            logging.info("\n✅ All tests passed!")
        else:
            logging.info("\n❌ Some tests failed or had errors.")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()