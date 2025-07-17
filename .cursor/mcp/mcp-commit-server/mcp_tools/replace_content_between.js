import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Helper to get __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Calculate project root (assuming this file is in .cursor/mcp/mcp-commit-server/mcp_tools/)
const projectRoot = path.resolve(__dirname, '..', '..', '..', '..');

// Define the Zod schema for the tool's arguments
const replaceContentBetweenSchema = z.object({
    target_file: z.string().describe("The relative path to the file to be modified."),
    start_marker: z.string().describe("The string that marks the beginning of the content to replace."),
    end_marker: z.string().describe("The string that marks the end of the content to replace."),
    replacement_content: z.string().describe("The new content to insert between the markers.")
});

/**
 * Replaces the content between a start and end marker in a specified file.
 * This tool targets the first occurrence of the start_marker followed by the first
 * occurrence of the end_marker. If either marker is not found, the file will not be modified.
 *
 * @param {object} args - The arguments for the tool, matching the Zod schema.
 * @param {string} args.target_file - The path to the file to modify.
 * @param {string} args.start_marker - The starting delimiter.
 * @param {string} args.end_marker - The ending delimiter.
 * @param {string} args.replacement_content - The content to insert.
 * @returns {Promise<object>} A MCP response object with content field.
 */
async function replace_content_between({ target_file, start_marker, end_marker, replacement_content }) {
    // Use path.join with internally calculated projectRoot (same pattern as consult_image)
    const absolutePath = path.join(projectRoot, target_file);

    // Security Check: Ensure the path doesn't escape the project root directory
    if (!absolutePath.startsWith(projectRoot)) {
        const errorResponse = {
            success: false,
            error: `Access denied: Path '${target_file}' resolves outside the project root directory.`,
            original_content: null
        };
        return {
            content: [{
                type: 'text',
                text: JSON.stringify(errorResponse, null, 2)
            }]
        };
    }

    let original_content;
    try {
        original_content = await fs.readFile(absolutePath, 'utf8');
    } catch (error) {
        const errorResponse = {
            success: false,
            error: `File not found or could not be read: ${target_file}. Resolved to: ${absolutePath}. Error: ${error.message}`,
            original_content: null
        };
        return {
            content: [{
                type: 'text',
                text: JSON.stringify(errorResponse, null, 2)
            }]
        };
    }

    const startIndex = original_content.indexOf(start_marker);
    if (startIndex === -1) {
        const errorResponse = {
            success: false,
            error: `Start marker not found: "${start_marker}"`,
            original_content: original_content
        };
        return {
            content: [{
                type: 'text',
                text: JSON.stringify(errorResponse, null, 2)
            }]
        };
    }

    const endIndex = original_content.indexOf(end_marker, startIndex + start_marker.length);
    if (endIndex === -1) {
        const errorResponse = {
            success: false,
            error: `End marker not found after start marker: "${end_marker}"`,
            original_content: original_content
        };
        return {
            content: [{
                type: 'text',
                text: JSON.stringify(errorResponse, null, 2)
            }]
        };
    }

    const contentBefore = original_content.substring(0, startIndex);
    const contentAfter = original_content.substring(endIndex + end_marker.length);

    const newContent = `${contentBefore}${start_marker}\n${replacement_content}\n${end_marker}${contentAfter}`;

    try {
        await fs.writeFile(absolutePath, newContent, 'utf8');
        const successResponse = {
            success: true,
            message: `Successfully replaced content in ${target_file}.`,
            target_file: target_file,
            resolved_path: absolutePath,
            start_marker: start_marker,
            end_marker: end_marker,
            replacement_applied: true
        };
        return {
            content: [{
                type: 'text',
                text: JSON.stringify(successResponse, null, 2)
            }]
        };
    } catch (error) {
        const errorResponse = {
            success: false,
            error: `Failed to write to file: ${error.message}`,
            original_content: original_content
        };
        return {
            content: [{
                type: 'text',
                text: JSON.stringify(errorResponse, null, 2)
            }]
        };
    }
}

// Export the function directly to match the pattern of other MCP tools
export { replace_content_between as handleReplaceContentBetween };

// Keep the tool object for backward compatibility if needed
export const replaceContentBetweenTool = {
    name: "replace_content_between",
    description: "Replaces the content between the first occurrence of a start marker and the subsequent end marker in a file. This provides a more predictable way to edit files than regex-based replacements.",
    schema: replaceContentBetweenSchema,
    func: replace_content_between,
}; 