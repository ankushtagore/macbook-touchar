#!/usr/bin/env python3
"""
Simple Working Touch Bar Integration for MacBook Pro
Uses a minimal approach to avoid API issues
"""

import sys
import os
import signal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import macOS APIs
try:
    import objc
    from Foundation import NSObject, NSRunLoop, NSDefaultRunLoopMode
    from AppKit import (
        NSApplication,
        NSApp,
        NSAlert,
        NSWindow,
        NSView,
        NSButton,
        NSTextField,
        NSMakeRect,
        NSRect,
        NSWindowStyleMaskTitled,
        NSWindowStyleMaskClosable,
        NSBackingStoreBuffered,
        NSApplicationActivationPolicyRegular,
        NSTouchBar,
        NSTouchBarItem,
        NSTouchBarItemIdentifier,
    )

    TOUCHBAR_AVAILABLE = True
    print("✅ Simple Touch Bar APIs loaded successfully!")

except ImportError as e:
    print(f"macOS APIs not available: {e}")
    TOUCHBAR_AVAILABLE = False


class SimpleTouchBarIntegration(NSObject):
    """Simple Touch Bar integration that avoids API issues"""

    def init(self):
        self = objc.super(SimpleTouchBarIntegration, self).init()
        if self is None:
            return None

        self.is_active = False
        self.touch_bar = None
        self.window = None

        if not TOUCHBAR_AVAILABLE:
            raise RuntimeError("Touch Bar APIs not available on this system")

        return self

    def setup_touch_bar(self):
        """Setup the Touch Bar with a simple button"""
        try:
            print("🔧 Setting up Simple Touch Bar...")

            # Create a visible window to make the app active
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(100, 100, 400, 200),
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
                NSBackingStoreBuffered,
                False,
            )

            self.window.setTitle_("Touch Bar Coding Assistant - Simple")

            # Add a label to the window
            content_view = self.window.contentView()
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 50, 360, 100))
            label.setStringValue_(
                "Touch Bar Coding Assistant is running!\n\nThis is a simple version that should work reliably.\n\nLook for '🔍 Code' button on your Touch Bar.\n\nIf the button doesn't appear:\n1. Make sure this window is active\n2. Try Touch Bar customization"
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
                objc.selector(self.simple_test_action, signature=b"v@:@")
            )
            content_view.addSubview_(test_button)

            self.window.makeKeyAndOrderFront_(None)

            print("✅ Window created successfully!")

            # Create Touch Bar with minimal setup
            self.touch_bar = NSTouchBar.alloc().init()
            self.touch_bar.setDelegate_(self)
            self.touch_bar.setDefaultItemIdentifiers_(["simple-search-button"])
            self.touch_bar.setCustomizationIdentifier_("simple-coding-assistant")
            self.touch_bar.setCustomizationAllowedItemIdentifiers_(
                ["simple-search-button"]
            )

            print("✅ Touch Bar created successfully!")

            # Set the Touch Bar for the application
            NSApp.setTouchBar_(self.touch_bar)

            print("✅ Touch Bar set for application!")

            # Make the application active
            NSApp.activateIgnoringOtherApps_(True)

            self.is_active = True
            print(
                "🎯 Simple Touch Bar button added! Look for '🔍 Code' on your Touch Bar"
            )
            print("💡 The app window should be visible and active")

        except Exception as e:
            print(f"❌ Error setting up Touch Bar: {str(e)}")
            raise

    def touchBar_makeItemForIdentifier_(self, touchBar, identifier):
        """Create Touch Bar item with minimal API usage"""
        try:
            if identifier == "simple-search-button":
                # Create the Touch Bar item
                item = NSTouchBarItem.alloc().initWithIdentifier_(identifier)

                # Create the button with minimal setup
                button = NSButton.buttonWithTitle_target_action_(
                    "🔍 Code",
                    self,
                    objc.selector(self.simple_search_action, signature=b"v@:@"),
                )

                # Set the button as the item's view
                item.setView_(button)

                return item
            return None
        except Exception as e:
            print(f"❌ Error creating Touch Bar item: {str(e)}")
            return None

    def simple_search_action(self, sender):
        """Handle search button press with simple method"""
        try:
            print("🎯 Simple Touch Bar button pressed!")

            # Create a simple alert
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Touch Bar Coding Assistant")
            alert.setInformativeText_(
                "Simple Touch Bar button pressed! This will open the search window."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def simple_test_action(self, sender):
        """Handle test button press with simple method"""
        try:
            print("🎯 Simple test button pressed!")

            # Create a simple alert
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Touch Bar Test")
            alert.setInformativeText_(
                "Simple test button pressed! This confirms the app is working."
            )
            alert.addButtonWithTitle_("OK")
            alert.runModal()

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def cleanup(self):
        """Cleanup Touch Bar resources"""
        try:
            if self.is_active:
                print("🧹 Cleaning up Simple Touch Bar resources...")
                NSApp.setTouchBar_(None)
                if self.window:
                    self.window.close()
                self.is_active = False
                print("✅ Simple Touch Bar resources cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up: {str(e)}")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n👋 Received interrupt signal, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function to run the simple Touch Bar integration"""
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
        print("🚀 Starting Simple Touch Bar Coding Assistant...")

        # Initialize NSApplication
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        print("✅ NSApplication initialized!")

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
    finally:
        if touch_bar:
            touch_bar.cleanup()
        print("✅ Touch Bar Coding Assistant stopped")


if __name__ == "__main__":
    main()
