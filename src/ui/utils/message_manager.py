"""
Message management utilities for the Streamlit app.
Handles reading and deletion of user messages.
"""

import json
from pathlib import Path
from typing import List, Dict
import streamlit as st


def read_user_messages():
    """Read user messages from to_user.json"""
    try:
        messages_file = Path(".cursor/memory-bank/workflow/to_user.json")
        if messages_file.exists():
            with open(messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("messages", [])
        return []
    except Exception as e:
        st.error(f"Error reading messages: {e}")
        return []


def delete_message(message_id):
    """Delete a message from to_user.json"""
    try:
        messages_file = Path(".cursor/memory-bank/workflow/to_user.json")
        if not messages_file.exists():
            return False

        with open(messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_count = len(data.get("messages", []))
        data["messages"] = [msg for msg in data["messages"] if msg.get("id") != message_id]
        
        if len(data["messages"]) < original_count:
            with open(messages_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False # Message not found
    except Exception as e:
        st.error(f"Error deleting message: {e}")
        return False


def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def get_rule_emoji(rule):
    """Get emoji for workflow rule"""
    rule_emojis = {
        "start-workflow": "🚀",
        "task-decomposition": "📋",
        "implementation": "⚙️",
        "fix": "🔧",
        "context-update": "📝",
        "experience-execution": "🧪",
        "workflow-complete": "✅"
    }
    return rule_emojis.get(rule, "📄") 