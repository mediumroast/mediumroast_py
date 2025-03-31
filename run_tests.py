import unittest
import os
from dotenv import load_dotenv
import logging

class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        pass  # Do not print the dot

    def printErrors(self):
        # Do not print a newline character after each test case
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify required environment variables
    required_vars = ['MR_CLIENT_ID', 'MR_APP_ID', 'YOUR_INSTALLATION_ID', 
                     'YOUR_PEM_FILE', 'YOUR_PAT_FILE', 'YOUR_ORG']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please ensure your .env file contains all required variables.")
        return
    
    # Verify client ID is valid (non-empty)
    if not os.getenv('MR_CLIENT_ID') or os.getenv('MR_CLIENT_ID') == 'your_oauth_app_client_id':
        print("ERROR: MR_CLIENT_ID is missing or using placeholder value.")
        print("Please update your .env file with a valid OAuth client ID.")
        return
        
    # Create a TestSuite
    suite = unittest.TestSuite()

    # Add tests to the TestSuite
    loader = unittest.TestLoader()
    suite.addTests(loader.discover(start_dir='tests'))

    # Run the tests in serial with custom result class
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    runner.run(suite)

if __name__ == "__main__":
    main()
