#!/usr/bin/env python3
"""
Touch Bar Input Handler for MTMR
Shows input field directly on Touch Bar and gets answers
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


async def show_touchbar_input():
    """Show input field directly on Touch Bar"""
    try:
        # Create a temporary file for the input
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file_path = temp_file.name

        # Use osascript to show a Touch Bar-like input
        # This creates a floating input field that appears near the Touch Bar
        script = f"""
tell application "System Events"
    activate
end tell

-- Create a floating input window
set inputDialog to display dialog "Enter your coding question:" default answer "" buttons {{"Cancel", "Ask"}} default button "Ask" with title "Touch Bar Coding Assistant"

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
                # Show "Thinking..." dialog
                thinking_script = """
tell application "System Events"
    activate
end tell

display dialog "Thinking..." buttons {"Cancel"} default button "Cancel" with title "Touch Bar Coding Assistant"
"""

                # Start thinking dialog in background
                thinking_process = subprocess.Popen(
                    ["osascript", "-e", thinking_script]
                )

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
                        ["osascript", "-e", answer_script],
                        capture_output=True,
                        text=True,
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

                    # Show error
                    error_script = f"""
tell application "System Events"
    activate
end tell

display dialog "Error: {str(e)}" buttons {{"OK"}} default button "OK" with title "Touch Bar Coding Assistant Error"
"""
                    subprocess.run(["osascript", "-e", error_script])

    except Exception as e:
        error_script = f"""
tell application "System Events"
    activate
end tell

display dialog "Error: {str(e)}" buttons {{"OK"}} default button "OK" with title "Touch Bar Coding Assistant Error"
"""
        subprocess.run(["osascript", "-e", error_script])


def main():
    """Main function"""
    try:
        # Run the async function
        asyncio.run(show_touchbar_input())
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
