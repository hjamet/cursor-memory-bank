import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';
import * as pdf from 'pdf-to-img';

// Helper to get __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Calculate project root (assuming this file is in .cursor/mcp/mcp-commit-server/mcp_tools/)
const projectRoot = path.resolve(__dirname, '..', '..', '..', '..'); // Use internal calculation (4 levels)

/**
 * MCP Tool handler for taking a screenshot of a specific PDF page.
 * Reproduces EXACTLY the same patterns as consult_image.js with PDF adaptation.
 * @param {object} params - Parameters object.
 * @param {string} params.path - Relative path to the PDF file.
 * @param {number} params.page - Page number to capture (starting from 1).
 * @returns {Promise<{ content: Array<{type: string, text?: string, data?: string, mimeType?: string}>> }>} - MCP response object.
 */
export async function handleTakePdfScreenshot(params) {
    const relativePath = params.path;
    const pageNumber = params.page;

    if (!relativePath || typeof relativePath !== 'string') {
        return { content: [{ type: 'text', text: 'Error: Missing or invalid \'path\' parameter.' }] };
    }

    if (!pageNumber || typeof pageNumber !== 'number' || pageNumber < 1 || !Number.isInteger(pageNumber)) {
        return { content: [{ type: 'text', text: 'Error: Missing or invalid \'page\' parameter. Must be a positive integer starting from 1.' }] };
    }

    // Use path.join with internally calculated projectRoot
    const absolutePath = path.join(projectRoot, relativePath);
    const fileExtension = path.extname(absolutePath).toLowerCase();

    if (fileExtension !== '.pdf') {
        return { content: [{ type: 'text', text: `Error: Unsupported file type for '${relativePath}'. Only PDF files are supported.` }] };
    }

    try {
        // Security Check: Ensure the path doesn't escape the project root directory
        if (!absolutePath.startsWith(projectRoot)) {
            throw new Error(`Access denied: Path '${relativePath}' resolves outside the project root directory.`);
        }

        await fs.access(absolutePath, fs.constants.R_OK); // Check read access

        // Convert PDF to images using pdf-to-img
        const pdfBuffer = await fs.readFile(absolutePath);

        // Convert PDF document
        const doc = await pdf.pdf(pdfBuffer);

        if (!doc || pageNumber > doc.length) {
            throw new Error(`Failed to convert page ${pageNumber} or page does not exist in PDF. PDF has ${doc?.length || 0} pages.`);
        }

        // Get specific page as image
        const pageImage = await doc.getPage(pageNumber);
        const imageBuffer = pageImage; // The pageImage is already a PNG buffer

        // Process the image using sharp (same as consult_image.js)
        const processedImageBuffer = await sharp(imageBuffer)
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
        // Same error handling pattern as consult_image.js
        let errorMessage = `Error processing PDF file '${relativePath}'.`;
        if (error.code === 'ENOENT') {
            errorMessage = `Error: PDF file not found at '${relativePath}'. Resolved to: ${absolutePath}`;
        } else if (error.message.startsWith('Access denied')) {
            errorMessage = `Error: ${error.message}`;
        } else if (error.message.includes('page does not exist') || error.message.includes('Failed to convert page')) {
            errorMessage = `Error: Page ${pageNumber} does not exist in PDF '${relativePath}' or conversion failed.`;
        } else {
            console.error(`[take_pdf_screenshot] Error processing PDF ${absolutePath}:`, error); // Keep one essential log
            errorMessage = `Error processing PDF file '${relativePath}'. Details: ${error.message}`;
        }
        return { content: [{ type: 'text', text: errorMessage }] };
    }
} 