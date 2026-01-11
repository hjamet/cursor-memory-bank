import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TASKS_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'tasks.json');

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

async function writeTasks(tasks) {
    await fs.writeFile(TASKS_FILE_PATH, JSON.stringify(tasks, null, 2), 'utf-8');
}

export async function handleUpdateTaskStatus(params) {
    try {
        const { task_id, status, comment } = params;

        const tasks = await readTasks();
        const taskIndex = tasks.findIndex(task => task.id === task_id);

        if (taskIndex === -1) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Task with ID ${task_id} not found`,
                    }, null, 2)
                }]
            };
        }

        const updatedTask = { ...tasks[taskIndex] };
        updatedTask.status = status;
        updatedTask.updated_date = new Date().toISOString();

        if (comment) {
            const newComment = {
                timestamp: updatedTask.updated_date,
                comment: comment,
                status_change: status,
            };
            updatedTask.comments = updatedTask.comments || [];
            updatedTask.comments.push(newComment);
            updatedTask.last_comment = newComment.comment;
            updatedTask.last_comment_timestamp = newComment.timestamp;
        }

        tasks[taskIndex] = updatedTask;

        await writeTasks(tasks);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'success',
                    message: `Task ${task_id} status updated to ${status}`,
                    updated_task: updatedTask,
                }, null, 2)
            }]
        };

    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `An unexpected error occurred: ${error.message}`,
                    stack: error.stack
                }, null, 2)
            }]
        };
    }
} 