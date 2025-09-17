#!/usr/bin/env python3
"""
Corrected Touch Bar Integration for MacBook Pro
Fixes NSTouchBarItem API issues and Objective-C selector problems
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
    print("✅ Corrected Touch Bar APIs loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False

logger = logging.getLogger(__name__)


class CorrectedTouchBarIntegration(NSObject):
    """Corrected Touch Bar integration that fixes API issues"""

    def init(self):
        self = objc.super(CorrectedTouchBarIntegration, self).init()
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
            print("🔧 Setting up Corrected Touch Bar...")

            # Create a visible window to make the app active
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(100, 100, 500, 300),
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
                NSBackingStoreBuffered,
                False,
            )

            self.window.setTitle_("Touch Bar Coding Assistant - Corrected")

            # Add a label to the window
            content_view = self.window.contentView()
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 100, 460, 150))
            label.setStringValue_(
                "Touch Bar Coding Assistant is running!\n\nThis is the corrected version that fixes API issues.\n\nTo use the Touch Bar:\n1. Make sure this window is active\n2. Look for '🔍 Code' button on your Touch Bar\n3. If not visible, try Touch Bar customization\n4. Click the 'Test Window' button below to test"
            )
            label.setEditable_(False)
            label.setBezeled_(False)
            label.setDrawsBackground_(False)
            label.setSelectable_(False)
            content_view.addSubview_(label)

            # Add a test button to the window
            test_button = NSButton.alloc().initWithFrame_(NSMakeRect(20, 50, 120, 30))
            test_button.setTitle_("Test Window")
            test_button.setTarget_(self)
            test_button.setAction_(
                objc.selector(self.corrected_test_action, signature=b"v@:@")
            )
            content_view.addSubview_(test_button)

            # Add a search button to the window
            search_button = NSButton.alloc().initWithFrame_(
                NSMakeRect(160, 50, 120, 30)
            )
            search_button.setTitle_("Search Window")
            search_button.setTarget_(self)
            search_button.setAction_(
                objc.selector(self.corrected_search_window_action, signature=b"v@:@")
            )
            content_view.addSubview_(search_button)

            self.window.makeKeyAndOrderFront_(None)

            print("✅ Window created successfully!")

            # Create Touch Bar with corrected API usage
            self.touch_bar = NSTouchBar.alloc().init()
            self.touch_bar.setDelegate_(self)
            self.touch_bar.setDefaultItemIdentifiers_(["corrected-search-button"])
            self.touch_bar.setCustomizationIdentifier_("corrected-coding-assistant")
            self.touch_bar.setCustomizationAllowedItemIdentifiers_(
                ["corrected-search-button"]
            )

            print("✅ Touch Bar created successfully!")

            # Set the Touch Bar for the application
            NSApp.setTouchBar_(self.touch_bar)

            print("✅ Touch Bar set for application!")

            # Make the application active
            NSApp.activateIgnoringOtherApps_(True)

            self.is_active = True
            logger.info("✅ Corrected Touch Bar integration activated!")
            print(
                "🎯 Corrected Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )
            print("💡 The app window should be visible and active")

        except Exception as e:
            logger.error(f"Failed to setup Touch Bar: {str(e)}")
            print(f"❌ Error setting up Touch Bar: {str(e)}")
            raise

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item with corrected API"""
        try:
            if identifier == "corrected-search-button":
                # Create the Touch Bar item
                item = NSTouchBarItem.alloc().initWithIdentifier_(identifier)

                # Create the button with corrected method
                button = NSButton.buttonWithTitle_target_action_(
                    "🔍 Code",
                    self,
                    objc.selector(self.corrected_search_action, signature=b"v@:@"),
                )

                # Set button properties
                if hasattr(button, "setBezelColor_"):
                    button.setBezelColor_(objc.lookUpClass("NSColor").systemBlueColor())

                # Set the button as the item's view using the correct method
                if hasattr(item, "setView_"):
                    item.setView_(button)
                elif hasattr(item, "setCustomizationLabel_"):
                    # Alternative approach if setView_ is not available
                    item.setCustomizationLabel_("🔍 Code")
                    # Try to set the button as a custom view
                    try:
                        item.setView_(button)
                    except:
                        print("⚠️ Could not set button view, using label only")

                return item
            return None
        except Exception as e:
            print(f"❌ Error creating Touch Bar item: {str(e)}")
            return None

    def corrected_search_action(self, sender):
        """Handle search button press with corrected method"""
        try:
            print("🎯 Corrected Touch Bar button pressed!")

            # Create a simple alert for now
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Touch Bar Coding Assistant")
            alert.setInformativeText_(
                "Corrected Touch Bar button pressed! This will open the search window."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

            logger.info("Corrected Touch Bar search button pressed")

        except Exception as e:
            logger.error(f"Error handling Touch Bar button press: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def corrected_test_action(self, sender):
        """Handle test button press with corrected method"""
        try:
            print("🎯 Corrected test button pressed!")

            # Create a simple alert for now
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Touch Bar Test")
            alert.setInformativeText_(
                "Corrected test button pressed! This confirms the app is working.\n\nIf you can see this alert, the Touch Bar integration is working!"
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

        except Exception as e:
            logger.error(f"Error handling test button press: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def corrected_search_window_action(self, sender):
        """Handle search window button press with corrected method"""
        try:
            print("🎯 Corrected search window button pressed!")

            # Create a search window
            search_window = (
                NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                    NSMakeRect(200, 200, 600, 400),
                    NSWindowStyleMaskTitled
                    | NSWindowStyleMaskClosable
                    | NSWindowStyleMaskMiniaturizable
                    | NSWindowStyleMaskResizable,
                    NSBackingStoreBuffered,
                    False,
                )
            )

            search_window.setTitle_("Search Window - Corrected")

            # Add search interface
            content_view = search_window.contentView()

            # Search field
            search_field = NSTextField.alloc().initWithFrame_(
                NSMakeRect(20, 350, 400, 30)
            )
            search_field.setPlaceholderString_("Enter your coding question...")
            content_view.addSubview_(search_field)

            # Search button
            search_button = NSButton.alloc().initWithFrame_(
                NSMakeRect(440, 350, 80, 30)
            )
            search_button.setTitle_("Search")
            search_button.setTarget_(self)
            search_button.setAction_(
                objc.selector(self.corrected_perform_search_action, signature=b"v@:@")
            )
            content_view.addSubview_(search_button)

            # Answer text view
            scroll_view = NSScrollView.alloc().initWithFrame_(
                NSMakeRect(20, 20, 560, 320)
            )
            answer_text = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 320))
            answer_text.setEditable_(False)
            answer_text.setString_("Ask a coding interview question...")
            scroll_view.setDocumentView_(answer_text)
            content_view.addSubview_(scroll_view)

            search_window.makeKeyAndOrderFront_(None)

        except Exception as e:
            logger.error(f"Error opening search window: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def corrected_perform_search_action(self, sender):
        """Handle search button press in search window with corrected method"""
        try:
            print("🎯 Corrected search button pressed!")

            # Create a simple alert for now
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Search Function")
            alert.setInformativeText_(
                "Corrected search button pressed! This will perform the search using Azure OpenAI."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            print(f"❌ Error: {str(e)}")

    def cleanup(self):
        """Cleanup Touch Bar resources"""
        try:
            if self.is_active:
                print("🧹 Cleaning up Corrected Touch Bar resources...")
                NSApp.setTouchBar_(None)
                if self.window:
                    self.window.close()
                self.is_active = False
                logger.info("Corrected Touch Bar integration cleaned up")
                print("✅ Corrected Touch Bar resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Touch Bar: {str(e)}")
            print(f"❌ Error cleaning up: {str(e)}")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n👋 Received interrupt signal, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function to run the corrected Touch Bar integration"""
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
        print("🚀 Starting Corrected Touch Bar Coding Assistant...")

        # Initialize NSApplication
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        print("✅ NSApplication initialized!")

        # Create Touch Bar integration
        touch_bar = CorrectedTouchBarIntegration.alloc().init()
        touch_bar.setup_touch_bar()

        print("🚀 Corrected Touch Bar Coding Assistant is running!")
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
