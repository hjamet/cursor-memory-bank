import streamlit as st
import json
import requests
from datetime import datetime

st.set_page_config(page_title="Add Request", page_icon="➕")

st.markdown("# ➕ Add New Request")
st.sidebar.header("Add Request")

st.markdown("Use this page to add new requests to the userbrief. These requests will be automatically processed by the agent's workflow system.")

# Helper function to add request via MCP API
def add_request_via_mcp(request_text):
    """Add a new request using the MCP MemoryBankMCP server"""
    try:
        # For now, we'll simulate the MCP call by directly modifying the JSON file
        # In a real implementation, this would make an HTTP request to the MCP server
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
        
        # Create new request with "new" status (to be processed)
        new_id = userbrief_data["last_id"] + 1
        timestamp = datetime.now().isoformat()
        
        new_request = {
            "id": new_id,
            "content": request_text,
            "status": "new",  # Status "new" for processing, not archived
            "created_at": timestamp,
            "updated_at": timestamp,
            "history": [
                {
                    "timestamp": timestamp,
                    "action": "created",
                    "comment": f"New request added via Streamlit interface with status 'new' for processing."
                }
            ]
        }
        
        # Add to requests and update last_id
        userbrief_data["requests"].append(new_request)
        userbrief_data["last_id"] = new_id
        
        # Write back to file
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(userbrief_data, f, indent=2, ensure_ascii=False)
        
        return True, f"Request #{new_id} added successfully with status 'new' for processing"
        
    except Exception as e:
        return False, f"Error adding request: {str(e)}"

# Helper function to get userbrief status from JSON
def get_userbrief_status():
    """Get userbrief status from the JSON file"""
    try:
        userbrief_file = ".cursor/memory-bank/workflow/userbrief.json"
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            userbrief_data = json.load(f)
        
        requests = userbrief_data.get("requests", [])
        
        # Count by status
        new_requests = [req for req in requests if req.get("status") == "new"]
        in_progress_requests = [req for req in requests if req.get("status") == "in_progress"]
        archived_requests = [req for req in requests if req.get("status") == "archived"]
        
        return {
            "total_requests": len(requests),
            "new_requests": len(new_requests),
            "in_progress_requests": len(in_progress_requests),
            "archived_requests": len(archived_requests),
            "recent_new": new_requests[-3:] if new_requests else []  # Last 3 new requests
        }
        
    except Exception as e:
        st.error(f"Error reading userbrief: {e}")
        return None

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
            # Add to userbrief via MCP as new request (status "new")
            success, message = add_request_via_mcp(request_text.strip())
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                
                # Clear form suggestion
                st.info("💡 Your request has been added with status 'new' and will be analyzed by the workflow system.")
                
            else:
                st.error(f"❌ {message}")
        else:
            st.error("⚠️ Please enter a request description before submitting.")

# Display current userbrief status
st.header("📊 Current Userbrief Status")

userbrief_status = get_userbrief_status()

if userbrief_status:
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", userbrief_status['total_requests'])
    
    with col2:
        st.metric("New (To Process)", userbrief_status['new_requests'], help="Requests waiting to be processed")
    
    with col3:
        st.metric("In Progress", userbrief_status['in_progress_requests'], help="Requests currently being worked on")
    
    with col4:
        st.metric("Archived", userbrief_status['archived_requests'], help="Completed requests")
    
    # Show recent new requests
    if userbrief_status['recent_new']:
        st.subheader("🆕 Recent New Requests")
        with st.expander("Recent Requests (Last 3)"):
            for req in userbrief_status['recent_new']:
                st.write(f"**#{req['id']}** - {req['content'][:100]}..." if len(req['content']) > 100 else f"**#{req['id']}** - {req['content']}")
                st.caption(f"Created: {req['created_at'][:19].replace('T', ' ')}")
                st.markdown("---")

else:
    st.warning("No userbrief file found or error reading it.")

# Information about the new system
st.header("ℹ️ About the New System")
st.info("""
**New Request Status System:**
- **New**: Requests waiting to be processed by the agent workflow
- **In Progress**: Requests currently being worked on
- **Archived**: Completed requests with resolution comments

Your requests are now managed through a structured JSON system that integrates with the MCP (Model Context Protocol) tools for better tracking and processing.
""")

# Auto-refresh info
st.sidebar.markdown("---")
st.sidebar.info("💡 After adding a request, check the Agent Status page to see how the system processes it automatically via the `next_rule` tool.") 