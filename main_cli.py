#!/usr/bin/env python3
"""
Touch Bar Coding Assistant - CLI Version
A command-line version for testing and demonstration without GUI dependencies
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.azure_service import AzureOpenAIService

# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TouchBarCLI:
    """CLI version of Touch Bar Coding Assistant"""

    def __init__(self):
        self.sample_questions = [
            "What is the time complexity of binary search?",
            "How to implement a hash table?",
            "Explain dynamic programming",
            "What is the difference between BFS and DFS?",
            "How to find duplicates in an array?",
            "What is a binary tree?",
            "Explain quicksort algorithm",
            "How to reverse a linked list?",
            "What is memoization?",
            "Explain the sliding window technique",
        ]

    async def get_answer(self, question: str) -> str:
        """Get answer for a coding question"""
        try:
            print(f"\n🔍 Question: {question}")
            print("-" * 60)

            answer = await AzureOpenAIService.get_coding_answer(question)
            print(f"💡 Answer: {answer}")
            print(f"📏 Length: {len(answer)} characters")

            if len(answer) > settings.MAX_ANSWER_LENGTH:
                print("⚠️  Answer was truncated for Touch Bar display")

            return answer

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(error_msg)
            return error_msg

    async def interactive_mode(self):
        """Run in interactive mode"""
        print("\n🚀 Touch Bar Coding Assistant - CLI Mode")
        print("=" * 60)
        print("Enter coding interview questions (or 'quit' to exit)")
        print("Type 'sample' to see sample questions")
        print("Type 'demo' to run a quick demo")

        while True:
            try:
                question = input("\n❓ Question: ").strip()

                if question.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if question.lower() == "sample":
                    print("\n📝 Sample Questions:")
                    for i, q in enumerate(self.sample_questions, 1):
                        print(f"  {i}. {q}")
                    continue

                if question.lower() == "demo":
                    await self.run_demo(3)
                    continue

                if not question:
                    print("⚠️  Please enter a question")
                    continue

                await self.get_answer(question)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")

    async def run_demo(self, num_questions: int = 3):
        """Run a demo with sample questions"""
        print(f"\n🎯 Running demo with {num_questions} questions...")
        print("=" * 80)

        for i, question in enumerate(self.sample_questions[:num_questions], 1):
            print(f"\n📝 Question {i}/{num_questions}")
            await self.get_answer(question)

            # Add a small delay between questions
            await asyncio.sleep(1)

        print("\n🎉 Demo completed!")

    def show_info(self):
        """Show application information"""
        print("\n📋 Touch Bar Coding Assistant - Information")
        print("=" * 50)
        print(
            f"📐 Touch Bar Dimensions: {settings.TOUCH_BAR_WIDTH}x{settings.TOUCH_BAR_HEIGHT}"
        )
        print(f"📏 Max Answer Length: {settings.MAX_ANSWER_LENGTH} characters")
        print(f"🎨 Background Color: {settings.BACKGROUND_COLOR}")
        print(f"🎨 Text Color: {settings.TEXT_COLOR}")
        print(f"🎨 Accent Color: {settings.ACCENT_COLOR}")
        print(f"🔤 Font Size: {settings.FONT_SIZE}")
        print(f"⏱️  Search Timeout: {settings.SEARCH_TIMEOUT} seconds")
        print(f"🧠 Max Tokens: {settings.MAX_TOKENS}")
        print(f"🌡️  Temperature: {settings.TEMPERATURE}")

        print("\n🎬 Usage Scenarios:")
        print("  📚 During Coding Interviews:")
        print("     - Quick algorithm complexity lookup")
        print("     - Data structure explanations")
        print("     - Problem-solving approach hints")
        print("     - Code optimization tips")

        print("\n  💻 During Development:")
        print("     - Algorithm reference")
        print("     - Best practices reminder")
        print("     - Performance optimization tips")
        print("     - Code review assistance")


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


async def test_azure_connection():
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


async def main():
    """Main CLI application entry point"""
    parser = argparse.ArgumentParser(
        description="Touch Bar Coding Assistant - CLI Version"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test Azure OpenAI connection only"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run a quick demo with sample questions"
    )
    parser.add_argument("--question", type=str, help="Ask a specific question")
    parser.add_argument(
        "--info", action="store_true", help="Show application information"
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
        if await test_azure_connection():
            logger.info("All tests passed!")
            sys.exit(0)
        else:
            logger.error("Tests failed!")
            sys.exit(1)

    # Test connection before starting
    if not await test_azure_connection():
        logger.error("Cannot start application - Azure OpenAI connection failed")
        sys.exit(1)

    cli = TouchBarCLI()

    try:
        if args.info:
            cli.show_info()
        elif args.demo:
            await cli.run_demo()
        elif args.question:
            await cli.get_answer(args.question)
        else:
            await cli.interactive_mode()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
