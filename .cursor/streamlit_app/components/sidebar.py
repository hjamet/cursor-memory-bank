import streamlit as st
from streamlit_autorefresh import st_autorefresh
from . import task_utils

def display_sidebar():
    """
    Sets up the sidebar with project metrics, current task, and controls.
    """
    with st.sidebar:
        st.header("📊 Project Dashboard")

        # --- Metrics ---
        all_tasks = task_utils.get_all_tasks()
        # Remaining tasks now includes 'REVIEW' status as they are not fully completed yet.
        remaining_tasks = [t for t in all_tasks if t.get('status') not in ['DONE', 'APPROVED']]
        unprocessed_requests = task_utils.get_unprocessed_requests_count()
        work_queue_count = len(remaining_tasks) + unprocessed_requests
        
        # In-progress task
        in_progress_tasks = [t for t in remaining_tasks if t.get('status') == 'IN_PROGRESS']

        # Centered display of Remaining Tasks (includes both tasks and unprocessed requests)
        st.markdown(
            f"""
            <div style="text-align: center; margin: 20px 0;">
                <h3 style="color: #1f77b4; margin-bottom: 5px;">Remaining Tasks</h3>
                <h2 style="color: #333; margin-top: 0;">{work_queue_count}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

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
        else:
            st.markdown("---")
            st.subheader("Agent Status")
            st.info("Agent is idle. Ready for next task.")

        st.markdown("---")
        # Auto-refresh is enabled by default every 10 seconds to keep the dashboard updated.
        st_autorefresh(interval=10000, limit=None, key="auto_refresh_widget")
