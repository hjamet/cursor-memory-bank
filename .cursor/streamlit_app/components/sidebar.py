import streamlit as st
from streamlit_autorefresh import st_autorefresh
from . import task_utils
import json
from pathlib import Path
from datetime import datetime

def load_agent_memories(limit=5):
    """Load recent agent memories from the memories.json file"""
    try:
        # Try multiple possible paths for the memories file
        possible_paths = [
            Path("../memory-bank/workflow/agent_memory.json"),
            Path("../../memory-bank/workflow/agent_memory.json"),
            Path(".cursor/memory-bank/workflow/agent_memory.json"),
            Path("data/memories.json")
        ]
        
        memories_file = None
        for path in possible_paths:
            if path.exists():
                memories_file = path
                break
        
        if not memories_file:
            return []
        
        with open(memories_file, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        
        # The file contains directly an array of memories
        if not memories:
            return []
            
        # Sort by timestamp descending and take the limit
        sorted_memories = sorted(memories, key=lambda x: x.get('timestamp', ''), reverse=True)
        return sorted_memories[:limit]
    except Exception as e:
        # Return empty list instead of crashing
        return []

def add_user_message(content: str) -> bool:
    """Add a user message to the user_messages.json file"""
    try:
        user_messages_file = Path(".cursor/memory-bank/workflow/user_messages.json")
        
        # Read existing data or create new structure
        if user_messages_file.exists():
            with open(user_messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"version": "1.0.0", "last_id": 0, "messages": []}
        
        # Generate new ID and create message
        new_id = data.get("last_id", 0) + 1
        timestamp = datetime.now().isoformat()
        
        new_message = {
            "id": new_id,
            "content": content.strip(),
            "created_at": timestamp,
            "status": "pending"
        }
        
        # Add message and update last_id
        data["messages"].append(new_message)
        data["last_id"] = new_id
        
        # Ensure directory exists
        user_messages_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save updated data
        with open(user_messages_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error adding user message: {e}")
        return False

def display_sidebar():
    """
    Sets up the sidebar with project metrics, current task, and controls.
    """
    with st.sidebar:
        # --- Workflow Control Toggle ---
        st.markdown("### ⚙️ Workflow Control")
        
        # Read current workflow mode from JSON file
        workflow_state = _load_workflow_state()
        current_mode = workflow_state.get("mode", "infinite")
        
        # Create toggle button
        workflow_toggle = st.toggle(
            "Workflow Infini",
            value=(current_mode == "infinite"),
            help="Actif: L'agent continue indéfiniment • Inactif: L'agent s'arrête à context-update"
        )
        
        # Update workflow state if changed
        new_mode = "infinite" if workflow_toggle else "task_by_task"
        if new_mode != current_mode:
            _update_workflow_state(new_mode)
        
        # Display current mode status
        if new_mode == "infinite":
            st.success("🔄 Mode: **Workflow Infini** - L'agent continue automatiquement")
        else:
            st.info("⏸️ Mode: **Tâche par Tâche** - L'agent s'arrêtera à context-update")
        
        st.divider()
        
        st.header("📊 Project Dashboard")

        # --- Notification Indicators ---
        review_tasks_count = task_utils.get_review_tasks_count()
        messages_count = task_utils.get_agent_messages_count()
        total_notifications = review_tasks_count + messages_count
        
        if total_notifications > 0:
            st.markdown("### 🔔 Notifications")
            
            # Create notification card
            notification_text = []
            if review_tasks_count > 0:
                notification_text.append(f"✅ **{review_tasks_count}** task(s) to review")
            if messages_count > 0:
                notification_text.append(f"📨 **{messages_count}** agent message(s)")
            
            notification_content = "\n\n".join(notification_text)
            
            # Make the notification indicator clickable with intelligent redirection
            if st.button(
                f"🔴 {total_notifications} item(s) need attention",
                key="notification_redirect_button",
                help="Click to navigate to Review & Communication page",
                use_container_width=True,
                type="secondary"
            ):
                # Intelligent navigation logic
                if messages_count > 0:
                    # Priority to messages if they exist
                    st.session_state.active_tab = "messages"
                elif review_tasks_count > 0:
                    # Otherwise go to review tasks
                    st.session_state.active_tab = "review"
                else:
                    # Fallback to add request tab
                    st.session_state.active_tab = "add"
                
                # Navigate to the main page (Review & Communication)
                st.switch_page("app.py")
            
            with st.expander("📋 Details", expanded=False):
                st.markdown(notification_content)
            
            st.markdown("---")

        # --- Metrics ---
        all_tasks = task_utils.get_all_tasks()
        remaining_tasks = [t for t in all_tasks if t.get('status') not in ['DONE', 'APPROVED', 'REVIEW']]
        unprocessed_requests = task_utils.get_unprocessed_requests_count()
        work_queue_count = len(remaining_tasks) + unprocessed_requests
        
        # In-progress task
        in_progress_tasks = [t for t in remaining_tasks if t.get('status') == 'IN_PROGRESS']

        # Modern card-style display of Remaining Tasks (includes both tasks and unprocessed requests)
        st.markdown(
            f"""
            <div style="
                text-align: center; 
                margin: 20px 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <h3 style="
                    color: #ffffff; 
                    margin-bottom: 8px; 
                    font-weight: 600;
                    font-size: 16px;
                    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
                ">Remaining Tasks</h3>
                <h1 style="
                    color: #ffffff; 
                    margin-top: 0; 
                    margin-bottom: 0;
                    font-weight: 700;
                    font-size: 32px;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                ">{work_queue_count}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Display current workflow rule/step
        current_rule = task_utils.get_current_workflow_rule()
        formatted_rule = task_utils.format_workflow_rule(current_rule)
        
        # Always show Agent Status with workflow step
        st.markdown("---")
        
        # Display Agent Status with current workflow step (always visible)
        if current_rule and current_rule != 'idle':
            st.subheader(f"🤖 Agent Status ({formatted_rule})")
            
            if in_progress_tasks:
                # Show current task details under Agent Status
                task = in_progress_tasks[0]  # Show first task if multiple
                title = task.get('title', 'No Title')
                description = task.get('short_description', '')
                info_text = f"**Current Task:** **{title}**"
                if description:
                    info_text += f"\n\n*{description}*"
                st.info(info_text)
            else:
                st.info(f"**Workflow Step:** {formatted_rule}\n\nAgent is processing workflow rules.")
        else:
            st.subheader(f"🤖 Agent Status ({formatted_rule})")
            
            if in_progress_tasks:
                # Show current task details under Agent Status
                task = in_progress_tasks[0]  # Show first task if multiple  
                title = task.get('title', 'No Title')
                description = task.get('short_description', '')
                info_text = f"**Current Task:** {title}"
                if description:
                    info_text += f"\n\n{description}"
                st.info(info_text)
            else:
                st.info("Agent is idle. Ready for next task.")

        # Display Recent Memories
        try:
            recent_memories = load_agent_memories(1)
            if recent_memories:
                with st.expander("🧠 Recent Memory", expanded=False):
                    for memory in recent_memories:
                        
                        # Get memory content (past, present, future)
                        past = memory.get('past', '')
                        present = memory.get('present', '')
                        future = memory.get('future', '')
                        
                        # Create expandable memory entry
                        if past:
                            st.markdown(f"**Passé:** {past}")
                        if present:
                            st.markdown(f"**Présent:** {present}")
                        if future:
                            st.markdown(f"**Futur:** {future}")
            else:
                with st.expander("🧠 Recent Memories (5)", expanded=False):
                    st.info("Aucun souvenir disponible pour le moment.")
        except Exception as e:
            with st.expander("🧠 Recent Memories (5)", expanded=False):
                st.error(f"Erreur lors du chargement des souvenirs: {str(e)}")

        st.markdown("---")


def _load_workflow_state():
    """Load workflow state from JSON file"""
    import json
    import os
    from pathlib import Path
    
    # Path to workflow state file
    current_dir = Path(__file__).resolve().parent
    workflow_state_file = current_dir.parent.parent / 'memory-bank' / 'workflow' / 'workflow_state.json'
    
    try:
        if workflow_state_file.exists():
            with open(workflow_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return default state
            return {"mode": "infinite"}
    except Exception:
        # Return default state if file is corrupted
        return {"mode": "infinite"}


def _update_workflow_state(new_mode):
    """Update workflow state with new mode"""
    import json
    import os
    from pathlib import Path
    from datetime import datetime
    
    # Path to workflow state file
    current_dir = Path(__file__).resolve().parent
    workflow_state_file = current_dir.parent.parent / 'memory-bank' / 'workflow' / 'workflow_state.json'
    
    try:
        # Load existing state
        workflow_state = _load_workflow_state()
        
        # Update mode and timestamp
        workflow_state["mode"] = new_mode
        workflow_state["updated_at"] = datetime.now().isoformat()
        
        # Ensure directory exists
        workflow_state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write updated state
        with open(workflow_state_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_state, f, indent=2, ensure_ascii=False)
            
        # Show success message
        import streamlit as st
        if new_mode == "infinite":
            st.toast("🔄 Mode Workflow Infini activé", icon="✅")
        else:
            st.toast("⏸️ Mode Tâche par Tâche activé", icon="✅")
            
    except Exception as e:
        import streamlit as st
        st.error(f"Erreur lors de la mise à jour du mode workflow: {e}")
        
        # User Message Form
        st.markdown("### 💬 Send Message to Agent")
        
        with st.form(key="user_message_form", clear_on_submit=True):
            user_message = st.text_area(
                "Message",
                placeholder="Send a quick message to the agent...",
                height=80,
                help="Send a message to the agent"
            )
            
            submitted = st.form_submit_button("📤 Send Message", type="primary")
            
            if submitted:
                if user_message and user_message.strip():
                    if add_user_message(user_message):
                        st.success("✅ Message sent to agent!")
                        st.toast("Message sent successfully!", icon="✅")
                    else:
                        st.error("❌ Failed to send message. Please try again.")
                else:
                    st.warning("⚠️ Please enter a message before sending.")
        
        st.markdown("---")
        # Enhanced Auto-refresh System with Diagnostics
        # This ensures the dashboard updates every 2 seconds to reflect changes in real-time
        refresh_count = st_autorefresh(interval=2000, limit=None, key="auto_refresh_widget")
        
        # Debug information in sidebar (with toggle option)
        show_debug = st.checkbox("🔍 Show Auto-Refresh Debug", value=False, key="show_auto_refresh_debug")
        if refresh_count > 0 and show_debug:
            with st.expander("🔄 Auto-Refresh Status", expanded=True):
                st.caption(f"Refresh count: {refresh_count}")
                st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
                st.caption(f"Interval: 2000ms (2 seconds)")
                st.caption(f"Status: {'🟢 Active' if refresh_count > 0 else '🔴 Inactive'}")
                
        # Force session state update to ensure data refreshes
        if 'last_refresh_count' not in st.session_state:
            st.session_state.last_refresh_count = 0
            
        if refresh_count != st.session_state.last_refresh_count:
            st.session_state.last_refresh_count = refresh_count
            # Clear any cached data that might prevent updates
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            # Force rerun to ensure UI updates
            if refresh_count > 1:  # Avoid infinite loop on first load
                st.rerun()
