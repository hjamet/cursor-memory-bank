import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
import statistics

def get_tasks_file() -> Optional[Path]:
    """Get the path to the tasks file, prioritizing MCP-managed file."""
    possible_paths = [
        Path('.cursor/memory-bank/streamlit_app/tasks.json'),
        Path('.cursor/streamlit_app/tasks.json'),
        Path('.cursor/memory-bank/tasks.json'),
        Path('tasks.json')
    ]
    for path in possible_paths:
        if path.exists():
            return path
    return None

def get_all_tasks() -> List[Dict[str, Any]]:
    """Loads all tasks from the tasks.json file."""
    tasks_file = get_tasks_file()
    if not tasks_file:
        return []
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get('tasks', [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def calculate_task_completion_stats(tasks: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
    """Calculate average completion time and standard deviation for completed tasks."""
    completed_tasks = [t for t in tasks if t.get('status') in ['DONE', 'APPROVED']]
    completion_times = []

    for task in completed_tasks:
        history = task.get('status_history', [])
        
        start_time = None
        done_time = None

        # Find first IN_PROGRESS time
        if history:
            for record in history:
                if record.get('status') == 'IN_PROGRESS':
                    timestamp_str = record.get('timestamp')
                    if timestamp_str:
                        try:
                            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            start_time = dt
                            break
                        except (ValueError, TypeError):
                            pass
        
        # If no IN_PROGRESS in history, use created_date
        if start_time is None:
            created_date_str = task.get('created_date')
            if created_date_str:
                try:
                    dt = datetime.fromisoformat(created_date_str.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    start_time = dt
                except (ValueError, TypeError):
                    pass

        # Find last DONE/APPROVED time
        if history:
            for record in reversed(history):
                if record.get('status') in ['DONE', 'APPROVED']:
                    timestamp_str = record.get('timestamp')
                    if timestamp_str:
                        try:
                            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            done_time = dt
                            break
                        except (ValueError, TypeError):
                            pass
        
        if start_time and done_time and done_time > start_time:
            completion_times.append((done_time - start_time).total_seconds() / 3600)  # in hours

    if not completion_times:
        return None, None
    
    mean_time = statistics.mean(completion_times)
    std_dev = statistics.stdev(completion_times) if len(completion_times) > 1 else 0.0
    
    return mean_time, std_dev

def estimate_remaining_time(remaining_tasks_count: int, mean_time: Optional[float], std_dev: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    """Estimate total remaining time with a simple confidence interval."""
    if mean_time is None or std_dev is None:
        return None, None
    
    total_time_mean = remaining_tasks_count * mean_time
    total_time_std_dev = (remaining_tasks_count ** 0.5) * std_dev
    
    # Simple estimation: mean and a range based on one std dev
    lower_bound = max(0, total_time_mean - total_time_std_dev)
    upper_bound = total_time_mean + total_time_std_dev
    
    return lower_bound, upper_bound

def format_time_estimate(hours_range: Tuple[Optional[float], Optional[float]]) -> str:
    """Format the time estimate range into a human-readable string."""
    lower, upper = hours_range
    
    if lower is None or upper is None:
        return "Not enough data"
        
    if lower == 0 and upper == 0:
        return "No tasks remaining"

    if abs(lower - upper) < 0.5: # If range is small, just show one number
        avg_days = lower / 8
        return f"~{lower:.1f} hours ({avg_days:.1f} days)"

    avg_days_lower = lower / 8
    avg_days_upper = upper / 8
    
    return f"{lower:.1f}-{upper:.1f} hours ({avg_days_lower:.1f}-{avg_days_upper:.1f} days)"

def get_userbrief_file() -> Optional[Path]:
    """Get the path to the userbrief.json file."""
    # This path is based on the new structure.
    # Adjust if your structure is different.
    path = Path('.cursor/memory-bank/workflow/userbrief.json')
    if path.exists():
        return path
    return None

def get_unprocessed_requests_count() -> int:
    """Loads user brief and counts unprocessed requests."""
    userbrief_file = get_userbrief_file()
    if not userbrief_file:
        return 0
    try:
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'requests' not in data or not isinstance(data.get('requests'), list):
            return 0
            
        unprocessed_count = 0
        for request in data['requests']:
            if request.get('status') == 'new':
                unprocessed_count += 1
                
        return unprocessed_count
    except (json.JSONDecodeError, FileNotFoundError):
        return 0

def get_workflow_state_file() -> Optional[Path]:
    """Get the path to the workflow_state.json file."""
    path = Path('.cursor/memory-bank/workflow/workflow_state.json')
    if path.exists():
        return path
    return None

def get_current_workflow_rule() -> Optional[str]:
    """Get the current workflow rule/step from workflow_state.json."""
    workflow_file = get_workflow_state_file()
    if not workflow_file:
        return None
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        current_rule = data.get('current_rule')
        if current_rule:
            return current_rule
        
        # Fallback: try to determine rule from recent activity
        status = data.get('status', 'idle')
        if status == 'idle':
            return 'idle'
        
        # Check history for most recent rule
        history = data.get('history', [])
        if history and isinstance(history, list) and len(history) > 0:
            latest_entry = history[0]
            if isinstance(latest_entry, dict) and 'rule' in latest_entry:
                return latest_entry['rule']
        
        return None
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        # Log error for debugging but don't crash the UI
        print(f"Warning: Could not read workflow state: {e}")
        return None

def format_workflow_rule(rule: Optional[str]) -> str:
    """Format the workflow rule for display in the UI."""
    if not rule:
        return "Unknown"
    
    if rule == 'idle':
        return "Idle"
    
    # Convert rule names to user-friendly format
    rule_mapping = {
        'start-workflow': 'Starting Workflow',
        'task-decomposition': 'Task Decomposition',
        'implementation': 'Implementation',
        'fix': 'Bug Fixing',
        'context-update': 'Context Update',
        'experience-execution': 'Testing & Validation'
    }
    
    return rule_mapping.get(rule, rule.replace('-', ' ').title())

def get_review_tasks_count() -> int:
    """Get the count of tasks that need review (REVIEW or BLOCKED status)."""
    tasks = get_all_tasks()
    return len([t for t in tasks if t.get('status') in ['REVIEW', 'BLOCKED']])

def get_agent_messages_count() -> int:
    """Get the count of agent messages that need attention."""
    try:
        messages_file = Path('.cursor/memory-bank/workflow/to_user.json')
        if not messages_file.exists():
            return 0
        
        with open(messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict) and 'messages' in data:
            return len(data['messages'])
        
        return 0
    except (json.JSONDecodeError, FileNotFoundError):
        return 0

def get_total_notification_count() -> int:
    """Get the total count of items requiring user attention (tasks + messages)."""
    return get_review_tasks_count() + get_agent_messages_count()

def get_workflow_metadata() -> Dict[str, Any]:
    """Get detailed workflow state metadata including timing and history."""
    workflow_file = get_workflow_state_file()
    if not workflow_file:
        return {
            'current_rule': None,
            'status': 'unknown',
            'last_updated': None,
            'history_count': 0,
            'is_active': False
        }
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        current_rule = data.get('current_rule')
        status = data.get('status', 'idle')
        last_updated = data.get('last_updated')
        history = data.get('history', [])
        
        return {
            'current_rule': current_rule,
            'status': status,
            'last_updated': last_updated,
            'history_count': len(history) if isinstance(history, list) else 0,
            'is_active': status == 'active' and current_rule is not None,
            'formatted_rule': format_workflow_rule(current_rule) if current_rule else 'Unknown'
        }
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Warning: Could not read workflow metadata: {e}")
        return {
            'current_rule': None,
            'status': 'error',
            'last_updated': None,
            'history_count': 0,
            'is_active': False,
            'formatted_rule': 'Error'
        } 