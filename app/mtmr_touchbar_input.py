#!/usr/bin/env python3
"""
MTMR Touch Bar Input Integration
Shows input field directly on Touch Bar for coding questions
"""

import os
import json
import subprocess
import sys
from pathlib import Path


class MTMRTouchBarInput:
    """MTMR Touch Bar input integration"""

    def __init__(self):
        self.mtmr_config_dir = Path.home() / "Library/Application Support/MTMR"
        self.items_config_file = self.mtmr_config_dir / "items.json"

        # Touch Bar input configuration
        self.touchbar_input_config = {
            "type": "shellScript",
            "title": "🔍 Code",
            "align": "center",
            "width": 80,
            "bordered": True,
            "refreshInterval": 1,
            "executablePath": "/usr/bin/python3",
            "shellArguments": [
                str(Path(__file__).parent / "touchbar_input_handler.py")
            ],
        }

    def setup_touchbar_input(self):
        """Setup Touch Bar input integration"""
        try:
            print("🔧 Setting up Touch Bar Input integration...")

            # Create MTMR config directory if it doesn't exist
            self.mtmr_config_dir.mkdir(parents=True, exist_ok=True)

            # Create or update items.json with Touch Bar input
            self._create_touchbar_input_config()

            # Create the Touch Bar input handler script
            self._create_touchbar_input_handler()

            print("✅ Touch Bar Input integration setup complete!")
            print("🎯 Touch Bar button will show input field directly on Touch Bar")
            print("💡 Make sure MTMR is running for the button to appear")

        except Exception as e:
            print(f"❌ Error setting up Touch Bar Input integration: {str(e)}")
            raise

    def _create_touchbar_input_config(self):
        """Create or update MTMR items.json configuration with Touch Bar input"""
        try:
            # Load existing config or create new one
            if self.items_config_file.exists():
                with open(self.items_config_file, "r") as f:
                    config = json.load(f)
            else:
                config = []

            # Check if config is in array format (existing) or presets format (new)
            if isinstance(config, list):
                # Array format - add our button to the array
                coding_button_exists = any(
                    item.get("title") == "🔍 Code" for item in config
                )

                if not coding_button_exists:
                    # Add our button after the escape button
                    insert_index = 0
                    for i, item in enumerate(config):
                        if item.get("type") == "escape":
                            insert_index = i + 1
                            break

                    config.insert(insert_index, self.touchbar_input_config)
                    print("✅ Added Touch Bar input button to MTMR config")
                else:
                    print("ℹ️ Touch Bar input button already exists in MTMR config")

            elif isinstance(config, dict) and "presets" in config:
                # Presets format - add to first preset
                preset = config["presets"][0]
                if "items" not in preset:
                    preset["items"] = []

                coding_button_exists = any(
                    item.get("title") == "🔍 Code" for item in preset["items"]
                )

                if not coding_button_exists:
                    preset["items"].append(self.touchbar_input_config)
                    print("✅ Added Touch Bar input button to MTMR config")
                else:
                    print("ℹ️ Touch Bar input button already exists in MTMR config")

            # Save the configuration
            with open(self.items_config_file, "w") as f:
                json.dump(config, f, indent=2)

            print(f"✅ MTMR configuration saved to: {self.items_config_file}")

        except Exception as e:
            print(f"❌ Error creating MTMR config: {str(e)}")
            raise

    def _create_touchbar_input_handler(self):
        """Create the Touch Bar input handler script"""
        script_path = Path(__file__).parent / "touchbar_input_handler.py"

        script_content = '''#!/usr/bin/env python3
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
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
'''

        with open(script_path, "w") as f:
            f.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o755)

        print(f"✅ Touch Bar input handler created: {script_path}")

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
        """Show instructions for using the Touch Bar input"""
        print("\n" + "=" * 60)
        print("🎯 Touch Bar Input Integration Instructions")
        print("=" * 60)
        print()
        print("✅ Setup Complete! Here's how to use your Touch Bar input:")
        print()
        print("1. 🔍 Look for '🔍 Code' button on your Touch Bar")
        print("2. 👆 Click the button to open input field")
        print("3. 📝 Type your coding question in the input field")
        print("4. 🔍 Click 'Ask' to get the answer")
        print("5. 📖 The answer will appear in a dialog")
        print("6. 📋 Click 'Copy' to copy answer to clipboard")
        print()
        print("💡 Features:")
        print("   - Input field appears directly when you click the button")
        print("   - 'Thinking...' dialog shows while getting answer")
        print("   - Answer is displayed in a scrollable dialog")
        print("   - Copy button to copy answer to clipboard")
        print()
        print("💡 If the button doesn't appear:")
        print("   - Make sure MTMR is running")
        print("   - Right-click Touch Bar → Customize Touch Bar")
        print("   - Look for '🔍 Code' in the customization area")
        print("   - Drag it to your Touch Bar")
        print()
        print("🔧 MTMR Configuration:")
        print(f"   - Config file: {self.items_config_file}")
        print(
            f"   - Script file: {Path(__file__).parent / 'touchbar_input_handler.py'}"
        )
        print()
        print("🌐 MTMR Website: https://mtmr.app")
        print("📖 MTMR Documentation: https://github.com/Toxblh/MTMR")
        print("=" * 60)


def main():
    """Main function"""
    try:
        print("🚀 Setting up Touch Bar Input Integration...")

        # Create Touch Bar input integration
        touchbar_input = MTMRTouchBarInput()

        # Install MTMR if needed
        touchbar_input.install_mtmr()

        # Setup the integration
        touchbar_input.setup_touchbar_input()

        # Show instructions
        touchbar_input.show_instructions()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Please check the MTMR documentation: https://github.com/Toxblh/MTMR")


if __name__ == "__main__":
    main()
