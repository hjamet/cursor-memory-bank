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
        if not history:
            continue

        start_time = None
        done_time = None

        # Find the latest transition to a "working" state and the first transition to a "done" state
        for i, record in enumerate(history):
            if record.get('status') in ['IN_PROGRESS', 'TODO', 'BLOCKED', 'REVIEW'] and start_time is None:
                 # Try to find the start time from created_date if no other state is found
                created_date_str = task.get('created_date')
                if created_date_str:
                    try:
                        start_time = datetime.fromisoformat(created_date_str.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        pass

            if record.get('status') in ['IN_PROGRESS']:
                 try:
                    start_time = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                 except (ValueError, TypeError):
                        pass
            
            if record.get('status') in ['DONE', 'APPROVED'] and start_time is not None:
                try:
                    done_time = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                    completion_times.append((done_time - start_time).total_seconds() / 3600)  # in hours
                    start_time = None # Reset for tasks that might have been reopened
                except (ValueError, TypeError):
                    pass

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
        
        unprocessed_count = 0
        if 'active_request' in data and data['active_request']:
            unprocessed_count += 1
        if 'new_requests' in data:
            unprocessed_count += len(data['new_requests'])
            
        return unprocessed_count
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return 0 