import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from typing import Optional, Callable
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from app.config import settings
from app.azure_service import AzureOpenAIService
import logging

logger = logging.getLogger(__name__)


class TouchBarUI:
    """Touch Bar interface for coding interview assistant"""

    def __init__(self):
        self.root = None
        self.search_entry = None
        self.answer_label = None
        self.search_button = None
        self.clear_button = None
        self.status_label = None
        self.is_searching = False
        self.search_callback: Optional[Callable] = None

        # Global hotkey components
        self.keyboard_listener = None
        self.is_visible = False
        self.hotkey_active = False

    def create_ui(self):
        """Create the Touch Bar UI"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Touch Bar Coding Assistant")
        self.root.geometry(f"{settings.TOUCH_BAR_WIDTH}x{settings.TOUCH_BAR_HEIGHT}")
        self.root.resizable(False, False)

        # Configure window to stay on top
        self.root.attributes("-topmost", True)

        # Set window position to bottom of screen (Touch Bar location)
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"+0+{screen_height - settings.TOUCH_BAR_HEIGHT}")

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        style.configure("TouchBar.TFrame", background=settings.BACKGROUND_COLOR)
        style.configure(
            "TouchBar.TLabel",
            background=settings.BACKGROUND_COLOR,
            foreground=settings.TEXT_COLOR,
            font=("SF Pro Display", settings.FONT_SIZE),
        )
        style.configure(
            "TouchBar.TButton",
            background=settings.ACCENT_COLOR,
            foreground=settings.TEXT_COLOR,
            font=("SF Pro Display", settings.FONT_SIZE - 2),
        )
        style.configure(
            "Search.TEntry",
            fieldbackground=settings.BACKGROUND_COLOR,
            foreground=settings.TEXT_COLOR,
            font=("SF Pro Display", settings.FONT_SIZE),
        )

        # Main frame
        main_frame = ttk.Frame(self.root, style="TouchBar.TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Search section
        search_frame = ttk.Frame(main_frame, style="TouchBar.TFrame")
        search_frame.pack(fill="x", pady=(0, 5))

        # Search label
        search_label = ttk.Label(
            search_frame, text="Question:", style="TouchBar.TLabel"
        )
        search_label.pack(side="left", padx=(0, 5))

        # Search entry
        self.search_entry = ttk.Entry(search_frame, style="Search.TEntry", width=50)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", self._on_search)
        self.search_entry.focus()

        # Search button
        self.search_button = ttk.Button(
            search_frame,
            text="Search",
            style="TouchBar.TButton",
            command=self._on_search,
        )
        self.search_button.pack(side="left", padx=(0, 5))

        # Clear button
        self.clear_button = ttk.Button(
            search_frame, text="Clear", style="TouchBar.TButton", command=self._on_clear
        )
        self.clear_button.pack(side="left")

        # Answer section
        answer_frame = ttk.Frame(main_frame, style="TouchBar.TFrame")
        answer_frame.pack(fill="both", expand=True)

        # Answer label
        self.answer_label = ttk.Label(
            answer_frame,
            text="Ask a coding interview question...",
            style="TouchBar.TLabel",
            wraplength=settings.TOUCH_BAR_WIDTH - 40,
            justify="left",
        )
        self.answer_label.pack(fill="both", expand=True, anchor="w")

        # Status section
        status_frame = ttk.Frame(main_frame, style="TouchBar.TFrame")
        status_frame.pack(fill="x", pady=(5, 0))

        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            style="TouchBar.TLabel",
            font=("SF Pro Display", settings.FONT_SIZE - 2),
        )
        self.status_label.pack(side="left")

        # Keyboard shortcuts
        self.root.bind("<Command-s>", self._on_search)
        self.root.bind("<Command-c>", self._on_clear)
        self.root.bind("<Escape>", lambda e: self.root.focus())

        # Set search callback
        self.search_callback = self._perform_search

        # Setup global hotkey (Option+G)
        self._setup_global_hotkey()

        # Initially hide the window
        self.root.withdraw()
        self.is_visible = False

    def _on_search(self, event=None):
        """Handle search button click or Enter key"""
        print(f"🔍 Debug: Search triggered with event: {event}")

        if self.is_searching:
            print("⚠️ Debug: Already searching, ignoring request")
            return

        question = self.search_entry.get().strip()
        print(f"🔍 Debug: Question: '{question}'")

        if not question:
            print("⚠️ Debug: Empty question, showing warning")
            messagebox.showwarning("Warning", "Please enter a question")
            return

        print(f"🚀 Debug: Starting search for: '{question}'")
        self._start_search(question)

        # Auto-hide after successful search (optional)
        # Uncomment the line below if you want the Touch Bar to auto-hide after search
        # self.root.after(5000, self._auto_hide)  # Hide after 5 seconds

    def _auto_hide(self):
        """Auto-hide the Touch Bar after a delay"""
        if self.is_visible and not self.is_searching:
            self.root.withdraw()
            self.is_visible = False
            print("👻 Touch Bar auto-hidden")

    def _on_clear(self, event=None):
        """Handle clear button click"""
        self.search_entry.delete(0, tk.END)
        self.answer_label.config(text="Ask a coding interview question...")
        self.status_label.config(text="Ready")
        self.search_entry.focus()

    def _start_search(self, question: str):
        """Start the search process"""
        print(f"🚀 Debug: Starting search process for: '{question}'")

        self.is_searching = True
        self.search_button.config(state="disabled")
        self.status_label.config(text="Searching...")
        self.answer_label.config(text="Generating answer...")

        # Run search in background thread
        thread = threading.Thread(target=self._run_search, args=(question,))
        thread.daemon = True
        thread.start()

        print(f"✅ Debug: Search thread started")

    def _run_search(self, question: str):
        """Run the search in a background thread"""
        print(f"🔄 Debug: Running search in background thread for: '{question}'")

        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            print(f"🔍 Debug: Calling search callback...")
            # Run the async search
            answer = loop.run_until_complete(self.search_callback(question))
            print(f"✅ Debug: Got answer: '{answer}'")

            # Update UI in main thread
            self.root.after(0, self._update_answer, answer)
            print(f"✅ Debug: Scheduled UI update")

        except Exception as e:
            print(f"❌ Debug: Search error: {str(e)}")
            logger.error(f"Search error: {str(e)}")
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self._update_answer, error_msg)
        finally:
            loop.close()
            print(f"✅ Debug: Search thread completed")

    def _update_answer(self, answer: str):
        """Update the answer display"""
        print(f"📝 Debug: Updating answer display with: '{answer}'")

        self.answer_label.config(text=answer)
        self.status_label.config(text="Ready")
        self.search_button.config(state="normal")
        self.is_searching = False

        print(f"✅ Debug: Answer display updated successfully")

    async def _perform_search(self, question: str) -> str:
        """Perform the actual search using Azure OpenAI"""
        try:
            answer = await AzureOpenAIService.get_coding_answer(question)
            return answer
        except Exception as e:
            logger.error(f"Azure OpenAI error: {str(e)}")
            return f"Error: Unable to get answer - {str(e)}"

    def _setup_global_hotkey(self):
        """Setup global hotkey (Option+G) to show/hide Touch Bar"""
        try:
            # Define the hotkey combination (Option+G)
            hotkey = {Key.alt, KeyCode.from_char("g")}

            # Create keyboard listener
            self.keyboard_listener = keyboard.GlobalHotKeys(
                {"<alt>+g": self._toggle_touch_bar}
            )

            # Start listening for hotkeys
            self.keyboard_listener.start()
            self.hotkey_active = True

            logger.info("✅ Global hotkey (Option+G) activated successfully!")
            print("🎯 Global hotkey (Option+G) is now active!")
            print("   Press Option+G to show/hide the Touch Bar")

        except Exception as e:
            logger.error(f"Failed to setup global hotkey: {str(e)}")
            print(f"❌ Failed to setup global hotkey: {str(e)}")

    def _toggle_touch_bar(self):
        """Toggle Touch Bar visibility with global hotkey"""
        try:
            if not self.root:
                return

            if self.is_visible:
                # Hide the Touch Bar
                self.root.withdraw()
                self.is_visible = False
                logger.info("Touch Bar hidden")
                print("👻 Touch Bar hidden")
            else:
                # Show the Touch Bar and focus on search
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                self.search_entry.focus()
                self.search_entry.select_range(0, tk.END)
                self.is_visible = True
                logger.info("Touch Bar shown and focused")
                print("🎯 Touch Bar shown and focused - ready to search!")

        except Exception as e:
            logger.error(f"Error toggling Touch Bar: {str(e)}")
            print(f"❌ Error toggling Touch Bar: {str(e)}")

    def _stop_global_hotkey(self):
        """Stop the global hotkey listener"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.hotkey_active = False
            logger.info("Global hotkey listener stopped")

    def run(self):
        """Start the Touch Bar UI"""
        if not self.root:
            self.create_ui()

        try:
            print("🚀 Touch Bar Coding Assistant is running!")
            print("🎯 Press Option+G to show/hide the Touch Bar")
            print("💡 Type your coding question and press Enter to search")
            print("🔄 Press Ctrl+C to exit")

            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            print("\n👋 Shutting down Touch Bar Coding Assistant...")
        except Exception as e:
            logger.error(f"UI error: {str(e)}")
            print(f"❌ UI error: {str(e)}")
        finally:
            # Cleanup global hotkey
            self._stop_global_hotkey()
            if self.root:
                self.root.destroy()
            print("✅ Touch Bar Coding Assistant stopped")


class TouchBarSimulator:
    """Simulator for testing Touch Bar functionality without actual Touch Bar"""

    def __init__(self):
        self.ui = TouchBarUI()

    def run(self):
        """Run the Touch Bar simulator"""
        print("Starting Touch Bar Coding Assistant Simulator...")
        print("This simulates the Touch Bar interface for development and testing.")
        print("Press Ctrl+C to exit.")

        self.ui.run()


if __name__ == "__main__":
    # For testing
    simulator = TouchBarSimulator()
    simulator.run()
