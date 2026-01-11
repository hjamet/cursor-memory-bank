/**
 * Circular Dependency Validation Module
 * Provides utilities to detect and prevent circular dependencies in task graphs
 * 
 * This module implements a robust DFS-based cycle detection algorithm that can identify
 * all circular dependency chains in a task system. It's designed to be used as a 
 * preventive validation layer before task creation or dependency updates.
 */

/**
 * Detects circular dependencies in a task graph using Depth-First Search
 * @param {Array} tasks - All tasks in the system
 * @param {Map} taskMap - Task lookup map for efficient access
 * @returns {Array} Array of circular dependency chains, each chain is an array of task IDs
 */
export function detectCircularDependencies(tasks, taskMap) {
    const visited = new Set();
    const recursionStack = new Set();
    const cycles = [];

    function dfs(taskId, path = []) {
        if (recursionStack.has(taskId)) {
            // Found a cycle - extract the circular portion
            const cycleStart = path.indexOf(taskId);
            const cycle = path.slice(cycleStart).concat([taskId]);
            cycles.push(cycle);
            return;
        }

        if (visited.has(taskId)) return;

        visited.add(taskId);
        recursionStack.add(taskId);
        path.push(taskId);

        const task = taskMap.get(taskId);
        if (task && task.dependencies) {
            task.dependencies.forEach(depId => {
                dfs(depId, [...path]);
            });
        }

        recursionStack.delete(taskId);
    }

    // Check all tasks for cycles
    tasks.forEach(task => {
        if (!visited.has(task.id)) {
            dfs(task.id);
        }
    });

    return cycles;
}

/**
 * Validates that adding new dependencies won't create circular dependencies
 * @param {Array} tasks - All existing tasks
 * @param {number} taskId - ID of the task receiving new dependencies
 * @param {Array} newDependencies - Array of new dependency IDs to add
 * @returns {Object} Validation result with status and details
 */
export function validateNoCycles(tasks, taskId, newDependencies) {
    // Create a temporary task map for validation
    const taskMap = new Map(tasks.map(task => [task.id, task]));

    // Find the target task
    const targetTask = taskMap.get(taskId);
    if (!targetTask) {
        return {
            isValid: false,
            error: `Task with ID ${taskId} not found`,
            cycles: []
        };
    }

    // Create a temporary modified task with new dependencies
    const modifiedTask = {
        ...targetTask,
        dependencies: [...(targetTask.dependencies || []), ...newDependencies]
    };

    // Update the task map with the modified task
    taskMap.set(taskId, modifiedTask);

    // Detect cycles in the modified graph
    const cycles = detectCircularDependencies(tasks, taskMap);

    // Filter cycles that involve the modified task
    const relevantCycles = cycles.filter(cycle => cycle.includes(taskId));

    if (relevantCycles.length > 0) {
        return {
            isValid: false,
            error: 'Circular dependency detected',
            cycles: relevantCycles,
            affectedTask: taskId,
            newDependencies: newDependencies
        };
    }

    return {
        isValid: true,
        error: null,
        cycles: []
    };
}

/**
 * Validates that replacing dependencies won't create circular dependencies
 * @param {Array} tasks - All existing tasks
 * @param {number} taskId - ID of the task whose dependencies are being replaced
 * @param {Array} replacementDependencies - Array of new dependency IDs to replace existing ones
 * @returns {Object} Validation result with status and details
 */
export function validateReplacementDependencies(tasks, taskId, replacementDependencies) {
    // Create a temporary task map for validation
    const taskMap = new Map(tasks.map(task => [task.id, task]));

    // Find the target task
    const targetTask = taskMap.get(taskId);
    if (!targetTask) {
        return {
            isValid: false,
            error: `Task with ID ${taskId} not found`,
            cycles: []
        };
    }

    // Create a temporary modified task with replacement dependencies
    const modifiedTask = {
        ...targetTask,
        dependencies: replacementDependencies || []
    };

    // Update the task map with the modified task
    taskMap.set(taskId, modifiedTask);

    // Detect cycles in the modified graph
    const cycles = detectCircularDependencies(tasks, taskMap);

    // Filter cycles that involve the modified task
    const relevantCycles = cycles.filter(cycle => cycle.includes(taskId));

    if (relevantCycles.length > 0) {
        return {
            isValid: false,
            error: 'Circular dependency detected',
            cycles: relevantCycles,
            affectedTask: taskId,
            replacementDependencies: replacementDependencies
        };
    }

    return {
        isValid: true,
        error: null,
        cycles: []
    };
}

/**
 * Formats circular dependency cycles into human-readable error messages
 * @param {Array} cycles - Array of cycles (each cycle is an array of task IDs)
 * @param {Map} taskMap - Task lookup map for getting task titles
 * @returns {Array} Array of formatted error messages
 */
export function formatCycleErrors(cycles, taskMap) {
    return cycles.map((cycle, index) => {
        const cycleDescription = cycle.map(taskId => {
            const task = taskMap.get(taskId);
            return task ? `Task ${taskId} (${task.title})` : `Task ${taskId} (Unknown)`;
        }).join(' → ');

        return `Cycle ${index + 1}: ${cycleDescription}`;
    });
}

/**
 * Comprehensive validation function for new task creation
 * @param {Array} tasks - All existing tasks
 * @param {Array} proposedDependencies - Dependencies for the new task
 * @returns {Object} Validation result
 */
export function validateNewTaskDependencies(tasks, proposedDependencies) {
    if (!proposedDependencies || proposedDependencies.length === 0) {
        return {
            isValid: true,
            error: null,
            cycles: []
        };
    }

    // Check if all proposed dependencies exist
    const taskIds = new Set(tasks.map(t => t.id));
    const missingDependencies = proposedDependencies.filter(depId => !taskIds.has(depId));

    if (missingDependencies.length > 0) {
        return {
            isValid: false,
            error: `Dependencies reference non-existent tasks: ${missingDependencies.join(', ')}`,
            cycles: [],
            missingDependencies: missingDependencies
        };
    }

    // For new tasks, we only need to check if the dependencies themselves form cycles
    // The new task can't create a cycle since it doesn't exist yet and nothing depends on it
    const taskMap = new Map(tasks.map(task => [task.id, task]));
    const dependencySubgraph = tasks.filter(task => proposedDependencies.includes(task.id));
    const cycles = detectCircularDependencies(dependencySubgraph, taskMap);

    if (cycles.length > 0) {
        return {
            isValid: false,
            error: 'Proposed dependencies contain circular references',
            cycles: cycles,
            proposedDependencies: proposedDependencies
        };
    }

    return {
        isValid: true,
        error: null,
        cycles: []
    };
}

/**
 * Advanced cycle detection with detailed analysis
 * @param {Array} tasks - All tasks in the system
 * @returns {Object} Detailed analysis of the dependency graph
 */
export function analyzeDependencyGraph(tasks) {
    const taskMap = new Map(tasks.map(task => [task.id, task]));
    const cycles = detectCircularDependencies(tasks, taskMap);

    // Analyze graph properties
    const totalTasks = tasks.length;
    const tasksWithDependencies = tasks.filter(t => t.dependencies && t.dependencies.length > 0).length;
    const totalDependencyEdges = tasks.reduce((sum, t) => sum + (t.dependencies ? t.dependencies.length : 0), 0);

    // Find strongly connected components (tasks involved in cycles)
    const tasksInCycles = new Set();
    cycles.forEach(cycle => {
        cycle.forEach(taskId => tasksInCycles.add(taskId));
    });

    return {
        isHealthy: cycles.length === 0,
        totalTasks: totalTasks,
        tasksWithDependencies: tasksWithDependencies,
        totalDependencyEdges: totalDependencyEdges,
        cycleCount: cycles.length,
        cycles: cycles,
        tasksInCycles: Array.from(tasksInCycles),
        cycleDetails: cycles.map(cycle => ({
            length: cycle.length - 1, // Subtract 1 because the cycle includes the starting node twice
            tasks: cycle.slice(0, -1), // Remove the duplicate starting node
            description: formatCycleErrors([cycle], taskMap)[0]
        }))
    };
} 