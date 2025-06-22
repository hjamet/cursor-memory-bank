import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Task Status", page_icon="✅")

st.markdown("# ✅ Task Status")
st.sidebar.header("Task Status")

# Helper functions for task management
def update_task_status(task_id, new_status):
    """Update a task's status in the tasks file"""
    # Check multiple possible task file locations
    task_locations = [
        Path('.cursor/memory-bank/tasks.json'),
        Path('.cursor/streamlit_app/tasks.json'),
        Path('tasks.json')
    ]
    
    for tasks_file in task_locations:
        if tasks_file.exists():
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
                        task['updated_at'] = datetime.now().isoformat()
                        
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
    
    st.error("Tasks file not found")
    return False

def delete_task(task_id):
    """Delete a task from the tasks file"""
    # Check multiple possible task file locations
    task_locations = [
        Path('.cursor/memory-bank/tasks.json'),
        Path('.cursor/streamlit_app/tasks.json'),
        Path('tasks.json')
    ]
    
    for tasks_file in task_locations:
        if tasks_file.exists():
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
    
    st.error("Tasks file not found")
    return False

# Path to tasks file (check multiple possible locations)
possible_paths = [
    Path('.cursor/memory-bank/tasks.json'),
    Path('.cursor/streamlit_app/tasks.json'),
    Path('tasks.json')
]

tasks_file = None
for path in possible_paths:
    if path.exists():
        tasks_file = path
        break

if tasks_file and tasks_file.exists():
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            tasks = data
        else:
            tasks = data.get('tasks', [])
        
        if tasks:
            st.header(f"📋 Current Tasks ({len(tasks)} total)")
            
            # Count tasks by status
            status_counts = {}
            for task in tasks:
                status = task.get('status', 'TODO')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Display status metrics
            if status_counts:
                cols = st.columns(len(status_counts))
                for i, (status, count) in enumerate(status_counts.items()):
                    with cols[i]:
                        # Use appropriate emoji for status
                        emoji = {
                            'TODO': '⏳',
                            'IN_PROGRESS': '🔄',
                            'DONE': '✅',
                            'BLOCKED': '🚫',
                            'REVIEW': '👀'
                        }.get(status, '📝')
                        st.metric(f"{emoji} {status}", count)
            
            st.markdown("---")
            
            # Display tasks grouped by status
            for status in ['TODO', 'IN_PROGRESS', 'REVIEW', 'BLOCKED', 'DONE']:
                status_tasks = [t for t in tasks if t.get('status') == status]
                if status_tasks:
                    emoji = {
                        'TODO': '⏳',
                        'IN_PROGRESS': '🔄',
                        'DONE': '✅',
                        'BLOCKED': '🚫',
                        'REVIEW': '👀'
                    }.get(status, '📝')
                    
                    st.subheader(f"{emoji} {status} ({len(status_tasks)})")
                    
                    for task in status_tasks:
                        # Task card with accordion
                        task_id = task.get('id', task.get('task_id', 'N/A'))
                        title = task.get('title', 'Untitled')
                        short_desc = task.get('short_description', task.get('description', 'No description'))
                        priority = task.get('priority', 3)
                        
                        # Priority indicator
                        priority_emoji = '🔴' if priority >= 4 else '🟡' if priority == 3 else '🟢'
                        
                        # Display task title and short description
                        st.markdown(f"### {title} {priority_emoji}")
                        st.markdown(f"**#{task_id}** - {short_desc}")
                        
                        # Create accordion for detailed information
                        with st.expander(f"Details for #{task_id}", expanded=False):
                            # Skip short description since it's shown above
                            
                            # Create columns for better layout
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Detailed description
                                detailed_desc = task.get('detailed_description', task.get('long_description'))
                                if detailed_desc:
                                    st.markdown("**📋 Detailed Description:**")
                                    st.markdown(detailed_desc)
                                
                                # Validation criteria
                                validation = task.get('validation_criteria', task.get('acceptance_criteria'))
                                if validation:
                                    st.markdown("**✅ Validation Criteria:**")
                                    st.markdown(validation)
                            
                            with col2:
                                # Task metadata
                                st.markdown("**📊 Task Info:**")
                                st.write(f"**ID:** #{task_id}")
                                st.write(f"**Status:** {status}")
                                st.write(f"**Priority:** {priority_emoji} {priority}")
                                
                                # Dependencies
                                dependencies = task.get('dependencies', [])
                                if dependencies:
                                    st.write(f"**Dependencies:** #{', #'.join(map(str, dependencies))}")
                                
                                # Parent task
                                parent_id = task.get('parent_id')
                                if parent_id:
                                    st.write(f"**Parent:** #{parent_id}")
                                
                                # Timestamps
                                created_at = task.get('created_at')
                                if created_at:
                                    # Format date nicely
                                    date_str = created_at[:10] if len(created_at) > 10 else created_at
                                    st.write(f"**Created:** {date_str}")
                                
                                updated_at = task.get('updated_at')
                                if updated_at:
                                    date_str = updated_at[:10] if len(updated_at) > 10 else updated_at
                                    st.write(f"**Updated:** {date_str}")
                            
                            # Impacted files (full width)
                            impacted_files = task.get('impacted_files', [])
                            if impacted_files:
                                st.markdown("**📁 Impacted Files:**")
                                for file in impacted_files:
                                    st.code(file, language=None)
                            
                            # Action buttons
                            st.markdown("---")
                            button_col1, button_col2, button_col3, button_col4 = st.columns(4)
                            
                            with button_col1:
                                if st.button(f"⏳ TODO", key=f"todo_{task_id}", help="Reset to TODO"):
                                    # Update task status to TODO
                                    if update_task_status(task_id, "TODO"):
                                        st.success(f"Task #{task_id} reset to TODO!")
                                        st.rerun()
                            
                            with button_col2:
                                if st.button(f"🔄 In Progress", key=f"progress_{task_id}", help="Mark as In Progress"):
                                    if update_task_status(task_id, "IN_PROGRESS"):
                                        st.info(f"Task #{task_id} marked as In Progress!")
                                        st.rerun()
                            
                            with button_col3:
                                if st.button(f"✅ Complete", key=f"complete_{task_id}", help="Mark as Done"):
                                    if update_task_status(task_id, "DONE"):
                                        st.success(f"Task #{task_id} marked as Complete!")
                                        st.rerun()
                            
                            with button_col4:
                                if st.button(f"🗑️ Delete", key=f"delete_{task_id}", help="Delete this task"):
                                    if delete_task(task_id):
                                        st.success(f"Task #{task_id} deleted!")
                                        st.rerun()
        else:
            st.info("No tasks found in the system.")
            st.markdown("Tasks will appear here once they are created through the workflow system.")
            
    except json.JSONDecodeError:
        st.error(f"Error: Invalid JSON in tasks file: {tasks_file}")
    except Exception as e:
        st.error(f"Error reading tasks: {e}")
else:
    st.warning("No tasks file found. Tasks will appear here once created.")
    st.info("💡 Tasks are automatically created when the agent processes requests through the task-decomposition workflow step.")
    st.markdown("**Checked locations:**")
    for path in possible_paths:
        st.code(str(path))

# Sidebar controls
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Controls")

if st.sidebar.button("🔄 Refresh Tasks"):
    st.rerun()

auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Task statistics in sidebar
if tasks_file and tasks_file.exists():
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            tasks = data
        else:
            tasks = data.get('tasks', [])
        
        if tasks:
            st.sidebar.markdown("### 📊 Quick Stats")
            
            # Calculate completion rate
            completed = len([t for t in tasks if t.get('status') == 'DONE'])
            total = len(tasks)
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            st.sidebar.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            # Average priority
            priorities = [t.get('priority', 3) for t in tasks]
            avg_priority = sum(priorities) / len(priorities) if priorities else 0
            st.sidebar.metric("Avg Priority", f"{avg_priority:.1f}")
            
            # Tasks with dependencies
            with_deps = len([t for t in tasks if t.get('dependencies')])
            st.sidebar.metric("With Dependencies", with_deps)
            
    except:
        pass

# Help section in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Help")
st.sidebar.info("Click on any task to expand and see full details. Use the action buttons to manage task status and lifecycle.") 