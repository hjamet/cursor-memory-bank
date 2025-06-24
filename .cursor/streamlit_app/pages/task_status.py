import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
import statistics
from typing import Tuple, Optional

# Add the parent directory of the pages directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.sidebar import display_sidebar
from components import task_utils

st.set_page_config(page_title="Task Status", page_icon="✅")

display_sidebar()

st.markdown("# ✅ Task Status")

# Helper functions for task management using MCP tools
def update_task_via_mcp(task_id, **kwargs):
    """Update a task using the MCP update_task tool"""
    try:
        # This would typically call the MCP tool, but for now we'll use the local file approach
        # In a real implementation, this would use st.session_state or a proper MCP client
        return update_task_local(task_id, **kwargs)
    except Exception as e:
        st.error(f"Error updating task via MCP: {e}")
        return False

def delete_task_via_mcp(task_id):
    """Delete a task using MCP tools"""
    try:
        # This would typically call the MCP tool, but for now we'll use the local file approach
        return delete_task_local(task_id)
    except Exception as e:
        st.error(f"Error deleting task via MCP: {e}")
        return False

def update_task_local(task_id, **kwargs):
    """Update a task in the local tasks file"""
    tasks_file = task_utils.get_tasks_file()
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
                
                # If status is being updated, manage history
                if 'status' in kwargs and kwargs['status'] != task.get('status'):
                    now_iso = datetime.now().isoformat()
                    if 'status_history' not in task or not task['status_history']:
                        # Initialize history for older tasks.
                        # This creates a baseline from its creation date and current status.
                        task['status_history'] = [{'status': task.get('status', 'TODO'), 'timestamp': task.get('created_date')}]
                    
                    # Append new status change
                    task['status_history'].append({
                        'status': kwargs['status'],
                        'timestamp': now_iso
                    })
                    task['updated_date'] = now_iso
                else:
                    task['updated_date'] = datetime.now().isoformat()

                # Update other fields
                for key, value in kwargs.items():
                    task[key] = value
                
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

def delete_task_local(task_id):
    """Delete a task from the local tasks file"""
    tasks_file = task_utils.get_tasks_file()
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
        
        # Find and remove the task
        original_length = len(tasks)
        tasks = [task for task in tasks if str(task.get('id', task.get('task_id'))) != str(task_id)]
        
        if len(tasks) < original_length:
            # Save back to file
            if data_format == 'array':
                save_data = tasks
            else:
                save_data = {'tasks': tasks}
            
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
        else:
            st.error(f"Task #{task_id} not found")
            return False
            
    except Exception as e:
        st.error(f"Error deleting task: {e}")
        return False
    
    return False

def get_userbrief_requests():
    """Get unprocessed userbrief requests"""
    userbrief_file = Path('.cursor/memory-bank/workflow/userbrief.json')
    if not userbrief_file.exists():
        return []
    
    try:
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        requests = data.get('requests', [])
        # Return only unprocessed requests (new or in_progress)
        unprocessed = [req for req in requests if req.get('status') in ['new', 'in_progress']]
        return unprocessed
    except Exception as e:
        st.error(f"Error reading userbrief: {e}")
        return []

def get_user_request(request_id: int):
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

def sort_tasks_by_dependencies_and_priority(tasks):
    """Sort tasks by dependencies first, then by priority"""
    # Create a dependency graph
    task_dict = {str(task.get('id', task.get('task_id'))): task for task in tasks}
    
    def get_dependency_level(task_id, visited=None):
        if visited is None:
            visited = set()
        
        if task_id in visited:
            return 0  # Circular dependency, treat as level 0
        
        visited.add(task_id)
        task = task_dict.get(str(task_id))
        if not task:
            return 0
        
        dependencies = task.get('dependencies', [])
        if not dependencies:
            return 0
        
        max_dep_level = 0
        for dep_id in dependencies:
            dep_level = get_dependency_level(str(dep_id), visited.copy())
            max_dep_level = max(max_dep_level, dep_level)
        
        return max_dep_level + 1
    
    # Sort by dependency level first, then by priority (descending)
    def sort_key(task):
        task_id = str(task.get('id', task.get('task_id')))
        dep_level = get_dependency_level(task_id)
        priority = task.get('priority', 3)
        return (dep_level, -priority)  # Negative priority for descending order
    
    return sorted(tasks, key=sort_key)

def render_task_card(task, show_inline_edit=True):
    """Render a task card with optional inline editing and improved visual design"""
    task_id = task.get('id', task.get('task_id', 'N/A'))
    title = task.get('title', 'Untitled')
    short_desc = task.get('short_description', task.get('description', 'No description'))
    status = task.get('status', 'TODO')
    priority = task.get('priority', 3)
    dependencies = task.get('dependencies', [])
    
    # Priority emoji and color mapping
    priority_config = {
        5: {"emoji": "🔥", "color": "#FF4B4B", "label": "Critical"},
        4: {"emoji": "🔴", "color": "#FF6B6B", "label": "High"},
        3: {"emoji": "🟡", "color": "#FFD93D", "label": "Normal"},
        2: {"emoji": "🟢", "color": "#6BCF7F", "label": "Low"},
        1: {"emoji": "⚪", "color": "#E0E0E0", "label": "Minimal"}
    }
    priority_info = priority_config.get(priority, {"emoji": "📝", "color": "#808080", "label": "Unknown"})
    
    # Status emoji and color mapping (improved colors)
    status_config = {
        'TODO': {"emoji": "⏳", "color": "#FFA500", "bg_color": "#FFF4E6"},
        'IN_PROGRESS': {"emoji": "🔄", "color": "#4169E1", "bg_color": "#E6F0FF"},
        'BLOCKED': {"emoji": "🚫", "color": "#DC143C", "bg_color": "#FFE6E6"},
        'REVIEW': {"emoji": "👀", "color": "#9932CC", "bg_color": "#F3E6FF"},
        'DONE': {"emoji": "✅", "color": "#228B22", "bg_color": "#E6FFE6"},
        'APPROVED': {"emoji": "🎯", "color": "#008B8B", "bg_color": "#E6FFFF"}
    }
    status_info = status_config.get(status, {"emoji": "📝", "color": "#808080", "bg_color": "#F5F5F5"})
    
    # Check if task has associated image
    has_image = task.get('image') and task.get('image').strip()
    image_indicator = " 📸" if has_image else ""
    
    # Create a styled container for the task
    with st.container():
        # Task header with improved styling
        st.markdown(
            f"""
            <div style="
                background-color: {status_info['bg_color']};
                padding: 10px;
                border-radius: 8px;
                border-left: 4px solid {status_info['color']};
                margin-bottom: 10px;
            ">
                <h3 style="margin: 0; color: {status_info['color']};">
                    {status_info['emoji']} #{task_id} - {title}{image_indicator}
                </h3>
                <p style="margin: 5px 0 0 0; color: #666;">
                    📝 {short_desc}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Task metadata and controls in organized columns
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            # Dependencies info with better styling
            if dependencies:
                dep_str = ', '.join([f"#{dep}" for dep in dependencies])
                st.markdown(f"⚠️ **Depends on:** {dep_str}")
                st.caption("🔗 This task cannot start until dependencies are completed")
            else:
                st.markdown("✅ **No dependencies** - Ready to start")
        
        with col2:
            # Priority display/edit with visual improvements
            if show_inline_edit:
                priority_options = {
                    1: f"⚪ Minimal (1)",
                    2: f"🟢 Low (2)", 
                    3: f"🟡 Normal (3)",
                    4: f"🔴 High (4)",
                    5: f"🔥 Critical (5)"
                }
                new_priority = st.selectbox(
                    "Priority:",
                    [1, 2, 3, 4, 5],
                    index=[1, 2, 3, 4, 5].index(priority),
                    format_func=lambda x: priority_options[x],
                    key=f"priority_{task_id}",
                    help="Change task priority level"
                )
                
                if new_priority != priority:
                    if update_task_via_mcp(task_id, priority=new_priority):
                        st.success(f"Priority updated to {priority_config[new_priority]['label']}!")
                        st.rerun()
            else:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 5px; background-color: {priority_info['color']}20; border-radius: 5px;">
                        <strong>{priority_info['emoji']} P{priority}</strong><br>
                        <small>{priority_info['label']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col3:
            # Status display/edit with improved visuals
            if show_inline_edit:
                status_options = {
                    'TODO': '⏳ To Do',
                    'IN_PROGRESS': '🔄 In Progress',
                    'BLOCKED': '🚫 Blocked',
                    'REVIEW': '👀 Review',
                    'DONE': '✅ Done',
                    'APPROVED': '🎯 Approved'
                }
                status_list = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW', 'DONE', 'APPROVED']
                current_index = status_list.index(status) if status in status_list else 0
                new_status = st.selectbox(
                    "Status:",
                    status_list,
                    index=current_index,
                    format_func=lambda x: status_options[x],
                    key=f"status_{task_id}",
                    help="Change task status"
                )
                
                if new_status != status:
                    if update_task_via_mcp(task_id, status=new_status):
                        st.success(f"Status updated to {new_status}!")
                        st.rerun()
            else:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 5px; background-color: {status_info['color']}20; border-radius: 5px;">
                        <strong>{status_info['emoji']} {status}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col4:
            # Task metadata display
            created_date = task.get('created_date', 'Unknown')
            if created_date != 'Unknown':
                try:
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    days_old = (datetime.now().replace(tzinfo=created_dt.tzinfo) - created_dt).days
                    st.caption(f"📅 **Created:** {days_old} days ago")
                except:
                    st.caption(f"📅 **Created:** {created_date[:10]}")
            else:
                st.caption("📅 **Created:** Unknown")
        
        # Action buttons for inline editing with improved layout
        if show_inline_edit:
            st.markdown("### ⚡ Quick Actions")
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if st.button(f"📋 Details", key=f"details_{task_id}", help="Show/hide detailed information"):
                    # Toggle detailed view state
                    detail_key = f"show_details_{task_id}"
                    if detail_key not in st.session_state:
                        st.session_state[detail_key] = False
                    st.session_state[detail_key] = not st.session_state[detail_key]
                    st.rerun()
            
            with action_col2:
                if status not in ['DONE', 'APPROVED']:
                    if st.button(f"✅ Complete", key=f"complete_{task_id}", type="primary", help="Mark task as completed"):
                        if update_task_via_mcp(task_id, status='DONE'):
                            st.success(f"Task #{task_id} completed!")
                            st.rerun()
            
            with action_col3:
                if status == 'TODO':
                    if st.button(f"🚀 Start", key=f"start_{task_id}", help="Mark task as in progress"):
                        if update_task_via_mcp(task_id, status='IN_PROGRESS'):
                            st.success(f"Task #{task_id} started!")
                            st.rerun()
                elif status == 'IN_PROGRESS':
                    if st.button(f"⏸️ Pause", key=f"pause_{task_id}", help="Move task back to TODO"):
                        if update_task_via_mcp(task_id, status='TODO'):
                            st.success(f"Task #{task_id} paused!")
                            st.rerun()
            
            with action_col4:
                # Delete button with confirmation
                delete_key = f"confirm_delete_{task_id}"
                if delete_key in st.session_state and st.session_state[delete_key]:
                    if st.button(f"⚠️ Confirm Delete", key=f"confirm_del_{task_id}", help="Confirm deletion"):
                        if delete_task_via_mcp(task_id):
                            st.success(f"Task #{task_id} deleted!")
                            if delete_key in st.session_state:
                                del st.session_state[delete_key]
                            st.rerun()
                else:
                    if st.button(f"🗑️ Delete", key=f"delete_{task_id}", help="Delete this task"):
                        st.session_state[delete_key] = True
                        st.warning(f"⚠️ Click 'Confirm Delete' to delete Task #{task_id}")
                        st.rerun()
        
        # Show detailed view if toggled
        detail_key = f"show_details_{task_id}"
        if st.session_state.get(detail_key, False):
            st.markdown("---")
            st.markdown("### 📋 Detailed Task Information")
            
            # Create a detailed information container
            with st.container():
                # Basic information in columns
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.markdown(f"**🆔 Task ID:** #{task_id}")
                    st.markdown(f"**📝 Title:** {title}")
                    st.markdown(f"**🎯 Status:** {status_info['emoji']} {status}")
                    st.markdown(f"**⭐ Priority:** {priority_info['emoji']} {priority} ({priority_info['label']})")
                
                with info_col2:
                    if dependencies:
                        dep_str = ', '.join([f"#{dep}" for dep in dependencies])
                        st.markdown(f"**🔗 Dependencies:** {dep_str}")
                    else:
                        st.markdown("**🔗 Dependencies:** None")
                    
                    # Timestamps
                    created_date = task.get('created_date', 'Unknown')
                    updated_date = task.get('updated_date', 'Unknown')
                    
                    if created_date != 'Unknown':
                        try:
                            created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            st.markdown(f"**📅 Created:** {created_dt.strftime('%Y-%m-%d %H:%M')}")
                        except:
                            st.markdown(f"**📅 Created:** {created_date}")
                    
                    if updated_date != 'Unknown':
                        try:
                            updated_dt = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
                            st.markdown(f"**🔄 Updated:** {updated_dt.strftime('%Y-%m-%d %H:%M')}")
                        except:
                            st.markdown(f"**🔄 Updated:** {updated_date}")
                
                # Descriptions
                st.markdown("**📋 Short Description:**")
                st.write(short_desc)
                
                detailed_desc = task.get('detailed_description', 'No detailed description available')
                if detailed_desc and detailed_desc != 'No detailed description available':
                    st.markdown("**📖 Detailed Description:**")
                    st.write(detailed_desc)
                
                # Validation criteria if available
                validation_criteria = task.get('validation_criteria', '')
                if validation_criteria:
                    st.markdown("**✅ Validation Criteria:**")
                    st.write(validation_criteria)
                
                # Impacted files if available
                impacted_files = task.get('impacted_files', [])
                if impacted_files:
                    st.markdown("**📁 Impacted Files:**")
                    for file in impacted_files:
                        st.code(file, language="text")
                
                # Image preview if available
                if has_image:
                    st.markdown("**📸 Associated Image:**")
                    image_path = task.get('image')
                    if os.path.exists(image_path):
                        try:
                            st.image(image_path, caption=f"Image for Task #{task_id}", use_column_width=True)
                            # Show image metadata
                            file_size = os.path.getsize(image_path)
                            st.caption(f"📄 File: {os.path.basename(image_path)} ({file_size:,} bytes)")
                        except Exception as e:
                            st.error(f"❌ Could not display image: {str(e)}")
                    else:
                        st.warning(f"⚠️ Image file not found: {image_path}")
             
            # Hide details button
            if st.button(f"🔼 Hide Details", key=f"hide_details_{task_id}"):
                st.session_state[detail_key] = False
                st.rerun()
    
    st.markdown("---")

def render_userbrief_request(request):
    """Render a userbrief request card"""
    req_id = request.get('id', 'N/A')
    content = request.get('content', 'No content')
    status = request.get('status', 'new')
    created_at = request.get('created_at', '')[:10] if request.get('created_at') else 'Unknown'
    
    # Initialize session state for editing
    edit_key = f"edit_request_{req_id}"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    with st.container(border=True):
        st.markdown(f"#### 📋 Request #{req_id}")
        st.caption(f"📅 **Created:** {created_at} | 🏷️ **Status:** {status}")

        if st.session_state[edit_key]:
            # --- EDITING MODE ---
            with st.form(key=f"edit_form_{req_id}"):
                new_content = st.text_area("Edit request content:", value=content, height=150, key=f"text_{req_id}")
                
                submit_col, cancel_col = st.columns(2)
                with submit_col:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        if update_user_request(req_id, new_content):
                            st.success(f"Request #{req_id} updated.")
                            st.session_state[edit_key] = False
                            st.rerun()
                        else:
                            st.error("Failed to update request.")
                with cancel_col:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state[edit_key] = False
                        st.rerun()
        else:
            # --- DISPLAY MODE ---
            display_content = content[:250] + "..." if len(content) > 250 else content
            st.info(display_content)
            
            if len(content) > 250:
                with st.expander("📖 Read Full Content"):
                    st.markdown(content)

            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 5])
            with col1:
                if st.button("✏️ Edit", key=f"start_edit_{req_id}", help="Edit this request"):
                    st.session_state[edit_key] = True
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{req_id}", help="Delete this request"):
                    if delete_user_request(req_id):
                        st.toast(f"Request #{req_id} deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete request.")
    
    st.markdown("---")

def fuzzy_search_tasks(tasks, userbrief_requests, search_query):
    """
    Perform fuzzy search on tasks and userbrief requests
    Returns filtered tasks and requests that match the search query
    """
    if not search_query.strip():
        return tasks, userbrief_requests
    
    # Normalize search query
    query_lower = search_query.lower().strip()
    query_words = query_lower.split()
    
    def matches_task(task):
        """Check if task matches search criteria"""
        # Search in task ID
        task_id = str(task.get('id', ''))
        if query_lower in task_id or f"#{task_id}" in query_lower:
            return True
        
        # Search in status
        status = task.get('status', '').lower()
        if query_lower in status:
            return True
        
        # Search in title
        title = task.get('title', '').lower()
        if any(word in title for word in query_words):
            return True
        
        # Search in short description
        short_desc = task.get('short_description', '').lower()
        if any(word in short_desc for word in query_words):
            return True
        
        # Search in detailed description
        detailed_desc = task.get('detailed_description', '').lower()
        if any(word in detailed_desc for word in query_words):
            return True
        
        # Search in validation criteria
        validation = task.get('validation_criteria', '').lower()
        if any(word in validation for word in query_words):
            return True
        
        # Search in impacted files
        files = ' '.join(task.get('impacted_files', [])).lower()
        if any(word in files for word in query_words):
            return True
        
        return False
    
    def matches_request(request):
        """Check if userbrief request matches search criteria"""
        # Search in request ID
        req_id = str(request.get('id', ''))
        if query_lower in req_id or f"#{req_id}" in query_lower:
            return True
        
        # Search in status
        status = request.get('status', '').lower()
        if query_lower in status:
            return True
        
        # Search in content
        content = request.get('content', '').lower()
        if any(word in content for word in query_words):
            return True
        
        return False
    
    # Filter tasks and requests
    filtered_tasks = [task for task in tasks if matches_task(task)]
    filtered_requests = [req for req in userbrief_requests if matches_request(req)]
    
    return filtered_tasks, filtered_requests

def render_advanced_search_and_filters():
    """Render advanced search and filtering controls"""
    st.markdown("### 🔍 Search & Filters")
    
    # Create columns for search and filters
    search_col, filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1, 1])
    
    with search_col:
        search_query = st.text_input(
            "🔍 Search tasks...",
            placeholder="Search by ID, title, description, status, or files",
            help="Enter keywords to search across all task fields",
            key="task_search_query"
        )
    
    with filter_col1:
        # Status filter
        status_options = ['Active', 'All', 'TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW', 'DONE', 'APPROVED']
        status_filter = st.selectbox(
            "📊 Status:",
            status_options,
            index=0, # Default to 'Active'
            help="Filter tasks by status. 'Active' hides DONE and APPROVED.",
            key="status_filter"
        )
    
    with filter_col2:
        # Priority filter
        priority_options = ['All', '🔥 Critical (5)', '🔴 High (4)', '🟡 Normal (3)', '🟢 Low (2)', '⚪ Minimal (1)']
        priority_filter = st.selectbox(
            "⭐ Priority:",
            priority_options,
            help="Filter tasks by priority level",
            key="priority_filter"
        )
    
    with filter_col3:
        # Dependency filter
        dependency_options = ['All', 'No Dependencies', 'Has Dependencies', 'Blocked by Dependencies']
        dependency_filter = st.selectbox(
            "🔗 Dependencies:",
            dependency_options,
            help="Filter tasks by dependency status",
            key="dependency_filter"
        )
    
    # Additional filters row
    filter_row2_col1, filter_row2_col2, filter_row2_col3, filter_row2_col4 = st.columns(4)
    
    with filter_row2_col1:
        # Date range filter
        date_filter = st.selectbox(
            "📅 Created:",
            ['All Time', 'Last 7 days', 'Last 30 days', 'Last 90 days'],
            help="Filter tasks by creation date",
            key="date_filter"
        )
    
    with filter_row2_col2:
        # Image filter
        image_filter = st.selectbox(
            "📸 Images:",
            ['All', 'With Images', 'Without Images'],
            help="Filter tasks with or without associated images",
            key="image_filter"
        )
    
    with filter_row2_col3:
        # Sort options
        sort_options = [
            'Dependencies & Priority',
            'Priority (High to Low)',
            'Priority (Low to High)',
            'Created Date (Newest)',
            'Created Date (Oldest)',
            'Status',
            'Title (A-Z)',
            'Title (Z-A)'
        ]
        sort_option = st.selectbox(
            "📊 Sort by:",
            sort_options,
            help="Choose how to sort the tasks",
            key="sort_option"
        )
    
    with filter_row2_col4:
        # Reset filters button
        if st.button("🔄 Reset Filters", help="Clear all filters and search"):
            # Clear all filter states
            for key in ['task_search_query', 'status_filter', 'priority_filter', 'dependency_filter', 
                       'date_filter', 'image_filter', 'sort_option']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    return {
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'dependency_filter': dependency_filter,
        'date_filter': date_filter,
        'image_filter': image_filter,
        'sort_option': sort_option
    }

def apply_advanced_filters(tasks, filters):
    """Apply advanced filters to task list"""
    filtered_tasks = tasks.copy()
    
    # Apply search query
    if filters['search_query'].strip():
        search_results, _ = fuzzy_search_tasks(filtered_tasks, [], filters['search_query'])
        filtered_tasks = search_results
    
    # Apply status filter
    if filters['status_filter'] == 'Active':
        filtered_tasks = [task for task in filtered_tasks if task.get('status') not in ['DONE', 'APPROVED']]
    elif filters['status_filter'] != 'All':
        filtered_tasks = [task for task in filtered_tasks if task.get('status') == filters['status_filter']]
    
    # Apply priority filter
    if filters['priority_filter'] != 'All':
        priority_map = {'🔥 Critical (5)': 5, '🔴 High (4)': 4, '🟡 Normal (3)': 3, '🟢 Low (2)': 2, '⚪ Minimal (1)': 1}
        target_priority = priority_map.get(filters['priority_filter'])
        if target_priority:
            filtered_tasks = [task for task in filtered_tasks if task.get('priority') == target_priority]
    
    # Apply dependency filter
    if filters['dependency_filter'] != 'All':
        if filters['dependency_filter'] == 'No Dependencies':
            filtered_tasks = [task for task in filtered_tasks if not task.get('dependencies')]
        elif filters['dependency_filter'] == 'Has Dependencies':
            filtered_tasks = [task for task in filtered_tasks if task.get('dependencies')]
        elif filters['dependency_filter'] == 'Blocked by Dependencies':
            # This would require checking if dependencies are completed
            # For now, just show tasks with dependencies
            filtered_tasks = [task for task in filtered_tasks if task.get('dependencies')]
    
    # Apply date filter
    if filters['date_filter'] != 'All Time':
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if filters['date_filter'] == 'Last 7 days':
            cutoff = now - timedelta(days=7)
        elif filters['date_filter'] == 'Last 30 days':
            cutoff = now - timedelta(days=30)
        elif filters['date_filter'] == 'Last 90 days':
            cutoff = now - timedelta(days=90)
        else:
            cutoff = None
        
        if cutoff:
            def is_recent(task):
                created_date = task.get('created_date')
                if not created_date:
                    return False
                try:
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    return created_dt.replace(tzinfo=None) >= cutoff
                except:
                    return False
            
            filtered_tasks = [task for task in filtered_tasks if is_recent(task)]
    
    # Apply image filter
    if filters['image_filter'] != 'All':
        if filters['image_filter'] == 'With Images':
            filtered_tasks = [task for task in filtered_tasks if task.get('image') and task.get('image').strip()]
        elif filters['image_filter'] == 'Without Images':
            filtered_tasks = [task for task in filtered_tasks if not (task.get('image') and task.get('image').strip())]
    
    # Apply sorting
    sort_option = filters['sort_option']
    if sort_option == 'Dependencies & Priority':
        filtered_tasks = sort_tasks_by_dependencies_and_priority(filtered_tasks)
    elif sort_option == 'Priority (High to Low)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('priority', 3), reverse=True)
    elif sort_option == 'Priority (Low to High)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('priority', 3))
    elif sort_option == 'Created Date (Newest)':
        def sort_by_date_desc(task):
            created_date = task.get('created_date', '')
            try:
                return datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            except:
                return datetime.min.replace(tzinfo=None)
        filtered_tasks = sorted(filtered_tasks, key=sort_by_date_desc, reverse=True)
    elif sort_option == 'Created Date (Oldest)':
        def sort_by_date_asc(task):
            created_date = task.get('created_date', '')
            try:
                return datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            except:
                return datetime.max.replace(tzinfo=None)
        filtered_tasks = sorted(filtered_tasks, key=sort_by_date_asc)
    elif sort_option == 'Status':
        status_order = {'TODO': 1, 'IN_PROGRESS': 2, 'BLOCKED': 3, 'REVIEW': 4, 'DONE': 5, 'APPROVED': 6}
        filtered_tasks = sorted(filtered_tasks, key=lambda x: status_order.get(x.get('status', 'TODO'), 0))
    elif sort_option == 'Title (A-Z)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('title', '').lower())
    elif sort_option == 'Title (Z-A)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('title', '').lower(), reverse=True)
    
    return filtered_tasks

def main():
    
    tasks = task_utils.get_all_tasks()
    userbrief_requests = get_userbrief_requests()

    if not tasks and not userbrief_requests:
        st.info("No tasks or user requests found.")
        st.write("Checked locations:")
        return

    # Advanced Search & Filtering
    filters = render_advanced_search_and_filters()
    
    # Apply all filters, including search query
    tasks = apply_advanced_filters(tasks, filters)
    
    # Sort tasks
    tasks = sort_tasks_by_dependencies_and_priority(tasks)

    # --- Display Tasks ---
    st.header("Task Details")
    if tasks:
        for task in tasks:
            render_task_card(task)
    else:
        st.info("No tasks match the current filters.")

    # --- Display User Brief Requests ---
    if userbrief_requests:
        st.header("Unprocessed User Requests")
        for request in userbrief_requests:
            render_userbrief_request(request)

if __name__ == "__main__":
    main() 