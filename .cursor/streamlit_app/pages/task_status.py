import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Task Status", page_icon="✅")

st.markdown("# Task Status")
st.sidebar.header("Task Status")

# Correctly locate the tasks.json file relative to this script's location
try:
    # Path is relative to the project root, where the app is run
    tasks_file = Path('.cursor/streamlit_app/tasks.json')
    
    with open(tasks_file, 'r') as f:
        tasks = json.load(f)

    st.write("Here is the current status of the tasks:")

    status_map = {
        "DONE": "🟢",
        "IN_PROGRESS": "🟡",
        "TODO": "⚪️"
    }

    for task in tasks:
        status_emoji = status_map.get(task.get("status"), "❓")
        st.markdown(f"### {status_emoji} {task.get('title', 'No Title')}")
        st.write(f"**Description:** {task.get('description', 'No Description')}")
        st.divider()

except FileNotFoundError:
    st.error(f"Could not find the `tasks.json` file. Make sure it is at `{tasks_file}` and you are running the app from the project root.")
except json.JSONDecodeError:
    st.error("Could not decode the `tasks.json` file. Please check its format.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}") 