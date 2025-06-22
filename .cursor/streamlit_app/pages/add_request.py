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
        
        # Format the new entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"{emoji} - {request_text}\n"
        
        # Read existing content
        existing_content = ""
        if userbrief_file.exists():
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Add new entry at the end
        updated_content = existing_content.rstrip() + "\n" + new_entry
        
        # Write back to file
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True, f"Request added successfully at {timestamp}"
        
    except Exception as e:
        return False, f"Error adding request: {str(e)}"

# Main form
st.header("📝 New Request Form")

with st.form("add_request_form"):
    st.markdown("### Request Details")
    
    # Request type selection
    request_type = st.radio(
        "Request Type:",
        options=["Task Request", "User Preference"],
        help="Task Request: A specific task or feature to implement. User Preference: A general preference that should be remembered throughout the project."
    )
    
    # Text area for request
    request_text = st.text_area(
        "Request Description:",
        height=150,
        placeholder="Describe your request in detail. Be specific about what you want to accomplish...",
        help="Provide a clear and detailed description of what you want. For tasks, include specific requirements. For preferences, explain the general approach or style you prefer."
    )
    
    # Additional context (optional)
    context = st.text_area(
        "Additional Context (Optional):",
        height=100,
        placeholder="Any additional context, constraints, or background information...",
        help="Optional: Provide any additional context that might help the agent understand and implement your request better."
    )
    
    # Priority selection
    priority = st.selectbox(
        "Priority Level:",
        options=["Normal", "High", "Low"],
        index=0,
        help="Priority level for this request. High priority requests may be processed sooner."
    )
    
    # Submit button
    submitted = st.form_submit_button("➕ Add Request", type="primary")
    
    if submitted:
        if request_text.strip():
            # Combine request text with additional info
            full_request = request_text.strip()
            
            # Add context if provided
            if context.strip():
                full_request += f"\n\nAdditional Context: {context.strip()}"
            
            # Add priority if not normal
            if priority != "Normal":
                full_request += f"\n\nPriority: {priority}"
            
            # Determine if it's a preference
            is_preference = (request_type == "User Preference")
            
            # Add to userbrief
            success, message = add_request_to_userbrief(full_request, is_preference)
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                
                # Show what was added
                with st.expander("View Added Request"):
                    emoji = "📌" if is_preference else "🗄️"
                    st.markdown(f"**Type:** {request_type}")
                    st.markdown(f"**Content:** {emoji} - {full_request}")
                
                # Clear form suggestion
                st.info("💡 You can add another request by filling out the form again.")
                
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

# Help section
with st.expander("💡 Tips for Writing Good Requests"):
    st.markdown("""
    **For Task Requests:**
    - Be specific about what you want to accomplish
    - Include any technical requirements or constraints
    - Mention if this relates to existing code or features
    - Specify expected outcomes or acceptance criteria
    
    **For User Preferences:**
    - Describe general approaches or styles you prefer
    - Mention coding standards or patterns you like
    - Include any architectural preferences
    - Note any tools or technologies you prefer to use
    
    **Examples:**
    - Task: "Implement user authentication with JWT tokens, including login/logout endpoints and password hashing"
    - Preference: "I prefer using TypeScript over JavaScript for better type safety in all new code"
    """)

# Auto-refresh info
st.sidebar.markdown("---")
st.sidebar.info("💡 After adding a request, check the Agent Status page to see how the system processes it automatically via the `next_rule` tool.") 