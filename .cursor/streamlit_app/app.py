import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict, Optional
from PIL import Image, ImageGrab
import uuid
from streamlit_shortcuts import shortcut_button

# Add the parent directory to the path to find the 'components' module
sys.path.append(str(Path(__file__).resolve().parent))
from components.sidebar import display_sidebar

st.set_page_config(page_title="Review & Communication", page_icon="📨")

display_sidebar()

st.markdown("# 📨 Review & Communication")

st.markdown("Review tasks awaiting validation and view messages from the agent.")

# --- Start of functions from add_request.py ---

def get_next_request_id():
    """Get the next available request ID from userbrief.json"""
    userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
    if userbrief_file.exists():
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("last_id", 0) + 1
    return 1

def save_uploaded_image(uploaded_file, request_id):
    """Save uploaded image to a structured directory and return metadata."""
    if uploaded_file is not None:
        try:
            # Create a unique filename to avoid collisions
            ext = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"req_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
            
            # Define save path
            save_dir = Path(".cursor/temp/images")
            save_dir.mkdir(parents=True, exist_ok=True)
            image_path = save_dir / unique_filename
            
            # Save the file
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Get image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Return image metadata
            return {
                "path": str(image_path),
                "filename": unique_filename,
                "size": uploaded_file.size,
                "width": width,
                "height": height,
                "content_type": uploaded_file.type
            }
        except Exception as e:
            st.error(f"Error saving image: {e}")
            return None
    return None

def get_image_from_clipboard():
    """Attempt to get an image from the clipboard."""
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            return image
    except Exception:
        # Silently ignore errors, as this can fail on some OS
        # if the clipboard is empty or doesn't contain an image.
        pass
    return None

def save_pasted_image(image: Image.Image, request_id: int):
    """Save a pasted image from clipboard to a structured directory and return metadata."""
    if image:
        try:
            # Create a unique filename
            unique_filename = f"req_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_pasted.png"
            
            # Define save path
            save_dir = Path(".cursor/temp/images")
            save_dir.mkdir(parents=True, exist_ok=True)
            image_path = save_dir / unique_filename
            
            # Save the image as PNG
            image.save(image_path, "PNG")

            # Get image metadata
            width, height = image.size
            size = os.path.getsize(image_path)
            
            return {
                "path": str(image_path),
                "filename": unique_filename,
                "size": size,
                "width": width,
                "height": height,
                "content_type": "image/png"
            }
        except Exception as e:
            st.error(f"Error saving pasted image: {e}")
            return None
    return None

def create_new_request(content: str, image_metadata: Optional[Dict] = None):
    """Create a new request in userbrief.json, with optional image attachment."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        
        if userbrief_file.exists():
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"version": "1.0.0", "last_id": 0, "requests": []}

        new_id = data.get("last_id", 0) + 1
        timestamp = datetime.now().isoformat()
        
        new_req = {
            "id": new_id,
            "content": content,
            "status": "new",
            "image": image_metadata, # Can be None
            "created_at": timestamp,
            "updated_at": timestamp,
            "history": [{
                "timestamp": timestamp,
                "action": "created",
                "comment": "Request created via Streamlit app."
            }]
        }

        data["requests"].append(new_req)
        data["last_id"] = new_id

        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error creating request: {e}")
        return False

def get_user_request(request_id: int) -> Optional[Dict]:
    """Get a specific user request by its ID."""
    userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
    if not userbrief_file.exists():
        return None
    with open(userbrief_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            return req
    return None

def delete_user_request(request_id: int) -> bool:
    """Deletes a user request from userbrief.json."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        if not userbrief_file.exists():
            return False

        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_count = len(data.get("requests", []))
        data["requests"] = [req for req in data["requests"] if req.get("id") != request_id]
        
        if len(data["requests"]) < original_count:
            with open(userbrief_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False # Request not found
    except Exception as e:
        st.error(f"Error deleting request: {e}")
        return False

def update_user_request(request_id: int, new_content: str) -> bool:
    """Updates the content of a user request."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        if not userbrief_file.exists():
            return False

        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        request_found = False
        for req in data.get("requests", []):
            if req.get("id") == request_id:
                req["content"] = new_content
                req["updated_at"] = datetime.now().isoformat()
                request_found = True
                break
        
        if request_found:
            with open(userbrief_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False # Request not found
    except Exception as e:
        st.error(f"Error updating request: {e}")
        return False

# --- End of functions from add_request.py ---


# --- Start of functions from communication.py ---

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
            
            original_count = len(data.get('messages', []))
            data['messages'] = [msg for msg in data.get('messages', []) if msg.get('id') != message_id]
            
            if len(data['messages']) < original_count:
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

# --- End of functions from communication.py ---


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
            st.image(image, caption=f"Associated Image: {os.path.basename(image_path)}", use_column_width=True)
        except Exception as e:
            st.warning(f"Could not load image {image_path}: {e}")
    elif image_path:
        st.warning(f"Image not found at path: {image_path}")

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
        col1, col2, col3 = st.columns([1, 6, 2])
        
        with col1:
            st.markdown(f"**{priority_icon}**")
        
        with col2:
            st.markdown(f"**Task #{task_id}**: {title}{image_icon}")
        
        with col3:
            st.markdown(f"**Status: {status}**")
        
        st.info(task.get('short_description', 'N/A'))
        
        # Render image preview if available
        render_image_preview(task)
        
        # Task details expander
        with st.expander("View Task Details", expanded=False):
            st.markdown(f"**Detailed Description:**")
            st.code(task.get('detailed_description', 'N/A'), language='markdown')
            
            st.markdown(f"**Validation Criteria:**")
            st.code(task.get('validation_criteria', 'N/A'), language='markdown')
            
            col_created, col_updated = st.columns(2)
            with col_created:
                st.write(f"**Created:** {format_timestamp(task.get('created_date', ''))}")
            with col_updated:
                st.write(f"**Updated:** {format_timestamp(task.get('updated_date', ''))}")

        # Action buttons
        st.markdown("**Actions:**")
        approve_col, reject_col, notes_col = st.columns([1,1,2])
        
        with approve_col:
            if st.button("👍 Approve", key=f"approve_{task_id}", help="Approve this task. The task status will be set to 'APPROVED'."):
                if update_task_status(task_id, 'APPROVED'):
                    st.success(f"Task #{task_id} approved!")
                    # Clean up associated image if it exists
                    delete_task_image(task)
                    
                    # Check for remaining tasks to decide which tab to show next
                    remaining_review_tasks = [t for t in load_tasks() if t.get('status') == 'REVIEW']
                    
                    if not remaining_review_tasks:
                        st.session_state.active_tab = 'add'
                    else:
                        st.session_state.active_tab = 'review'

                    st.rerun()
        
        with reject_col:
            if st.button("👎 Reject", key=f"reject_{task_id}", help="Reject this task. A new userbrief request will be created automatically for correction."):
                st.session_state[f'reject_form_{task_id}'] = True
        
        # Rejection form (if reject button was clicked)
        if st.session_state.get(f'reject_form_{task_id}', False):
            with st.form(f"rejection_form_{task_id}"):
                st.warning(f"Please provide feedback for rejecting Task #{task_id}:")
                rejection_reason = st.text_area("Reason for rejection:", key=f"rejection_reason_{task_id}", height=100)
                submitted = st.form_submit_button("Submit Rejection")
                
                if submitted:
                    if rejection_reason:
                        rejection_content = f"Correction for Task #{task_id} ({title}):\n\n{rejection_reason}"
                        if create_new_request(rejection_content) and update_task_status(task_id, 'TODO'):
                            st.success(f"Task #{task_id} rejected. New userbrief request created.")
                            del st.session_state[f'reject_form_{task_id}']
                            st.rerun()
                        else:
                            st.error("Failed to process rejection.")
                    else:
                        st.error("Please provide a reason for rejection.")

        st.markdown("---")

def render_message_review_card(message: Dict):
    """Render a card for reviewing an agent message."""
    message_id = message.get('id')
    content = message.get('content', 'No content')
    timestamp = message.get('timestamp', '')
    
    with st.container(border=True):
        st.caption(f"📨 Agent Message | {format_timestamp(timestamp)} | ID: {message_id}")
        st.markdown(f"> {content}")

        action_col1, action_col2 = st.columns([1, 5])
        
        with action_col1:
            if st.button("✅ Acknowledge", key=f"validate_{message_id}", help="Acknowledge and delete this message."):
                if delete_message(message_id):
                    st.toast(f"Message {message_id} acknowledged.")
                    if 'answering_message_id' in st.session_state and st.session_state.answering_message_id == message_id:
                        del st.session_state.answering_message_id
                    st.rerun()
                else:
                    st.error("Failed to delete message.")

        with action_col2:
            if st.button("❓ Ask a question", key=f"answer_{message_id}", help="Ask a follow-up question. This will create a new request."):
                st.session_state.answering_message_id = message_id

        # Answer form, now inside the container
        if st.session_state.get('answering_message_id') == message_id:
            with st.form(key=f"answer_form_{message_id}"):
                user_question = st.text_area("Your question or comment:", key=f"question_{message_id}", height=100)
                submitted = st.form_submit_button("Send Question")
                
                if submitted:
                    if user_question:
                        # Create new userbrief request
                        request_content = f"Question regarding agent message #{message_id}: \"{content[:100]}...\"\n\nMy question: {user_question}"
                        if create_new_request(request_content):
                            st.success("Your question has been sent as a new request.")
                            # Delete the original message after it has been answered
                            delete_message(message_id)
                            del st.session_state.answering_message_id
                            st.rerun()
                        else:
                            st.error("Failed to create a new request.")
                    else:
                        st.warning("Please enter a question or comment.")
        
        st.markdown("---")

def render_add_request_tab():
    """Render the UI for adding a new user request."""
    st.header("✨ Add New Request")

    # Initialize session states
    if 'pasted_image_obj' not in st.session_state:
        st.session_state.pasted_image_obj = None
    if 'last_submitted_request_id' not in st.session_state:
        st.session_state.last_submitted_request_id = None
    if 'editing_request_id' not in st.session_state:
        st.session_state.editing_request_id = None
    if 'clear_request_form' not in st.session_state:
        st.session_state.clear_request_form = False

    # If a form was just submitted, clear the state before rendering widgets
    if st.session_state.clear_request_form:
        st.session_state.request_content_area = ""
        st.session_state.pasted_image_obj = None
        st.session_state.clear_request_form = False

    # If editing, load the content
    request_content_default = ""
    if st.session_state.editing_request_id:
        request_to_edit = get_user_request(st.session_state.editing_request_id)
        if request_to_edit:
            request_content_default = request_to_edit.get("content", "")

    request_content = st.text_area("Request Description", value=request_content_default, height=250, placeholder="Please provide a detailed description of your request...", label_visibility="collapsed", key="request_content_area")
    
    with st.expander("📎 Attach an Image (Optional)"):
        col1, col2 = st.columns(2)
        with col1:
            uploaded_image = st.file_uploader(
                "Upload an image",
                type=['png', 'jpg', 'jpeg', 'gif'],
                label_visibility="collapsed"
            )

        with col2:
            if shortcut_button("📋 Paste from clipboard", "ctrl+v", help="Press Ctrl+V to paste an image from your clipboard."):
                pasted_image = get_image_from_clipboard()
                if pasted_image:
                    st.session_state.pasted_image_obj = pasted_image
                    st.toast("Image captured from clipboard! Preview below.")
                    uploaded_image = None # Clear file uploader
                else:
                    st.warning("No image found on clipboard.")
    
        # Display preview for uploaded or pasted image
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded image preview", width=300)
            st.session_state.pasted_image_obj = None  # Clear pasted image if user uploads
        elif st.session_state.pasted_image_obj:
            st.image(st.session_state.pasted_image_obj, caption="Pasted image preview", width=300)

    # Determine button label and action
    is_editing = st.session_state.editing_request_id is not None
    submit_label = "Update Request" if is_editing else "Submit New Request"
    
    # Use shortcut_button with Ctrl+Enter shortcut
    if shortcut_button(submit_label, "ctrl+enter", type="primary", use_container_width=True):
        if request_content:
            if is_editing:
                # Update existing request
                if update_user_request(st.session_state.editing_request_id, request_content):
                    st.success(f"Request #{st.session_state.editing_request_id} updated successfully!")
                    st.session_state.last_submitted_request_id = st.session_state.editing_request_id
                    st.session_state.editing_request_id = None
                    st.session_state.clear_request_form = True # Clear form on next run
                    # st.rerun() # This is likely interrupting the balloons animation
                else:
                    st.error("Failed to update the request.")
            else:
                # Create new request
                next_id = get_next_request_id()
                image_meta = None
                if uploaded_image:
                    image_meta = save_uploaded_image(uploaded_image, next_id)
                elif st.session_state.pasted_image_obj:
                    image_meta = save_pasted_image(st.session_state.pasted_image_obj, next_id)

                if create_new_request(request_content, image_meta):
                    st.success(f"Request #{next_id} submitted successfully!")
                    st.balloons()
                    st.session_state.pasted_image_obj = None
                    st.session_state.last_submitted_request_id = next_id
                    st.session_state.clear_request_form = True # Clear form on next run
                    # st.rerun() # This is likely interrupting the balloons animation
                else:
                    st.error("Failed to submit the request. Please check the logs.")
        else:
            st.warning("Please enter a description for your request.")

    # Display the last submitted request for editing/deleting
    if st.session_state.last_submitted_request_id and st.session_state.editing_request_id is None:
        st.markdown("---")
        st.subheader("Last Submitted Request")
        last_request = get_user_request(st.session_state.last_submitted_request_id)

        if last_request:
            if last_request.get("status") == "new":
                with st.container(border=True):
                    st.markdown(f"**Request #{last_request['id']}** (Status: {last_request['status']})")
                    st.info(last_request['content'])

                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{last_request['id']}"):
                            st.session_state.editing_request_id = last_request['id']
                            st.rerun()
                    with col2:
                        if st.button("❌ Delete", key=f"delete_{last_request['id']}"):
                            if delete_user_request(last_request['id']):
                                st.toast(f"Request #{last_request['id']} deleted.")
                                st.session_state.last_submitted_request_id = None
                                st.rerun()
                            else:
                                st.error("Failed to delete the request.")
            else:
                 st.info(f"Request #{last_request['id']} has already been processed by the agent and cannot be modified here.")

    # This block was causing state modification errors and is no longer needed.
    # The new 'clear_request_form' flag handles state reset safely.
    if st.session_state.get('form_submitted'):
        st.session_state.form_submitted = False
        st.rerun()

def main():
    """Main function to render the review page"""
    # Initialize session state for active tab if not present
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "add"

    # Load data upfront
    tasks = load_tasks()
    messages = read_user_messages()
    
    # Calculate counts for badges
    review_tasks_count = len([t for t in tasks if t.get('status') == 'REVIEW'])
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
        review_tasks = [t for t in tasks if t.get('status') == 'REVIEW']
        
        if not review_tasks:
            st.info("No tasks are currently awaiting review.")
        else:
            st.markdown(f"**{len(review_tasks)}** task(s) to review:")
            for task in sorted(review_tasks, key=lambda x: x.get('id', 0), reverse=True):
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