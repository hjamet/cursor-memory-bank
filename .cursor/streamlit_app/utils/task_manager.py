"""
Task management utilities for the Streamlit app.
Handles loading, updating and managing tasks.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st


def get_tasks_file():
    """Get the path to the tasks file"""
    # Check for local override first
    local_tasks_file = Path(".cursor/memory-bank/streamlit_app/tasks.json")
    if local_tasks_file.exists():
        return local_tasks_file
    
    # Default to main tasks file
    return Path(".cursor/memory-bank/workflow/tasks.json")


def load_tasks() -> List[Dict]:
    """Load tasks from the tasks file"""
    try:
        tasks_file = get_tasks_file()
        if tasks_file.exists():
            with open(tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both array format and object format
                if isinstance(data, list):
                    return data
                else:
                    return data.get("tasks", [])
        return []
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        return []


def update_task_status(task_id: int, new_status: str, validation_data: Optional[Dict] = None) -> bool:
    """Update the status of a task"""
    try:
        tasks_file = get_tasks_file()
        if not tasks_file.exists():
            return False

        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        task_found = False
        # Handle both array format and object format
        if isinstance(data, list):
            tasks_list = data
        else:
            tasks_list = data.get("tasks", [])
            
        for task in tasks_list:
            if task.get("id") == task_id:
                task["status"] = new_status
                task["updated_date"] = datetime.now().isoformat()
                
                # Add validation data if provided (for APPROVED status)
                if validation_data and new_status == "APPROVED":
                    if "validation" not in task:
                        task["validation"] = {}
                    task["validation"].update(validation_data)
                
                task_found = True
                break

        if task_found:
            with open(tasks_file, 'w', encoding='utf-8') as f:
                # Save in the same format as loaded
                if isinstance(data, list):
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False # Task not found
    except Exception as e:
        st.error(f"Error updating task status: {e}")
        return False


def has_associated_image(task: Dict) -> bool:
    """Check if a task has an associated image"""
    return task.get("image") is not None


def get_image_path(task: Dict) -> Optional[str]:
    """Get the image path for a task"""
    image_info = task.get("image")
    if image_info and isinstance(image_info, str):
        # Handle old format where image is just a path string
        if os.path.exists(image_info):
            return image_info
    elif image_info and isinstance(image_info, dict):
        # Handle new format where image is metadata dict
        image_path = image_info.get("path")
        if image_path and os.path.exists(image_path):
            return image_path
    return None


def delete_task_image(task: Dict) -> bool:
    """Delete the image file associated with a task"""
    image_path = get_image_path(task)
    if image_path:
        try:
            os.remove(image_path)
            return True
        except Exception as e:
            st.error(f"Error deleting image {image_path}: {e}")
            return False
    return False 