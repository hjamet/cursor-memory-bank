import { promises as fs, readFileSync, writeFileSync, mkdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { z } from 'zod';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const userbriefFilePath = path.join(__dirname, '..', '..', '..', '..', '.cursor', 'memory-bank', 'workflow', 'userbrief.json');

// Archive size limits
const MAX_ARCHIVED_REQUESTS = 50;

/**
 * Clean up archived requests to maintain maximum limit
 * Keeps only the most recent archived requests based on updated_at
 */
function cleanupArchivedRequests(userbriefData) {
    const archivedRequests = userbriefData.requests.filter(req => req.status === 'archived');

    if (archivedRequests.length > MAX_ARCHIVED_REQUESTS) {
        const sortedArchived = archivedRequests.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

        const requestsToKeep = sortedArchived.slice(0, MAX_ARCHIVED_REQUESTS);
        const requestsToRemove = sortedArchived.slice(MAX_ARCHIVED_REQUESTS);

        if (requestsToRemove.length > 0) {
            // console.log(`[UserBrief] Cleaned up ${requestsToRemove.length} old archived requests, keeping ${requestsToKeep.length} most recent`);
            const updatedRequests = userbriefData.requests.filter(req => !requestsToRemove.some(r => r.id === req.id));
            userbriefData.requests = updatedRequests;
            writeUserbriefData(userbriefData);
        }
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

/**
 * Generate a unique userbrief request ID with collision detection
 * @param {Object} userbriefData - Current userbrief data
 * @returns {number} Unique request ID
 */
function generateUniqueRequestId(userbriefData) {
    // Method 1: Use last_id + 1 (standard approach)
    let candidateId = userbriefData.last_id + 1;

    // Method 2: Verify against existing IDs (defense against corruption)
    const existingIds = userbriefData.requests.map(r => r.id);
    if (existingIds.length > 0) {
        const maxExistingId = Math.max(...existingIds);

        // Ensure candidate ID is higher than any existing ID
        if (candidateId <= maxExistingId) {
            candidateId = maxExistingId + 1;
            console.warn(`[UserBrief] ID collision detected, adjusting from ${userbriefData.last_id + 1} to ${candidateId}`);
        }
    }

    // Method 3: Final collision check
    while (existingIds.includes(candidateId)) {
        candidateId++;
        console.warn(`[UserBrief] ID ${candidateId - 1} already exists, trying ${candidateId}`);
    }

    return candidateId;
}

/**
 * Validate userbrief data integrity
 * @param {Object} userbriefData - Userbrief data to validate
 * @throws {Error} If duplicate IDs are found
 */
function validateUserbriefIntegrity(userbriefData) {
    const ids = userbriefData.requests.map(r => r.id);
    const uniqueIds = new Set(ids);

    if (ids.length !== uniqueIds.size) {
        const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
        throw new Error(`Duplicate userbrief request IDs detected: ${duplicates.join(', ')}`);
    }

    // Validate last_id consistency
    if (ids.length > 0) {
        const maxId = Math.max(...ids);
        if (userbriefData.last_id < maxId) {
            console.warn(`[UserBrief] last_id (${userbriefData.last_id}) is lower than max existing ID (${maxId}), correcting...`);
            userbriefData.last_id = maxId;
        }
    }
}

export function addUserbriefRequest(content) {
    const userbriefData = readUserbriefData();

    // Validate existing data integrity before adding new request
    validateUserbriefIntegrity(userbriefData);

    const nextId = generateUniqueRequestId(userbriefData);

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

    // Final validation before saving
    validateUserbriefIntegrity(userbriefData);

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
    // console.warn('[UserBrief] parseUserbrief is deprecated, system now uses JSON format');
    return { requests: [], hasChanges: false, newLines: [] };
}

function serializeUserbrief(requests) {
    // This function is now deprecated but kept for compatibility
    // console.warn('[UserBrief] serializeUserbrief is deprecated, system now uses JSON format');
    return '';
} 