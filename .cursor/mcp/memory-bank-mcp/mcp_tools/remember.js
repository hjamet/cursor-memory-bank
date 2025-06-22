import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { readUserbrief } from '../lib/userbrief_manager.js';
import { readTasks } from '../lib/task_manager.js';
import { encodeText, findSimilarMemories } from '../lib/semantic_search.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const memoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'agent_memory.json');
const longTermMemoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'long_term_memory.json');
const MAX_MEMORIES = 100;

async function getPossibleNextSteps() {
    try {
        const userbrief = await readUserbrief();
        if (userbrief && userbrief.requests && userbrief.requests.some(r => r.status === 'new' || r.status === 'in_progress')) {
            return ['task-decomposition'];
        }

        const tasks = await readTasks();
        if (tasks && tasks.some(t => t.status === 'TODO' || t.status === 'IN_PROGRESS')) {
            return ['implementation'];
        }

        // Default when no work is pending
        return ['context-update', 'system'];

    } catch (error) {
        // This can happen on first run if no context files exist.
        // In this case, the only valid next step is to start the process.
        if (error.code === 'ENOENT') {
            return ['START'];
        }
        console.error(`Error determining next steps: ${error.message}`);
        // Fallback to a safe default
        return ['system'];
    }
}

async function remember(args) {
    const { past, present, future, long_term_memory } = args;

    // Handle long-term memory with semantic encoding
    let longTermMemories = [];
    let currentLongTermMemory = null;

    // Read existing long-term memories
    try {
        const data = await fs.readFile(longTermMemoryFilePath, 'utf8');
        const parsed = JSON.parse(data);
        longTermMemories = Array.isArray(parsed) ? parsed : [parsed];
    } catch (error) {
        if (error.code !== 'ENOENT') {
            throw new Error(`Failed to read long-term memory file: ${error.message}`);
        }
        // File doesn't exist, start with empty array
        longTermMemories = [];
    }

    // Add new long-term memory if provided
    if (long_term_memory) {
        try {
            // Encode the new memory
            const embedding = await encodeText(long_term_memory);
            const newMemory = {
                content: long_term_memory,
                timestamp: new Date().toISOString(),
                embedding: embedding
            };

            longTermMemories.push(newMemory);
            currentLongTermMemory = long_term_memory;

            // Save updated memories
            await fs.mkdir(path.dirname(longTermMemoryFilePath), { recursive: true });
            await fs.writeFile(longTermMemoryFilePath, JSON.stringify(longTermMemories, null, 2), 'utf8');
        } catch (error) {
            throw new Error(`Failed to write long-term memory file: ${error.message}`);
        }
    }

    // Read preferences from userbrief (status === 'preference')
    let preferences = [];
    try {
        const userbriefData = await readUserbrief();
        if (userbriefData && userbriefData.requests) {
            preferences = userbriefData.requests
                .filter(req => req.status === 'preference')
                .map(req => req.content);
        }
    } catch (error) {
        // console.warn(`[Remember] Could not read preferences from userbrief: ${error.message}`);
        // Do not throw; failing to read userbrief should not stop the remember tool.
    }

    let memories = [];
    try {
        const data = await fs.readFile(memoryFilePath, 'utf8');
        memories = JSON.parse(data);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            throw new Error(`Failed to read memory file: ${error.message}`);
        }
        // File doesn't exist, will be created.
    }

    const newMemory = {
        timestamp: new Date().toISOString(),
        past,
        present,
        future,
    };

    memories.push(newMemory);

    if (memories.length > MAX_MEMORIES) {
        memories = memories.slice(memories.length - MAX_MEMORIES);
    }

    try {
        await fs.mkdir(path.dirname(memoryFilePath), { recursive: true });
        await fs.writeFile(memoryFilePath, JSON.stringify(memories, null, 2), 'utf8');
    } catch (error) {
        throw new Error(`Failed to write memory file: ${error.message}`);
    }

    const recentMemories = memories.slice(-10); // Get 10 most recent working memories
    const lastMemory = memories[memories.length - 1];
    const possible_next_steps = await getPossibleNextSteps();

    // Find semantically similar long-term memories based on the last "future" 
    let semanticLongTermMemories = [];
    if (lastMemory && lastMemory.future && longTermMemories.length > 0) {
        semanticLongTermMemories = await findSimilarMemories(lastMemory.future, longTermMemories, 3);
    }

    const response = {
        message: "Memory successfully recorded.",
        current_state: lastMemory ? lastMemory.future : "No current state.",
        possible_next_steps: possible_next_steps,
        user_preferences: preferences, // Always show preferences
        long_term_memory: currentLongTermMemory, // Only the newly added one, if any
        recent_working_memories: recentMemories, // 10 most recent working memories
        semantic_long_term_memories: semanticLongTermMemories, // 3 most semantically relevant long-term memories
        total_memories_count: memories.length,
        total_long_term_memories_count: longTermMemories.length
    };

    return {
        content: [{
            type: 'text',
            text: JSON.stringify(response, null, 2)
        }]
    };
}

export const rememberSchema = {
    past: z.string().describe("A description of what the agent originally planned to do."),
    present: z.string().describe("A description of what the agent actually did, any problems encountered, and decisions made."),
    future: z.string().describe("A description of what the agent plans to do next."),
    long_term_memory: z.string().optional().describe("Critical project information to be stored persistently (e.g., database schemas, architectural decisions). If provided, this will overwrite any existing long-term memory."),
};

export { remember as handleRemember }; 