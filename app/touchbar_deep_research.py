#!/usr/bin/env python3
"""
Deep Touch Bar Research Script
Research what Touch Bar APIs are actually available and working
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔍 Deep Touch Bar Research Starting...")
print("=" * 50)

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
    )

    print("✅ Basic macOS APIs loaded successfully!")

    # Check for Touch Bar APIs
    print("\n🔍 Checking Touch Bar APIs...")

    try:
        from AppKit import NSTouchBar, NSTouchBarItem, NSTouchBarItemIdentifier

        print("✅ NSTouchBar APIs available!")

        # Test creating a Touch Bar
        print("\n🔍 Testing Touch Bar creation...")
        try:
            touch_bar = NSTouchBar.alloc().init()
            print("✅ Touch Bar creation successful!")

            # Test setting properties
            touch_bar.setDefaultItemIdentifiers_(["test-button"])
            print("✅ Touch Bar properties set successfully!")

        except Exception as e:
            print(f"❌ Touch Bar creation failed: {e}")

    except ImportError as e:
        print(f"❌ NSTouchBar APIs not available: {e}")

    # Check for Touch Bar framework
    print("\n🔍 Checking Touch Bar framework...")
    try:
        objc.loadBundle(
            "DFRFoundation",
            globals(),
            "/System/Library/PrivateFrameworks/DFRFoundation.framework",
        )
        print("✅ DFRFoundation framework loaded!")

        # List available classes
        print("\n🔍 Available Touch Bar Classes:")
        touch_bar_classes = [
            "DFRDisplayServer",
            "DFRTouchBarItem",
            "DFRTouchBar",
            "DFRDisplay",
            "DFRFoundation",
            "DFRDisplayServerClient",
            "DFRTouchBarItemView",
            "DFRTouchBarItemViewController",
        ]

        for class_name in touch_bar_classes:
            try:
                cls = objc.lookUpClass(class_name)
                print(f"✅ {class_name}: Available")
            except Exception as e:
                print(f"❌ {class_name}: Not available - {e}")

    except Exception as e:
        print(f"❌ DFRFoundation framework not available: {e}")

    # Check system Touch Bar info
    print("\n🔍 System Touch Bar Info:")
    try:
        import subprocess

        result = subprocess.run(
            ["system_profiler", "SPTouchBarDataType"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Touch Bar detected in system")
            print("Touch Bar Info:")
            print(result.stdout[:1000] + "...")
        else:
            print("❌ Touch Bar not detected in system")
    except Exception as e:
        print(f"❌ Error checking system Touch Bar: {e}")

    # Check macOS version
    print("\n🔍 macOS Version Info:")
    try:
        import subprocess

        result = subprocess.run(["sw_vers"], capture_output=True, text=True)
        if result.returncode == 0:
            print("macOS Version Info:")
            print(result.stdout)
        else:
            print("❌ Could not get macOS version")
    except Exception as e:
        print(f"❌ Error getting macOS version: {e}")

    # Check if Touch Bar is enabled
    print("\n🔍 Touch Bar Status:")
    try:
        import subprocess

        result = subprocess.run(
            ["defaults", "read", "com.apple.touchbar.agent", "PresentationModeGlobal"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            mode = result.stdout.strip()
            print(f"Touch Bar Presentation Mode: {mode}")
        else:
            print("❌ Could not get Touch Bar presentation mode")
    except Exception as e:
        print(f"❌ Error checking Touch Bar status: {e}")

    # Test simple NSApplication
    print("\n🔍 Testing NSApplication...")
    try:
        app = NSApplication.sharedApplication()
        print("✅ NSApplication creation successful!")

        # Test different activation policies
        print("\n🔍 Testing activation policies...")
        try:
            app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
            print("✅ Regular activation policy set!")
        except Exception as e:
            print(f"❌ Regular activation policy failed: {e}")

        try:
            app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            print("✅ Accessory activation policy set!")
        except Exception as e:
            print(f"❌ Accessory activation policy failed: {e}")

    except Exception as e:
        print(f"❌ NSApplication creation failed: {e}")

    # Test simple window creation
    print("\n🔍 Testing window creation...")
    try:
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(100, 100, 300, 200),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False,
        )
        print("✅ Window creation successful!")

        # Test window operations
        window.setTitle_("Test Window")
        print("✅ Window title set!")

        window.makeKeyAndOrderFront_(None)
        print("✅ Window made key and front!")

        # Close the window
        window.close()
        print("✅ Window closed!")

    except Exception as e:
        print(f"❌ Window creation failed: {e}")

    # Test simple button creation
    print("\n🔍 Testing button creation...")
    try:
        button = NSButton.buttonWithTitle_target_action_("Test Button", None, None)
        print("✅ Button creation successful!")

        # Test button properties
        button.setBezelColor_(objc.lookUpClass("NSColor").systemBlueColor())
        print("✅ Button properties set!")

    except Exception as e:
        print(f"❌ Button creation failed: {e}")

    print("\n🔍 Deep Touch Bar Research Complete!")
    print("=" * 50)

except ImportError as e:
    print(f"❌ macOS APIs not available: {e}")

print("\n🎯 Research Summary:")
print("This research will help us understand what Touch Bar APIs are available")
print("and how to properly integrate with the Touch Bar.")
