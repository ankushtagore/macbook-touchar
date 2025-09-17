#!/usr/bin/env python3
"""
Working Touch Bar Integration for MacBook Pro
Uses available macOS APIs to add buttons to the Touch Bar
"""

import asyncio
import threading
import logging
import sys
import os
from typing import Optional, Callable

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.azure_service import AzureOpenAIService

# Import macOS APIs
try:
    import objc
    from Foundation import NSObject, NSRunLoop, NSDefaultRunLoopMode
    from AppKit import (
        NSApplication,
        NSApp,
        NSStatusBar,
        NSMenu,
        NSMenuItem,
        NSAlert,
        NSInformationalAlertStyle,
        NSWindow,
        NSView,
        NSButton,
        NSTextField,
        NSScrollView,
        NSTextView,
        NSMakeRect,
        NSRect,
        NSSize,
        NSPoint,
        NSWindowStyleMaskTitled,
        NSWindowStyleMaskClosable,
        NSWindowStyleMaskMiniaturizable,
        NSWindowStyleMaskResizable,
        NSBackingStoreBuffered,
        NSWindowLevelFloating,
        NSApplicationActivationPolicyAccessory,
    )

    # Try to import Touch Bar specific APIs
    try:
        # Try to load Touch Bar framework
        objc.loadBundle(
            "DFRFoundation",
            globals(),
            "/System/Library/PrivateFrameworks/DFRFoundation.framework",
        )
        TOUCHBAR_AVAILABLE = True
    except Exception:
        TOUCHBAR_AVAILABLE = False

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class TouchBarSearchWindow(NSObject):
    """Search window that appears when Touch Bar button is pressed"""

    def init(self):
        self = objc.super(TouchBarSearchWindow, self).init()
        if self is None:
            return None

        # Create the search window
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(100, 100, 600, 400),
            NSWindowStyleMaskTitled
            | NSWindowStyleMaskClosable
            | NSWindowStyleMaskMiniaturizable
            | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False,
        )

        self.window.setTitle_("Touch Bar Coding Assistant")
        self.window.setLevel_(NSWindowLevelFloating)
        self.window.makeKeyAndOrderFront_(None)

        # Create the search interface
        self._create_search_interface()

        return self

    def _create_search_interface(self):
        """Create the search interface elements"""
        content_view = self.window.contentView()

        # Search field
        self.search_field = NSTextField.alloc().initWithFrame_(
            NSMakeRect(20, 350, 400, 30)
        )
        self.search_field.setPlaceholderString_("Enter your coding question...")
        content_view.addSubview_(self.search_field)

        # Search button
        self.search_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(440, 350, 80, 30)
        )
        self.search_button.setTitle_("Search")
        self.search_button.setBezelStyle_(1)  # Rounded button
        self.search_button.setTarget_(self)
        self.search_button.setAction_(
            objc.selector(self.search_action_, signature=b"v@:@")
        )
        content_view.addSubview_(self.search_button)

        # Answer text view
        scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 20, 560, 320))
        self.answer_text = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 320))
        self.answer_text.setEditable_(False)
        self.answer_text.setString_("Ask a coding interview question...")
        scroll_view.setDocumentView_(self.answer_text)
        content_view.addSubview_(scroll_view)

        # Bind Enter key to search
        self.search_field.setTarget_(self)
        self.search_field.setAction_(
            objc.selector(self.search_action_, signature=b"v@:@")
        )

    def search_action_(self, sender):
        """Handle search button click or Enter key"""
        question = self.search_field.stringValue().strip()
        if not question:
            return

        # Update UI
        self.search_button.setEnabled_(False)
        self.answer_text.setString_("Searching...")

        # Run search in background
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
            answer = loop.run_until_complete(self._perform_search(question))

            # Update UI in main thread
            self.window.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(self._update_answer_, signature=b"v@:@"), answer, False
            )

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            error_msg = f"Error: {str(e)}"
            self.window.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(self._update_answer_, signature=b"v@:@"), error_msg, False
            )
        finally:
            loop.close()

    def _update_answer_(self, answer: str):
        """Update the answer display"""
        self.answer_text.setString_(answer)
        self.search_button.setEnabled_(True)

    async def _perform_search(self, question: str) -> str:
        """Perform the actual search using Azure OpenAI"""
        try:
            answer = await AzureOpenAIService.get_coding_answer(question)
            return answer
        except Exception as e:
            logger.error(f"Azure OpenAI error: {str(e)}")
            return f"Error: Unable to get answer - {str(e)}"


class WorkingTouchBarIntegration(NSObject):
    """Working Touch Bar integration for MacBook Pro"""

    def init(self):
        self = objc.super(WorkingTouchBarIntegration, self).init()
        if self is None:
            return None

        self.search_window = None
        self.is_active = False
        self.touch_bar_item = None

        if not TOUCHBAR_AVAILABLE:
            raise RuntimeError("Touch Bar APIs not available on this system")

        return self

    def setup_touch_bar(self):
        """Setup the Touch Bar with a search button"""
        try:
            # Get the shared display server
            display_server = objc.lookUpClass("DFRDisplayServer").sharedDisplayServer()

            # Create Touch Bar item
            self.touch_bar_item = objc.lookUpClass("DFRTouchBarItem").alloc().init()

            # Configure the Touch Bar item
            self.touch_bar_item.setTitle_("🔍 Code")
            self.touch_bar_item.setCustomizationLabel_("Coding Assistant")
            self.touch_bar_item.setCustomizationAllowed_(True)
            self.touch_bar_item.setWidth_(100)
            self.touch_bar_item.setTarget_(self)
            self.touch_bar_item.setAction_(
                objc.selector(self._search_button_pressed, signature=b"v@:@")
            )
            self.touch_bar_item.setEnabled_(True)

            # Add to Touch Bar
            display_server.addTouchBarItem_(self.touch_bar_item)

            self.is_active = True
            logger.info("✅ Working Touch Bar integration activated!")
            print(
                "🎯 Working Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            raise

    def _search_button_pressed(self, sender):
        """Handle Touch Bar button press"""
        try:
            if not self.search_window:
                self.search_window = TouchBarSearchWindow.alloc().init()
            else:
                self.search_window.window.makeKeyAndOrderFront_(None)

            logger.info("Touch Bar search button pressed")
            print("🎯 Touch Bar search window opened!")

        except Exception as e:
            logger.error(f"Error handling Touch Bar button press: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def cleanup(self):
        """Cleanup Touch Bar resources"""
        if self.is_active and hasattr(self, "touch_bar_item") and self.touch_bar_item:
            try:
                display_server = objc.lookUpClass(
                    "DFRDisplayServer"
                ).sharedDisplayServer()
                display_server.removeTouchBarItem_(self.touch_bar_item)
                self.is_active = False
                logger.info("Touch Bar integration cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Touch Bar: {str(e)}")


def main():
    """Main function to run the working Touch Bar integration"""
    if not TOUCHBAR_AVAILABLE:
        print("❌ Touch Bar APIs not available on this system")
        print("This feature requires macOS with Touch Bar support")
        print("Make sure you're running on a MacBook Pro with Touch Bar")
        return

    try:
        # Initialize NSApplication
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        # Create Touch Bar integration
        touch_bar = WorkingTouchBarIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Working Touch Bar Coding Assistant is running!")
        print("🎯 Look for '🔍 Code' button on your Touch Bar")
        print("💡 Click it to open the search window")
        print("🔄 Press Ctrl+C to exit")

        # Run the application
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Shutting down Touch Bar Coding Assistant...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Application error: {str(e)}")
    finally:
        if "touch_bar" in locals():
            touch_bar.cleanup()
        print("✅ Touch Bar Coding Assistant stopped")


if __name__ == "__main__":
    main()
