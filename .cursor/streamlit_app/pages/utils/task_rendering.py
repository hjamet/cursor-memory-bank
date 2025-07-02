"""
Task and request rendering utilities.
Handles the display of task cards and userbrief request cards with interactive elements.
"""

import streamlit as st
import os
from datetime import datetime
import task_crud_operations
import userbrief_operations
import uuid

# Import specific functions
update_task_via_mcp = task_crud_operations.update_task_via_mcp
delete_task_via_mcp = task_crud_operations.delete_task_via_mcp
update_user_request = userbrief_operations.update_user_request
delete_user_request = userbrief_operations.delete_user_request


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
    
    # Generate a unique identifier to prevent Streamlit key collisions
    # This ensures that even if req_id is duplicated or 'N/A', each component has a unique key
    unique_id = f"{req_id}_{uuid.uuid4().hex[:8]}"
    
    # Initialize session state for editing
    edit_key = f"edit_request_{unique_id}"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    with st.container(border=True):
        st.markdown(f"#### 📋 Request #{req_id}")
        st.caption(f"📅 **Created:** {created_at} | 🏷️ **Status:** {status}")

        if st.session_state[edit_key]:
            # --- EDITING MODE ---
            with st.form(key=f"edit_form_{unique_id}"):
                new_content = st.text_area("Edit request content:", value=content, height=150, key=f"text_{unique_id}")
                
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
                if st.button("✏️ Edit", key=f"start_edit_{unique_id}", help="Edit this request"):
                    st.session_state[edit_key] = True
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{unique_id}", help="Delete this request"):
                    if delete_user_request(req_id):
                        st.toast(f"Request #{req_id} deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete request.")
    
    st.markdown("---") 