#!/usr/bin/env python3
"""
Test runner script for the TaskFlow API project.

This script runs the test suite for the project owner management system
and other components.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py test_project_owners # Run specific test file
    python run_tests.py -v                 # Run with verbose output
"""

import sys
import subprocess
import os

def run_tests(args=None):
    """Run the test suite using pytest"""
    
    # Set environment variables for testing
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["TESTING"] = "1"
    os.environ["SECRET_KEY"] = "test-secret-key"
    
    # Base pytest command
    cmd = ["python3", "-m", "pytest"]
    
    # Add default arguments
    default_args = [
        "tests/",           # Test directory
        "-v",               # Verbose output
        "-s",               # Don't capture stdout (show print statements)
        "--tb=short",       # Short traceback format
    ]
    
    # Add any additional arguments passed to this script
    if args:
        cmd.extend(args)
    else:
        cmd.extend(default_args)
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    # Pass any command line arguments to pytest
    exit_code = run_tests(sys.argv[1:] if len(sys.argv) > 1 else None)
    sys.exit(exit_code)
