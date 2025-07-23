import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { findSimilarMemories } from './semantic_search.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths to context files
const contextDir = path.join(__dirname, '..', '..', '..', 'memory-bank', 'context');
const workflowDir = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow');

async function readFileIfExists(filePath) {
    try {
        return await fs.readFile(filePath, 'utf8');
    } catch (error) {
        if (error.code === 'ENOENT') {
            return null;
        }
        throw error;
    }
}

export async function readMemoryContext() {
    const context = {};

    // Read README.md as project context
    context.project_context = await readFileIfExists(path.join(__dirname, '..', '..', '..', 'README.md'));

    // Read agent memory
    const memoryFilePath = path.join(workflowDir, 'agent_memory.json');
    const longTermMemoryFilePath = path.join(workflowDir, 'long_term_memory.json');

    let agentMemory = null;
    let longTermMemory = null;

    try {
        const memoryData = await fs.readFile(memoryFilePath, 'utf8');
        agentMemory = JSON.parse(memoryData);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            console.warn(`Could not read agent memory: ${error.message}`);
        }
    }

    try {
        const longTermData = await fs.readFile(longTermMemoryFilePath, 'utf8');
        longTermMemory = JSON.parse(longTermData);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            console.warn(`Could not read long-term memory: ${error.message}`);
        }
    }

    // Get recent memories (last 10)
    context.recent_memories = agentMemory ? agentMemory.slice(-10) : [];

    // Get previous rule from last memory
    if (agentMemory && agentMemory.length > 0) {
        const lastMemory = agentMemory[agentMemory.length - 1];
        // Try to extract rule name from the future field
        const futureText = lastMemory.future || '';
        const ruleMatch = futureText.match(/(\w+-\w+|\w+)\s+(rule|step)/i);
        context.previous_rule = ruleMatch ? ruleMatch[1] : 'start-workflow';
    } else {
        context.previous_rule = 'start-workflow';
    }

    // Get relevant long-term memories using semantic search
    let relevantLongTermMemories = [];
    if (agentMemory && agentMemory.length > 0 && longTermMemory) {
        const lastMemory = agentMemory[agentMemory.length - 1];
        if (lastMemory.future) {
            try {
                const longTermMemories = Array.isArray(longTermMemory) ? longTermMemory : [longTermMemory];
                relevantLongTermMemories = await findSimilarMemories(lastMemory.future, longTermMemories, 10);
            } catch (error) {
                console.warn(`Could not perform semantic search: ${error.message}`);
                relevantLongTermMemories = Array.isArray(longTermMemory) ? longTermMemory.slice(0, 3) : [longTermMemory];
            }
        }
    }
    context.relevant_long_term_memories = relevantLongTermMemories;

    // Get current tasks summary
    try {
        const tasksFilePath = path.join(workflowDir, 'tasks.md');
        const tasksContent = await readFileIfExists(tasksFilePath);
        if (tasksContent) {
            // Extract task summaries (simplified)
            const todoTasks = (tasksContent.match(/⚪️.*$/gm) || []).length;
            const inProgressTasks = (tasksContent.match(/🟡.*$/gm) || []).length;
            const doneTasks = (tasksContent.match(/🟢.*$/gm) || []).length;

            context.current_tasks_summary = `TODO: ${todoTasks}, IN_PROGRESS: ${inProgressTasks}, DONE: ${doneTasks}`;
        } else {
            context.current_tasks_summary = 'No tasks file found';
        }
    } catch (error) {
        context.current_tasks_summary = `Error reading tasks: ${error.message}`;
    }

    return context;
} 