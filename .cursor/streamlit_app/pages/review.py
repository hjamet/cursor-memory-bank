import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict, Optional
from PIL import Image

st.set_page_config(page_title="Review & Communication", page_icon="📨")

st.markdown("# 📨 Review & Communication")

st.markdown("This page displays tasks that are ready for review and messages from the agent.")

# Helper functions for task and userbrief management
def get_tasks_file():
    """Get the path to the tasks file, prioritizing MCP-managed file"""
    possible_paths = [
        Path('.cursor/memory-bank/streamlit_app/tasks.json'),  # MCP-managed file (primary)
        Path('.cursor/streamlit_app/tasks.json'),  # Local streamlit file
        Path('.cursor/memory-bank/tasks.json'),  # Legacy location
        Path('tasks.json')  # Fallback
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def load_tasks() -> List[Dict]:
    """Load tasks from the tasks file"""
    tasks_file = get_tasks_file()
    if not tasks_file:
        return []
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            return data
        else:
            return data.get('tasks', [])
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        return []

def update_task_status(task_id: int, new_status: str, validation_data: Optional[Dict] = None) -> bool:
    """Update task status and optionally add validation data"""
    tasks_file = get_tasks_file()
    if not tasks_file:
        return False
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            tasks = data
            data_format = 'array'
        else:
            tasks = data.get('tasks', [])
            data_format = 'object'
        
        # Find and update the task
        for task in tasks:
            if str(task.get('id', task.get('task_id'))) == str(task_id):
                task['status'] = new_status
                task['updated_date'] = datetime.now().isoformat()
                
                # Add validation data if provided
                if validation_data:
                    task['validation'] = validation_data
                
                # Save back to file
                if data_format == 'array':
                    save_data = tasks
                else:
                    save_data = {'tasks': tasks}
                
                with open(tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                
                return True
                
    except Exception as e:
        st.error(f"Error updating task: {e}")
        return False
    
    return False

def create_userbrief_request(content: str) -> bool:
    """Create a new userbrief request for task corrections"""
    try:
        userbrief_file = ".cursor/memory-bank/workflow/userbrief.json"
        
        # Read current userbrief
        try:
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                userbrief_data = json.load(f)
        except FileNotFoundError:
            userbrief_data = {
                "version": "1.0.0",
                "last_id": 0,
                "requests": []
            }
        
        # Create new request
        new_id = userbrief_data["last_id"] + 1
        timestamp = datetime.now().isoformat()
        
        new_request = {
            "id": new_id,
            "content": content,
            "status": "new",
            "created_at": timestamp,
            "updated_at": timestamp,
            "history": [
                {
                    "timestamp": timestamp,
                    "action": "created",
                    "comment": "Request created automatically from task rejection in To Review page."
                }
            ]
        }
        
        # Add to requests and update last_id
        userbrief_data["requests"].append(new_request)
        userbrief_data["last_id"] = new_id
        
        # Save updated userbrief
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(userbrief_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        st.error(f"Error creating userbrief request: {e}")
        return False

def has_associated_image(task: Dict) -> bool:
    """Check if task has an associated image"""
    return task.get('image') is not None and task.get('image') != ''

def get_image_path(task: Dict) -> Optional[str]:
    """Get the full path to the task's associated image"""
    if has_associated_image(task):
        image_data = task.get('image')
        
        # Handle different image data formats
        if isinstance(image_data, dict):
            # Image metadata format (from new implementation)
            return image_data.get('path')
        elif isinstance(image_data, str):
            # Simple string path format
            if image_data.startswith('.cursor/temp/images/'):
                return image_data
            else:
                return os.path.join('.cursor', 'temp', 'images', image_data)
    return None

def delete_task_image(task: Dict) -> bool:
    """Delete the image file associated with a task"""
    image_path = get_image_path(task)
    if image_path and os.path.exists(image_path):
        try:
            # Security check: ensure path is within temp images directory
            normalized_path = os.path.normpath(image_path)
            temp_images_dir = os.path.normpath('.cursor/temp/images/')
            
            if not normalized_path.startswith(temp_images_dir):
                st.warning(f"Security warning: Image path {image_path} is outside temp directory")
                return False
            
            os.remove(image_path)
            return True
        except Exception as e:
            st.warning(f"Could not delete image {image_path}: {e}")
            return False
    return True  # No image to delete or already deleted

def render_image_preview(task: Dict):
    """Render image preview if task has an associated image"""
    if not has_associated_image(task):
        return
    
    image_path = get_image_path(task)
    if image_path and os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            
            # Get image metadata
            image_data = task.get('image', {})
            if isinstance(image_data, dict):
                original_name = image_data.get('original_name', 'Unknown')
                file_size = image_data.get('size', 0)
                source = image_data.get('source', 'upload')
            else:
                original_name = os.path.basename(image_path)
                file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
                source = 'upload'
            
            with st.expander(f"📸 Associated Image: {original_name}"):
                col_img, col_info = st.columns([2, 1])
                
                with col_img:
                    st.image(image, caption=f"Image: {original_name}", use_column_width=True)
                
                with col_info:
                    st.markdown("**Image Information:**")
                    st.write(f"**Filename:** {original_name}")
                    st.write(f"**Size:** {file_size:,} bytes")
                    st.write(f"**Dimensions:** {image.width} x {image.height} px")
                    st.write(f"**Format:** {image.format}")
                    st.write(f"**Source:** {source.title()}")
                    
                    if source == 'clipboard':
                        st.info("📋 Image was pasted with Ctrl+V")
                    
        except Exception as e:
            st.error(f"Error displaying image: {e}")
    else:
        st.warning("📸 Task has associated image but file not found")

def render_task_review_card(task: Dict):
    """Render a task card with review/validation options"""
    task_id = task.get('id', task.get('task_id'))
    title = task.get('title', 'Untitled Task')
    status = task.get('status', 'UNKNOWN')
    priority = task.get('priority', 3)
    
    # Priority color mapping
    priority_colors = {
        1: "🟢",  # Low
        2: "🟡",  # Medium-Low
        3: "🔵",  # Medium
        4: "🟠",  # High
        5: "🔴"   # Critical
    }
    
    priority_icon = priority_colors.get(priority, "⚪")
    
    # Check if task has associated image
    has_image = has_associated_image(task)
    image_icon = " 📸" if has_image else ""
    
    with st.container():
        st.markdown(f"### {priority_icon} Task #{task_id}: {title}{image_icon}")
        st.markdown(f"**Status:** {status}")
        
        short_desc = task.get('short_description')
        if short_desc:
            st.write(short_desc)
        
        with st.expander("📖 Task Details", expanded=False):
            st.markdown(f"**Detailed Description:**")
            st.write(task.get('detailed_description', 'No detailed description.'))
            
            st.markdown("**Validation Criteria:**")
            st.write(task.get('validation_criteria', 'No validation criteria.'))

            impacted_files = task.get('impacted_files', [])
            if impacted_files:
                st.markdown("**Impacted Files:**")
                for file in impacted_files:
                    st.code(file)

        render_image_preview(task)

        # Rejection form
        rejection_reason = st.text_area(
            "Rejection Reason (if any):", 
            key=f"rejection_{task_id}",
            help="If you reject this task, provide a reason for the new request."
        )

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Approve", key=f"approve_{task_id}"):
                validation_data = {
                    'status': 'approved',
                    'approved_at': datetime.now().isoformat(),
                    'comment': 'Approved via To Review interface'
                }
                if update_task_status(task_id, 'APPROVED', validation_data):
                    st.success(f"Task #{task_id} approved!")
                    # Clean up associated image if it exists
                    delete_task_image(task)
                    st.rerun()

        with col2:
            if st.button("👎 Reject", key=f"reject_{task_id}"):
                if rejection_reason.strip():
                    request_content = f"Task #{task_id} was rejected.\n\nReason: {rejection_reason}\n\nOriginal Task Title: {title}"
                    if create_userbrief_request(request_content):
                        validation_data = {
                            'status': 'rejected',
                            'rejected_at': datetime.now().isoformat(),
                            'comment': rejection_reason
                        }
                        # Update task status to TODO to be re-evaluated
                        update_task_status(task_id, 'TODO', validation_data)
                        st.success(f"Task #{task_id} rejected. New request created.")
                        st.rerun()
                else:
                    st.warning("Please provide a reason for rejection.")
        
        st.markdown("---")

# Functions from communication.py
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

def render_messages(messages):
    st.markdown("## 💬 Agent Messages")
    if not messages:
        st.info("No messages from the agent yet.")
        return

    sorted_messages = sorted(messages, key=lambda x: x['timestamp'], reverse=True)
    
    total_messages = len(messages)
    st.metric("Total Messages", total_messages)
    st.markdown("---")

    for message in sorted_messages:
        message_id = message.get('id')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')
        context = message.get('context', {})
        
        with st.container():
            col1, col2, col3 = st.columns([1, 6, 2])
            with col1:
                st.markdown(f"**💬**")
            with col2:
                st.markdown(f"**Message #{message_id}** - {format_timestamp(timestamp)}")
            with col3:
                if st.button("✅ Mark Read", key=f"delete_msg_{message_id}", help="Mark as read and delete this message"):
                    if delete_message(message_id):
                        st.success("Message deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete message")
            
            st.markdown(f"**Content:** {content}")
            
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

def main():
    # Tabs for Tasks and Messages
    tab1, tab2 = st.tabs(["🔍 Tasks to Review", "💬 Agent Messages"])

    with tab1:
        tasks = load_tasks()
        review_tasks = [task for task in tasks if task.get('status') == 'REVIEW']
        
        st.metric("Tasks to Review", len(review_tasks))
        
        if not review_tasks:
            st.success("🎉 No tasks are currently waiting for review.")
        else:
            sorted_tasks = sorted(review_tasks, key=lambda x: x.get('updated_date', ''), reverse=True)
            for task in sorted_tasks:
                render_task_review_card(task)

    with tab2:
        messages = read_user_messages()
        render_messages(messages)


if __name__ == "__main__":
    main() 