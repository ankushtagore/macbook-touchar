#!/usr/bin/env python3
"""
MTMR Advanced Touch Bar Input Integration
Uses MTMR's native input capabilities for better Touch Bar experience
"""

import os
import json
import subprocess
import sys
from pathlib import Path


class MTMRAdvancedInput:
    """MTMR Advanced Touch Bar input integration"""

    def __init__(self):
        self.mtmr_config_dir = Path.home() / "Library/Application Support/MTMR"
        self.items_config_file = self.mtmr_config_dir / "items.json"

        # Advanced Touch Bar input configuration with multiple buttons
        self.advanced_config = [
            {
                "type": "shellScript",
                "title": "🔍 Ask",
                "align": "center",
                "width": 60,
                "bordered": True,
                "refreshInterval": 1,
                "executablePath": "/usr/bin/python3",
                "shellArguments": [
                    str(Path(__file__).parent / "advanced_input_handler.py"),
                    "ask",
                ],
            },
            {
                "type": "shellScript",
                "title": "📝 Input",
                "align": "center",
                "width": 60,
                "bordered": True,
                "refreshInterval": 1,
                "executablePath": "/usr/bin/python3",
                "shellArguments": [
                    str(Path(__file__).parent / "advanced_input_handler.py"),
                    "input",
                ],
            },
            {
                "type": "shellScript",
                "title": "💡 Quick",
                "align": "center",
                "width": 60,
                "bordered": True,
                "refreshInterval": 1,
                "executablePath": "/usr/bin/python3",
                "shellArguments": [
                    str(Path(__file__).parent / "advanced_input_handler.py"),
                    "quick",
                ],
            },
        ]

    def setup_advanced_input(self):
        """Setup advanced Touch Bar input integration"""
        try:
            print("🔧 Setting up Advanced Touch Bar Input integration...")

            # Create MTMR config directory if it doesn't exist
            self.mtmr_config_dir.mkdir(parents=True, exist_ok=True)

            # Create or update items.json with advanced input
            self._create_advanced_input_config()

            # Create the advanced input handler script
            self._create_advanced_input_handler()

            print("✅ Advanced Touch Bar Input integration setup complete!")
            print("🎯 Three Touch Bar buttons will be available:")
            print("   - 🔍 Ask: Opens input dialog for questions")
            print("   - 📝 Input: Quick input field")
            print("   - 💡 Quick: Pre-defined quick questions")
            print("💡 Make sure MTMR is running for the buttons to appear")

        except Exception as e:
            print(f"❌ Error setting up Advanced Touch Bar Input integration: {str(e)}")
            raise

    def _create_advanced_input_config(self):
        """Create or update MTMR items.json configuration with advanced input"""
        try:
            # Load existing config or create new one
            if self.items_config_file.exists():
                with open(self.items_config_file, "r") as f:
                    config = json.load(f)
            else:
                config = []

            # Check if config is in array format (existing) or presets format (new)
            if isinstance(config, list):
                # Array format - add our buttons to the array
                buttons_exist = any(
                    item.get("title") in ["🔍 Ask", "📝 Input", "💡 Quick"]
                    for item in config
                )

                if not buttons_exist:
                    # Add our buttons after the escape button
                    insert_index = 0
                    for i, item in enumerate(config):
                        if item.get("type") == "escape":
                            insert_index = i + 1
                            break

                    # Insert all three buttons
                    for button_config in self.advanced_config:
                        config.insert(insert_index, button_config)
                        insert_index += 1

                    print("✅ Added advanced Touch Bar input buttons to MTMR config")
                else:
                    print(
                        "ℹ️ Advanced Touch Bar input buttons already exist in MTMR config"
                    )

            elif isinstance(config, dict) and "presets" in config:
                # Presets format - add to first preset
                preset = config["presets"][0]
                if "items" not in preset:
                    preset["items"] = []

                buttons_exist = any(
                    item.get("title") in ["🔍 Ask", "📝 Input", "💡 Quick"]
                    for item in preset["items"]
                )

                if not buttons_exist:
                    preset["items"].extend(self.advanced_config)
                    print("✅ Added advanced Touch Bar input buttons to MTMR config")
                else:
                    print(
                        "ℹ️ Advanced Touch Bar input buttons already exist in MTMR config"
                    )

            # Save the configuration
            with open(self.items_config_file, "w") as f:
                json.dump(config, f, indent=2)

            print(f"✅ MTMR configuration saved to: {self.items_config_file}")

        except Exception as e:
            print(f"❌ Error creating MTMR config: {str(e)}")
            raise

    def _create_advanced_input_handler(self):
        """Create the advanced input handler script"""
        script_path = Path(__file__).parent / "advanced_input_handler.py"

        script_content = '''#!/usr/bin/env python3
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
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
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and "ASKED" in result.stdout:
            # Read the question from temp file
            with open(temp_file_path, 'r') as f:
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
            ["osascript", "-e", script],
            capture_output=True,
            text=True
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
            ["osascript", "-e", script],
            capture_output=True,
            text=True
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
            answer_script = f"""
tell application "System Events"
    activate
end tell

-- Create a scrollable text view for the answer
set answerText to "{answer.replace('"', '\\"').replace("'", "\\'")}"

display dialog "Answer:" default answer answerText buttons {{"Copy", "OK"}} default button "OK" with title "Touch Bar Coding Assistant"
"""
            
            result = subprocess.run(["osascript", "-e", answer_script], capture_output=True, text=True)
            
            if result.returncode == 0 and "Copy" in result.stdout:
                # Copy to clipboard
                copy_script = f"""
set the clipboard to "{answer.replace('"', '\\"').replace("'", "\\'")}"
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
'''

        with open(script_path, "w") as f:
            f.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o755)

        print(f"✅ Advanced input handler created: {script_path}")

    def install_mtmr(self):
        """Install MTMR if not already installed"""
        try:
            print("🔧 Checking if MTMR is installed...")

            # Check if MTMR is installed via Homebrew
            result = subprocess.run(
                ["brew", "list", "mtmr"], capture_output=True, text=True
            )

            if result.returncode != 0:
                print("📦 Installing MTMR via Homebrew...")
                subprocess.run(["brew", "install", "mtmr"], check=True)
                print("✅ MTMR installed successfully!")
            else:
                print("✅ MTMR is already installed")

            # Start MTMR
            print("🚀 Starting MTMR...")
            subprocess.Popen(["open", "-a", "MTMR"])
            print("✅ MTMR started!")

        except Exception as e:
            print(f"❌ Error installing/starting MTMR: {str(e)}")
            print("💡 Please install MTMR manually from: https://mtmr.app")

    def show_instructions(self):
        """Show instructions for using the advanced Touch Bar input"""
        print("\n" + "=" * 60)
        print("🎯 Advanced Touch Bar Input Integration Instructions")
        print("=" * 60)
        print()
        print("✅ Setup Complete! Here's how to use your Touch Bar input buttons:")
        print()
        print("🔍 Ask Button:")
        print("   - Click '🔍 Ask' to open input dialog")
        print("   - Type your coding question")
        print("   - Click 'Ask' to get answer")
        print()
        print("📝 Input Button:")
        print("   - Click '📝 Input' for quick input")
        print("   - Type question and click 'Go'")
        print("   - Faster than Ask mode")
        print()
        print("💡 Quick Button:")
        print("   - Click '💡 Quick' for pre-defined questions")
        print("   - Select from common coding questions")
        print("   - Instant access to popular topics")
        print()
        print("💡 Features:")
        print("   - Three different input methods")
        print("   - 'Thinking...' dialog while processing")
        print("   - Answer displayed in scrollable dialog")
        print("   - Copy button to copy answer to clipboard")
        print()
        print("💡 If buttons don't appear:")
        print("   - Make sure MTMR is running")
        print("   - Right-click Touch Bar → Customize Touch Bar")
        print("   - Look for '🔍 Ask', '📝 Input', '💡 Quick'")
        print("   - Drag them to your Touch Bar")
        print()
        print("🔧 MTMR Configuration:")
        print(f"   - Config file: {self.items_config_file}")
        print(
            f"   - Script file: {Path(__file__).parent / 'advanced_input_handler.py'}"
        )
        print()
        print("🌐 MTMR Website: https://mtmr.app")
        print("📖 MTMR Documentation: https://github.com/Toxblh/MTMR")
        print("=" * 60)


def main():
    """Main function"""
    try:
        print("🚀 Setting up Advanced Touch Bar Input Integration...")

        # Create advanced Touch Bar input integration
        advanced_input = MTMRAdvancedInput()

        # Install MTMR if needed
        advanced_input.install_mtmr()

        # Setup the integration
        advanced_input.setup_advanced_input()

        # Show instructions
        advanced_input.show_instructions()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Please check the MTMR documentation: https://github.com/Toxblh/MTMR")


if __name__ == "__main__":
    main()
