import streamlit as st
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Add Request", page_icon="➕")

st.markdown("# ➕ Add New Request")
st.sidebar.header("Add Request")

st.markdown("Use this page to add new requests to the userbrief. These requests will be automatically processed by the agent's workflow system.")

# Helper function to add request to userbrief
def add_request_to_userbrief(request_text, is_preference=False):
    userbrief_file = Path('.cursor/memory-bank/userbrief.md')
    
    try:
        # Determine emoji based on request type
        emoji = "📌" if is_preference else "🗄️"
        
        # Format the new entry (TODO mode, not archived)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"{emoji} - {request_text}\n"
        
        # Read existing content
        existing_content = ""
        if userbrief_file.exists():
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Find the right section to add the request
        lines = existing_content.split('\n') if existing_content else []
        
        # Find where to insert the new request (before archived section if it exists)
        insert_index = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith('## Archived') or line.strip().startswith('🧠'):
                insert_index = i
                break
        
        # Insert the new entry
        lines.insert(insert_index, new_entry.rstrip())
        
        # Join back and write
        updated_content = '\n'.join(lines)
        
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, f"Request added successfully at {timestamp}"
        
    except Exception as e:
        return False, f"Error adding request: {str(e)}"

# Main form
st.header("📝 New Request")

with st.form("add_request_form"):
    # Simple text input for request
    request_text = st.text_area(
        "Request Description:",
        height=150,
        placeholder="Describe what you want to accomplish...",
        help="Enter your request. It will be processed automatically by the task-analysis workflow."
    )
    
    # Submit button
    submitted = st.form_submit_button("➕ Add Request", type="primary")
    
    if submitted:
        if request_text.strip():
            # Add to userbrief as unprocessed request (🗄️)
            success, message = add_request_to_userbrief(request_text.strip(), is_preference=False)
            
            if success:
                st.success(f"✅ Request added and will be processed automatically!")
                st.balloons()
                
                # Clear form suggestion
                st.info("💡 Your request will be analyzed and converted to tasks by the workflow system.")
                
            else:
                st.error(f"❌ {message}")
        else:
            st.error("⚠️ Please enter a request description before submitting.")

# Display current userbrief status
st.header("📊 Current Userbrief Status")

userbrief_file = Path('.cursor/memory-bank/userbrief.md')
if userbrief_file.exists():
    try:
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count entries
        lines = content.split('\n')
        total_entries = 0
        active_requests = 0
        preferences = 0
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('📌') or line.startswith('🗄️') or line.startswith('🧠'):
                    total_entries += 1
                    if line.startswith('📌'):
                        preferences += 1
                    elif not any(status in line for status in ['DONE:', 'ARCHIVED:']):
                        active_requests += 1
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Entries", total_entries)
        
        with col2:
            st.metric("Active Requests", active_requests)
        
        with col3:
            st.metric("User Preferences", preferences)
        
        # Show recent entries
        if total_entries > 0:
            with st.expander("Recent Entries (Last 5)"):
                recent_entries = []
                for line in reversed(lines):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith('📌') or line.startswith('🗄️') or line.startswith('🧠'):
                            recent_entries.append(line)
                            if len(recent_entries) >= 5:
                                break
                
                for entry in recent_entries:
                    st.write(entry)
        
    except Exception as e:
        st.error(f"Error reading userbrief: {e}")
else:
    st.warning("No userbrief file found. Your first request will create the file.")



# Auto-refresh info
st.sidebar.markdown("---")
st.sidebar.info("💡 After adding a request, check the Agent Status page to see how the system processes it automatically via the `next_rule` tool.") 