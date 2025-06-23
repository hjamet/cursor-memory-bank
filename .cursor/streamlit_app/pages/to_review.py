import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

st.set_page_config(page_title="To Review", page_icon="🔍")

st.markdown("# 🔍 To Review")
st.sidebar.header("To Review")

# Helper functions for task management
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

def update_task_status(task_id: int, new_status: str, user_comment: str = "") -> bool:
    """Update task status with validation info"""
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
                
                # Add validation info
                if 'validation' not in task:
                    task['validation'] = {}
                
                if new_status == 'APPROVED':
                    task['validation']['approved_at'] = datetime.now().isoformat()
                    task['validation']['approved_by'] = 'user'
                    if user_comment:
                        task['validation']['user_comment'] = user_comment
                elif new_status == 'TODO':
                    task['validation']['rejected_at'] = datetime.now().isoformat()
                    task['validation']['rejected_by'] = 'user'
                    if user_comment:
                        task['validation']['rejection_reason'] = user_comment
                
                # Save validation history
                if 'validation_history' not in task['validation']:
                    task['validation']['validation_history'] = []
                
                task['validation']['validation_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'approved' if new_status == 'APPROVED' else 'rejected',
                    'comment': user_comment
                })
                
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
    """Create a new userbrief request for rejected tasks"""
    userbrief_file = Path('.cursor/memory-bank/workflow/userbrief.json')
    
    try:
        # Load existing userbrief data
        if userbrief_file.exists():
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "version": "1.0.0",
                "last_id": 0,
                "requests": []
            }
        
        # Create new request
        new_id = data.get('last_id', 0) + 1
        new_request = {
            "id": new_id,
            "content": content,
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "history": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "created",
                    "comment": "Request created from task rejection in To Review page"
                }
            ]
        }
        
        # Add to requests and update last_id
        data['requests'].append(new_request)
        data['last_id'] = new_id
        
        # Save back to file
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        st.error(f"Error creating userbrief request: {e}")
        return False

def render_task_for_review(task: Dict):
    """Render a task card for review with approve/reject buttons"""
    task_id = task.get('id', task.get('task_id'))
    title = task.get('title', 'Untitled Task')
    short_desc = task.get('short_description', '')
    detailed_desc = task.get('detailed_description', '')
    validation_criteria = task.get('validation_criteria', '')
    priority = task.get('priority', 3)
    created_date = task.get('created_date', '')
    updated_date = task.get('updated_date', '')
    impacted_files = task.get('impacted_files', [])
    
    # Format dates
    try:
        if created_date:
            created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            created_str = created_dt.strftime('%Y-%m-%d %H:%M')
        else:
            created_str = 'Unknown'
            
        if updated_date:
            updated_dt = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
            updated_str = updated_dt.strftime('%Y-%m-%d %H:%M')
        else:
            updated_str = 'Unknown'
    except:
        created_str = created_date[:19] if created_date else 'Unknown'
        updated_str = updated_date[:19] if updated_date else 'Unknown'
    
    # Priority color
    priority_colors = {1: "🔵", 2: "🟢", 3: "🟡", 4: "🟠", 5: "🔴"}
    priority_color = priority_colors.get(priority, "⚪")
    
    with st.container():
        st.markdown(f"### {priority_color} Task #{task_id}: {title}")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Priority:** {priority} | **Created:** {created_str} | **Completed:** {updated_str}")
            
            if short_desc:
                st.markdown(f"**Summary:** {short_desc}")
            
            # Show task details in expander
            with st.expander("📋 Task Details", expanded=False):
                if detailed_desc:
                    st.markdown("**Detailed Description:**")
                    st.markdown(detailed_desc)
                
                if validation_criteria:
                    st.markdown("**Validation Criteria:**")
                    st.markdown(validation_criteria)
                
                if impacted_files:
                    st.markdown("**Impacted Files:**")
                    for file in impacted_files:
                        st.markdown(f"- `{file}`")
        
        with col2:
            st.markdown("**Actions:**")
            
            # Approve button
            if st.button("✅ Approve", key=f"approve_{task_id}", type="primary"):
                comment = st.session_state.get(f"comment_{task_id}", "")
                if update_task_status(task_id, 'APPROVED', comment):
                    st.success(f"✅ Task #{task_id} approved!")
                    st.rerun()
                else:
                    st.error("Failed to approve task")
            
            # Reject button
            if st.button("❌ Reject", key=f"reject_{task_id}", type="secondary"):
                st.session_state[f"show_reject_form_{task_id}"] = True
            
            # Comment area (always visible)
            comment = st.text_area(
                "Comment (optional):",
                key=f"comment_{task_id}",
                height=80,
                placeholder="Add feedback or notes about this task..."
            )
        
        # Reject form popup
        if st.session_state.get(f"show_reject_form_{task_id}", False):
            st.markdown("---")
            st.markdown("### ❌ Reject Task")
            st.warning("You are about to reject this task. Please provide feedback to help improve future implementations.")
            
            rejection_reason = st.text_area(
                "Why are you rejecting this task? (optional but recommended)",
                key=f"rejection_reason_{task_id}",
                height=100,
                placeholder="Explain what needs to be fixed or improved..."
            )
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("🚫 Confirm Rejection", key=f"confirm_reject_{task_id}", type="primary"):
                    # Create rejection message
                    rejection_content = f"Task #{task_id} '{title}' was rejected by the user."
                    if rejection_reason:
                        rejection_content += f"\n\nUser feedback: {rejection_reason}"
                    rejection_content += f"\n\nPlease review this task implementation carefully, test the functionality, and ensure it meets the requirements. Check the validation criteria and verify all impacted files have been correctly modified."
                    
                    # Update task status to TODO and create userbrief request
                    success1 = update_task_status(task_id, 'TODO', rejection_reason)
                    success2 = create_userbrief_request(rejection_content)
                    
                    if success1 and success2:
                        st.success(f"✅ Task #{task_id} rejected and new request created for re-implementation!")
                        st.session_state[f"show_reject_form_{task_id}"] = False
                        st.rerun()
                    else:
                        st.error("Failed to reject task or create new request")
            
            with col_cancel:
                if st.button("↩️ Cancel", key=f"cancel_reject_{task_id}"):
                    st.session_state[f"show_reject_form_{task_id}"] = False
                    st.rerun()
        
        st.markdown("---")

# Main page content
def main():
    # Load tasks
    tasks = load_tasks()
    
    if not tasks:
        st.warning("No tasks file found. Please ensure the task management system is properly set up.")
        return
    
    # Filter tasks that are DONE (ready for review)
    done_tasks = [task for task in tasks if task.get('status') == 'DONE']
    approved_tasks = [task for task in tasks if task.get('status') == 'APPROVED']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Tasks Pending Review", len(done_tasks))
    
    with col2:
        st.metric("✅ Tasks Approved", len(approved_tasks))
    
    with col3:
        total_completed = len(done_tasks) + len(approved_tasks)
        st.metric("🎯 Total Completed", total_completed)
    
    with col4:
        if total_completed > 0:
            approval_rate = (len(approved_tasks) / total_completed) * 100
            st.metric("📊 Approval Rate", f"{approval_rate:.1f}%")
        else:
            st.metric("📊 Approval Rate", "N/A")
    
    # Main content
    if not done_tasks:
        st.info("🎉 No tasks pending review! All completed tasks have been validated.")
        
        if approved_tasks:
            st.markdown("### ✅ Recently Approved Tasks")
            # Show last 5 approved tasks
            recent_approved = sorted(approved_tasks, 
                                   key=lambda x: x.get('updated_date', ''), 
                                   reverse=True)[:5]
            
            for task in recent_approved:
                task_id = task.get('id', task.get('task_id'))
                title = task.get('title', 'Untitled Task')
                approved_at = task.get('validation', {}).get('approved_at', '')
                user_comment = task.get('validation', {}).get('user_comment', '')
                
                try:
                    if approved_at:
                        approved_dt = datetime.fromisoformat(approved_at.replace('Z', '+00:00'))
                        approved_str = approved_dt.strftime('%Y-%m-%d %H:%M')
                    else:
                        approved_str = 'Unknown'
                except:
                    approved_str = approved_at[:19] if approved_at else 'Unknown'
                
                with st.expander(f"✅ Task #{task_id}: {title} (Approved {approved_str})"):
                    st.markdown(task.get('short_description', ''))
                    if user_comment:
                        st.markdown(f"**User Comment:** {user_comment}")
        
        return
    
    # Sort tasks by priority (highest first) and then by completion date
    done_tasks.sort(key=lambda x: (-x.get('priority', 3), x.get('updated_date', '')))
    
    st.markdown("### 📋 Tasks Ready for Review")
    st.markdown(f"Found **{len(done_tasks)}** completed tasks awaiting your validation.")
    
    # Filter options
    with st.expander("🔍 Filter Options", expanded=False):
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            priority_filter = st.selectbox(
                "Filter by Priority:",
                options=["All", "5 (Critical)", "4 (High)", "3 (Normal)", "2 (Low)", "1 (Very Low)"],
                index=0
            )
        
        with col_filter2:
            sort_option = st.selectbox(
                "Sort by:",
                options=["Priority (High to Low)", "Completion Date (Recent First)", "Completion Date (Oldest First)"],
                index=0
            )
    
    # Apply filters
    filtered_tasks = done_tasks.copy()
    
    if priority_filter != "All":
        priority_num = int(priority_filter.split()[0])
        filtered_tasks = [task for task in filtered_tasks if task.get('priority', 3) == priority_num]
    
    # Apply sorting
    if sort_option == "Priority (High to Low)":
        filtered_tasks.sort(key=lambda x: (-x.get('priority', 3), x.get('updated_date', '')))
    elif sort_option == "Completion Date (Recent First)":
        filtered_tasks.sort(key=lambda x: x.get('updated_date', ''), reverse=True)
    elif sort_option == "Completion Date (Oldest First)":
        filtered_tasks.sort(key=lambda x: x.get('updated_date', ''))
    
    if not filtered_tasks:
        st.info("No tasks match the current filter criteria.")
        return
    
    st.markdown(f"Showing **{len(filtered_tasks)}** tasks:")
    
    # Render tasks for review
    for task in filtered_tasks:
        render_task_for_review(task)

# Auto-refresh option in sidebar
st.sidebar.markdown("### ⚙️ Settings")

if st.sidebar.checkbox("🔄 Auto-refresh (10s)", value=False):
    import time
    time.sleep(10)
    st.rerun()

# Run main function
if __name__ == "__main__":
    main() 