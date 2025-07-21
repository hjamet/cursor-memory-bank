import streamlit as st
from pages.utils import userbrief_operations
from pages.utils import task_sorting_utils
from pages.utils import task_rendering
from components import task_utils

def render_simplified_task_view():
    """Renders a simplified view of tasks and user requests."""
    # Removed excessive spacing - eliminated st.markdown("---") separator
    st.subheader("Current Workload")

    tasks = task_utils.get_all_tasks()
    userbrief_requests = userbrief_operations.get_userbrief_requests()

    if not tasks and not userbrief_requests:
        st.info("No active tasks or unprocessed user requests.")
        return

    # Invert order for userbrief_requests to show newest first
    if userbrief_requests:
        st.markdown("##### Unprocessed User Requests")
        for request in sorted(userbrief_requests, key=lambda x: x.get('id'), reverse=True):
            task_rendering.render_userbrief_request(request)

    # Display active tasks
    if tasks:
        st.markdown("##### Active Tasks")
        active_tasks = [task for task in tasks if task.get('status') not in ['DONE', 'APPROVED']]
        sorted_tasks = task_sorting_utils.sort_tasks_by_dependencies_and_priority(active_tasks)
        if sorted_tasks:
            for task in sorted_tasks:
                task_rendering.render_task_card(task)
        else:
            st.info("No active tasks to display.") 