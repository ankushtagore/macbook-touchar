#!/usr/bin/env python3
"""
Touch Bar Coding Assistant
A Python application that uses the Apple Touch Bar to search for coding interview questions
and display answers directly on the Touch Bar using Azure OpenAI APIs.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Import macOS APIs for Touch Bar
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory

    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.touch_bar_ui import TouchBarUI, TouchBarSimulator
from app.touch_bar_button import TouchBarButton
from app.touchbar_fixed import FixedTouchBarIntegration
from app.config import settings
from app.azure_service import AzureOpenAIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("touch_bar_assistant.log"),
    ],
)

logger = logging.getLogger(__name__)


def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.error("Please set these variables in your .env file or environment")
        return False

    return True


def test_azure_connection():
    """Test the Azure OpenAI connection"""
    try:
        logger.info("Testing Azure OpenAI connection...")
        # This will test the connection during initialization
        AzureOpenAIService.get_llm()
        logger.info("✅ Azure OpenAI connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Azure OpenAI connection failed: {str(e)}")
        return False


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Touch Bar Coding Assistant - Search coding interview questions on your Touch Bar"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test Azure OpenAI connection only"
    )
    parser.add_argument(
        "--simulator",
        action="store_true",
        help="Run in simulator mode (for development)",
    )
    parser.add_argument(
        "--button",
        action="store_true",
        help="Run with floating Touch Bar button (recommended for MacBook Pro)",
    )
    parser.add_argument(
        "--touchbar",
        action="store_true",
        help="Run with real Touch Bar integration (MacBook Pro with Touch Bar only)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Test connection if requested
    if args.test:
        if test_azure_connection():
            logger.info("All tests passed!")
            sys.exit(0)
        else:
            logger.error("Tests failed!")
            sys.exit(1)

    # Test connection before starting UI
    if not test_azure_connection():
        logger.error("Cannot start application - Azure OpenAI connection failed")
        sys.exit(1)

    try:
        if args.simulator:
            logger.info("Starting Touch Bar Simulator...")
            simulator = TouchBarSimulator()
            simulator.run()
        elif args.button:
            logger.info("Starting Touch Bar Button...")
            touch_bar_button = TouchBarButton()
            touch_bar_button.run()
        elif args.touchbar:
            logger.info("Starting Real Touch Bar Integration...")
            touch_bar = FixedTouchBarIntegration.alloc().init()
            touch_bar.setup_touch_bar()
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            app.run()
        else:
            logger.info("Starting Touch Bar Coding Assistant...")
            ui = TouchBarUI()
            ui.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
