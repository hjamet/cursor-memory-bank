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
        remaining_tasks = [t for t in all_tasks if t.get('status') not in ['DONE', 'APPROVED', 'REVIEW']]
        
        # In-progress task
        in_progress_tasks = [t for t in remaining_tasks if t.get('status') == 'IN_PROGRESS']

        col1, col2 = st.columns(2)
        col1.metric("Total Tasks", len(all_tasks))
        col2.metric("Remaining", len(remaining_tasks))

        mean_time, std_dev = task_utils.calculate_task_completion_stats(all_tasks)
        est_lower, est_upper = task_utils.estimate_remaining_time(len(remaining_tasks), mean_time, std_dev)
        formatted_est = task_utils.format_time_estimate((est_lower, est_upper))
        st.metric("Estimated Time to Completion", formatted_est)

        if in_progress_tasks:
            st.markdown("---")
            st.subheader("⚡ Current Task")
            for task in in_progress_tasks:
                st.info(f"**{task.get('title', 'No Title')}**")
        else:
            st.markdown("---")
            st.subheader("Agent Status")
            st.info("Agent is idle. Ready for next task.")

        st.markdown("---")
        st.header("⚙️ Controls")
        if st.checkbox("Enable Auto-Refresh (10s)", key="auto_refresh_checkbox"):
            st_autorefresh(interval=10000, limit=None, key="auto_refresh_widget")
