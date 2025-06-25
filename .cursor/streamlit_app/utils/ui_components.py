"""
UI components for the Streamlit app.
Handles rendering of tasks, messages and other UI elements.
"""

import streamlit as st
from datetime import datetime
from typing import Dict
from .task_manager import has_associated_image, get_image_path, delete_task_image, update_task_status
from .message_manager import format_timestamp, get_rule_emoji, delete_message
from .request_manager import create_new_request


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
    task_id = task.get('id', task.get('task_id'))
    title = task.get('title', 'No title')
    
    with st.container(border=True):
        # Header with task ID and status
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**Task #{task_id}** - {title}")
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

        # Action buttons - Approve and Ask for modification
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Approve", key=f"approve_{task_id}", type="primary"):
                validation_data = {
                    "approved_at": datetime.now().isoformat(),
                    "approved_by": "user_review"
                }
                if update_task_status(task_id, "APPROVED", validation_data):
                    st.toast(f"Task #{task_id} approved!")
                    st.rerun()
                else:
                    st.error("Failed to approve task.")

        with col2:
            if st.button("📝 Ask for modification", key=f"ask_modification_{task_id}"):
                st.session_state['active_modification_form'] = task_id
                st.rerun()

        with col3:
            if has_associated_image(task):
                if st.button("🗑️ Delete Image", key=f"delete_img_{task_id}"):
                    if delete_task_image(task):
                        st.toast("Image deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete image.")

        # Modification form (shown when "Ask for modification" button is clicked)
        if st.session_state.get('active_modification_form') == task_id:
            st.markdown("---")
            with st.form(f"modification_form_{task_id}"):
                st.warning(f"Please provide feedback for Task #{task_id}:")
                modification_reason = st.text_area(
                    "What needs to be modified or improved?", 
                    key=f"modification_reason_{task_id}", 
                    height=100,
                    placeholder="Explain what needs to be changed, what's missing, or what's not working as expected..."
                )
                
                col_submit, col_cancel = st.columns([1, 1])
                with col_submit:
                    submitted = st.form_submit_button("📤 Submit Modification Request", type="primary")
                with col_cancel:
                    cancelled = st.form_submit_button("❌ Cancel")
                
                if submitted:
                    if modification_reason.strip():
                        # Create the modification request content with full context
                        modification_content = f"""Modification request for Task #{task_id} ({title}):

**Original Task Details:**
- **Title:** {title}
- **Description:** {short_desc}
- **Status:** {status}
- **Priority:** {priority}

**Detailed Task Description:**
{detailed_desc if detailed_desc else 'No detailed description available'}

**Validation Criteria:**
{validation_criteria if validation_criteria else 'No validation criteria specified'}

**User Feedback:**
{modification_reason.strip()}

**Action Required:**
Please review the user's feedback above and make the necessary modifications to address their concerns. The task has been reset to TODO status pending your improvements."""
                        
                        # Create new userbrief request and update task status
                        if create_new_request(modification_content) and update_task_status(task_id, 'TODO'):
                            st.success(f"Task #{task_id} modification request sent! The task has been reset to TODO status.")
                            del st.session_state['active_modification_form']
                            st.rerun()
                        else:
                            st.error("Failed to process modification request.")
                    else:
                        st.error("Please provide feedback explaining what needs to be modified.")
                
                if cancelled:
                    # Clean up session state
                    del st.session_state['active_modification_form']
                    st.rerun()


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
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Mark as Read", key=f"read_msg_{message['id']}", type="primary"):
                if delete_message(message['id']):
                    st.toast(f"Message #{message['id']} marked as read!")
                    st.rerun()
                else:
                    st.error("Failed to mark message as read.")

        with col2:
            if st.button("💬 Reply", key=f"reply_msg_{message['id']}"):
                st.session_state[f'replying_to_{message["id"]}'] = True

        # Reply form (shown when Reply button is clicked)
        if st.session_state.get(f'replying_to_{message["id"]}', False):
            st.markdown("---")
            with st.form(key=f"reply_form_{message['id']}"):
                st.markdown("**Reply to this message:**")
                
                # Show original message context
                with st.expander("📨 Original Message Context", expanded=False):
                    st.markdown(f"**Message ID:** #{message['id']}")
                    st.markdown(f"**Rule:** {message.get('rule', 'unknown')}")
                    st.markdown(f"**Content:** {content}")
                    
                    # Show task context if available
                    task_context = message.get('context', {})
                    if task_context.get('active_task'):
                        st.markdown(f"**Related Task:** #{task_context['active_task']}")
                    if task_context.get('workflow_rule'):
                        st.markdown(f"**Workflow Rule:** {task_context['workflow_rule']}")
                
                # User input for reply
                user_reply = st.text_area(
                    "Your reply or question:",
                    key=f"reply_text_{message['id']}",
                    height=100,
                    placeholder="Ask a question, provide feedback, or give additional instructions..."
                )
                
                # Form submission buttons
                col_submit, col_cancel = st.columns([1, 1])
                with col_submit:
                    submitted = st.form_submit_button("📤 Send Reply", type="primary")
                with col_cancel:
                    cancelled = st.form_submit_button("❌ Cancel")
                
                if submitted and user_reply.strip():
                    # Create the reply content with context
                    reply_content = f"""Reply to Agent Message #{message['id']}:

**Original Message:** "{content[:200]}{'...' if len(content) > 200 else ''}"

**My Reply:** {user_reply.strip()}

**Message Context:**
- Rule: {message.get('rule', 'unknown')}
- Timestamp: {timestamp}"""
                    
                    # Add task context if available
                    task_context = message.get('context', {})
                    if task_context.get('active_task'):
                        reply_content += f"\n- Related Task: #{task_context['active_task']}"
                    if task_context.get('workflow_rule'):
                        reply_content += f"\n- Workflow Rule: {task_context['workflow_rule']}"
                    
                    # Create new request
                    if create_new_request(reply_content):
                        st.success("Your reply has been sent as a new request!")
                        # Clean up session state
                        del st.session_state[f'replying_to_{message["id"]}']
                        # Mark original message as read since user replied to it
                        delete_message(message['id'])
                        st.rerun()
                    else:
                        st.error("Failed to send reply. Please try again.")
                
                elif submitted and not user_reply.strip():
                    st.warning("Please enter a reply before submitting.")
                
                if cancelled:
                    # Clean up session state
                    del st.session_state[f'replying_to_{message["id"]}']
                    st.rerun() 