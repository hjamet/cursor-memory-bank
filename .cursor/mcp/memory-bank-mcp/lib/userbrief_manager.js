import { promises as fs, readFileSync, writeFileSync, mkdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const userbriefFilePath = path.join(__dirname, '..', '..', '..', '..', '.cursor', 'memory-bank', 'workflow', 'userbrief.json');

// Archive size limits
const MAX_ARCHIVED_REQUESTS = 25;

/**
 * Clean up archived requests to maintain maximum limit
 * Keeps only the most recent archived requests based on updated_at
 */
function cleanupArchivedRequests(userbriefData) {
    const archivedRequests = userbriefData.requests.filter(req => req.status === 'archived');

    if (archivedRequests.length > MAX_ARCHIVED_REQUESTS) {
        // Sort archived requests by updated_at (most recent first)
        archivedRequests.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

        // Keep only the most recent MAX_ARCHIVED_REQUESTS
        const requestsToKeep = archivedRequests.slice(0, MAX_ARCHIVED_REQUESTS);
        const requestsToRemove = archivedRequests.slice(MAX_ARCHIVED_REQUESTS);

        // Remove old archived requests from the main requests array
        requestsToRemove.forEach(requestToRemove => {
            const index = userbriefData.requests.findIndex(req => req.id === requestToRemove.id);
            if (index !== -1) {
                userbriefData.requests.splice(index, 1);
            }
        });

        console.log(`[UserBrief] Cleaned up ${requestsToRemove.length} old archived requests, keeping ${requestsToKeep.length} most recent`);
    }
}

export async function readUserbrief() {
    try {
        const content = await fs.readFile(userbriefFilePath, 'utf8');
        const userbriefData = JSON.parse(content);
        return userbriefData;
    } catch (error) {
        if (error.code === 'ENOENT') {
            return { version: "1.0.0", last_id: 0, requests: [] }; // Return empty structure if file doesn't exist
        }
        throw error;
    }
}

// Synchronous version for compatibility
export function readUserbriefData() {
    try {
        const content = readFileSync(userbriefFilePath, 'utf8');
        const userbriefData = JSON.parse(content);
        return userbriefData;
    } catch (error) {
        if (error.code === 'ENOENT') {
            return { version: "1.0.0", last_id: 0, requests: [] };
        }
        throw error;
    }
}

export function writeUserbriefData(userbriefData) {
    try {
        // Clean up archived requests before writing
        cleanupArchivedRequests(userbriefData);

        // Ensure directory exists
        const dir = path.dirname(userbriefFilePath);
        mkdirSync(dir, { recursive: true });

        // Write the JSON file
        writeFileSync(userbriefFilePath, JSON.stringify(userbriefData, null, 2), 'utf8');
    } catch (error) {
        throw new Error(`Failed to write userbrief: ${error.message}`);
    }
}

export function addUserbriefRequest(content) {
    const userbriefData = readUserbriefData();
    const nextId = userbriefData.last_id + 1;

    const newRequest = {
        id: nextId,
        content: content,
        status: 'new',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        history: [
            {
                timestamp: new Date().toISOString(),
                action: 'created',
                comment: 'New request added via Streamlit interface with status \'new\' for processing.'
            }
        ]
    };

    userbriefData.requests.push(newRequest);
    userbriefData.last_id = nextId;
    writeUserbriefData(userbriefData);
    return newRequest;
}

export function updateUserbriefRequest(id, updates) {
    const userbriefData = readUserbriefData();
    const requestIndex = userbriefData.requests.findIndex(req => req.id === id);

    if (requestIndex === -1) {
        throw new Error(`Request with ID ${id} not found`);
    }

    const originalStatus = userbriefData.requests[requestIndex].status;
    const updatedRequest = {
        ...userbriefData.requests[requestIndex],
        ...updates,
        updated_at: new Date().toISOString()
    };

    userbriefData.requests[requestIndex] = updatedRequest;

    // If request was just archived, cleanup will happen in writeUserbriefData
    writeUserbriefData(userbriefData);
    return updatedRequest;
}

// Legacy functions for backward compatibility (now using JSON)
function parseUserbrief(content) {
    // This function is now deprecated but kept for compatibility
    console.warn('[UserBrief] parseUserbrief is deprecated, system now uses JSON format');
    return { requests: [], hasChanges: false, newLines: [] };
}

function serializeUserbrief(requests) {
    // This function is now deprecated but kept for compatibility
    console.warn('[UserBrief] serializeUserbrief is deprecated, system now uses JSON format');
    return '';
} 