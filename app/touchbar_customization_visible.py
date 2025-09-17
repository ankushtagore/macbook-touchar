#!/usr/bin/env python3
"""
Touch Bar Customization Visible Integration for MacBook Pro
Uses Touch Bar customization to make the button visible in the Touch Bar
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
    print("✅ Touch Bar Customization APIs loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class TouchBarCustomizationIntegration(NSObject):
    """Touch Bar customization integration that makes the button visible"""

    def init(self):
        self = objc.super(TouchBarCustomizationIntegration, self).init()
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
                NSMakeRect(100, 100, 400, 150),
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
                NSBackingStoreBuffered,
                False,
            )

            self.window.setTitle_("Touch Bar Coding Assistant")

            # Add a label to the window
            content_view = self.window.contentView()
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 50, 360, 60))
            label.setStringValue_(
                "Touch Bar Coding Assistant is running!\n\nLook for '🔍 Code' button in your Touch Bar customization area.\n\nTo customize your Touch Bar:\n1. Right-click on your Touch Bar\n2. Select 'Customize Touch Bar'\n3. Look for 'Coding Assistant' in the customization area\n4. Drag it to your Touch Bar"
            )
            label.setEditable_(False)
            label.setBezeled_(False)
            label.setDrawsBackground_(False)
            label.setSelectable_(False)
            content_view.addSubview_(label)

            self.window.makeKeyAndOrderFront_(None)

            # Create Touch Bar
            self.touch_bar = NSTouchBar.alloc().init()
            self.touch_bar.setDelegate_(self)
            self.touch_bar.setDefaultItemIdentifiers_(["customization-search-button"])
            self.touch_bar.setCustomizationIdentifier_("coding-assistant-customization")
            self.touch_bar.setCustomizationAllowedItemIdentifiers_(
                ["customization-search-button"]
            )

            # Set the Touch Bar for the application
            NSApp.setTouchBar_(self.touch_bar)

            # Make the application active
            NSApp.activateIgnoringOtherApps_(True)

            self.is_active = True
            logger.info("✅ Touch Bar Customization integration activated!")
            print("🎯 Touch Bar Customization button added!")
            print("💡 To see the button:")
            print("   1. Right-click on your Touch Bar")
            print("   2. Select 'Customize Touch Bar'")
            print("   3. Look for 'Coding Assistant' in the customization area")
            print("   4. Drag it to your Touch Bar")

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            raise

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item"""
        if identifier == "customization-search-button":
            item = NSTouchBarItem.alloc().initWithIdentifier_(identifier)
            button = NSButton.buttonWithTitle_target_action_(
                "🔍 Code",
                self,
                objc.selector(self.customization_search_action, signature=b"v@:@"),
            )
            button.setBezelColor_(objc.lookUpClass("NSColor").systemBlueColor())
            item.setView_(button)
            return item
        return None

    def customization_search_action(self, sender):
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
    """Main function to run the Touch Bar customization integration"""
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
        touch_bar = TouchBarCustomizationIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Touch Bar Customization Coding Assistant is running!")
        print("🎯 Look for '🔍 Code' button in Touch Bar customization")
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
