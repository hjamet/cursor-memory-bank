import { z } from 'zod';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get project root directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../../../..');

// Valid context file names and their paths
const CONTEXT_FILES = {
    'activeContext': '.cursor/memory-bank/context/activeContext.md',
    'projectBrief': '.cursor/memory-bank/context/projectBrief.md',
    'techContext': '.cursor/memory-bank/context/techContext.md'
};

// Zod schema for the read_memory tool
export const readMemorySchema = {
    context_file: z.enum(['activeContext', 'projectBrief', 'techContext'])
        .describe('Name of context file to read (activeContext, projectBrief, techContext)')
};

/**
 * Handles the read_memory tool call
 * Reads complete content of specified context file
 * 
 * @param {Object} params - Tool parameters
 * @param {string} params.context_file - Name of context file to read (activeContext, projectBrief, techContext)
 * @returns {Object} Tool response with file content or error
 */
export async function handleReadMemory(params) {
    try {
        const { context_file } = params;

        console.log(`[ReadMemory] Reading context file: ${context_file}`);

        // Validate context file name
        if (!CONTEXT_FILES[context_file]) {
            const validFiles = Object.keys(CONTEXT_FILES).join(', ');
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Invalid context file name: ${context_file}. Valid options: ${validFiles}`,
                        content: null
                    }, null, 2)
                }]
            };
        }

        // Get full file path
        const filePath = path.join(projectRoot, CONTEXT_FILES[context_file]);

        // Check if file exists
        if (!fs.existsSync(filePath)) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Context file not found: ${filePath}`,
                        suggestion: 'Use edit_memory tool to create this file with initial content',
                        content: null
                    }, null, 2)
                }]
            };
        }

        // Read file content
        const content = fs.readFileSync(filePath, 'utf8');

        console.log(`[ReadMemory] Successfully read ${content.length} characters from ${context_file}`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'success',
                    message: `Successfully read context file: ${context_file}`,
                    file_path: CONTEXT_FILES[context_file],
                    content_length: content.length,
                    content: content
                }, null, 2)
            }]
        };

    } catch (error) {
        console.error('[ReadMemory] Error:', error);
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error reading context file: ${error.message}`,
                    content: null
                }, null, 2)
            }]
        };
    }
} 