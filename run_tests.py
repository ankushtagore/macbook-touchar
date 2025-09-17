#!/usr/bin/env python3
"""
Test runner for Touch Bar Coding Assistant
Runs all tests and generates coverage reports
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print("=" * 50)

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False


def install_test_dependencies():
    """Install test dependencies"""
    dependencies = ["pytest", "pytest-asyncio", "pytest-cov", "pytest-mock"]

    for dep in dependencies:
        command = f"pip install {dep}"
        if not run_command(command, f"Installing {dep}"):
            return False
    return True


def run_unit_tests():
    """Run unit tests"""
    command = "python -m pytest tests/ -v --tb=short"
    return run_command(command, "Unit Tests")


def run_coverage_tests():
    """Run tests with coverage"""
    command = (
        "python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing"
    )
    return run_command(command, "Coverage Tests")


def run_specific_tests():
    """Run specific test categories"""
    test_files = ["tests/test_azure_service.py", "tests/test_touch_bar_ui.py"]

    all_passed = True
    for test_file in test_files:
        command = f"python -m pytest {test_file} -v"
        if not run_command(command, f"Running {test_file}"):
            all_passed = False

    return all_passed


def run_integration_tests():
    """Run integration tests (if any)"""
    command = "python -m pytest tests/ -m integration -v"
    return run_command(command, "Integration Tests")


def check_code_quality():
    """Check code quality with flake8"""
    command = "python -m flake8 app/ --max-line-length=100 --ignore=E501,W503"
    return run_command(command, "Code Quality Check (flake8)")


def main():
    """Main test runner"""
    print("🧪 Touch Bar Coding Assistant - Test Runner")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)

    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not install_test_dependencies():
        print("❌ Failed to install test dependencies")
        sys.exit(1)

    # Run tests
    test_results = []

    print("\n🔍 Running test suite...")

    # Unit tests
    test_results.append(("Unit Tests", run_unit_tests()))

    # Specific test files
    test_results.append(("Specific Tests", run_specific_tests()))

    # Coverage tests
    test_results.append(("Coverage Tests", run_coverage_tests()))

    # Code quality check
    test_results.append(("Code Quality", check_code_quality()))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} test categories passed")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
