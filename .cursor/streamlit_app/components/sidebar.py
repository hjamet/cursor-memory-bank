import streamlit as st
from streamlit_autorefresh import st_autorefresh
from . import task_utils

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
            
            st.markdown(
                f"""
                <div style="
                    padding: 15px; 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    margin-bottom: 15px;
                ">
                    <div style="
                        color: #ffffff; 
                        font-weight: 600;
                        font-size: 14px;
                        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
                        text-align: center;
                    ">
                        🔴 {total_notifications} item(s) need attention
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.expander("📋 Details", expanded=False):
                st.markdown(notification_content)
            
            st.markdown("---")

        # --- Metrics ---
        all_tasks = task_utils.get_all_tasks()
        # Remaining tasks now includes 'REVIEW' status as they are not fully completed yet.
        remaining_tasks = [t for t in all_tasks if t.get('status') not in ['DONE', 'APPROVED']]
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
        
        if in_progress_tasks:
            st.markdown("---")
            st.subheader("⚡ Current Task")
            for task in in_progress_tasks:
                title = task.get('title', 'No Title')
                description = task.get('short_description', '')
                info_text = f"**{title}**"
                if description:
                    info_text += f"\n\n{description}"
                st.info(info_text)
            # Show workflow rule below current task
            st.markdown("**Current Workflow Step:**")
            st.markdown(f"🔄 {formatted_rule}")
        else:
            # Show workflow rule in the agent status section
            st.markdown("---")
            st.subheader("🤖 Agent Status")
            if current_rule and current_rule != 'idle':
                st.info(f"**Workflow Step:** {formatted_rule}\n\nAgent is processing workflow rules.")
            else:
                st.info("Agent is idle. Ready for next task.")

        st.markdown("---")
        # Auto-refresh is enabled by default every 5 seconds to keep the dashboard updated.
        st_autorefresh(interval=5000, limit=None, key="auto_refresh_widget")
