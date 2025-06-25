"""
Task filtering and search utilities.
Handles advanced search, filtering, and sorting operations for tasks.
"""

import streamlit as st
from datetime import datetime, timedelta
import task_sorting_utils

# Import specific functions
sort_tasks_by_dependencies_and_priority = task_sorting_utils.sort_tasks_by_dependencies_and_priority


def fuzzy_search_tasks(tasks, userbrief_requests, search_query):
    """
    Perform fuzzy search on tasks and userbrief requests
    Returns filtered tasks and requests that match the search query
    """
    if not search_query.strip():
        return tasks, userbrief_requests
    
    # Normalize search query
    query_lower = search_query.lower().strip()
    query_words = query_lower.split()
    
    def matches_task(task):
        """Check if task matches search criteria"""
        # Search in task ID
        task_id = str(task.get('id', ''))
        if query_lower in task_id or f"#{task_id}" in query_lower:
            return True
        
        # Search in status
        status = task.get('status', '').lower()
        if query_lower in status:
            return True
        
        # Search in title
        title = task.get('title', '').lower()
        if any(word in title for word in query_words):
            return True
        
        # Search in short description
        short_desc = task.get('short_description', '').lower()
        if any(word in short_desc for word in query_words):
            return True
        
        # Search in detailed description
        detailed_desc = task.get('detailed_description', '').lower()
        if any(word in detailed_desc for word in query_words):
            return True
        
        # Search in validation criteria
        validation = task.get('validation_criteria', '').lower()
        if any(word in validation for word in query_words):
            return True
        
        # Search in impacted files
        files = ' '.join(task.get('impacted_files', [])).lower()
        if any(word in files for word in query_words):
            return True
        
        return False
    
    def matches_request(request):
        """Check if userbrief request matches search criteria"""
        # Search in request ID
        req_id = str(request.get('id', ''))
        if query_lower in req_id or f"#{req_id}" in query_lower:
            return True
        
        # Search in status
        status = request.get('status', '').lower()
        if query_lower in status:
            return True
        
        # Search in content
        content = request.get('content', '').lower()
        if any(word in content for word in query_words):
            return True
        
        return False
    
    # Filter tasks and requests
    filtered_tasks = [task for task in tasks if matches_task(task)]
    filtered_requests = [req for req in userbrief_requests if matches_request(req)]
    
    return filtered_tasks, filtered_requests


def render_advanced_search_and_filters():
    """Render advanced search and filtering controls"""
    st.markdown("### 🔍 Search & Filters")
    
    # Create columns for search and filters
    search_col, filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1, 1])
    
    with search_col:
        search_query = st.text_input(
            "🔍 Search tasks...",
            placeholder="Search by ID, title, description, status, or files",
            help="Enter keywords to search across all task fields",
            key="task_search_query"
        )
    
    with filter_col1:
        # Status filter
        status_options = ['Active', 'All', 'TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW', 'DONE', 'APPROVED']
        status_filter = st.selectbox(
            "📊 Status:",
            status_options,
            index=0, # Default to 'Active'
            help="Filter tasks by status. 'Active' hides DONE and APPROVED.",
            key="status_filter"
        )
    
    with filter_col2:
        # Priority filter
        priority_options = ['All', '🔥 Critical (5)', '🔴 High (4)', '🟡 Normal (3)', '🟢 Low (2)', '⚪ Minimal (1)']
        priority_filter = st.selectbox(
            "⭐ Priority:",
            priority_options,
            help="Filter tasks by priority level",
            key="priority_filter"
        )
    
    with filter_col3:
        # Dependency filter
        dependency_options = ['All', 'No Dependencies', 'Has Dependencies', 'Blocked by Dependencies']
        dependency_filter = st.selectbox(
            "🔗 Dependencies:",
            dependency_options,
            help="Filter tasks by dependency status",
            key="dependency_filter"
        )
    
    # Additional filters row
    filter_row2_col1, filter_row2_col2, filter_row2_col3, filter_row2_col4 = st.columns(4)
    
    with filter_row2_col1:
        # Date range filter
        date_filter = st.selectbox(
            "📅 Created:",
            ['All Time', 'Last 7 days', 'Last 30 days', 'Last 90 days'],
            help="Filter tasks by creation date",
            key="date_filter"
        )
    
    with filter_row2_col2:
        # Image filter
        image_filter = st.selectbox(
            "📸 Images:",
            ['All', 'With Images', 'Without Images'],
            help="Filter tasks with or without associated images",
            key="image_filter"
        )
    
    with filter_row2_col3:
        # Sort options
        sort_options = [
            'Dependencies & Priority',
            'Priority (High to Low)',
            'Priority (Low to High)',
            'Created Date (Newest)',
            'Created Date (Oldest)',
            'Status',
            'Title (A-Z)',
            'Title (Z-A)'
        ]
        sort_option = st.selectbox(
            "📊 Sort by:",
            sort_options,
            help="Choose how to sort the tasks",
            key="sort_option"
        )
    
    with filter_row2_col4:
        # Reset filters button
        if st.button("🔄 Reset Filters", help="Clear all filters and search"):
            # Clear all filter states
            for key in ['task_search_query', 'status_filter', 'priority_filter', 'dependency_filter', 
                       'date_filter', 'image_filter', 'sort_option']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    return {
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'dependency_filter': dependency_filter,
        'date_filter': date_filter,
        'image_filter': image_filter,
        'sort_option': sort_option
    }


def apply_advanced_filters(tasks, filters):
    """Apply advanced filters to task list"""
    filtered_tasks = tasks.copy()
    
    # Apply search query
    if filters['search_query'].strip():
        search_results, _ = fuzzy_search_tasks(filtered_tasks, [], filters['search_query'])
        filtered_tasks = search_results
    
    # Apply status filter
    if filters['status_filter'] == 'Active':
        filtered_tasks = [task for task in filtered_tasks if task.get('status') not in ['DONE', 'APPROVED']]
    elif filters['status_filter'] != 'All':
        filtered_tasks = [task for task in filtered_tasks if task.get('status') == filters['status_filter']]
    
    # Apply priority filter
    if filters['priority_filter'] != 'All':
        priority_map = {'🔥 Critical (5)': 5, '🔴 High (4)': 4, '🟡 Normal (3)': 3, '🟢 Low (2)': 2, '⚪ Minimal (1)': 1}
        target_priority = priority_map.get(filters['priority_filter'])
        if target_priority:
            filtered_tasks = [task for task in filtered_tasks if task.get('priority') == target_priority]
    
    # Apply dependency filter
    if filters['dependency_filter'] != 'All':
        if filters['dependency_filter'] == 'No Dependencies':
            filtered_tasks = [task for task in filtered_tasks if not task.get('dependencies')]
        elif filters['dependency_filter'] == 'Has Dependencies':
            filtered_tasks = [task for task in filtered_tasks if task.get('dependencies')]
        elif filters['dependency_filter'] == 'Blocked by Dependencies':
            # This would require checking if dependencies are completed
            # For now, just show tasks with dependencies
            filtered_tasks = [task for task in filtered_tasks if task.get('dependencies')]
    
    # Apply date filter
    if filters['date_filter'] != 'All Time':
        now = datetime.now()
        
        if filters['date_filter'] == 'Last 7 days':
            cutoff = now - timedelta(days=7)
        elif filters['date_filter'] == 'Last 30 days':
            cutoff = now - timedelta(days=30)
        elif filters['date_filter'] == 'Last 90 days':
            cutoff = now - timedelta(days=90)
        else:
            cutoff = None
        
        if cutoff:
            def is_recent(task):
                created_date = task.get('created_date')
                if not created_date:
                    return False
                try:
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    return created_dt.replace(tzinfo=None) >= cutoff
                except:
                    return False
            
            filtered_tasks = [task for task in filtered_tasks if is_recent(task)]
    
    # Apply image filter
    if filters['image_filter'] != 'All':
        if filters['image_filter'] == 'With Images':
            filtered_tasks = [task for task in filtered_tasks if task.get('image') and task.get('image').strip()]
        elif filters['image_filter'] == 'Without Images':
            filtered_tasks = [task for task in filtered_tasks if not (task.get('image') and task.get('image').strip())]
    
    # Apply sorting
    sort_option = filters['sort_option']
    if sort_option == 'Dependencies & Priority':
        filtered_tasks = sort_tasks_by_dependencies_and_priority(filtered_tasks)
    elif sort_option == 'Priority (High to Low)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('priority', 3), reverse=True)
    elif sort_option == 'Priority (Low to High)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('priority', 3))
    elif sort_option == 'Created Date (Newest)':
        def sort_by_date_desc(task):
            created_date = task.get('created_date', '')
            try:
                return datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            except:
                return datetime.min.replace(tzinfo=None)
        filtered_tasks = sorted(filtered_tasks, key=sort_by_date_desc, reverse=True)
    elif sort_option == 'Created Date (Oldest)':
        def sort_by_date_asc(task):
            created_date = task.get('created_date', '')
            try:
                return datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            except:
                return datetime.max.replace(tzinfo=None)
        filtered_tasks = sorted(filtered_tasks, key=sort_by_date_asc)
    elif sort_option == 'Status':
        status_order = {'TODO': 1, 'IN_PROGRESS': 2, 'BLOCKED': 3, 'REVIEW': 4, 'DONE': 5, 'APPROVED': 6}
        filtered_tasks = sorted(filtered_tasks, key=lambda x: status_order.get(x.get('status', 'TODO'), 0))
    elif sort_option == 'Title (A-Z)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('title', '').lower())
    elif sort_option == 'Title (Z-A)':
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('title', '').lower(), reverse=True)
    
    return filtered_tasks 