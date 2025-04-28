import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';

// Helper to get __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Calculate project root (assuming this file is in .cursor/mcp/mcp-commit-server/mcp_tools/)
const projectRoot = path.resolve(__dirname, '..', '..', '..', '..'); // Use internal calculation (4 levels)

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
 * MINIMAL DEBUG VERSION
 * @param {object} params - Parameters object.
 * @param {string} params.path - Relative path to the image file.
 * @returns {Promise<{ content: Array<{type: string, text?: string, data?: string, mimeType?: string}>> }>} - MCP response object.
 */
export async function handleConsultImage(params) {
    const relativePath = params.path;
    if (!relativePath || typeof relativePath !== 'string') {
        return { content: [{ type: 'text', text: 'Error: Missing or invalid \'path\' parameter.' }] };
    }

    // Use path.join with internally calculated projectRoot
    const absolutePath = path.join(projectRoot, relativePath);
    const fileExtension = path.extname(absolutePath).toLowerCase();

    const mimeType = commonImageMimeTypes[fileExtension];

    if (!mimeType) {
        return { content: [{ type: 'text', text: `Error: Unsupported file type for '${relativePath}'. Only common image types (${Object.keys(commonImageMimeTypes).join(', ')}) are supported.` }] };
    }

    try {
        // Security Check: Ensure the path doesn't escape the project root directory
        if (!absolutePath.startsWith(projectRoot)) {
            throw new Error(`Access denied: Path '${relativePath}' resolves outside the project root directory.`);
        }

        await fs.access(absolutePath, fs.constants.R_OK); // Check read access

        const fileBuffer = await fs.readFile(absolutePath);

        // Resize and compress the image using sharp
        const processedImageBuffer = await sharp(fileBuffer)
            .resize({ width: 1024, withoutEnlargement: true }) // Resize to max 1024 width, don't enlarge if smaller
            .jpeg({ quality: 80 }) // Convert to JPEG with 80% quality
            .toBuffer();

        const base64Data = processedImageBuffer.toString('base64'); // Encode the *processed* buffer

        return {
            content: [
                {
                    type: "image",
                    data: base64Data, // Return the processed base64 data
                    mimeType: "image/jpeg", // MimeType is now always jpeg
                },
            ]
        };
    } catch (error) {
        // Restore original error handling
        let errorMessage = `Error reading file '${relativePath}'.`;
        if (error.code === 'ENOENT') {
            errorMessage = `Error: File not found at '${relativePath}'. Resolved to: ${absolutePath}`;
        } else if (error.message.startsWith('Access denied')) {
            errorMessage = `Error: ${error.message}`;
        } else {
            console.error(`[consult_image] Error reading file ${absolutePath}:`, error); // Keep one essential log
            errorMessage = `Error reading file '${relativePath}'. Details: ${error.message}`;
        }
        return { content: [{ type: 'text', text: errorMessage }] };
    }
}

/* 
// --- ORIGINAL IMPLEMENTATION ---
export async function handleConsultImage(params) {
    const relativePath = params.path;
    if (!relativePath || typeof relativePath !== 'string') {
        return { content: [{ type: 'text', text: 'Error: Missing or invalid \'path\' parameter.' }] };
    }

    // Use path.join with internally calculated projectRoot
    const absolutePath = path.join(projectRoot, relativePath);
    const fileExtension = path.extname(absolutePath).toLowerCase();

    const mimeType = commonImageMimeTypes[fileExtension];

    if (!mimeType) {
        return { content: [{ type: 'text', text: `Error: Unsupported file type for '${relativePath}'. Only common image types (${Object.keys(commonImageMimeTypes).join(', ')}) are supported.` }] };
    }

    try {
        // Security Check: Ensure the path doesn't escape the project root directory
        if (!absolutePath.startsWith(projectRoot)) {
            throw new Error(`Access denied: Path '${relativePath}' resolves outside the project root directory.`);
        }

        const fileBuffer = await fs.readFile(absolutePath);
        const base64Data = fileBuffer.toString('base64');

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
            console.error(`[consult_image] Error reading file ${absolutePath}:`, error); // Keep one essential log
            errorMessage = `Error reading file '${relativePath}'. Details: ${error.message}`;
        }
        return { content: [{ type: 'text', text: errorMessage }] };
    }
}
*/ 