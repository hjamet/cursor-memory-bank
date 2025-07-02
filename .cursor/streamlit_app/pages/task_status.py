import streamlit as st
import sys
from pathlib import Path

# Add the parent directory of the pages directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.sidebar import display_sidebar
from components import task_utils

# Import the new modular utilities with absolute paths
current_dir = Path(__file__).resolve().parent
utils_dir = current_dir / "utils"
sys.path.insert(0, str(utils_dir))

import userbrief_operations
import task_sorting_utils
import task_rendering
import task_filtering

# Import specific functions
get_userbrief_requests = userbrief_operations.get_userbrief_requests
sort_tasks_by_dependencies_and_priority = task_sorting_utils.sort_tasks_by_dependencies_and_priority
render_task_card = task_rendering.render_task_card
render_userbrief_request = task_rendering.render_userbrief_request
render_advanced_search_and_filters = task_filtering.render_advanced_search_and_filters
apply_advanced_filters = task_filtering.apply_advanced_filters

st.set_page_config(page_title="Task Status", page_icon="✅")

display_sidebar()

st.markdown("# ✅ Task Status")


def main():
    """Main function to render the task status page"""
    
    tasks = task_utils.get_all_tasks()
    userbrief_requests = get_userbrief_requests()

    if not tasks and not userbrief_requests:
        st.info("No tasks or user requests found.")
        st.write("Checked locations:")
        return

    # Advanced Search & Filtering
    filters = render_advanced_search_and_filters()
    
    # Apply all filters, including search query
    tasks = apply_advanced_filters(tasks, filters)
    
    # Sort tasks
    tasks = sort_tasks_by_dependencies_and_priority(tasks)

    # --- Display Tasks ---
    st.header("Task Details")
    if tasks:
        for task in tasks:
            render_task_card(task)
    else:
        st.info("No tasks match the current filters.")

    # --- Display User Brief Requests ---
    if userbrief_requests:
        st.header("Unprocessed User Requests")
        for request in userbrief_requests:
            render_userbrief_request(request)


if __name__ == "__main__":
    main() 