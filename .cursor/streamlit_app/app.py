"""
Main Streamlit app for Review & Communication.
Refactored version with modular components.
Enhanced with robust navigation debouncing mechanism.
"""
import streamlit as st
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path to find the 'components' module
sys.path.append(str(Path(__file__).resolve().parent))

from components.sidebar import display_sidebar
from utils import (
    load_tasks, read_user_messages, render_task_review_card, 
    render_message_review_card, render_add_request_tab
)
from utils.ui_components import (
    render_message_review_card,
)
from utils.simplified_task_view import render_simplified_task_view

# Import memory utilities for toast notifications
current_dir = Path(__file__).resolve().parent
utils_dir = current_dir / "pages" / "utils"
sys.path.insert(0, str(utils_dir))
import memory_data_manager
import memory_ui_components

st.set_page_config(page_title="Review & Communication", page_icon="📨")

display_sidebar()

# Optimized header with reduced spacing
st.markdown("# 📨 Review & Communication")
st.caption("Review tasks awaiting validation and view messages from the agent.")

def main():
    """Main function to render the review page"""
    # Initialize session state for active tab if not present
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "main"

    # Initialize session state for memory notifications
    if 'seen_present_memories' not in st.session_state:
        st.session_state.seen_present_memories = set()

    # Initialize debouncing for navigation interactions
    if 'last_navigation_interaction' not in st.session_state:
        st.session_state.last_navigation_interaction = None
    
    # Check if we're in a navigation debounce period (3 seconds after last interaction)
    current_time = datetime.now()
    navigation_debounce_active = (
        st.session_state.last_navigation_interaction is not None and 
        (current_time - st.session_state.last_navigation_interaction).total_seconds() < 3
    )

    # Apply enhanced toast styles for better notifications appearance (legacy support)
    memory_ui_components._apply_enhanced_toast_styles()
    
    # Apply new custom notification styles for the alternative system
    memory_ui_components._apply_custom_notification_styles()

    # Check for new agent memories and show enhanced custom notifications
    try:
        agent_memories = memory_data_manager.get_agent_memories(10)
        # Use the new enhanced notification system with markdown support and longer duration
        memory_ui_components._check_and_notify_new_present_memories_v2(agent_memories)
    except Exception as e:
        # Silently handle errors to avoid disrupting the main page
        pass

    # Load data upfront - Force reload every time to ensure fresh data
    # This ensures manual refresh shows updated information
    tasks = load_tasks()
    messages = read_user_messages()
    
    # Enhanced data freshness tracking with visual indicators
    current_timestamp = datetime.now()
    if 'last_data_load' not in st.session_state:
        st.session_state.last_data_load = current_timestamp
    else:
        st.session_state.last_data_load = current_timestamp
    
    # Calculate counts for badges (keep for tabs functionality)
    review_tasks_count = len([t for t in tasks if t.get('status') in ['REVIEW', 'BLOCKED']])
    messages_count = len(messages)
    
    # Remove excessive spacing - eliminated st.markdown("---") separator
    
    # Create dynamic tab labels
    review_tab_label = f"✅ To Review ({review_tasks_count} 🔴)" if review_tasks_count > 0 else "✅ Tasks to Review"
    messages_tab_label = f"📨 Messages ({messages_count} 🔴)" if messages_count > 0 else "📨 Agent Messages"
    
    # Define tabs with static keys and dynamic labels
    tabs = {
        "main": "📨 Communication",
        "review": review_tab_label,
        "messages": messages_tab_label,
    }
    tab_keys = list(tabs.keys())
    tab_labels = list(tabs.values())

    # Use radio buttons as tabs and control with session state
    try:
        default_index = tab_keys.index(st.session_state.active_tab)
    except (ValueError, KeyError):
        default_index = 0 # Default to first tab if key is invalid

    # Store the previous tab to detect changes
    previous_tab = st.session_state.active_tab

    selected_label = st.radio(
        "Navigation", 
        options=tab_labels, 
        index=default_index, 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Update session state with the key of the selected tab
    selected_key = tab_keys[tab_labels.index(selected_label)]
    
    # Detect navigation interaction and update debounce timestamp
    if selected_key != previous_tab:
        # Update debounce timestamp BEFORE any other operations
        st.session_state.last_navigation_interaction = current_time
        
        # Update the active tab immediately
        st.session_state.active_tab = selected_key
        
        # Add a brief delay to ensure state consistency
        time.sleep(0.1)
        
        # Force immediate rerun to ensure navigation takes effect
        st.rerun()
    else:
        # Ensure tab state is always synchronized even when no change detected
        st.session_state.active_tab = selected_key

    # Reduce spacing after radio buttons and between sections with enhanced CSS
    st.markdown("""
    <style>
    div[data-testid="stRadio"] {
        margin-bottom: -20px !important;
    }
    .main .block-container {
        padding-top: 2rem !important;
    }
    /* Reduce spacing for subheaders that follow radio buttons */
    h3[data-testid="stMarkdown"] {
        margin-top: -10px !important;
        padding-top: 0px !important;
    }
    /* Target the specific elements after radio buttons */
    div[data-testid="stRadio"] + div h3 {
        margin-top: -15px !important;
        padding-top: 5px !important;
    }
    /* Enhanced radio button responsiveness with anti-double-click optimization */
    div[data-testid="stRadio"] label {
        cursor: pointer !important;
        transition: all 0.1s ease !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        pointer-events: auto !important;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: rgba(0, 0, 0, 0.08) !important;
        transform: scale(1.03) !important;
    }
    div[data-testid="stRadio"] label:active {
        transform: scale(0.97) !important;
        background-color: rgba(0, 0, 0, 0.15) !important;
    }
    /* Prevent double-click text selection and optimize click handling */
    div[data-testid="stRadio"] label {
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    /* Optimize input radio for better responsiveness */
    div[data-testid="stRadio"] input[type="radio"] {
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render content based on the selected tab key
    if st.session_state.active_tab == "main":
        render_add_request_tab()
        render_simplified_task_view()
    elif st.session_state.active_tab == "review":
        st.header("Tasks Awaiting Validation")
        review_tasks = [t for t in tasks if t.get('status') in ['REVIEW', 'BLOCKED']]
        
        if not review_tasks:
            st.info("No tasks are currently awaiting review.")
        else:
            # Separate tasks by status for better organization
            review_status_tasks = [t for t in review_tasks if t.get('status') == 'REVIEW']
            blocked_status_tasks = [t for t in review_tasks if t.get('status') == 'BLOCKED']
            
            st.markdown(f"**{len(review_tasks)}** task(s) to review:")
            
            # Display REVIEW tasks first
            if review_status_tasks:
                st.markdown("### ✅ Tasks Ready for Review")
                for task in sorted(review_status_tasks, key=lambda x: x.get('id', 0), reverse=True):
                    render_task_review_card(task)
            
            # Display BLOCKED tasks with a clear distinction
            if blocked_status_tasks:
                st.markdown("### 🚫 Blocked Tasks Requiring Attention")
                for task in sorted(blocked_status_tasks, key=lambda x: x.get('id', 0), reverse=True):
                    render_task_review_card(task)
    elif st.session_state.active_tab == "messages":
        st.header("Messages from Agent")

        if not messages:
            st.info("No new messages from the agent.")
        else:
            st.markdown(f"**{len(messages)}** message(s) to review:")
            for message in sorted(messages, key=lambda x: x.get('id', 0), reverse=True):
                render_message_review_card(message)

if __name__ == "__main__":
    main() 