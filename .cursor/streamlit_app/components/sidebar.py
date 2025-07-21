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
    Enhanced with auto-refresh coordination for navigation debouncing.
    """
    with st.sidebar:
        # Intelligent auto-refresh with navigation debouncing coordination
        current_time = datetime.now()
        navigation_debounce_active = False
        
        # Check if navigation interaction is active (within 3 seconds)
        # ROBUSTNESS FIX: Add safeguards for edge cases and inactivity
        if (hasattr(st.session_state, 'last_navigation_interaction') and 
            st.session_state.last_navigation_interaction is not None):
            try:
                time_since_interaction = (current_time - st.session_state.last_navigation_interaction).total_seconds()
                navigation_debounce_active = time_since_interaction < 3
                
                # SAFEGUARD: If interaction is too old (>10 minutes), reset it to allow fresh start
                if time_since_interaction > 600:  # 10 minutes
                    st.session_state.last_navigation_interaction = None
                    navigation_debounce_active = False
                    
            except (TypeError, AttributeError):
                # FALLBACK: If timestamp is corrupted, reset and continue
                st.session_state.last_navigation_interaction = None
                navigation_debounce_active = False
        
        # Auto-refresh logic with conditional pause during navigation
        # CRITICAL: This MUST run during inactivity periods to ensure permanent auto-refresh
        if navigation_debounce_active:
            # Pause auto-refresh during navigation interactions
            st.info("🔄 Auto-refresh pausé pendant interaction navigation")
        else:
            # Normal auto-refresh every 2 seconds when no navigation interaction
            # PERMANENT AUTO-REFRESH: This ensures continuous operation as required by user
            st_autorefresh(interval=2000, key="sidebar_autorefresh")
        
        # --- Workflow Control Toggle ---
        st.markdown("### ⚙️ Workflow Control")
        
        # Read current workflow mode from JSON file
        workflow_state = _load_workflow_state()
        current_mode = workflow_state.get("mode", "infinite")
        
        # Determine agent activity status
        agent_status = _get_agent_status(workflow_state)
        
        # Create two columns for toggle and status indicator
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Create toggle button
            workflow_toggle = st.toggle(
                "Workflow Infini",
                value=(current_mode == "infinite"),
                help="Actif: L'agent continue indéfiniment • Inactif: L'agent s'arrête à context-update"
            )
        
        with col2:
            # Agent status indicator
            if agent_status["is_active"]:
                st.markdown(f"🟢 **Actif**", help=f"Agent en cours d'exécution: {agent_status['current_step']}")
            else:
                st.markdown(f"🔴 **Inactif**", help=f"Agent arrêté depuis: {agent_status['last_activity']}")
        
        # Update workflow state if changed
        new_mode = "infinite" if workflow_toggle else "task_by_task"
        if new_mode != current_mode:
            _update_workflow_state(new_mode)
        
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
                # Set navigation debounce timestamp to prevent auto-refresh interference
                st.session_state.last_navigation_interaction = datetime.now()
                
                # Intelligent navigation logic
                if messages_count > 0:
                    # Priority to messages if they exist
                    st.session_state.active_tab = "messages"
                elif review_tasks_count > 0:
                    # Otherwise go to review tasks
                    st.session_state.active_tab = "review"
                else:
                    # Fallback to main tab
                    st.session_state.active_tab = "main"
                
                # Enhanced coordination: brief delay + force rerun for state consistency
                import time
                time.sleep(0.1)
                
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
                margin: 12px 0; 
                padding: 12px; 
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
        
        # End of sidebar content - auto-refresh sections removed for cleaner interface
        # Note: Auto-refresh functionality is preserved and runs automatically at the top of sidebar


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


def _get_agent_status(workflow_state):
    """Determine if agent is currently active based on workflow state and timing"""
    from datetime import datetime, timedelta
    
    # Agent is considered active if:
    # 1. Status is "active" in workflow state
    # 2. Last update was within the last 5 minutes
    # 3. Current rule is not "workflow-complete"
    
    status = workflow_state.get("status", "inactive")
    current_rule = workflow_state.get("current_rule", "unknown")
    updated_at = workflow_state.get("updated_at")
    
    # Check if agent is explicitly marked as active and not in complete state
    is_explicitly_active = (status == "active" and current_rule != "workflow-complete")
    
    # Check if recent activity (within last 5 minutes)
    is_recently_active = False
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(last_update.tzinfo) if last_update.tzinfo else datetime.now()
            time_diff = now - last_update
            is_recently_active = time_diff < timedelta(minutes=5)
        except Exception:
            is_recently_active = False
    
    # Agent is active if both conditions are met
    is_active = is_explicitly_active and is_recently_active
    
    # Format activity information
    if is_active:
        current_step = current_rule.replace("-", " ").title() if current_rule else "Unknown"
        return {
            "is_active": True,
            "current_step": current_step,
            "last_activity": None
        }
    else:
        # Format last activity time
        last_activity = "Inconnu"
        if updated_at:
            try:
                last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                last_activity = last_update.strftime("%H:%M:%S")
            except Exception:
                pass
        
        return {
            "is_active": False,
            "current_step": None,
            "last_activity": last_activity
        }


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
