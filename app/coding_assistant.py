#!/usr/bin/env python3
"""
Coding Assistant Script for MTMR Touch Bar Integration
This script is executed when the Touch Bar button is pressed
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.azure_service import AzureOpenAIService

async def show_search_window():
    """Show the search window for coding questions"""
    try:
        # Create a simple search window using osascript
        script = """tell application "System Events"
    activate
end tell

set question to text returned of (display dialog "Enter your coding interview question:" default answer "" buttons {"Cancel", "Search"} default button "Search")

if question is not "" then
    return question
else
    return "CANCELLED"
end if"""
        
        # Run the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            question = result.stdout.strip()
            if question and question != "CANCELLED":
                # Get the answer using Azure OpenAI
                answer = await AzureOpenAIService.get_coding_answer(question)
                
                # Show the answer
                answer_script = f"""tell application "System Events"
    activate
end tell

display dialog "Answer:" default answer "{answer}" buttons {{"OK"}} default button "OK" with title "Coding Assistant" """
                
                subprocess.run(["osascript", "-e", answer_script])
        
    except Exception as e:
        error_script = f"""tell application "System Events"
    activate
end tell

display dialog "Error: {str(e)}" buttons {{"OK"}} default button "OK" with title "Coding Assistant Error" """
        
        subprocess.run(["osascript", "-e", error_script])

def main():
    """Main function"""
    try:
        # Run the async function
        asyncio.run(show_search_window())
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
