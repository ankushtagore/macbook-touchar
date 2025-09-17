#!/usr/bin/env python3
"""
Robust Touch Bar Integration for MacBook Pro
Uses a more robust approach to avoid crashes and handle errors better
"""

import asyncio
import threading
import logging
import sys
import os
import signal
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
    print("✅ Robust Touch Bar APIs loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class RobustTouchBarIntegration(NSObject):
    """Robust Touch Bar integration that handles errors better"""

    def init(self):
        self = objc.super(RobustTouchBarIntegration, self).init()
        if self is None:
            return None

        self.is_active = False
        self.touch_bar = None
        self.window = None
        self.app = None

        if not TOUCHBAR_AVAILABLE:
            raise RuntimeError("Touch Bar APIs not available on this system")

        return self

    def setup_touch_bar(self):
        """Setup the Touch Bar with a search button"""
        try:
            print("🔧 Setting up Touch Bar...")

            # Create a visible window to make the app active
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(100, 100, 400, 200),
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
                NSBackingStoreBuffered,
                False,
            )

            self.window.setTitle_("Touch Bar Coding Assistant")

            # Add a label to the window
            content_view = self.window.contentView()
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 50, 360, 100))
            label.setStringValue_(
                "Touch Bar Coding Assistant is running!\n\nLook for '🔍 Code' button on your Touch Bar.\n\nIf the button doesn't appear:\n1. Make sure this window is active\n2. Check Touch Bar customization\n3. Try clicking in this window"
            )
            label.setEditable_(False)
            label.setBezeled_(False)
            label.setDrawsBackground_(False)
            label.setSelectable_(False)
            content_view.addSubview_(label)

            # Add a test button to the window
            test_button = NSButton.alloc().initWithFrame_(NSMakeRect(20, 20, 100, 30))
            test_button.setTitle_("Test Alert")
            test_button.setTarget_(self)
            test_button.setAction_(
                objc.selector(self.test_alert_action, signature=b"v@:@")
            )
            content_view.addSubview_(test_button)

            self.window.makeKeyAndOrderFront_(None)

            print("✅ Window created successfully!")

            # Create Touch Bar
            self.touch_bar = NSTouchBar.alloc().init()
            self.touch_bar.setDelegate_(self)
            self.touch_bar.setDefaultItemIdentifiers_(["robust-search-button"])
            self.touch_bar.setCustomizationIdentifier_("robust-coding-assistant")
            self.touch_bar.setCustomizationAllowedItemIdentifiers_(
                ["robust-search-button"]
            )

            print("✅ Touch Bar created successfully!")

            # Set the Touch Bar for the application
            NSApp.setTouchBar_(self.touch_bar)

            print("✅ Touch Bar set for application!")

            # Make the application active
            NSApp.activateIgnoringOtherApps_(True)

            self.is_active = True
            logger.info("✅ Robust Touch Bar integration activated!")
            print(
                "🎯 Robust Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )
            print("💡 The app window should be visible and active")

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            print(f"❌ Error setting up Touch Bar: {str(e)}")
            raise

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item"""
        try:
            if identifier == "robust-search-button":
                item = NSTouchBarItem.alloc().initWithIdentifier_(identifier)
                button = NSButton.buttonWithTitle_target_action_(
                    "🔍 Code",
                    self,
                    objc.selector(self.robust_search_action, signature=b"v@:@"),
                )
                button.setBezelColor_(objc.lookUpClass("NSColor").systemBlueColor())
                item.setView_(button)
                return item
            return None
        except Exception as e:
            print(f"❌ Error creating Touch Bar item: {str(e)}")
            return None

    def robust_search_action(self, sender):
        """Handle search button press"""
        try:
            print("🎯 Touch Bar button pressed!")

            # Create a simple alert for now
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Touch Bar Coding Assistant")
            alert.setInformativeText_(
                "Touch Bar button pressed! This will open the search window."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

            logger.info("Touch Bar search button pressed")

        except Exception as e:
            logger.error(f"Error handling Touch Bar button press: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def test_alert_action(self, sender):
        """Handle test button press"""
        try:
            print("🎯 Test button pressed!")

            # Create a simple alert for now
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Test Alert")
            alert.setInformativeText_(
                "Test button pressed! This confirms the app is working."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

        except Exception as e:
            logger.error(f"Error handling test button press: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def cleanup(self):
        """Cleanup Touch Bar resources"""
        try:
            if self.is_active:
                print("🧹 Cleaning up Touch Bar resources...")
                NSApp.setTouchBar_(None)
                if self.window:
                    self.window.close()
                self.is_active = False
                logger.info("Touch Bar integration cleaned up")
                print("✅ Touch Bar resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Touch Bar: {str(e)}")
            print(f"❌ Error cleaning up: {str(e)}")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n👋 Received interrupt signal, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function to run the robust Touch Bar integration"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not TOUCHBAR_AVAILABLE:
        print("❌ Touch Bar APIs not available on this system")
        print("This feature requires macOS with Touch Bar support")
        print("Make sure you're running on a MacBook Pro with Touch Bar")
        return

    touch_bar = None

    try:
        print("🚀 Starting Robust Touch Bar Coding Assistant...")

        # Initialize NSApplication
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        print("✅ NSApplication initialized!")

        # Create Touch Bar integration
        touch_bar = RobustTouchBarIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Robust Touch Bar Coding Assistant is running!")
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
        if touch_bar:
            touch_bar.cleanup()
        print("✅ Touch Bar Coding Assistant stopped")


if __name__ == "__main__":
    main()
