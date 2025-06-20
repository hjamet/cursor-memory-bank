import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const memoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'agent_memory.json');
const MAX_MEMORIES = 100;

async function remember(args) {
    const { past, present, future } = args;

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

    return {
        message: "Memory successfully recorded.",
        recent_memories: recentMemories,
    };
}

const rememberTool = {
    name: "remember",
    description: "Records a memory of the agent's state (past, present, future) and returns the last 15 memories. This tool replaces the need for activeContext.md.",
    args: z.object({
        past: z.string().describe("A description of what the agent originally planned to do."),
        present: z.string().describe("A description of what the agent actually did, any problems encountered, and decisions made."),
        future: z.string().describe("A description of what the agent plans to do next."),
    }),
    run: remember,
};

export default rememberTool; 