#!/usr/bin/env python3
"""
Test runner script for Friday-APIC Azure Function App.
Run different types of tests with various options.
"""

import subprocess
import sys
import os
import argparse


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test runner for Friday-APIC Azure Function App")
    parser.add_argument(
        "--type", 
        choices=["unit", "functional", "regression", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--html", 
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd_parts = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd_parts.append("-v")
    
    if args.coverage:
        cmd_parts.extend(["--cov=.", "--cov-report=term-missing"])
    
    if args.html:
        cmd_parts.append("--cov-report=html")
    
    # Add test type filter
    if args.type != "all":
        cmd_parts.append(f"-m {args.type}")
    
    cmd = " ".join(cmd_parts)
    
    # Run tests
    success = run_command(cmd, f"{args.type.title()} Tests")
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 