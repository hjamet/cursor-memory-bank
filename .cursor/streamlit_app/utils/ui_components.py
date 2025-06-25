"""
UI components for the Streamlit app.
Handles rendering of tasks, messages and other UI elements.
"""

import streamlit as st
from datetime import datetime
from typing import Dict
from .task_manager import has_associated_image, get_image_path, delete_task_image, update_task_status
from .message_manager import format_timestamp, get_rule_emoji, delete_message


def render_image_preview(task: Dict):
    """Render image preview for a task if it has an associated image"""
    if has_associated_image(task):
        image_path = get_image_path(task)
        if image_path:
            try:
                st.image(image_path, caption=f"Image for Task #{task['id']}", width=300)
            except Exception as e:
                st.error(f"Error displaying image: {e}")
        else:
            st.warning("⚠️ Image file not found or corrupted")


def render_task_review_card(task: Dict):
    """Render a task review card with all necessary information and actions"""
    with st.container(border=True):
        # Header with task ID and status
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**Task #{task['id']}** - {task.get('title', 'No title')}")
        with col2:
            status = task.get('status', 'UNKNOWN')
            if status == 'REVIEW':
                st.markdown("🔍 **REVIEW**")
            elif status == 'BLOCKED':
                st.markdown("🚫 **BLOCKED**")
            else:
                st.markdown(f"**{status}**")
        with col3:
            priority = task.get('priority', 3)
            priority_emoji = "🔴" if priority >= 4 else "🟡" if priority == 3 else "🟢"
            st.markdown(f"{priority_emoji} Priority {priority}")

        # Task description
        short_desc = task.get('short_description', 'No description available')
        st.markdown(f"**Description:** {short_desc}")
        
        # Show detailed description in expandable section
        detailed_desc = task.get('detailed_description', '')
        if detailed_desc and detailed_desc != short_desc:
            with st.expander("📄 Detailed Description"):
                st.markdown(detailed_desc)

        # Show validation criteria if available
        validation_criteria = task.get('validation_criteria', '')
        if validation_criteria:
            with st.expander("✅ Validation Criteria"):
                st.markdown(validation_criteria)

        # Show impacted files if available
        impacted_files = task.get('impacted_files', [])
        if impacted_files:
            with st.expander("📁 Impacted Files"):
                for file in impacted_files:
                    st.code(file)

        # Show dependencies if any
        dependencies = task.get('dependencies', [])
        if dependencies:
            with st.expander("🔗 Dependencies"):
                for dep in dependencies:
                    st.markdown(f"- Task #{dep}")

        # Show image preview if available
        render_image_preview(task)

        # Action buttons - Simple interface with Approve/Edit only
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Approve", key=f"approve_{task['id']}", type="primary"):
                validation_data = {
                    "approved_at": datetime.now().isoformat(),
                    "approved_by": "user_review"
                }
                if update_task_status(task['id'], "APPROVED", validation_data):
                    st.toast(f"Task #{task['id']} approved!")
                    st.rerun()
                else:
                    st.error("Failed to approve task.")

        with col2:
            if st.button("✏️ Edit/Needs Work", key=f"needs_work_{task['id']}"):
                if update_task_status(task['id'], "TODO"):
                    st.toast(f"Task #{task['id']} sent back for editing.")
                    st.rerun()
                else:
                    st.error("Failed to update task status.")

        with col3:
            if has_associated_image(task):
                if st.button("🗑️ Delete Image", key=f"delete_img_{task['id']}"):
                    if delete_task_image(task):
                        st.toast("Image deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete image.")


def render_message_review_card(message: Dict):
    """Render a message review card with message content and actions"""
    with st.container(border=True):
        # Header with message ID and rule info
        col1, col2 = st.columns([3, 1])
        with col1:
            rule = message.get('rule', 'unknown')
            rule_emoji = get_rule_emoji(rule)
            st.markdown(f"**Message #{message['id']}** {rule_emoji} `{rule}`")
        with col2:
            timestamp = message.get('timestamp', '')
            if timestamp:
                formatted_time = format_timestamp(timestamp)
                st.markdown(f"🕒 {formatted_time}")

        # Message content
        content = message.get('content', 'No content available')
        st.markdown(content)

        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("✅ Mark as Read", key=f"read_msg_{message['id']}", type="primary"):
                if delete_message(message['id']):
                    st.toast(f"Message #{message['id']} marked as read!")
                    st.rerun()
                else:
                    st.error("Failed to mark message as read.")

        with col2:
            st.markdown("") # Empty space for layout 