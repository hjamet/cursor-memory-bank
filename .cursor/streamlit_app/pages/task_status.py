import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import requests

st.set_page_config(page_title="Task Status", page_icon="✅")

st.markdown("# ✅ Task Status")
st.sidebar.header("Task Status")

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
                # Update fields
                for key, value in kwargs.items():
                    task[key] = value
                task['updated_date'] = datetime.now().isoformat()
                
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
    """Render a task card with optional inline editing"""
    task_id = task.get('id', task.get('task_id', 'N/A'))
    title = task.get('title', 'Untitled')
    short_desc = task.get('short_description', task.get('description', 'No description'))
    status = task.get('status', 'TODO')
    priority = task.get('priority', 3)
    dependencies = task.get('dependencies', [])
    
    # Priority emoji mapping
    priority_emojis = {5: "🔥", 4: "🔴", 3: "🟡", 2: "🟢", 1: "⚪"}
    priority_emoji = priority_emojis.get(priority, "📝")
    
    # Status emoji mapping
    status_emojis = {
        'TODO': '⏳',
        'IN_PROGRESS': '🔄', 
        'BLOCKED': '🚫',
        'REVIEW': '👀',
        'DONE': '✅'
    }
    status_emoji = status_emojis.get(status, '📝')
    
    # Task header
    st.markdown(f"### {status_emoji} #{task_id} - {title}")
    st.write(f"📝 {short_desc}")
    
    # Task details and inline editing
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Dependencies info
        if dependencies:
            dep_str = ', '.join([f"#{dep}" for dep in dependencies])
            st.caption(f"⚠️ **Depends on:** {dep_str}")
        else:
            st.caption("✅ **No dependencies**")
    
    with col2:
        # Priority display/edit
        if show_inline_edit:
            priority_options = {
                1: "⚪ Minimal (1)",
                2: "🟢 Low (2)", 
                3: "🟡 Normal (3)",
                4: "🔴 High (4)",
                5: "🔥 Critical (5)"
            }
            new_priority = st.selectbox(
                "Priority:",
                [1, 2, 3, 4, 5],
                index=[1, 2, 3, 4, 5].index(priority),
                format_func=lambda x: priority_options[x],
                key=f"priority_{task_id}",
                label_visibility="collapsed"
            )
            
            if new_priority != priority:
                if update_task_via_mcp(task_id, priority=new_priority):
                    st.success(f"Priority updated!")
                    st.rerun()
        else:
            st.write(f"{priority_emoji} **P{priority}**")
    
    with col3:
        # Status display/edit
        if show_inline_edit:
            status_options = {
                'TODO': '⏳ To Do',
                'IN_PROGRESS': '🔄 In Progress',
                'BLOCKED': '🚫 Blocked',
                'REVIEW': '👀 Review',
                'DONE': '✅ Done'
            }
            new_status = st.selectbox(
                "Status:",
                ['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW', 'DONE'],
                index=['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW', 'DONE'].index(status),
                format_func=lambda x: status_options[x],
                key=f"status_{task_id}",
                label_visibility="collapsed"
            )
            
            if new_status != status:
                if update_task_via_mcp(task_id, status=new_status):
                    st.success(f"Status updated!")
                    st.rerun()
        else:
            st.write(f"{status_emoji} **{status}**")
    
    # Action buttons for inline editing
    if show_inline_edit:
        st.markdown("**⚡ Actions:**")
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button(f"📋 Details", key=f"details_{task_id}"):
                # Show detailed description in expander
                detailed_desc = task.get('detailed_description', 'No detailed description available')
                with st.expander(f"📋 Task #{task_id} Details", expanded=True):
                    st.write(detailed_desc)
        
        with action_col2:
            if status != 'DONE':
                if st.button(f"✅ Complete", key=f"complete_{task_id}", type="primary"):
                    if update_task_via_mcp(task_id, status='DONE'):
                        st.success(f"Task #{task_id} completed!")
                        st.rerun()
        
        with action_col3:
            if st.button(f"🗑️ Delete", key=f"delete_{task_id}"):
                # Confirmation dialog
                if f"confirm_delete_{task_id}" not in st.session_state:
                    st.session_state[f"confirm_delete_{task_id}"] = True
                    st.warning(f"⚠️ Click again to confirm deletion of Task #{task_id}")
                else:
                    if delete_task_via_mcp(task_id):
                        st.success(f"Task #{task_id} deleted!")
                        del st.session_state[f"confirm_delete_{task_id}"]
                        st.rerun()
    
    st.markdown("---")

def render_userbrief_request(request):
    """Render a userbrief request card"""
    req_id = request.get('id', 'N/A')
    content = request.get('content', 'No content')
    status = request.get('status', 'new')
    created_at = request.get('created_at', '')[:10] if request.get('created_at') else 'Unknown'
    
    # Truncate content if too long
    display_content = content[:200] + "..." if len(content) > 200 else content
    
    st.markdown(f"### 📋 Request #{req_id}")
    st.write(f"📝 {display_content}")
    st.caption(f"📅 **Created:** {created_at} | 🏷️ **Status:** {status}")
    
    if len(content) > 200:
        with st.expander("📖 Full Content"):
            st.write(content)
    
    st.markdown("---")

# Main interface
st.markdown("## 🎯 Agent Workflow Overview")
st.info("📊 Complete view of the agent's work pipeline from requests to completion")

# Load tasks and userbrief data
tasks_file = get_tasks_file()
tasks = []

if tasks_file:
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            tasks = data
        else:
            tasks = data.get('tasks', [])
            
    except Exception as e:
        st.error(f"Error reading tasks: {e}")

userbrief_requests = get_userbrief_requests()

# Quick stats - Focus on remaining work only
if tasks or userbrief_requests:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unprocessed_count = len(userbrief_requests)
        st.metric("📋 Stage 0: Requests", unprocessed_count)
    
    with col2:
        todo_count = len([t for t in tasks if t.get('status') == 'TODO'])
        st.metric("⏳ Stage 1: Todo", todo_count)
    
    with col3:
        in_progress_count = len([t for t in tasks if t.get('status') == 'IN_PROGRESS'])
        st.metric("🔄 Stage 2: In Progress", in_progress_count)

# Add priority distribution visualization for remaining tasks
remaining_tasks = [t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW']]
if remaining_tasks:
    st.markdown("### 📊 Priority Distribution (Remaining Tasks)")
    
    # Calculate priority distribution
    priority_counts = {}
    for task in remaining_tasks:
        priority = task.get('priority', 3)
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Display as columns with emoji indicators
    priority_cols = st.columns(5)
    priority_emojis = {5: "🔥", 4: "🔴", 3: "🟡", 2: "🟢", 1: "⚪"}
    
    for i, priority in enumerate([5, 4, 3, 2, 1]):
        with priority_cols[i]:
            count = priority_counts.get(priority, 0)
            emoji = priority_emojis.get(priority, "📝")
            st.metric(f"{emoji} P{priority}", count)

st.markdown("---")

# SECTION 1: CURRENT TASK (IN_PROGRESS) - Always visible at top
current_tasks = [t for t in tasks if t.get('status') == 'IN_PROGRESS']
if current_tasks:
    st.markdown("## 🔄 Current Task (In Progress)")
    st.success("🎯 This is what the agent is currently working on")
    
    # Sort current tasks by priority
    current_tasks.sort(key=lambda x: x.get('priority', 3), reverse=True)
    
    for task in current_tasks:
        render_task_card(task, show_inline_edit=True)
else:
    st.markdown("## 🔄 Current Task")
    st.info("✨ No task currently in progress - agent is ready for new work!")

# SECTION 2: TODO TASKS - Open by default, sorted by dependencies then priority
todo_tasks = [t for t in tasks if t.get('status') == 'TODO']
if todo_tasks:
    st.markdown("## ⏳ Todo Tasks (Ready to Start)")
    st.caption("📋 Tasks ready for implementation, sorted by dependencies and priority")
    
    # Sort by dependencies and priority
    sorted_todo = sort_tasks_by_dependencies_and_priority(todo_tasks)
    
    for task in sorted_todo:
        render_task_card(task, show_inline_edit=True)
else:
    st.markdown("## ⏳ Todo Tasks")
    st.info("🎉 No pending tasks - all work is either in progress or completed!")

# SECTION 3: UNPROCESSED USERBRIEF REQUESTS - Open by default
if userbrief_requests:
    st.markdown("## 📋 Stage 0: Unprocessed Requests")
    st.caption("🔄 User requests waiting to be decomposed into tasks")
    
    for request in userbrief_requests:
        render_userbrief_request(request)
else:
    st.markdown("## 📋 Stage 0: Unprocessed Requests")
    st.info("📭 No unprocessed requests - all user requests have been converted to tasks!")

# SECTION 4: ARCHIVED/COMPLETED TASKS - Collapsed by default, limited selection
done_tasks = [t for t in tasks if t.get('status') == 'DONE']
if done_tasks:
    # Sort by updated date (most recent first) and show only last 10
    done_tasks.sort(key=lambda x: x.get('updated_date', ''), reverse=True)
    recent_done = done_tasks[:10]
    
    with st.expander(f"✅ Recently Completed Tasks ({len(recent_done)}/{len(done_tasks)})", expanded=False):
        st.caption("🎉 Recently completed tasks (showing last 10)")
        
        for task in recent_done:
            render_task_card(task, show_inline_edit=False)
        
        if len(done_tasks) > 10:
            st.info(f"📊 {len(done_tasks) - 10} more completed tasks not shown")

# OTHER STATUS TASKS (BLOCKED, REVIEW) - If any exist
blocked_tasks = [t for t in tasks if t.get('status') == 'BLOCKED']
review_tasks = [t for t in tasks if t.get('status') == 'REVIEW']

if blocked_tasks:
    with st.expander(f"🚫 Blocked Tasks ({len(blocked_tasks)})", expanded=True):
        st.caption("⛔ Tasks waiting on dependencies or external factors")
        for task in blocked_tasks:
            render_task_card(task, show_inline_edit=True)

if review_tasks:
    with st.expander(f"👀 Tasks in Review ({len(review_tasks)})", expanded=True):
        st.caption("🔍 Tasks awaiting review or testing")
        for task in review_tasks:
            render_task_card(task, show_inline_edit=True)

# Sidebar controls
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Controls")

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

# Quick stats in sidebar
if tasks:
    st.sidebar.markdown("### 📊 Quick Stats")
    
    # Calculate completion rate
    completed = len([t for t in tasks if t.get('status') == 'DONE'])
    total = len(tasks)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    st.sidebar.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Priority distribution of active tasks
    active_tasks = [t for t in tasks if t.get('status') in ['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW']]
    if active_tasks:
        priority_counts = {}
        for task in active_tasks:
            priority = task.get('priority', 3)
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        st.sidebar.markdown("**Priority Distribution:**")
        for priority in sorted(priority_counts.keys(), reverse=True):
            count = priority_counts[priority]
            emoji = {5: "🔥", 4: "🔴", 3: "🟡", 2: "🟢", 1: "⚪"}.get(priority, "📝")
            st.sidebar.write(f"{emoji} P{priority}: {count}")

# Help section
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Help")
st.sidebar.info("""
**Workflow Stages:**
- 📋 Stage 0: User requests not yet decomposed
- ⏳ Stage 1: Tasks ready to start
- 🔄 Stage 2: Tasks in progress
- ✅ Stage 3: Completed tasks

**Inline Editing:**
- Change priority and status directly
- Click Details to see full description
- Use Complete button for quick completion
- Delete with confirmation
""")

if not tasks and not userbrief_requests:
    st.markdown("---")
    st.info("🚀 **Getting Started:** Tasks and requests will appear here once the agent begins processing your requests through the workflow system.") 