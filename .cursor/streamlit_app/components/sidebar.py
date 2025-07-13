import streamlit as st
from streamlit_autorefresh import st_autorefresh
from . import task_utils
import json
from pathlib import Path
from datetime import datetime

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
        
        st.markdown("---")
        # Auto-refresh is enabled by default every 5 seconds to keep the dashboard updated.
        st_autorefresh(interval=2000, limit=None, key="auto_refresh_widget")
