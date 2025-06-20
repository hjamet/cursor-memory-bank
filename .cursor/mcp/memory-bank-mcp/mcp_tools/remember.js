import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { readUserbriefData } from '../lib/userbrief_manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const memoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'agent_memory.json');
const longTermMemoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'long_term_memory.json');
const MAX_MEMORIES = 100;

async function remember(args) {
    const { past, present, future, long_term_memory } = args;

    // Handle long-term memory
    let longTermMemoryContent = null;
    if (long_term_memory) {
        try {
            await fs.mkdir(path.dirname(longTermMemoryFilePath), { recursive: true });
            await fs.writeFile(longTermMemoryFilePath, JSON.stringify({ content: long_term_memory }, null, 2), 'utf8');
            longTermMemoryContent = long_term_memory;
        } catch (error) {
            throw new Error(`Failed to write long-term memory file: ${error.message}`);
        }
    } else {
        try {
            const data = await fs.readFile(longTermMemoryFilePath, 'utf8');
            longTermMemoryContent = JSON.parse(data).content;
        } catch (error) {
            if (error.code !== 'ENOENT') {
                throw new Error(`Failed to read long-term memory file: ${error.message}`);
            }
            // File doesn't exist, which is fine if no memory is being written.
        }
    }

    // Read pinned items from userbrief
    let pinnedItems = [];
    try {
        const userbriefData = readUserbriefData();
        if (userbriefData && userbriefData.requests) {
            pinnedItems = userbriefData.requests.filter(req => req.status === 'pinned');
        }
    } catch (error) {
        console.warn(`[Remember] Could not read pinned items from userbrief: ${error.message}`);
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

    const recentMemories = memories.slice(-15);
    const lastMemory = memories[memories.length - 1];

    return {
        message: "Memory successfully recorded.",
        current_state: lastMemory ? lastMemory.future : "No current state.",
        possible_next_rules: [], // To be implemented by the next_rule tool
        user_preferences: pinnedItems.map(item => item.content),
        long_term_memory: longTermMemoryContent,
        recent_memories: recentMemories,
    };
}

export const rememberSchema = {
    past: z.string().describe("A description of what the agent originally planned to do."),
    present: z.string().describe("A description of what the agent actually did, any problems encountered, and decisions made."),
    future: z.string().describe("A description of what the agent plans to do next."),
    long_term_memory: z.string().optional().describe("Critical project information to be stored persistently (e.g., database schemas, architectural decisions). If provided, this will overwrite any existing long-term memory."),
};

export { remember as handleRemember }; 