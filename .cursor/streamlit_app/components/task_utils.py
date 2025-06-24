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