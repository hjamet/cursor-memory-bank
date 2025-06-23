import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict, Optional

st.set_page_config(page_title="To Review", page_icon="🔍")

st.markdown("# 🔍 To Review")
st.sidebar.header("To Review")

st.markdown("This page displays tasks that are ready for review and validation. You can approve or reject tasks, and rejections will automatically create new userbrief requests for corrections.")

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
    
    with st.container():
        st.markdown(f"### {priority_icon} Task #{task_id}: {title}")
        
        # Task details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Status:** {status}")
            st.markdown(f"**Priority:** {priority}/5")
            
            short_desc = task.get('short_description', '')
            if short_desc:
                st.markdown(f"**Description:** {short_desc}")
            
            detailed_desc = task.get('detailed_description', '')
            if detailed_desc:
                with st.expander("📋 Detailed Specifications"):
                    st.markdown(detailed_desc)
            
            validation_criteria = task.get('validation_criteria', '')
            if validation_criteria:
                with st.expander("✅ Validation Criteria"):
                    st.markdown(validation_criteria)
            
            impacted_files = task.get('impacted_files', [])
            if impacted_files:
                with st.expander("📁 Impacted Files"):
                    for file in impacted_files:
                        st.markdown(f"- `{file}`")
        
        with col2:
            st.markdown("**Review Actions:**")
            
            # Approve button
            if st.button(f"✅ Approve Task #{task_id}", key=f"approve_{task_id}", type="primary"):
                validation_data = {
                    "approved_at": datetime.now().isoformat(),
                    "approved_by": "streamlit_reviewer",
                    "review_notes": "Task approved via Streamlit To Review page"
                }
                
                if update_task_status(task_id, "APPROVED", validation_data):
                    st.success(f"✅ Task #{task_id} has been approved!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to approve task #{task_id}")
            
            # Reject button
            if st.button(f"❌ Reject Task #{task_id}", key=f"reject_{task_id}", type="secondary"):
                # Show rejection form
                with st.form(f"reject_form_{task_id}"):
                    st.markdown("**Rejection Reason:**")
                    rejection_reason = st.text_area(
                        "Explain why this task is being rejected and what needs to be corrected:",
                        key=f"rejection_reason_{task_id}",
                        height=100,
                        placeholder="Example: The implementation doesn't meet the validation criteria because..."
                    )
                    
                    col_cancel, col_confirm = st.columns(2)
                    with col_cancel:
                        cancel_rejection = st.form_submit_button("Cancel", type="secondary")
                    with col_confirm:
                        confirm_rejection = st.form_submit_button("Confirm Rejection", type="primary")
                    
                    if confirm_rejection and rejection_reason.strip():
                        # Update task status to REJECTED
                        validation_data = {
                            "rejected_at": datetime.now().isoformat(),
                            "rejected_by": "streamlit_reviewer",
                            "rejection_reason": rejection_reason.strip(),
                            "review_notes": "Task rejected via Streamlit To Review page"
                        }
                        
                        # Create userbrief request for correction
                        correction_request = f"Corriger la tâche #{task_id} '{title}' qui a été rejetée.\n\nRaison du rejet:\n{rejection_reason.strip()}\n\nSpécifications originales:\n{detailed_desc}\n\nCritères de validation:\n{validation_criteria}"
                        
                        task_updated = update_task_status(task_id, "REJECTED", validation_data)
                        request_created = create_userbrief_request(correction_request)
                        
                        if task_updated and request_created:
                            st.success(f"❌ Task #{task_id} has been rejected and a correction request has been created!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to reject task #{task_id} or create correction request")
                    
                    elif confirm_rejection and not rejection_reason.strip():
                        st.error("Please provide a rejection reason.")
        
        st.markdown("---")

# Main page content
def main():
    # Load tasks
    tasks = load_tasks()
    
    if not tasks:
        st.warning("No tasks found. Make sure the tasks file exists and contains data.")
        return
    
    # Filter tasks with DONE status (ready for validation)
    review_tasks = [task for task in tasks if task.get('status') == 'DONE']
    
    if not review_tasks:
        st.info("🎉 No tasks currently need review! All tasks are either completed, in progress, or waiting in the queue.")
        
        # Show summary of task statuses
        status_counts = {}
        for task in tasks:
            status = task.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.markdown("### 📊 Current Task Status Summary:")
        for status, count in sorted(status_counts.items()):
            st.markdown(f"- **{status}**: {count} tasks")
        
        return
    
    # Show review tasks
    st.markdown(f"### 📋 Tasks Ready for Review ({len(review_tasks)})")
    st.markdown("Review the tasks below and approve or reject them based on the validation criteria.")
    
    # Sort tasks by priority (highest first) and then by ID
    review_tasks.sort(key=lambda x: (-x.get('priority', 3), x.get('id', x.get('task_id', 0))))
    
    for task in review_tasks:
        render_task_review_card(task)

if __name__ == "__main__":
    main() 