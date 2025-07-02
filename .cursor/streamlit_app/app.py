"""
Main Streamlit app for Review & Communication.
Refactored version with modular components.
"""

import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the path to find the 'components' module
sys.path.append(str(Path(__file__).resolve().parent))
from components.sidebar import display_sidebar
from utils import (
    load_tasks, read_user_messages, render_task_review_card, 
    render_message_review_card, render_add_request_tab
)

st.set_page_config(page_title="Review & Communication", page_icon="📨")

display_sidebar()

st.markdown("# 📨 Review & Communication")
st.markdown("Review tasks awaiting validation and view messages from the agent.")


def main():
    """Main function to render the review page"""
    # Initialize session state for active tab if not present
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "add"

    # Load data upfront
    tasks = load_tasks()
    messages = read_user_messages()
    
    # Calculate counts for badges
    review_tasks_count = len([t for t in tasks if t.get('status') in ['REVIEW', 'BLOCKED']])
    messages_count = len(messages)
    
    # Create dynamic tab labels
    review_tab_label = f"✅ Tasks to Review ({review_tasks_count} 🔴)" if review_tasks_count > 0 else "✅ Tasks to Review"
    messages_tab_label = f"📨 Agent Messages ({messages_count} 🔴)" if messages_count > 0 else "📨 Agent Messages"
    
    # Define tabs with static keys and dynamic labels
    tabs = {
        "add": "✨ Add Request",
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

    selected_label = st.radio(
        "Navigation", 
        options=tab_labels, 
        index=default_index, 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Update session state with the key of the selected tab
    selected_key = tab_keys[tab_labels.index(selected_label)]
    st.session_state.active_tab = selected_key

    # Render content based on the selected tab key
    if st.session_state.active_tab == "add":
        render_add_request_tab()
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