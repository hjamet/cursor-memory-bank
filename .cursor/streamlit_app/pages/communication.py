import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Communication", page_icon="💬")

st.markdown("# 💬 Agent Communication")
st.sidebar.header("Communication")

st.markdown("View messages sent by the agent via the remember tool's user_message parameter.")

# Helper functions for message management
def read_user_messages():
    """Read messages from to_user.json file"""
    try:
        messages_file = Path(".cursor/memory-bank/workflow/to_user.json")
        if messages_file.exists():
            with open(messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('messages', [])
        return []
    except Exception as e:
        st.error(f"Error reading messages: {e}")
        return []

def delete_message(message_id):
    """Delete a message from the to_user.json file"""
    try:
        messages_file = Path(".cursor/memory-bank/workflow/to_user.json")
        if messages_file.exists():
            with open(messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Remove the message with the specified ID
            original_count = len(data.get('messages', []))
            data['messages'] = [msg for msg in data.get('messages', []) if msg.get('id') != message_id]
            
            # Check if message was actually removed
            if len(data['messages']) < original_count:
                # Write back to file
                with open(messages_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            else:
                return False
    except Exception as e:
        st.error(f"Error deleting message: {e}")
        return False

def get_message_icon():
    """Get icon for messages (simplified since no status tracking)"""
    return '💬'  # Message icon for all messages

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def get_rule_emoji(rule):
    """Get emoji for workflow rule"""
    rule_emojis = {
        'start-workflow': '🚀',
        'task-decomposition': '📋',
        'implementation': '⚙️',
        'context-update': '🔄',
        'fix': '🔧',
        'experience-execution': '🧪',
        'system': '💻',
        'test': '🧪'
    }
    return rule_emojis.get(rule, '📝')

# Read messages
messages = read_user_messages()

if not messages:
    st.info("No messages from the agent yet. Messages will appear here when the agent uses the user_message parameter in the remember tool.")
else:
    # Sort messages by timestamp (most recent first)
    sorted_messages = sorted(messages, key=lambda x: x['timestamp'], reverse=True)
    
    # Display message statistics (simplified)
    total_messages = len(messages)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", total_messages)
    with col2:
        st.metric("💬 Active Messages", total_messages, help="Messages waiting for your review")
    with col3:
        # Show most recent message timestamp
        if messages:
            latest_msg = max(messages, key=lambda x: x.get('timestamp', ''))
            latest_time = format_timestamp(latest_msg.get('timestamp', ''))
            st.metric("Latest Message", latest_time[:10], help="Date of most recent message")
    
    st.markdown("---")
    
    # Display messages
    for message in sorted_messages:
        message_id = message.get('id')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')
        context = message.get('context', {})
        status = message.get('status', 'unread')
        
        # Create message container
        with st.container():
            # Message header with delete button
            col1, col2, col3 = st.columns([1, 6, 2])
            
            with col1:
                st.markdown(f"**{get_message_icon()}**")
            
            with col2:
                st.markdown(f"**Message #{message_id}** - {format_timestamp(timestamp)}")
            
            with col3:
                # Direct deletion with validation icon (no confirmation)
                if st.button("✅ Mark Read", key=f"delete_{message_id}", help="Mark as read and delete this message"):
                    if delete_message(message_id):
                        st.success("Message deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete message")
            
            # Message content
            st.markdown(f"**Content:** {content}")
            
            # Context information
            if context:
                with st.expander("📋 Context Information", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        workflow_rule = context.get('workflow_rule', 'unknown')
                        st.markdown(f"**Workflow Rule:** {get_rule_emoji(workflow_rule)} {workflow_rule}")
                        
                        agent_state = context.get('agent_state', 'unknown')
                        st.markdown(f"**Agent State:** {agent_state}")
                    
                    with col2:
                        active_task = context.get('active_task')
                        if active_task:
                            st.markdown(f"**Active Task:** {active_task}")
                        else:
                            st.markdown("**Active Task:** *None*")
            
            st.markdown("---")

# Sidebar information
with st.sidebar:
    st.markdown("### 💬 Communication Help")
    st.markdown("""
    This page displays messages sent by the agent to you via the remember tool.
    
    **Features:**
    - Messages are sorted by most recent first
    - Click "✅ Mark Read" to instantly delete messages
    - No confirmation needed - streamlined workflow
    - Expand context information to see workflow details
    
    **Message Management:**
    - 💬 All messages are active until marked as read
    - Marked messages are immediately and permanently removed
    - Simplified one-click deletion process
    
    **Context Information:**
    - **Workflow Rule:** The workflow step the agent was executing
    - **Agent State:** The current state of the agent
    - **Active Task:** The task the agent was working on (if any)
    """)
    
    if st.button("🔄 Refresh Messages"):
        st.rerun() 