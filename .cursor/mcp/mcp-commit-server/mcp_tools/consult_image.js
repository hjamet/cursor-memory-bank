import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Helper to get __dirname in ES modules
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

// Calculate project root (assuming this file is in .cursor/mcp/mcp-commit-server/mcp_tools/)
// const projectRoot = path.resolve(__dirname, '..', '..', '..'); // REMOVED - Will be passed in

const commonImageMimeTypes = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml' // Added SVG
};

/**
 * MCP Tool handler for consulting (reading and returning) an image file.
 * @param {object} params - Parameters object.
 * @param {string} params.path - Relative path to the image file from the project root.
 * @param {string} projectRoot - The absolute path to the project root, passed from the server.
 * @returns {Promise<{ content: Array<{type: string, text?: string, data?: string, mimeType?: string}>> }>} - MCP response object.
 */
export async function handleConsultImage(params, projectRoot) { // Added projectRoot parameter
    if (!projectRoot) {
        // Return error object wrapped in content array
        return { content: [{ type: 'text', text: 'Error: projectRoot was not provided to handleConsultImage.' }] };
    }
    const relativePath = params.path;
    if (!relativePath || typeof relativePath !== 'string') {
        // Return error object wrapped in content array
        return { content: [{ type: 'text', text: 'Error: Missing or invalid \'path\' parameter.' }] };
    }

    const absolutePath = path.resolve(projectRoot, relativePath);
    const fileExtension = path.extname(absolutePath).toLowerCase();

    const mimeType = commonImageMimeTypes[fileExtension];

    if (!mimeType) {
        // Return error object wrapped in content array
        return { content: [{ type: 'text', text: `Error: Unsupported file type. Only common image types (${Object.keys(commonImageMimeTypes).join(', ')}) are supported.` }] };
    }

    try {
        // Check if path is still within the project root to prevent directory traversal
        if (!absolutePath.startsWith(projectRoot)) {
            throw new Error('Access denied: Path is outside the project root.');
        }

        const fileBuffer = await fs.readFile(absolutePath);
        const base64Data = fileBuffer.toString('base64');

        // Return success object wrapped in content array
        return {
            content: [
                {
                    type: 'image',
                    data: base64Data,
                    mimeType: mimeType,
                },
            ]
        };
    } catch (error) {
        let errorMessage = `Error reading file '${relativePath}'.`;
        if (error.code === 'ENOENT') {
            errorMessage = `Error: File not found at '${relativePath}'. Resolved to: ${absolutePath}`;
        } else if (error.message.startsWith('Access denied')) {
            errorMessage = `Error: ${error.message}`;
        } else {
            console.error(`[consult_image] Error reading file ${absolutePath}:`, error);
            errorMessage = `Error reading file '${relativePath}'. Details: ${error.message}`;
        }
        // Return error object wrapped in content array
        return { content: [{ type: 'text', text: errorMessage }] };
    }
} 