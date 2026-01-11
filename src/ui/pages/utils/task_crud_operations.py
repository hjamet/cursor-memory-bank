"""
Task CRUD operations utilities.
Handles create, read, update, delete operations for tasks via MCP and local file methods.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys

# Add the parent directory to the path for task_utils import
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from components import task_utils


def update_task_via_mcp(task_id, **kwargs):
    """Update a task using the MCP update_task tool"""
    try:
        # This would typically call the MCP tool, but for now we'll use the local file approach
        # In a real implementation, this would use st.session_state or a proper MCP client
        return update_task_local(task_id, **kwargs)
    except Exception as e:
        st.error(f"Error updating task via MCP: {e}")
        return False


def delete_task_via_mcp(task_id):
    """Delete a task using MCP tools"""
    try:
        # This would typically call the MCP tool, but for now we'll use the local file approach
        return delete_task_local(task_id)
    except Exception as e:
        st.error(f"Error deleting task via MCP: {e}")
        return False


def update_task_local(task_id, **kwargs):
    """Update a task in the local tasks file"""
    tasks_file = task_utils.get_tasks_file()
    if not tasks_file:
        return False
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            tasks = data
            data_format = 'array'
        else:
            tasks = data.get('tasks', [])
            data_format = 'object'
        
        # Find and update the task
        for task in tasks:
            if str(task.get('id', task.get('task_id'))) == str(task_id):
                
                # If status is being updated, manage history
                if 'status' in kwargs and kwargs['status'] != task.get('status'):
                    now_iso = datetime.now().isoformat()
                    if 'status_history' not in task or not task['status_history']:
                        # Initialize history for older tasks.
                        # This creates a baseline from its creation date and current status.
                        task['status_history'] = [{'status': task.get('status', 'TODO'), 'timestamp': task.get('created_date')}]
                    
                    # Append new status change
                    task['status_history'].append({
                        'status': kwargs['status'],
                        'timestamp': now_iso
                    })
                    task['updated_date'] = now_iso
                else:
                    task['updated_date'] = datetime.now().isoformat()

                # Update other fields
                for key, value in kwargs.items():
                    task[key] = value
                
                # Save back to file
                if data_format == 'array':
                    save_data = tasks
                else:
                    save_data = {'tasks': tasks}
                
                with open(tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                
                return True
                
    except Exception as e:
        st.error(f"Error updating task: {e}")
        return False
    
    return False


def delete_task_local(task_id):
    """Delete a task from the local tasks file"""
    tasks_file = task_utils.get_tasks_file()
    if not tasks_file:
        return False
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array format and object format
        if isinstance(data, list):
            tasks = data
            data_format = 'array'
        else:
            tasks = data.get('tasks', [])
            data_format = 'object'
        
        # Find and remove the task
        original_length = len(tasks)
        tasks = [task for task in tasks if str(task.get('id', task.get('task_id'))) != str(task_id)]
        
        if len(tasks) < original_length:
            # Save back to file
            if data_format == 'array':
                save_data = tasks
            else:
                save_data = {'tasks': tasks}
            
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
        else:
            st.error(f"Task #{task_id} not found")
            return False
            
    except Exception as e:
        st.error(f"Error deleting task: {e}")
        return False
    
    return False 