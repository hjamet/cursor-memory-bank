"""
Test script for navigation debouncing mechanism
Verifies the double-click bug fix implementation
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time

# Add the current directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent))

st.set_page_config(page_title="Navigation Test", page_icon="🧪")

st.title("🧪 Navigation Debouncing Test")

def test_navigation_mechanism():
    """Test the navigation debouncing implementation"""
    
    # Initialize session state
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "tab1"
    
    if 'last_navigation_interaction' not in st.session_state:
        st.session_state.last_navigation_interaction = None
    
    # Current time for debouncing
    current_time = datetime.now()
    
    # Check debounce status
    navigation_debounce_active = (
        st.session_state.last_navigation_interaction is not None and 
        (current_time - st.session_state.last_navigation_interaction).total_seconds() < 3
    )
    
    # Display current status
    st.info(f"Current tab: {st.session_state.active_tab}")
    if navigation_debounce_active:
        time_since = (current_time - st.session_state.last_navigation_interaction).total_seconds()
        st.warning(f"🔄 Debouncing active - {time_since:.1f}s since last interaction")
    else:
        st.success("✅ Navigation ready - no debouncing active")
    
    # Test tabs
    tabs = {
        "tab1": "📋 Tab 1", 
        "tab2": "🔍 Tab 2", 
        "tab3": "📊 Tab 3"
    }
    
    tab_keys = list(tabs.keys())
    tab_labels = list(tabs.values())
    
    # Store previous tab
    previous_tab = st.session_state.active_tab
    
    # Radio buttons navigation
    try:
        default_index = tab_keys.index(st.session_state.active_tab)
    except (ValueError, KeyError):
        default_index = 0
    
    selected_label = st.radio(
        "Test Navigation", 
        options=tab_labels, 
        index=default_index, 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Get selected key
    selected_key = tab_keys[tab_labels.index(selected_label)]
    
    # Navigation detection and debouncing
    if selected_key != previous_tab:
        st.session_state.last_navigation_interaction = current_time
        st.session_state.active_tab = selected_key
        
        st.success(f"✨ Navigation detected: {previous_tab} → {selected_key}")
        
        # Brief delay and rerun
        time.sleep(0.1)
        st.rerun()
    else:
        st.session_state.active_tab = selected_key
    
    # Display content based on selected tab
    st.markdown("---")
    
    if st.session_state.active_tab == "tab1":
        st.header("📋 Tab 1 Content")
        st.write("This is the content for Tab 1. Navigation should work with a single click!")
    elif st.session_state.active_tab == "tab2":
        st.header("🔍 Tab 2 Content") 
        st.write("This is the content for Tab 2. Testing single-click navigation...")
    elif st.session_state.active_tab == "tab3":
        st.header("📊 Tab 3 Content")
        st.write("This is the content for Tab 3. Debouncing should prevent conflicts!")
    
    # Test button for manual interaction timing
    if st.button("🔄 Force Refresh (Test Debouncing)"):
        st.session_state.last_navigation_interaction = current_time
        st.rerun()
    
    # Display debug info
    with st.expander("🔧 Debug Information"):
        st.write("Session State:")
        st.json({
            "active_tab": st.session_state.active_tab,
            "last_navigation_interaction": str(st.session_state.last_navigation_interaction) if st.session_state.last_navigation_interaction else None,
            "debounce_active": navigation_debounce_active,
            "current_time": str(current_time)
        })

if __name__ == "__main__":
    test_navigation_mechanism() 