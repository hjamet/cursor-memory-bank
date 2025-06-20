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

// Zod schema for the edit_memory tool
export const editMemorySchema = {
    context_file: z.enum(['activeContext', 'projectBrief', 'techContext'])
        .describe('Name of context file to edit (activeContext, projectBrief, techContext)'),
    content: z.string().describe('New content to completely replace existing content')
};

/**
 * Handles the edit_memory tool call
 * Completely replaces content of specified context file
 * Creates file and directories if they don't exist
 * 
 * @param {Object} params - Tool parameters
 * @param {string} params.context_file - Name of context file to edit (activeContext, projectBrief, techContext)
 * @param {string} params.content - New content to completely replace existing content
 * @returns {Object} Tool response with success confirmation or error
 */
export async function handleEditMemory(params) {
    try {
        const { context_file, content } = params;

        console.log(`[EditMemory] Editing context file: ${context_file} (${content.length} characters)`);

        // Validate context file name
        if (!CONTEXT_FILES[context_file]) {
            const validFiles = Object.keys(CONTEXT_FILES).join(', ');
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Invalid context file name: ${context_file}. Valid options: ${validFiles}`,
                        operation: 'edit_failed'
                    }, null, 2)
                }]
            };
        }

        // Get full file path
        const filePath = path.join(projectRoot, CONTEXT_FILES[context_file]);
        const dirPath = path.dirname(filePath);

        // Create directory if it doesn't exist
        if (!fs.existsSync(dirPath)) {
            console.log(`[EditMemory] Creating directory: ${dirPath}`);
            fs.mkdirSync(dirPath, { recursive: true });
        }

        // Check if file exists to determine if this is creation or replacement
        const fileExists = fs.existsSync(filePath);
        const operation = fileExists ? 'replaced' : 'created';

        // Get original content length for comparison (if file exists)
        let originalLength = 0;
        if (fileExists) {
            try {
                const originalContent = fs.readFileSync(filePath, 'utf8');
                originalLength = originalContent.length;
            } catch (readError) {
                console.warn(`[EditMemory] Could not read original file for comparison: ${readError.message}`);
            }
        }

        // Write new content (completely replace)
        fs.writeFileSync(filePath, content, 'utf8');

        console.log(`[EditMemory] Successfully ${operation} ${context_file}: ${originalLength} → ${content.length} characters`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'success',
                    message: `Successfully ${operation} context file: ${context_file}`,
                    operation: operation,
                    file_path: CONTEXT_FILES[context_file],
                    content_length: content.length,
                    original_length: originalLength,
                    change: content.length - originalLength
                }, null, 2)
            }]
        };

    } catch (error) {
        console.error('[EditMemory] Error:', error);
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error editing context file: ${error.message}`,
                    operation: 'edit_failed'
                }, null, 2)
            }]
        };
    }
} 