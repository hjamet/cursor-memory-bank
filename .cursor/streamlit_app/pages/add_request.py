import streamlit as st
import json
import requests
from datetime import datetime
import pandas as pd
from collections import defaultdict

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
        
        # Save updated userbrief
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(userbrief_data, f, indent=2, ensure_ascii=False)
        
        return True, f"Request #{new_id} added successfully!"
        
    except Exception as e:
        return False, f"Error adding request: {e}"

def get_request_evolution_data():
    """Generate request evolution data over time for the graph"""
    try:
        userbrief_file = ".cursor/memory-bank/workflow/userbrief.json"
        
        try:
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                userbrief_data = json.load(f)
        except FileNotFoundError:
            return pd.DataFrame()
        
        requests = userbrief_data.get("requests", [])
        if not requests:
            return pd.DataFrame()
        
        # Create timeline data based on creation and status change timestamps
        timeline_events = []
        
        for req in requests:
            req_id = req.get('id')
            
            # Add creation event
            created_at = req.get('created_at', '')
            if created_at:
                try:
                    # Handle different timestamp formats
                    if created_at.endswith('Z'):
                        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_dt = datetime.fromisoformat(created_at)
                    
                    timeline_events.append({
                        'datetime': created_dt,
                        'date': created_dt.date(),
                        'event': 'created',
                        'request_id': req_id
                    })
                except Exception as e:
                    # Fallback parsing
                    try:
                        created_dt = datetime.fromisoformat(created_at.split('.')[0])
                        timeline_events.append({
                            'datetime': created_dt,
                            'date': created_dt.date(),
                            'event': 'created',
                            'request_id': req_id
                        })
                    except:
                        pass
            
            # Add archived event if request is archived
            if req.get('status') == 'archived':
                # Look for the most recent mark_archived action in history
                history = req.get('history', [])
                archived_timestamp = None
                
                for entry in reversed(history):  # Start from most recent
                    if entry.get('action') == 'mark_archived':
                        archived_timestamp = entry.get('timestamp', '')
                        break
                
                if archived_timestamp:
                    try:
                        # Handle different timestamp formats
                        if archived_timestamp.endswith('Z'):
                            archived_dt = datetime.fromisoformat(archived_timestamp.replace('Z', '+00:00'))
                        else:
                            archived_dt = datetime.fromisoformat(archived_timestamp)
                        
                        timeline_events.append({
                            'datetime': archived_dt,
                            'date': archived_dt.date(),
                            'event': 'archived',
                            'request_id': req_id
                        })
                    except Exception as e:
                        # Fallback parsing
                        try:
                            archived_dt = datetime.fromisoformat(archived_timestamp.split('.')[0])
                            timeline_events.append({
                                'datetime': archived_dt,
                                'date': archived_dt.date(),
                                'event': 'archived',
                                'request_id': req_id
                            })
                        except:
                            pass
        
        if not timeline_events:
            return pd.DataFrame()
        
        # Sort events by datetime (chronological order)
        timeline_events.sort(key=lambda x: x['datetime'])
        
        # Group by date and count events
        daily_data = defaultdict(lambda: {'created': 0, 'archived': 0})
        
        for event in timeline_events:
            date = event['date']
            event_type = event['event']
            daily_data[date][event_type] += 1
        
        # Convert to DataFrame with cumulative pending requests
        dates = sorted(daily_data.keys())
        if not dates:
            return pd.DataFrame()
        
        # Extend date range to include today if needed
        start_date = min(dates)
        end_date = max(max(dates), datetime.now().date())
        
        # Generate all dates in range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        data = []
        pending_count = 0
        
        for date in date_range:
            date_obj = date.date()
            created = daily_data[date_obj]['created']
            archived = daily_data[date_obj]['archived']
            
            # Update pending count
            pending_count += created - archived
            pending_count = max(0, pending_count)  # Ensure non-negative
            
            data.append({
                'Date': date_obj,
                'Pending Requests': pending_count,
                'Created Today': created,
                'Archived Today': archived,
                'Net Change': created - archived
            })
        
        df = pd.DataFrame(data)
        return df
        
    except Exception as e:
        st.error(f"Error generating evolution data: {e}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame()

def get_userbrief_status():
    """Get current userbrief status and recent requests"""
    try:
        userbrief_file = ".cursor/memory-bank/workflow/userbrief.json"
        
        try:
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                userbrief_data = json.load(f)
        except FileNotFoundError:
            return None
        
        requests = userbrief_data.get("requests", [])
        
        # Count by status
        new_requests = [req for req in requests if req.get("status") == "new"]
        in_progress_requests = [req for req in requests if req.get("status") == "in_progress"]
        archived_requests = [req for req in requests if req.get("status") == "archived"]
        
        # Sort new and in_progress requests by updated_at (most recent first) for proper display
        unprocessed_requests = sorted(new_requests + in_progress_requests, key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return {
            "total_requests": len(requests),
            "new_requests": len(new_requests),
            "in_progress_requests": len(in_progress_requests),
            "archived_requests": len(archived_requests),
            "unprocessed_requests": unprocessed_requests  # All new + in_progress for editing
        }
        
    except Exception as e:
        st.error(f"Error reading userbrief: {e}")
        return None

def save_json_file(file_path, data):
    """Save data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False

def update_request_content(request_id, new_content):
    """Update request content via direct file modification"""
    try:
        userbrief_file = ".cursor/memory-bank/workflow/userbrief.json"
        
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            userbrief_data = json.load(f)
        
        # Find and update the request
        for req in userbrief_data['requests']:
            if req['id'] == request_id:
                req['content'] = new_content
                req['updated_at'] = datetime.now().isoformat()
                
                if 'history' not in req:
                    req['history'] = []
                req['history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'content_updated',
                    'comment': 'Request content updated via Add Request interface'
                })
                break
        
        return save_json_file(userbrief_file, userbrief_data)
        
    except Exception as e:
        st.error(f"Error updating request: {e}")
        return False

def delete_request(request_id):
    """Delete request via direct file modification"""
    try:
        userbrief_file = ".cursor/memory-bank/workflow/userbrief.json"
        
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            userbrief_data = json.load(f)
        
        # Remove the request
        userbrief_data['requests'] = [req for req in userbrief_data['requests'] if req['id'] != request_id]
        
        return save_json_file(userbrief_file, userbrief_data)
        
    except Exception as e:
        st.error(f"Error deleting request: {e}")
        return False

# Initialize session state for text area and form control
# Main form with native Streamlit approach
st.header("📝 New Request")

# Use Streamlit form for reliable submission handling
with st.form("request_form", clear_on_submit=True):
    request_text = st.text_area(
        "Request Description:",
        height=150,
        placeholder="Describe what you want to accomplish...",
        help="Enter your request. It will be processed automatically by the task-analysis workflow. Press Ctrl+Enter to submit quickly.",
        key="request_input"
    )
    
    # Submit button within form for native behavior
    col1, col2 = st.columns([1, 4])
    with col1:
        submitted = st.form_submit_button("➕ Add Request", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("*Press Ctrl+Enter in the text area or click the button to submit*")

# Handle form submission with simplified approach
if submitted:
    current_text = request_text.strip()
    
    if current_text:
        # Add to userbrief via MCP as new request (status "new")
        success, message = add_request_via_mcp(current_text)
        
        if success:
            # Show success message and balloons
            st.success(f"✅ {message}")
            st.balloons()  # Show balloons immediately after success
            st.toast("🎉 Request submitted successfully! The agent will process it automatically.", icon="✅")
        else:
            st.error(f"❌ {message}")
    else:
        st.error("⚠️ Please enter a request description before submitting.")

# Enhanced JavaScript for reliable Ctrl+Enter support
st.markdown("""
<script>
function setupCtrlEnterForForm() {
    // Wait for DOM to be ready
    setTimeout(function() {
        // Find the form text area and submit button
        const formContainer = document.querySelector('[data-testid="stForm"]');
        if (!formContainer) return;
        
        const textArea = formContainer.querySelector('textarea');
        const submitButton = formContainer.querySelector('button[type="submit"]');
        
        if (textArea && submitButton && !textArea.hasAttribute('data-ctrl-enter-setup')) {
            textArea.setAttribute('data-ctrl-enter-setup', 'true');
            
            textArea.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    submitButton.click();
                }
            });
            
            // Also handle keypress for better compatibility
            textArea.addEventListener('keypress', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    submitButton.click();
                }
            });
        }
    }, 100);
}

// Setup immediately and after any DOM changes
setupCtrlEnterForForm();

// Re-setup when Streamlit updates the page
const observer = new MutationObserver(function(mutations) {
    let shouldResetup = false;
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            for (let node of mutation.addedNodes) {
                if (node.nodeType === 1 && (node.querySelector('[data-testid="stForm"]') || node.matches('[data-testid="stForm"]'))) {
                    shouldResetup = true;
                    break;
                }
            }
        }
    });
    if (shouldResetup) {
        setTimeout(setupCtrlEnterForForm, 100);
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
</script>
""", unsafe_allow_html=True)

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
    
    # Show unprocessed requests with inline editing (no accordion)
    if userbrief_status['unprocessed_requests']:
        st.subheader("🆕 Unprocessed Requests")
        st.markdown("**Requests waiting to be processed** - You can edit or delete them directly")
        
        for req in userbrief_status['unprocessed_requests']:
            req_id = req['id']
            status = req.get('status', 'unknown')
            
            # Container for each request
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Status indicator
                    status_emoji = "🆕" if status == "new" else "⚡" if status == "in_progress" else "❓"
                    st.markdown(f"**#{req_id}** {status_emoji} **{status.title()}**")
                    
                    # Check if this request is being edited
                    edit_key = f"edit_request_{req_id}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = False
                    
                    if st.session_state[edit_key]:
                        # Edit mode: show text area
                        new_content = st.text_area(
                            "Edit request content:",
                            value=req.get('content', ''),
                            height=100,
                            key=f"edit_content_{req_id}"
                        )
                        
                        # Save/Cancel buttons
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save", key=f"save_{req_id}"):
                                if update_request_content(req_id, new_content):
                                    st.success(f"✅ Request #{req_id} updated!")
                                    st.session_state[edit_key] = False
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{req_id}"):
                                st.session_state[edit_key] = False
                                st.rerun()
                    else:
                        # Display mode: show content
                        st.write(req['content'])
                        
                        # Show timestamps
                        created_time = req['created_at'][:19].replace('T', ' ') if req.get('created_at') else 'Unknown'
                        updated_time = req['updated_at'][:19].replace('T', ' ') if req.get('updated_at') else 'Unknown'
                        st.caption(f"Created: {created_time} | Updated: {updated_time}")
                
                with col2:
                    st.markdown("**Actions:**")
                    
                    # Edit button
                    if not st.session_state[edit_key]:
                        if st.button(f"✏️ Edit", key=f"edit_btn_{req_id}", help="Edit request content"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    
                    # Delete button with confirmation
                    delete_confirm_key = f"delete_confirm_{req_id}"
                    if delete_confirm_key not in st.session_state:
                        st.session_state[delete_confirm_key] = False
                    
                    if st.session_state[delete_confirm_key]:
                        st.warning("⚠️ Confirm deletion?")
                        col_confirm, col_abort = st.columns(2)
                        with col_confirm:
                            if st.button("🗑️ Yes", key=f"confirm_delete_{req_id}"):
                                if delete_request(req_id):
                                    st.success(f"✅ Request #{req_id} deleted!")
                                    st.session_state[delete_confirm_key] = False
                                    st.rerun()
                        with col_abort:
                            if st.button("❌ No", key=f"abort_delete_{req_id}"):
                                st.session_state[delete_confirm_key] = False
                                st.rerun()
                    else:
                        if st.button(f"🗑️ Delete", key=f"delete_btn_{req_id}", help="Delete this request"):
                            st.session_state[delete_confirm_key] = True
                            st.rerun()
                
                st.markdown("---")

else:
    st.warning("No userbrief file found or error reading it.")

 