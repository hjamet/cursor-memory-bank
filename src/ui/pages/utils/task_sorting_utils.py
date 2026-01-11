"""
Task sorting and dependency utilities.
Handles task sorting by dependencies and priority calculations.
"""


def sort_tasks_by_dependencies_and_priority(tasks):
    """Sort tasks by dependencies first, then by priority"""
    # Create a dependency graph
    task_dict = {str(task.get('id', task.get('task_id'))): task for task in tasks}
    
    def get_dependency_level(task_id, visited=None):
        if visited is None:
            visited = set()
        
        if task_id in visited:
            return 0  # Circular dependency, treat as level 0
        
        visited.add(task_id)
        task = task_dict.get(str(task_id))
        if not task:
            return 0
        
        dependencies = task.get('dependencies', [])
        if not dependencies:
            return 0
        
        max_dep_level = 0
        for dep_id in dependencies:
            dep_level = get_dependency_level(str(dep_id), visited.copy())
            max_dep_level = max(max_dep_level, dep_level)
        
        return max_dep_level + 1
    
    # Sort by dependency level first, then by priority (descending)
    def sort_key(task):
        task_id = str(task.get('id', task.get('task_id')))
        dep_level = get_dependency_level(task_id)
        priority = task.get('priority', 3)
        return (dep_level, -priority)  # Negative priority for descending order
    
    return sorted(tasks, key=sort_key) 