import os
import logging
from datetime import datetime
import sys

def test_logging_setup():
    """Test basic logging setup and file creation."""
    print("\n=== Testing Logging Setup ===")
    
    try:
        # 1. Get current directory and setup paths
        current_dir = os.getcwd()
        logs_dir = os.path.join(current_dir, 'logs')
        
        print(f"Current directory: {current_dir}")
        print(f"Logs directory path: {logs_dir}")
        
        # 2. Create logs directory
        if not os.path.exists(logs_dir):
            print("Creating logs directory...")
            os.makedirs(logs_dir)
            print("✅ Logs directory created")
        else:
            print("✅ Logs directory already exists")
            
        # 3. Create log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'test_simulation_{timestamp}.log')
        print(f"Creating log file: {log_file}")
        
        # 4. Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # 5. Write some test logs
        print("\nWriting test log messages...")
        logging.info("Test log message 1")
        logging.warning("Test warning message")
        logging.error("Test error message")
        
        # 6. Verify file exists and has content
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ Log file created successfully")
            print(f"✅ Log file size: {size} bytes")
            
            # Read and print the contents
            print("\nLog file contents:")
            print("-" * 50)
            with open(log_file, 'r') as f:
                print(f.read())
            print("-" * 50)
        else:
            print("❌ Failed to create log file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during logging test: {e}")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        return False

if __name__ == "__main__":
    success = test_logging_setup()
    print(f"\nTest {'passed' if success else 'failed'}") 