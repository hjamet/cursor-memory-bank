import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

// Use the absolute path that we know works
const TASKS_FILE_PATH = 'C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\memory-bank\\streamlit_app\\tasks.json';

async function readTasks() {
    try {
        const data = await fs.readFile(TASKS_FILE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            return [];
        }
        throw error;
    }
}

/**
 * Handles the get_next_tasks tool call
 * Returns the most urgent available tasks automatically determined by dependencies and priorities
 * 
 * @param {Object} params - Tool parameters (no parameters needed)
 * @returns {Object} Tool response with highest priority available tasks
 */
export async function handleGetNextTasks(params) {
    try {
        const { status, priority, limit = 10 } = params || {};

        const allTasks = await readTasks();

        // First, create a map for quick lookups
        const taskMap = new Map(allTasks.map(task => [task.id, task]));

        // Determine available tasks (dependencies met, not completed)
        let availableTasks = allTasks.filter(task => {
            if (task.status === 'DONE') return false; // Exclude completed
            if (!task.dependencies || task.dependencies.length === 0) return true; // No dependencies = available

            return task.dependencies.every(depId => {
                const depTask = taskMap.get(depId);
                return !depTask || depTask.status === 'DONE';
            });
        });

        // Sort by priority (highest first), then by status importance
        const statusPriority = { 'IN_PROGRESS': 1, 'TODO': 2, 'BLOCKED': 3, 'REVIEW': 4 };
        availableTasks.sort((a, b) => {
            // First by priority (5 = highest, 1 = lowest)
            const priorityDiff = (b.priority || 3) - (a.priority || 3);
            if (priorityDiff !== 0) return priorityDiff;

            // Then by status importance
            return (statusPriority[a.status] || 99) - (statusPriority[b.status] || 99);
        });

        // Find the highest priority level among available tasks
        const highestPriority = availableTasks.length > 0 ? availableTasks[0].priority || 3 : 3;

        // Return all tasks at the highest priority level
        const topPriorityTasks = availableTasks.filter(task => (task.priority || 3) === highestPriority);

        // Enhance tasks with dependency information
        const enhancedTasks = topPriorityTasks.map(task => {
            const dependencyDetails = (task.dependencies || []).map(depId => {
                const depTask = taskMap.get(depId);
                return depTask ? {
                    id: depTask.id,
                    title: depTask.title,
                    status: depTask.status
                } : {
                    id: depId,
                    title: 'Unknown Task',
                    status: 'NOT_FOUND'
                };
            });

            return {
                id: task.id,
                title: task.title,
                short_description: task.short_description,
                status: task.status,
                priority: task.priority,
                dependencies: task.dependencies || [],
                dependency_details: dependencyDetails,
                is_available: dependencyDetails.every(dep => dep.status === 'DONE' || dep.status === 'NOT_FOUND'),
                parent_id: task.parent_id,
                created_date: task.created_date,
                updated_date: task.updated_date
            };
        });

        // Generate statistics
        const statistics = {
            total_tasks: allTasks.length,
            available_tasks_count: availableTasks.length,
            tasks_returned: enhancedTasks.length,
            highest_priority_level: highestPriority,
            status_breakdown: allTasks.reduce((acc, task) => {
                acc[task.status] = (acc[task.status] || 0) + 1;
                return acc;
            }, {}),
            filters_applied: {
                automatic_priority_selection: true,
                excludes_completed: true,
                includes_blocked: true
            }
        };

        const response = {
            status: 'success',
            message: `Found ${enhancedTasks.length} highest priority available tasks (priority ${highestPriority})`,
            available_tasks: enhancedTasks,
            statistics,
            query_info: {
                selection_strategy: "All tasks at highest available priority level",
                priority_level_selected: highestPriority,
                total_available: availableTasks.length
            }
        };

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error retrieving next tasks: ${error.message}`,
                    available_tasks: [],
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message
                    }
                }, null, 2)
            }]
        };
    }
} 