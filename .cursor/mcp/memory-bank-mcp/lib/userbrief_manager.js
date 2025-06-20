import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine project root (assuming this file is in .cursor/mcp/memory-bank-mcp/lib/)
const projectRoot = path.resolve(__dirname, '../../../..');
const USERBRIEF_PATH = path.join(projectRoot, '.cursor/memory-bank/workflow/userbrief.json');

const defaultUserbrief = {
    version: "1.0.0",
    last_id: 0,
    requests: []
};

/**
 * Reads the userbrief.json file and returns its content.
 * If the file doesn't exist, it creates it with a default structure.
 * @returns {object} The parsed userbrief data.
 */
export function readUserbriefData() {
    try {
        if (!fs.existsSync(USERBRIEF_PATH)) {
            console.warn(`[UserBriefManager] userbrief.json not found at ${USERBRIEF_PATH}. Creating a new one.`);
            writeUserbriefData(defaultUserbrief);
            return defaultUserbrief;
        }

        const content = fs.readFileSync(USERBRIEF_PATH, 'utf-8');
        return JSON.parse(content);
    } catch (error) {
        console.error('[UserBriefManager] Error reading userbrief.json:', error);
        // If parsing fails, maybe return a default structure to avoid crashing consumers
        return defaultUserbrief;
    }
}

/**
 * Writes data to the userbrief.json file.
 * @param {object} data - The data to write to userbrief.json.
 */
export function writeUserbriefData(data) {
    try {
        const content = JSON.stringify(data, null, 2);
        fs.writeFileSync(USERBRIEF_PATH, content, 'utf-8');
        console.log('[UserBriefManager] userbrief.json updated successfully');
    } catch (error) {
        console.error('[UserBriefManager] Error writing userbrief.json:', error);
        throw error;
    }
}

/**
 * Adds a new request to the userbrief.json file.
 * @param {string} content - The content of the new request.
 * @returns {object} The newly created request object.
 */
export function addUserbriefRequest(content) {
    try {
        const data = readUserbriefData();
        const newId = data.last_id + 1;

        const newRequest = {
            id: newId,
            content: content,
            status: 'new',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            history: []
        };

        data.last_id = newId;
        data.requests.push(newRequest);

        writeUserbriefData(data);
        console.log(`[UserBriefManager] Added new request with ID ${newId}`);
        return newRequest;
    } catch (error) {
        console.error('[UserBriefManager] Error adding new request:', error);
        throw error;
    }
}
