import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Agent Status", page_icon="🤖")

st.markdown("# 🤖 Agent Status")
st.sidebar.header("Agent Status")

st.markdown("This page shows the current state of the AI agent including its active workflow, memory, and tasks.")

# Helper function to read JSON files safely
def read_json_file(file_path):
    try:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")
        return None

# Helper function to get the latest memory entry
def get_latest_memory():
    # Check multiple possible memory locations
    memory_locations = [
        Path('.cursor/memory-bank/context'),
        Path('.cursor/memory-bank/workflow'),
        Path('.cursor/memory-bank')
    ]
    
    for memory_dir in memory_locations:
        if memory_dir.exists():
            try:
                # Look for memory files (JSON or markdown)
                memory_files = list(memory_dir.glob('*.json')) + list(memory_dir.glob('*.md'))
                if memory_files:
                    # Get the most recent memory file
                    latest_file = max(memory_files, key=os.path.getmtime)
                    if latest_file.suffix == '.json':
                        return read_json_file(latest_file)
                    else:
                        # For markdown files, return basic info
                        return {
                            'file': latest_file.name,
                            'type': 'context',
                            'last_modified': datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        }
            except Exception as e:
                st.error(f"Error accessing memory files in {memory_dir}: {e}")
    
    return None

# Helper function to get current workflow step
def get_current_workflow_step():
    # Check if there's a current step indicator file
    step_file = Path('.cursor/memory-bank/context/current_step.txt')
    if step_file.exists():
        try:
            with open(step_file, 'r') as f:
                return f.read().strip()
        except:
            pass
    
    # Try to get from workflow directory if available
    workflow_dir = Path('.cursor/memory-bank/workflow')
    if workflow_dir.exists():
        # Look for the most recent workflow file
        workflow_files = list(workflow_dir.glob('*.md'))
        if workflow_files:
            latest_file = max(workflow_files, key=os.path.getmtime)
            return latest_file.stem
    
    return "Unknown"

# Helper function to get userbrief status
def get_userbrief_status():
    userbrief_file = Path('.cursor/memory-bank/userbrief.md')
    if userbrief_file.exists():
        try:
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse userbrief entries properly
                lines = content.split('\n')
                active_requests = []
                preferences = []
                total_entries = 0
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Count entries that start with emoji indicators
                        if line.startswith('📌') or line.startswith('🗄️') or line.startswith('🧠'):
                            total_entries += 1
                            # Extract the actual request text after the emoji and dash
                            if ' - ' in line:
                                request_text = line.split(' - ', 1)[1]
                                if '📌' in line:  # Pinned preferences
                                    preferences.append(request_text)
                                elif not request_text.startswith('DONE:') and not request_text.startswith('ARCHIVED:'):
                                    active_requests.append(request_text)
                
                return {
                    'active_requests': active_requests,
                    'preferences': preferences,
                    'total_lines': total_entries
                }
        except Exception as e:
            st.error(f"Error reading userbrief: {e}")
    return None

# Display Current Workflow Step
st.header("📋 Current Workflow Step")
current_step = get_current_workflow_step()
if current_step != "Unknown":
    st.success(f"**Active Step:** {current_step}")
    
    # Try to read the step file content
    step_file_path = Path(f'.cursor/workflow-steps/{current_step}.md')
    if step_file_path.exists():
        with st.expander("View Step Details"):
            try:
                with open(step_file_path, 'r', encoding='utf-8') as f:
                    step_content = f.read()
                    st.markdown(step_content)
            except Exception as e:
                st.error(f"Error reading step file: {e}")
else:
    st.warning("No active workflow step detected")

# Display Memory Status
st.header("🧠 Memory Status")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Working Memory")
    latest_memory = get_latest_memory()
    if latest_memory:
        st.success("✅ Active")
        with st.expander("View Latest Memory"):
            if isinstance(latest_memory, dict):
                for key, value in latest_memory.items():
                    st.write(f"**{key.title()}:** {value}")
            else:
                st.write(latest_memory)
    else:
        st.warning("No recent memory found")

with col2:
    st.subheader("Long-term Memory")
    # Check for semantic search model in multiple locations
    model_locations = [
        Path('.cursor/memory-bank/models'),
        Path('models'),
        Path('.cursor/models')
    ]
    
    model_found = False
    for models_dir in model_locations:
        if models_dir.exists() and any(models_dir.iterdir()):
            # Check if it contains the actual model files
            model_files = list(models_dir.rglob('*'))
            if any('sentence-transformers' in str(f) or 'all-MiniLM' in str(f) for f in model_files):
                st.success("✅ Semantic search enabled")
                st.caption(f"all-MiniLM-L6-v2 model in {models_dir}")
                model_found = True
                break
    
    if not model_found:
        st.warning("⚠️ Semantic search not available")
        st.caption("Model not downloaded - run install.sh to download")

# Display User Requests Status
st.header("📝 User Requests & Preferences")
st.info("ℹ️ User requests and next tasks are now automatically managed by the `next_rule` tool. The system will automatically detect pending requests and guide the workflow to either `task-decomposition` (for new user requests) or `implementation` (for existing tasks).")

userbrief_status = get_userbrief_status()

if userbrief_status:
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric("Total Entries", userbrief_status['total_lines'])
    
    with col4:
        st.metric("Active Requests", len(userbrief_status['active_requests']))
    
    with col5:
        st.metric("User Preferences", len(userbrief_status['preferences']))
    
    if userbrief_status['active_requests']:
        with st.expander("Active Requests (managed by next_rule)"):
            for req in userbrief_status['active_requests'][:3]:  # Show first 3
                st.write(f"• {req[:100]}..." if len(req) > 100 else f"• {req}")
            if len(userbrief_status['active_requests']) > 3:
                st.caption(f"... and {len(userbrief_status['active_requests']) - 3} more")
    
    if userbrief_status['preferences']:
        with st.expander("User Preferences (always included)"):
            for pref in userbrief_status['preferences']:
                st.write(f"📌 {pref[:100]}..." if len(pref) > 100 else f"📌 {pref}")
else:
    st.warning("No userbrief found")

# Display Task Status Summary
st.header("✅ Current Tasks")
tasks = read_json_file('.cursor/streamlit_app/tasks.json')

if tasks:
    # Count tasks by status
    status_counts = {}
    for task in tasks:
        status = task.get('status', 'UNKNOWN')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display metrics
    cols = st.columns(len(status_counts))
    status_colors = {
        'TODO': '🔵',
        'IN_PROGRESS': '🟡', 
        'DONE': '🟢',
        'BLOCKED': '🔴',
        'REVIEW': '🟣'
    }
    
    for i, (status, count) in enumerate(status_counts.items()):
        with cols[i]:
            emoji = status_colors.get(status, '⚪')
            st.metric(f"{emoji} {status}", count)
    
    # Show current task if any
    current_tasks = [t for t in tasks if t.get('status') == 'IN_PROGRESS']
    if current_tasks:
        st.subheader("🎯 Active Task")
        for task in current_tasks[:1]:  # Show first active task
            st.info(f"**{task.get('title', 'Untitled')}**\n\n{task.get('description', 'No description')}")
else:
    st.warning("No tasks found")

# System Status section removed as requested

# Auto-refresh option
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
if auto_refresh:
    st.sidebar.caption("Page will refresh automatically")
    # Add JavaScript for auto-refresh
    st.markdown("""
    <script>
    setTimeout(function(){
        window.location.reload(1);
    }, 30000);
    </script>
    """, unsafe_allow_html=True)

# Last updated timestamp
st.sidebar.markdown("---")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}") 