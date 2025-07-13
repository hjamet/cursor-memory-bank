import { z } from 'zod';
import { incrementImplementationCount } from '../lib/workflow_state.js';
import { taskManager } from '../lib/task_manager.js';

/**
 * MCP Tool: Increment Implementation Counter
 * 
 * Increments the implementation step counter and automatically generates
 * README update tasks every 10 implementations.
 */

const incrementImplementationSchema = z.object({
    trigger_reason: z.string().optional().describe('Optional reason for triggering this increment (for logging)')
});

async function incrementImplementation(args) {
    try {
        // Validate arguments
        const validatedArgs = incrementImplementationSchema.parse(args);

        // Increment the counter and check for README task trigger
        const result = await incrementImplementationCount();

        // If we should trigger a README task, generate it
        let readmeTask = null;
        if (result.shouldTriggerReadmeTask) {
            try {
                await taskManager.loadTasks();
                readmeTask = await taskManager.generateReadmeTask(result.count);
            } catch (error) {
                console.warn(`Failed to generate README task: ${error.message}`);
                // Don't fail the whole operation if README task generation fails
            }
        }

        // Prepare response
        const response = {
            status: 'success',
            implementation_count: result.count,
            readme_task_triggered: result.shouldTriggerReadmeTask,
            trigger_reason: result.triggerReason,
            message: `Implementation counter incremented to ${result.count}`,
            readme_task: readmeTask ? {
                id: readmeTask.id,
                title: readmeTask.title,
                priority: readmeTask.priority
            } : null
        };

        // Add context information
        if (result.shouldTriggerReadmeTask && readmeTask) {
            response.message += `. README update task #${readmeTask.id} automatically generated.`;
        }

        if (validatedArgs.trigger_reason) {
            console.log(`[ImplementationCounter] Incremented (${validatedArgs.trigger_reason}): ${result.count}`);
        }

        return response;

    } catch (error) {
        return {
            status: 'error',
            message: `Failed to increment implementation counter: ${error.message}`,
            implementation_count: null,
            readme_task_triggered: false,
            trigger_reason: null,
            readme_task: null
        };
    }
}

export default {
    name: 'increment_implementation',
    description: 'Increment the implementation step counter and automatically generate README tasks every 10 steps',
    inputSchema: incrementImplementationSchema,
    handler: incrementImplementation
}; 