#!/usr/bin/env python3
"""
Test script for auto-refresh inactivity fix validation
Tests that auto-refresh continues working after extended periods of inactivity
"""

import streamlit as st
from datetime import datetime, timedelta
import time

def test_inactivity_scenario():
    """
    Test auto-refresh behavior during extended inactivity periods
    """
    st.title("🧪 Auto-Refresh Inactivity Test")
    
    # Initialize session state
    if 'test_start_time' not in st.session_state:
        st.session_state.test_start_time = datetime.now()
    
    if 'last_navigation_interaction' not in st.session_state:
        st.session_state.last_navigation_interaction = None
        
    if 'simulated_inactivity' not in st.session_state:
        st.session_state.simulated_inactivity = False

    current_time = datetime.now()
    test_duration = (current_time - st.session_state.test_start_time).total_seconds()
    
    st.markdown("### Test Status")
    st.metric("Test Duration", f"{test_duration:.1f} seconds")
    st.metric("Current Time", current_time.strftime("%H:%M:%S"))
    
    # Simulate different scenarios
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Simulate Navigation"):
            st.session_state.last_navigation_interaction = datetime.now()
            st.success("Navigation interaction simulated!")
            
    with col2:
        if st.button("⏰ Simulate Old Interaction (15 min ago)"):
            st.session_state.last_navigation_interaction = datetime.now() - timedelta(minutes=15)
            st.success("Old interaction simulated!")
            
    with col3:
        if st.button("🔄 Reset Test"):
            st.session_state.last_navigation_interaction = None
            st.session_state.test_start_time = datetime.now()
            st.success("Test reset!")
    
    # Test the actual logic from sidebar.py
    st.markdown("### Auto-Refresh Logic Test")
    
    navigation_debounce_active = False
    
    if (hasattr(st.session_state, 'last_navigation_interaction') and 
        st.session_state.last_navigation_interaction is not None):
        try:
            time_since_interaction = (current_time - st.session_state.last_navigation_interaction).total_seconds()
            navigation_debounce_active = time_since_interaction < 3
            
            # Test the 10-minute auto-reset safeguard
            if time_since_interaction > 600:  # 10 minutes
                st.warning(f"🔧 SAFEGUARD TRIGGERED: Interaction too old ({time_since_interaction:.1f}s), would be reset")
                safeguard_triggered = True
            else:
                safeguard_triggered = False
                
            st.info(f"⏱️ Time since last interaction: {time_since_interaction:.1f} seconds")
            
        except (TypeError, AttributeError):
            st.error("🚨 FALLBACK TRIGGERED: Timestamp corrupted, would be reset")
            navigation_debounce_active = False
            safeguard_triggered = True
    else:
        st.success("✅ No recent navigation interaction")
        safeguard_triggered = False
    
    # Show auto-refresh status
    if navigation_debounce_active:
        time_remaining = max(0, 3 - time_since_interaction)
        st.warning(f"🔄 Auto-refresh PAUSED (resumes in {time_remaining:.1f}s)")
    else:
        st.success("✅ Auto-refresh ACTIVE")
    
    # Show safeguard status
    if safeguard_triggered:
        st.info("🛡️ Inactivity safeguard would activate - auto-refresh guaranteed")
    
    st.markdown("### Expected Behavior")
    st.markdown("""
    **✅ PASS CONDITIONS:**
    - Auto-refresh is ACTIVE when no recent navigation (>3s ago)
    - Auto-refresh is ACTIVE when interaction is very old (>10min ago)
    - Auto-refresh PAUSES only during 3-second navigation debounce window
    - Safeguards trigger for corrupted timestamps or very old interactions
    
    **❌ FAIL CONDITIONS:**
    - Auto-refresh stuck PAUSED indefinitely
    - No safeguard activation for old interactions
    - Permanent failures due to corrupted timestamps
    """)

if __name__ == "__main__":
    test_inactivity_scenario() 