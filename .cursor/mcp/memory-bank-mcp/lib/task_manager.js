import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const tasksFilePath = path.join(__dirname, '..', '..', '..', 'workflow', 'tasks.md');

// This is a simplified parser. A more robust solution would use a markdown parser.
function parseTasks(content) {
    const tasks = [];
    const lines = content.split('\n');
    let currentTask = null;

    for (const line of lines) {
        const taskMatch = line.match(/^([⚪️🟡🟢🔴🔵])\s*\*\*(.*?)\*\*/);
        if (taskMatch) {
            if (currentTask) {
                tasks.push(currentTask);
            }
            const statusMap = {
                '⚪️': 'TODO',
                '🟡': 'IN_PROGRESS',
                '🟢': 'DONE',
                '🔴': 'BLOCKED',
                '🔵': 'REVIEW',
            };
            currentTask = {
                title: taskMatch[2].trim(),
                status: statusMap[taskMatch[1]],
                description: '',
                subTasks: [],
            };
        } else if (currentTask && line.trim().startsWith('*   **Description**:')) {
            currentTask.description = line.replace('*   **Description**:', '').trim();
        }
    }
    if (currentTask) {
        tasks.push(currentTask);
    }
    return tasks;
}

export async function readTasks() {
    try {
        const content = await fs.readFile(tasksFilePath, 'utf8');
        return parseTasks(content);
    } catch (error) {
        if (error.code === 'ENOENT') {
            return []; // Return empty array if file doesn't exist
        }
        throw error;
    }
}
