#!/usr/bin/env python3
"""
Touch Bar Button Simulator
Creates a floating button on screen that mimics Touch Bar functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import logging
from typing import Optional, Callable
from app.config import settings
from app.azure_service import AzureOpenAIService

logger = logging.getLogger(__name__)


class TouchBarButton:
    """Floating Touch Bar button that appears on screen"""

    def __init__(self):
        self.root = None
        self.button = None
        self.search_window = None
        self.is_active = False

    def create_button(self):
        """Create the floating Touch Bar button"""
        # Create main window (hidden)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

        # Create floating button window
        self.button_window = tk.Toplevel(self.root)
        self.button_window.title("Touch Bar Button")
        self.button_window.geometry("80x40")
        self.button_window.resizable(False, False)

        # Configure button window
        self.button_window.configure(bg="black")
        self.button_window.attributes("-topmost", True)
        self.button_window.overrideredirect(True)  # Remove window decorations

        # Position at bottom center of screen (Touch Bar location)
        screen_width = self.button_window.winfo_screenwidth()
        screen_height = self.button_window.winfo_screenheight()
        x = (screen_width - 80) // 2
        y = screen_height - 50  # Near bottom of screen
        self.button_window.geometry(f"80x40+{x}+{y}")

        # Create the button
        self.button = tk.Button(
            self.button_window,
            text="🔍\nCode",
            font=("SF Pro Display", 10, "bold"),
            bg="#1e1e1e",
            fg="white",
            relief="flat",
            borderwidth=0,
            command=self._show_search_window,
        )
        self.button.pack(fill="both", expand=True, padx=2, pady=2)

        # Add hover effects
        self.button.bind("<Enter>", self._on_hover)
        self.button.bind("<Leave>", self._on_leave)

        # Add click animation
        self.button.bind("<Button-1>", self._on_click)

        self.is_active = True
        logger.info("✅ Touch Bar button created!")
        print("🎯 Touch Bar button created! Look for the floating '🔍 Code' button")

    def _on_hover(self, event):
        """Handle button hover"""
        self.button.configure(bg="#333333")

    def _on_leave(self, event):
        """Handle button leave"""
        self.button.configure(bg="#1e1e1e")

    def _on_click(self, event):
        """Handle button click"""
        self.button.configure(bg="#555555")
        self.button_window.after(100, lambda: self.button.configure(bg="#1e1e1e"))
        self._show_search_window()

    def _show_search_window(self):
        """Show the search window"""
        if not self.search_window:
            self.search_window = TouchBarSearchWindow()
            self.search_window.create_window()
        else:
            self.search_window.show_window()

        logger.info("Touch Bar button pressed - search window opened")
        print("🎯 Search window opened!")

    def run(self):
        """Run the Touch Bar button"""
        if not self.is_active:
            self.create_button()

        try:
            print("🚀 Touch Bar Button is running!")
            print("🎯 Look for the floating '🔍 Code' button on your screen")
            print("💡 Click it to open the search window")
            print("🔄 Press Ctrl+C to exit")

            self.root.mainloop()

        except KeyboardInterrupt:
            print("\n👋 Shutting down Touch Bar Button...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            logger.error(f"Button error: {str(e)}")
        finally:
            if self.root:
                self.root.destroy()
            print("✅ Touch Bar Button stopped")


class TouchBarSearchWindow:
    """Search window that appears when Touch Bar button is clicked"""

    def __init__(self):
        self.window = None
        self.search_entry = None
        self.answer_label = None
        self.search_button = None
        self.is_searching = False
        self.search_callback = None

    def create_window(self):
        """Create the search window"""
        # Create window
        self.window = tk.Toplevel()
        self.window.title("Touch Bar Coding Assistant")
        self.window.geometry("600x400")
        self.window.resizable(True, True)

        # Configure window
        self.window.configure(bg=settings.BACKGROUND_COLOR)
        self.window.attributes("-topmost", True)

        # Center window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 600) // 2
        y = (self.window.winfo_screenheight() - 400) // 2
        self.window.geometry(f"600x400+{x}+{y}")

        # Create UI elements
        self._create_ui()

        # Set search callback
        self.search_callback = self._perform_search

        # Show window
        self.window.deiconify()
        self.window.focus_force()
        self.search_entry.focus()

    def _create_ui(self):
        """Create the UI elements"""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Touch Bar Coding Assistant",
            font=("SF Pro Display", 16, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Search section
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 20))

        # Search label
        search_label = ttk.Label(
            search_frame, text="Question:", font=("SF Pro Display", 12)
        )
        search_label.pack(anchor="w")

        # Search entry
        self.search_entry = ttk.Entry(
            search_frame, font=("SF Pro Display", 12), width=50
        )
        self.search_entry.pack(fill="x", pady=(5, 10))
        self.search_entry.bind("<Return>", self._on_search)

        # Search button
        self.search_button = ttk.Button(
            search_frame, text="Search", command=self._on_search, style="Accent.TButton"
        )
        self.search_button.pack(anchor="e")

        # Answer section
        answer_frame = ttk.Frame(main_frame)
        answer_frame.pack(fill="both", expand=True)

        # Answer label
        answer_label = ttk.Label(
            answer_frame, text="Answer:", font=("SF Pro Display", 12)
        )
        answer_label.pack(anchor="w")

        # Answer text
        self.answer_text = tk.Text(
            answer_frame,
            font=("SF Pro Display", 11),
            wrap="word",
            height=15,
            bg="white",
            relief="solid",
            borderwidth=1,
        )
        self.answer_text.pack(fill="both", expand=True, pady=(5, 0))

        # Scrollbar for answer text
        scrollbar = ttk.Scrollbar(
            answer_frame, orient="vertical", command=self.answer_text.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.answer_text.configure(yscrollcommand=scrollbar.set)

        # Status bar
        self.status_label = ttk.Label(
            main_frame, text="Ready", font=("SF Pro Display", 10)
        )
        self.status_label.pack(anchor="w", pady=(10, 0))

    def _on_search(self, event=None):
        """Handle search button click or Enter key"""
        if self.is_searching:
            return

        question = self.search_entry.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question")
            return

        self._start_search(question)

    def _start_search(self, question: str):
        """Start the search process"""
        self.is_searching = True
        self.search_button.config(state="disabled")
        self.status_label.config(text="Searching...")
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(1.0, "Generating answer...")

        # Run search in background thread
        thread = threading.Thread(target=self._run_search, args=(question,))
        thread.daemon = True
        thread.start()

    def _run_search(self, question: str):
        """Run the search in background thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async search
            answer = loop.run_until_complete(self.search_callback(question))

            # Update UI in main thread
            self.window.after(0, self._update_answer, answer)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            error_msg = f"Error: {str(e)}"
            self.window.after(0, self._update_answer, error_msg)
        finally:
            loop.close()

    def _update_answer(self, answer: str):
        """Update the answer display"""
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(1.0, answer)
        self.status_label.config(text="Ready")
        self.search_button.config(state="normal")
        self.is_searching = False

    async def _perform_search(self, question: str) -> str:
        """Perform the actual search using Azure OpenAI"""
        try:
            answer = await AzureOpenAIService.get_coding_answer(question)
            return answer
        except Exception as e:
            logger.error(f"Azure OpenAI error: {str(e)}")
            return f"Error: Unable to get answer - {str(e)}"

    def show_window(self):
        """Show the search window"""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            self.search_entry.focus()


def main():
    """Main function to run the Touch Bar button"""
    try:
        # Create and run Touch Bar button
        touch_bar_button = TouchBarButton()
        touch_bar_button.run()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()
