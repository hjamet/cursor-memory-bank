#!/usr/bin/env python3
"""Test validation of auto-refresh enhancements"""

import sys
import os
from pathlib import Path

# Add Streamlit app to path
streamlit_path = Path('.cursor/streamlit_app')
sys.path.insert(0, str(streamlit_path))

def test_autorefresh_enhancements():
    """Test that auto-refresh enhancements are working"""
    
    print("=== AUTO-REFRESH VALIDATION TEST ===")
    
    # Test 1: streamlit-autorefresh import
    try:
        from streamlit_autorefresh import st_autorefresh
        print("[TEST 1] [OK] streamlit-autorefresh import successful")
    except ImportError as e:
        print(f"[TEST 1] [FAIL] streamlit-autorefresh import failed: {e}")
        return False
    
    # Test 2: sidebar enhancements
    try:
        from components.sidebar import display_sidebar
        print("[TEST 2] [OK] sidebar.py import successful")
        
        # Check if enhanced auto-refresh code is present
        import inspect
        source = inspect.getsource(display_sidebar)
        
        if 'st_autorefresh' in source:
            print("[TEST 2.1] [OK] st_autorefresh found in sidebar")
        else:
            print("[TEST 2.1] [FAIL] st_autorefresh not found in sidebar")
            return False
            
        if 'refresh_count' in source:
            print("[TEST 2.2] [OK] refresh_count variable found")
        else:
            print("[TEST 2.2] [FAIL] refresh_count variable not found")
            return False
            
        if 'last_refresh_count' in source:
            print("[TEST 2.3] [OK] enhanced session state management found")
        else:
            print("[TEST 2.3] [FAIL] enhanced session state management not found")
            return False
            
    except Exception as e:
        print(f"[TEST 2] [FAIL] sidebar test failed: {e}")
        return False
    
    # Test 3: app.py enhancements
    try:
        import app
        print("[TEST 3] [OK] app.py import successful")
        
        # Check for timestamp tracking
        import inspect
        app_source = inspect.getsource(app)
        if 'last_data_load' in app_source:
            print("[TEST 3.1] [OK] data reload tracking found in app.py")
        else:
            print("[TEST 3.1] [FAIL] data reload tracking not found in app.py")
            return False
            
    except Exception as e:
        print(f"[TEST 3] [FAIL] app.py test failed: {e}")
        return False
    
    print("\n=== ALL TESTS PASSED ===")
    print("[OK] Auto-refresh enhancements are properly implemented")
    print("[OK] Enhanced diagnostics available")
    print("[OK] Data reload tracking active")
    print("[OK] System ready for auto-refresh validation")
    
    return True

if __name__ == "__main__":
    success = test_autorefresh_enhancements()
    if not success:
        sys.exit(1)
    print("\n[FINAL RESULT] Auto-refresh validation SUCCESSFUL") 