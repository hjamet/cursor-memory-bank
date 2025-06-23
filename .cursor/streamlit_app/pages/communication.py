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

def mark_message_as_read(message_id):
    """Mark a message as read in the to_user.json file"""
    try:
        messages_file = Path(".cursor/memory-bank/workflow/to_user.json")
        if messages_file.exists():
            with open(messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find and update the message
            for message in data.get('messages', []):
                if message['id'] == message_id:
                    message['status'] = 'read'
                    message['read_at'] = datetime.now().isoformat()
                    break
            
            # Write back to file
            with open(messages_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
    except Exception as e:
        st.error(f"Error marking message as read: {e}")
        return False

def get_status_color(status):
    """Get color for message status"""
    if status == 'unread':
        return '🔵'  # Blue circle for unread
    else:
        return '✅'  # Green checkmark for read

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
    
    # Display message statistics
    total_messages = len(messages)
    unread_messages = len([m for m in messages if m.get('status') == 'unread'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", total_messages)
    with col2:
        st.metric("Unread Messages", unread_messages)
    with col3:
        st.metric("Read Messages", total_messages - unread_messages)
    
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
            # Message header with status and timestamp
            col1, col2, col3 = st.columns([1, 6, 2])
            
            with col1:
                st.markdown(f"**{get_status_color(status)}**")
            
            with col2:
                st.markdown(f"**Message #{message_id}** - {format_timestamp(timestamp)}")
            
            with col3:
                if status == 'unread':
                    if st.button(f"✓ Mark as Read", key=f"mark_read_{message_id}"):
                        if mark_message_as_read(message_id):
                            st.success("Message marked as read!")
                            st.rerun()
                        else:
                            st.error("Failed to mark message as read")
                else:
                    st.markdown("*Read*")
            
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
                        
                        # Show read timestamp if available
                        if status == 'read' and 'read_at' in message:
                            read_at = format_timestamp(message['read_at'])
                            st.markdown(f"**Read At:** {read_at}")
            
            st.markdown("---")

# Sidebar information
with st.sidebar:
    st.markdown("### 💬 Communication Help")
    st.markdown("""
    This page displays messages sent by the agent to you via the remember tool.
    
    **Message Status:**
    - 🔵 Unread message
    - ✅ Read message
    
    **Features:**
    - Messages are sorted by most recent first
    - Click "✓ Mark as Read" to mark messages as read
    - Expand context information to see workflow details
    - Messages persist across sessions
    
    **Context Information:**
    - **Workflow Rule:** The workflow step the agent was executing
    - **Agent State:** The current state of the agent
    - **Active Task:** The task the agent was working on (if any)
    """)
    
    if st.button("🔄 Refresh Messages"):
        st.rerun() 