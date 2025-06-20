import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Task Status", page_icon="✅")

st.markdown("# Task Status")
st.sidebar.header("Task Status")

# Correctly locate the tasks.json file relative to this script's location
try:
    # Go up one level from 'pages' to the 'src' directory
    base_path = Path(__file__).parent.parent 
    tasks_file = base_path / 'tasks.json'
    
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
    st.error("Could not find the `tasks.json` file. Make sure it is in the `src` directory.")
except json.JSONDecodeError:
    st.error("Could not decode the `tasks.json` file. Please check its format.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}") 