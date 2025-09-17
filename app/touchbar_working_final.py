#!/usr/bin/env python3
"""
Final Working Touch Bar Integration for MacBook Pro
Uses a different approach to avoid method signature issues
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
        NSApplicationActivationPolicyAccessory,
        NSTouchBar,
        NSTouchBarItem,
        NSTouchBarItemIdentifier,
    )

    TOUCHBAR_AVAILABLE = True
    print("✅ Final Touch Bar APIs loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class TouchBarSearchItem(NSObject):
    """Touch Bar item for search functionality"""

    def init(self):
        self = objc.super(TouchBarSearchItem, self).init()
        if self is None:
            return None
        return self

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item"""
        if identifier == "coding-assistant-search":
            item = NSTouchBarItem.alloc().initWithIdentifier_(identifier)
            button = NSButton.buttonWithTitle_target_action_(
                "🔍 Code", self, objc.selector(self.search_action_, signature=b"v@:@")
            )
            button.setBezelColor_(objc.lookUpClass("NSColor").systemBlueColor())
            item.setView_(button)
            return item
        return None

    def search_action_(self, sender):
        """Handle search button press"""
        try:
            # Create a simple alert for now
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Touch Bar Coding Assistant")
            alert.setInformativeText_(
                "Touch Bar button pressed! This will open the search window."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

            logger.info("Touch Bar search button pressed")
            print("🎯 Touch Bar button pressed!")

        except Exception as e:
            logger.error(f"Error handling Touch Bar button press: {str(e)}")
            print(f"❌ Error: {str(e)}")


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


class FinalTouchBarIntegration(NSObject):
    """Final Touch Bar integration using NSTouchBar API"""

    def init(self):
        self = objc.super(FinalTouchBarIntegration, self).init()
        if self is None:
            return None

        self.search_window = None
        self.is_active = False
        self.touch_bar = None
        self.touch_bar_item = None

        if not TOUCHBAR_AVAILABLE:
            raise RuntimeError("Touch Bar APIs not available on this system")

        return self

    def setup_touch_bar(self):
        """Setup the Touch Bar with a search button"""
        try:
            # Create Touch Bar
            self.touch_bar = NSTouchBar.alloc().init()
            self.touch_bar.setDelegate_(self)
            self.touch_bar.setDefaultItemIdentifiers_(["coding-assistant-search"])
            self.touch_bar.setCustomizationIdentifier_("coding-assistant-touchbar")
            self.touch_bar.setCustomizationAllowedItemIdentifiers_(
                ["coding-assistant-search"]
            )

            # Create Touch Bar item
            self.touch_bar_item = TouchBarSearchItem.alloc().init()

            # Set the Touch Bar for the application
            NSApp.setTouchBar_(self.touch_bar)

            self.is_active = True
            logger.info("✅ Final Touch Bar integration activated!")
            print(
                "🎯 Final Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            raise

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item"""
        return self.touch_bar_item.touchBar_makeItemForIdentifier_(touchBar, identifier)

    def cleanup(self):
        """Cleanup Touch Bar resources"""
        if self.is_active:
            try:
                NSApp.setTouchBar_(None)
                self.is_active = False
                logger.info("Touch Bar integration cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Touch Bar: {str(e)}")


def main():
    """Main function to run the final Touch Bar integration"""
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
        touch_bar = FinalTouchBarIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Final Touch Bar Coding Assistant is running!")
        print("🎯 Look for '🔍 Code' button on your Touch Bar")
        print("💡 Click it to test the integration")
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
