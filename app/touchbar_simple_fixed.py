#!/usr/bin/env python3
"""
Simple Fixed Touch Bar Integration for MacBook Pro
Uses a simpler approach to add buttons to the Touch Bar
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
    )

    # Load the Touch Bar framework
    objc.loadBundle(
        "DFRFoundation",
        globals(),
        "/System/Library/PrivateFrameworks/DFRFoundation.framework",
    )
    TOUCHBAR_AVAILABLE = True
    print("✅ Touch Bar framework loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class SimpleTouchBarIntegration(NSObject):
    """Simple Touch Bar integration for MacBook Pro"""

    def init(self):
        self = objc.super(SimpleTouchBarIntegration, self).init()
        if self is None:
            return None

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
            logger.info("✅ Simple Touch Bar integration activated!")
            print(
                "🎯 Simple Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            raise

    def _search_button_pressed(self, sender):
        """Handle Touch Bar button press"""
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
    """Main function to run the simple Touch Bar integration"""
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
        touch_bar = SimpleTouchBarIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Simple Touch Bar Coding Assistant is running!")
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
