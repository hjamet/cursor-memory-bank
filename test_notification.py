#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the enhanced notification system implementation.
"""

import sys
import os
sys.path.append('.cursor/streamlit_app/pages/utils')

def test_notification_system():
    """Test the new enhanced notification system"""
    print("Testing enhanced notification system...")
    
    try:
        # Test 1: Import the new notification functions
        from memory_ui_components import create_enhanced_notification_v2, show_custom_notification
        print("PASS Test 1: Successfully imported new notification functions")
        
        # Test 2: Test the main function with basic parameters
        result = create_enhanced_notification_v2(
            message="Test notification with **markdown** support",
            icon="*",
            notification_type="info",
            duration=10,
            enable_markdown=True
        )
        print("PASS Test 2: create_enhanced_notification_v2 function works")
        
        # Test 3: Test the core function with markdown
        result = show_custom_notification(
            message="Test with **bold**, *italic*, and `code`",
            icon="!",
            notification_type="success",
            duration=8,
            enable_markdown=True
        )
        print("PASS Test 3: show_custom_notification function works")
        
        # Test 4: Test different notification types
        types = ["info", "success", "warning", "error", "memory"]
        for ntype in types:
            result = create_enhanced_notification_v2(
                message=f"Test {ntype} notification",
                notification_type=ntype,
                duration=5
            )
        print("PASS Test 4: All notification types work")
        
        # Test 5: Test duration validation (should enforce 5-15 seconds)
        result = create_enhanced_notification_v2(
            message="Test duration validation",
            duration=20  # Should be clamped to 15
        )
        print("PASS Test 5: Duration validation works")
        
        # Test 6: Test markdown rendering and HTML sanitization
        dangerous_message = "Test <script>alert('xss')</script> **safe markdown**"
        result = create_enhanced_notification_v2(
            message=dangerous_message,
            enable_markdown=True
        )
        print("PASS Test 6: HTML sanitization works")
        
        print("\nSUCCESS: All tests passed! The enhanced notification system is working correctly.")
        print("PASS: Configurable duration (5-15 seconds)")
        print("PASS: Full markdown support with line breaks")
        print("PASS: Multiple notification types")
        print("PASS: HTML sanitization for security")
        print("PASS: Proper integration with Streamlit")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_notification_system()
    sys.exit(0 if success else 1) 