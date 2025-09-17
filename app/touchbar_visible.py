#!/usr/bin/env python3
"""
Visible Touch Bar Integration for MacBook Pro
Makes the application active to ensure Touch Bar button is visible
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
        NSApplicationActivationPolicyRegular,
        NSTouchBar,
        NSTouchBarItem,
        NSTouchBarItemIdentifier,
    )

    TOUCHBAR_AVAILABLE = True
    print("✅ Visible Touch Bar APIs loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class VisibleTouchBarIntegration(NSObject):
    """Visible Touch Bar integration that makes the app active"""

    def init(self):
        self = objc.super(VisibleTouchBarIntegration, self).init()
        if self is None:
            return None

        self.is_active = False
        self.touch_bar = None
        self.window = None

        if not TOUCHBAR_AVAILABLE:
            raise RuntimeError("Touch Bar APIs not available on this system")

        return self

    def setup_touch_bar(self):
        """Setup the Touch Bar with a search button"""
        try:
            # Create a visible window to make the app active
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(100, 100, 300, 100),
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
                NSBackingStoreBuffered,
                False,
            )

            self.window.setTitle_("Touch Bar Coding Assistant")
            self.window.makeKeyAndOrderFront_(None)

            # Create Touch Bar
            self.touch_bar = NSTouchBar.alloc().init()
            self.touch_bar.setDelegate_(self)
            self.touch_bar.setDefaultItemIdentifiers_(["visible-search-button"])
            self.touch_bar.setCustomizationIdentifier_("visible-coding-assistant")
            self.touch_bar.setCustomizationAllowedItemIdentifiers_(
                ["visible-search-button"]
            )

            # Set the Touch Bar for the application
            NSApp.setTouchBar_(self.touch_bar)

            # Make the application active
            NSApp.activateIgnoringOtherApps_(True)

            self.is_active = True
            logger.info("✅ Visible Touch Bar integration activated!")
            print(
                "🎯 Visible Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )
            print("💡 The app window should be visible and active")

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            raise

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item"""
        if identifier == "visible-search-button":
            item = NSTouchBarItem.alloc().initWithIdentifier_(identifier)
            button = NSButton.buttonWithTitle_target_action_(
                "🔍 Code",
                self,
                objc.selector(self.visible_search_action, signature=b"v@:@"),
            )
            button.setBezelColor_(objc.lookUpClass("NSColor").systemBlueColor())
            item.setView_(button)
            return item
        return None

    def visible_search_action(self, sender):
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

    def cleanup(self):
        """Cleanup Touch Bar resources"""
        if self.is_active:
            try:
                NSApp.setTouchBar_(None)
                if self.window:
                    self.window.close()
                self.is_active = False
                logger.info("Touch Bar integration cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Touch Bar: {str(e)}")


def main():
    """Main function to run the visible Touch Bar integration"""
    if not TOUCHBAR_AVAILABLE:
        print("❌ Touch Bar APIs not available on this system")
        print("This feature requires macOS with Touch Bar support")
        print("Make sure you're running on a MacBook Pro with Touch Bar")
        return

    try:
        # Initialize NSApplication
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        # Create Touch Bar integration
        touch_bar = VisibleTouchBarIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Visible Touch Bar Coding Assistant is running!")
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
