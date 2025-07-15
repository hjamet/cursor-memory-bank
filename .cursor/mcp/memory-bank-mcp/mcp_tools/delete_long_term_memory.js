import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to long-term memory file
const longTermMemoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'long_term_memory.json');

/**
 * MCP Tool Schema for delete_long_term_memory
 * Defines the input parameters and validation rules
 */
export const deleteLongTermMemorySchema = {
    id: z.string().describe("LONG TERM MEMORY ID: The unique identifier (timestamp) of the long-term memory to delete from the persistent storage. This tool allows the agent to remove obsolete, incorrect, or no longer relevant long-term memories to maintain a clean and pertinent memory base. The ID corresponds to the timestamp field of the memory entry in the long_term_memory.json file.")
};

/**
 * Delete a specific long-term memory by its ID
 * 
 * This tool allows the agent to remove obsolete or incorrect long-term memories
 * from the persistent storage. It performs validation, locates the memory,
 * removes it, and provides detailed feedback about the operation.
 * 
 * @param {Object} args - The arguments for the delete operation
 * @param {string} args.id - The unique identifier of the memory to delete
 * @returns {Object} Tool response with operation status and details
 */
async function deleteLongTermMemory(args) {
    try {
        // Validate input parameters
        const validatedArgs = deleteLongTermMemorySchema.parse(args);
        const { id } = validatedArgs;

        // Read existing long-term memories
        let longTermMemories = [];
        let fileExists = true;

        try {
            const data = await fs.readFile(longTermMemoryFilePath, 'utf8');
            const parsed = JSON.parse(data);
            longTermMemories = Array.isArray(parsed) ? parsed : [parsed];
        } catch (error) {
            if (error.code === 'ENOENT') {
                fileExists = false;
                return {
                    status: 'error',
                    error_type: 'file_not_found',
                    message: 'No long-term memory file found. No memories exist to delete.',
                    memory_id: id,
                    total_memories_remaining: 0
                };
            } else {
                throw new Error(`Failed to read long-term memory file: ${error.message}`);
            }
        }

        // Validate memory ID format (should be ISO timestamp with optional microseconds)
        const timestampRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3,6})?Z?$/;
        if (!timestampRegex.test(id)) {
            return {
                status: 'error',
                error_type: 'invalid_format',
                message: `Invalid memory ID format. Expected ISO timestamp format (e.g., "2025-07-13T18:26:37.454Z" or "2025-06-25T01:15:10.224858"), got: "${id}"`,
                memory_id: id,
                total_memories_remaining: longTermMemories.length
            };
        }

        // Find the memory to delete
        const memoryIndex = longTermMemories.findIndex(memory => memory.timestamp === id);

        if (memoryIndex === -1) {
            // Memory not found
            const availableIds = longTermMemories.map(m => m.timestamp).slice(0, 5); // Show first 5 IDs
            return {
                status: 'error',
                error_type: 'memory_not_found',
                message: `No long-term memory found with ID: "${id}"`,
                memory_id: id,
                total_memories_remaining: longTermMemories.length,
                available_memory_ids_sample: availableIds,
                suggestion: availableIds.length > 0 ?
                    `Available memory IDs include: ${availableIds.join(', ')}${longTermMemories.length > 5 ? ' (and others)' : ''}` :
                    'No memories are currently stored.'
            };
        }

        // Extract the memory to be deleted (for logging and response)
        const memoryToDelete = longTermMemories[memoryIndex];
        const deletedMemoryPreview = {
            timestamp: memoryToDelete.timestamp,
            content_preview: memoryToDelete.content ?
                (memoryToDelete.content.length > 100 ?
                    memoryToDelete.content.substring(0, 100) + '...' :
                    memoryToDelete.content) :
                'No content',
            content_length: memoryToDelete.content ? memoryToDelete.content.length : 0
        };

        // Remove the memory from the array
        longTermMemories.splice(memoryIndex, 1);

        // Save the updated memories array
        try {
            await fs.mkdir(path.dirname(longTermMemoryFilePath), { recursive: true });
            await fs.writeFile(longTermMemoryFilePath, JSON.stringify(longTermMemories, null, 2), 'utf8');
        } catch (error) {
            throw new Error(`Failed to save updated long-term memory file: ${error.message}`);
        }

        // Return success response with detailed information
        return {
            status: 'success',
            message: `Successfully deleted long-term memory with ID: "${id}"`,
            memory_id: id,
            deleted_memory: deletedMemoryPreview,
            total_memories_remaining: longTermMemories.length,
            operation_timestamp: new Date().toISOString(),
            file_updated: true
        };

    } catch (error) {
        // Handle validation errors and other exceptions
        if (error.name === 'ZodError') {
            return {
                status: 'error',
                error_type: 'validation_error',
                message: 'Invalid input parameters',
                details: error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '),
                memory_id: args.id || 'undefined'
            };
        }

        // Handle other errors
        return {
            status: 'error',
            error_type: 'internal_error',
            message: `Failed to delete long-term memory: ${error.message}`,
            memory_id: args.id || 'undefined'
        };
    }
}

/**
 * Main handler function for the delete_long_term_memory tool
 * @param {Object} args - Tool arguments
 * @returns {Object} Tool response
 */
export async function handleDeleteLongTermMemory(args) {
    return await deleteLongTermMemory(args);
}

/**
 * Default export for MCP tool registration
 */
export default {
    name: 'delete_long_term_memory',
    description: 'Delete a specific long-term memory by its ID (timestamp). Takes an id parameter with the unique identifier of the memory to delete.',
    schema: deleteLongTermMemorySchema,
    handler: handleDeleteLongTermMemory
}; 