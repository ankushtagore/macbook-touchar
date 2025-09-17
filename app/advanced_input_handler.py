#!/usr/bin/env python3
"""
Advanced Touch Bar Input Handler for MTMR
Provides multiple input methods for Touch Bar
"""

import sys
import os
import subprocess
import asyncio
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.azure_service import AzureOpenAIService


async def handle_ask_mode():
    """Handle ask mode - opens input dialog"""
    try:
        # Create a temporary file for the input
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file_path = temp_file.name

        # Show input dialog
        script = f"""
tell application "System Events"
    activate
end tell

-- Create input dialog
set inputDialog to display dialog "Ask your coding question:" default answer "" buttons {{"Cancel", "Ask"}} default button "Ask" with title "Touch Bar Coding Assistant"

if button returned of inputDialog is "Ask" then
    set question to text returned of inputDialog
    
    -- Write question to temp file
    set tempFile to "{temp_file_path}"
    set fileRef to open for access tempFile with write permission
    write question to fileRef
    close access fileRef
    
    return "ASKED"
else
    return "CANCELLED"
end if
"""

        # Run the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0 and "ASKED" in result.stdout:
            # Read the question from temp file
            with open(temp_file_path, "r") as f:
                question = f.read().strip()

            # Clean up temp file
            os.unlink(temp_file_path)

            if question:
                await get_and_show_answer(question)

    except Exception as e:
        show_error(f"Error in ask mode: {str(e)}")


async def handle_input_mode():
    """Handle input mode - quick input field"""
    try:
        # Show quick input dialog
        script = """
tell application "System Events"
    activate
end tell

-- Create quick input dialog
set inputDialog to display dialog "Quick question:" default answer "" buttons {"Cancel", "Go"} default button "Go" with title "Touch Bar Quick Input"

if button returned of inputDialog is "Go" then
    set question to text returned of inputDialog
    return question
else
    return "CANCELLED"
end if
"""

        # Run the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            question = result.stdout.strip()
            if question and question != "CANCELLED":
                await get_and_show_answer(question)

    except Exception as e:
        show_error(f"Error in input mode: {str(e)}")


async def handle_quick_mode():
    """Handle quick mode - pre-defined questions"""
    try:
        # Show quick question menu
        script = """
tell application "System Events"
    activate
end tell

-- Create quick question menu
set quickQuestions to {"What is a binary search tree?", "How do I implement quicksort?", "Explain dynamic programming", "What is Big O notation?", "How do I reverse a linked list?"}

set chosenQuestion to choose from list quickQuestions with title "Touch Bar Quick Questions" with prompt "Select a question:"

if chosenQuestion is not false then
    return item 1 of chosenQuestion
else
    return "CANCELLED"
end if
"""

        # Run the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            question = result.stdout.strip()
            if question and question != "CANCELLED":
                await get_and_show_answer(question)

    except Exception as e:
        show_error(f"Error in quick mode: {str(e)}")


async def get_and_show_answer(question):
    """Get answer from Azure OpenAI and show it"""
    try:
        # Show "Thinking..." dialog
        thinking_script = """
tell application "System Events"
    activate
end tell

display dialog "Thinking..." buttons {"Cancel"} default button "Cancel" with title "Touch Bar Coding Assistant"
"""

        # Start thinking dialog in background
        thinking_process = subprocess.Popen(["osascript", "-e", thinking_script])

        try:
            # Get the answer using Azure OpenAI
            answer = await AzureOpenAIService.get_coding_answer(question)

            # Close thinking dialog
            thinking_process.terminate()

            # Show the answer in a scrollable dialog
            # Escape the answer for AppleScript
            escaped_answer = answer.replace('"', '\\"').replace("'", "\\'")
            answer_script = f"""
tell application "System Events"
    activate
end tell

-- Create a scrollable text view for the answer
set answerText to "{escaped_answer}"

display dialog "Answer:" default answer answerText buttons {{"Copy", "OK"}} default button "OK" with title "Touch Bar Coding Assistant"
"""

            result = subprocess.run(
                ["osascript", "-e", answer_script], capture_output=True, text=True
            )

            if result.returncode == 0 and "Copy" in result.stdout:
                # Copy to clipboard
                copy_script = f"""
set the clipboard to "{escaped_answer}"
"""
                subprocess.run(["osascript", "-e", copy_script])
                print("✅ Answer copied to clipboard!")

        except Exception as e:
            # Close thinking dialog
            thinking_process.terminate()
            show_error(f"Error getting answer: {str(e)}")

    except Exception as e:
        show_error(f"Error showing answer: {str(e)}")


def show_error(message):
    """Show error dialog"""
    error_script = f"""
tell application "System Events"
    activate
end tell

display dialog "Error: {message}" buttons {{"OK"}} default button "OK" with title "Touch Bar Coding Assistant Error"
"""
    subprocess.run(["osascript", "-e", error_script])


async def main_async():
    """Main async function"""
    try:
        # Get the mode from command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1]

            if mode == "ask":
                await handle_ask_mode()
            elif mode == "input":
                await handle_input_mode()
            elif mode == "quick":
                await handle_quick_mode()
            else:
                print(f"Unknown mode: {mode}")
        else:
            # Default to ask mode
            await handle_ask_mode()

    except Exception as e:
        show_error(f"Error: {str(e)}")


def main():
    """Main function"""
    try:
        # Run the async function
        asyncio.run(main_async())
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
