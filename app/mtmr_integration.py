#!/usr/bin/env python3
"""
MTMR Integration for Touch Bar Coding Assistant
Uses MTMR (My TouchBar My Rules) approach for reliable Touch Bar integration
"""

import os
import json
import subprocess
import sys
from pathlib import Path


class MTMRIntegration:
    """MTMR-based Touch Bar integration"""

    def __init__(self):
        self.mtmr_config_dir = Path.home() / "Library/Application Support/MTMR"
        self.items_config_file = self.mtmr_config_dir / "items.json"
        self.coding_assistant_config = {
            "type": "shellScript",
            "title": "🔍 Code",
            "align": "center",
            "width": 80,
            "bordered": True,
            "refreshInterval": 1,
            "executablePath": "/usr/bin/python3",
            "shellArguments": [str(Path(__file__).parent / "coding_assistant.py")],
        }

    def setup_mtmr_integration(self):
        """Setup MTMR integration for Touch Bar"""
        try:
            print("🔧 Setting up MTMR Touch Bar integration...")

            # Create MTMR config directory if it doesn't exist
            self.mtmr_config_dir.mkdir(parents=True, exist_ok=True)

            # Create or update items.json
            self._create_items_config()

            # Create the coding assistant script
            self._create_coding_assistant_script()

            print("✅ MTMR integration setup complete!")
            print("🎯 Touch Bar button will appear as '🔍 Code'")
            print("💡 Make sure MTMR is running for the button to appear")

        except Exception as e:
            print(f"❌ Error setting up MTMR integration: {str(e)}")
            raise

    def _create_items_config(self):
        """Create or update MTMR items.json configuration"""
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

                    config.insert(insert_index, self.coding_assistant_config)
                    print("✅ Added coding assistant button to MTMR config")
                else:
                    print("ℹ️ Coding assistant button already exists in MTMR config")

            elif isinstance(config, dict) and "presets" in config:
                # Presets format - add to first preset
                preset = config["presets"][0]
                if "items" not in preset:
                    preset["items"] = []

                coding_button_exists = any(
                    item.get("title") == "🔍 Code" for item in preset["items"]
                )

                if not coding_button_exists:
                    preset["items"].append(self.coding_assistant_config)
                    print("✅ Added coding assistant button to MTMR config")
                else:
                    print("ℹ️ Coding assistant button already exists in MTMR config")

            # Save the configuration
            with open(self.items_config_file, "w") as f:
                json.dump(config, f, indent=2)

            print(f"✅ MTMR configuration saved to: {self.items_config_file}")

        except Exception as e:
            print(f"❌ Error creating MTMR config: {str(e)}")
            raise

    def _create_coding_assistant_script(self):
        """Create the coding assistant script that MTMR will execute"""
        script_path = Path(__file__).parent / "coding_assistant.py"

        script_content = '''#!/usr/bin/env python3
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
'''

        with open(script_path, "w") as f:
            f.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o755)

        print(f"✅ Coding assistant script created: {script_path}")

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
        """Show instructions for using the Touch Bar integration"""
        print("\n" + "=" * 60)
        print("🎯 MTMR Touch Bar Integration Instructions")
        print("=" * 60)
        print()
        print("✅ Setup Complete! Here's how to use your Touch Bar button:")
        print()
        print("1. 🔍 Look for '🔍 Code' button on your Touch Bar")
        print("2. 👆 Click the button to open the search dialog")
        print("3. 📝 Enter your coding interview question")
        print("4. 🔍 Click 'Search' to get the answer")
        print("5. 📖 The answer will appear in a dialog")
        print()
        print("💡 If the button doesn't appear:")
        print("   - Make sure MTMR is running")
        print("   - Right-click Touch Bar → Customize Touch Bar")
        print("   - Look for '🔍 Code' in the customization area")
        print("   - Drag it to your Touch Bar")
        print()
        print("🔧 MTMR Configuration:")
        print(f"   - Config file: {self.items_config_file}")
        print(f"   - Script file: {Path(__file__).parent / 'coding_assistant.py'}")
        print()
        print("🌐 MTMR Website: https://mtmr.app")
        print("📖 MTMR Documentation: https://github.com/Toxblh/MTMR")
        print("=" * 60)


def main():
    """Main function"""
    try:
        print("🚀 Setting up MTMR Touch Bar Integration...")

        # Create MTMR integration
        mtmr = MTMRIntegration()

        # Install MTMR if needed
        mtmr.install_mtmr()

        # Setup the integration
        mtmr.setup_mtmr_integration()

        # Show instructions
        mtmr.show_instructions()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Please check the MTMR documentation: https://github.com/Toxblh/MTMR")


if __name__ == "__main__":
    main()
