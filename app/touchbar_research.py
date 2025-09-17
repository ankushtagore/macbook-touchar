#!/usr/bin/env python3
"""
Touch Bar Research Script
Explore available Touch Bar APIs and find the correct integration method
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    print("✅ macOS APIs loaded successfully!")

    # Try to load Touch Bar framework
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

        # Try alternative approaches
        print("\n🔍 Alternative Touch Bar APIs:")

        # Check for NSTouchBar
        try:
            from AppKit import NSTouchBar, NSTouchBarItem, NSTouchBarItemIdentifier

            print("✅ NSTouchBar: Available")
        except ImportError:
            print("❌ NSTouchBar: Not available")

        # Check for Touch Bar in System Preferences
        print("\n🔍 System Touch Bar Info:")
        try:
            import subprocess

            result = subprocess.run(
                ["system_profiler", "SPTouchBarDataType"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ Touch Bar detected in system")
                print(result.stdout[:500] + "...")
            else:
                print("❌ Touch Bar not detected in system")
        except Exception as e:
            print(f"❌ Error checking system Touch Bar: {e}")

    except Exception as e:
        print(f"❌ Error loading DFRFoundation: {e}")

except ImportError as e:
    print(f"❌ macOS APIs not available: {e}")

print("\n🔍 Research Complete!")
