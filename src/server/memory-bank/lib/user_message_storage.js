/**
 * User Message Storage Manager
 * Manages temporary messages sent by users to the agent via Streamlit interface
 * Messages are stored in JSON format and consumed by the agent during remember() calls
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to user messages file
const USER_MESSAGES_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'user_messages.json');

/**
 * Read user messages data from JSON file
 * @returns {Object} User messages data structure
 */
export async function readUserMessages() {
    try {
        const data = await fs.readFile(USER_MESSAGES_FILE_PATH, 'utf8');
        const parsed = JSON.parse(data);

        // Ensure we have the expected structure
        if (!parsed.version || !Array.isArray(parsed.messages) || typeof parsed.last_id !== 'number') {
            return {
                version: "1.0.0",
                messages: [],
                last_id: 0
            };
        }

        return parsed;
    } catch (error) {
        if (error.code === 'ENOENT') {
            // File doesn't exist, return empty structure
            return {
                version: "1.0.0",
                messages: [],
                last_id: 0
            };
        }
        throw new Error(`Failed to read user messages file: ${error.message}`);
    }
}

/**
 * Write user messages data to JSON file
 * @param {Object} messagesData - User messages data to write
 */
export async function writeUserMessages(messagesData) {
    try {
        // Ensure directory exists
        const dir = path.dirname(USER_MESSAGES_FILE_PATH);
        await fs.mkdir(dir, { recursive: true });

        // Validate data integrity before writing
        validateUserMessagesIntegrity(messagesData);

        // Write the JSON file atomically
        await fs.writeFile(USER_MESSAGES_FILE_PATH, JSON.stringify(messagesData, null, 2), 'utf8');
    } catch (error) {
        throw new Error(`Failed to write user messages: ${error.message}`);
    }
}

/**
 * Generate a unique message ID with collision detection
 * @param {Object} messagesData - Current messages data
 * @returns {number} Unique message ID
 */
function generateUniqueMessageId(messagesData) {
    // Method 1: Use last_id + 1 (standard approach)
    let candidateId = messagesData.last_id + 1;

    // Method 2: Verify against existing IDs (defense against corruption)
    const existingIds = messagesData.messages.map(m => m.id);
    if (existingIds.length > 0) {
        const maxExistingId = Math.max(...existingIds);

        // Ensure candidate ID is higher than any existing ID
        if (candidateId <= maxExistingId) {
            candidateId = maxExistingId + 1;
            console.warn(`[UserMessages] ID collision detected, adjusting from ${messagesData.last_id + 1} to ${candidateId}`);
        }
    }

    // Method 3: Final collision check
    while (existingIds.includes(candidateId)) {
        candidateId++;
        console.warn(`[UserMessages] ID ${candidateId - 1} already exists, trying ${candidateId}`);
    }

    return candidateId;
}

/**
 * Validate user messages data integrity
 * @param {Object} messagesData - Messages data to validate
 * @throws {Error} If duplicate IDs are found
 */
function validateUserMessagesIntegrity(messagesData) {
    if (!messagesData || !Array.isArray(messagesData.messages)) {
        throw new Error('Invalid messages data structure');
    }

    const ids = messagesData.messages.map(m => m.id);
    const uniqueIds = new Set(ids);

    if (ids.length !== uniqueIds.size) {
        const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
        throw new Error(`Duplicate message IDs detected: ${duplicates.join(', ')}`);
    }

    // Validate last_id consistency
    if (ids.length > 0) {
        const maxId = Math.max(...ids);
        if (messagesData.last_id < maxId) {
            console.warn(`[UserMessages] last_id (${messagesData.last_id}) is lower than max existing ID (${maxId}), correcting...`);
            messagesData.last_id = maxId;
        }
    }
}

/**
 * Add a new user message
 * @param {string} content - Message content
 * @returns {Object} Created message
 */
export async function addUserMessage(content) {
    if (!content || typeof content !== 'string' || content.trim().length === 0) {
        throw new Error('Message content is required and must be a non-empty string');
    }

    const messagesData = await readUserMessages();

    // Validate existing data integrity before adding new message
    validateUserMessagesIntegrity(messagesData);

    const nextId = generateUniqueMessageId(messagesData);

    const newMessage = {
        id: nextId,
        content: content.trim(),
        created_at: new Date().toISOString(),
        status: 'pending'
    };

    messagesData.messages.push(newMessage);
    messagesData.last_id = nextId;

    // Final validation before saving
    validateUserMessagesIntegrity(messagesData);

    await writeUserMessages(messagesData);
    return newMessage;
}

/**
 * Get all pending messages
 * @returns {Array} Array of pending messages
 */
export async function getPendingMessages() {
    const messagesData = await readUserMessages();
    return messagesData.messages.filter(m => m.status === 'pending');
}

/**
 * Mark a message as consumed
 * @param {number} messageId - ID of the message to mark as consumed
 * @returns {boolean} True if message was found and marked, false otherwise
 */
export async function markMessageAsConsumed(messageId) {
    const messagesData = await readUserMessages();

    const message = messagesData.messages.find(m => m.id === messageId);
    if (!message) {
        return false;
    }

    message.status = 'consumed';
    message.consumed_at = new Date().toISOString();

    await writeUserMessages(messagesData);
    return true;
}

/**
 * Remove consumed messages (cleanup)
 * @returns {number} Number of messages removed
 */
export async function cleanupConsumedMessages() {
    const messagesData = await readUserMessages();

    const initialCount = messagesData.messages.length;
    messagesData.messages = messagesData.messages.filter(m => m.status !== 'consumed');
    const finalCount = messagesData.messages.length;

    if (initialCount !== finalCount) {
        await writeUserMessages(messagesData);
    }

    return initialCount - finalCount;
}

/**
 * Get message statistics
 * @returns {Object} Statistics about messages
 */
export async function getMessageStats() {
    const messagesData = await readUserMessages();

    const stats = {
        total: messagesData.messages.length,
        pending: messagesData.messages.filter(m => m.status === 'pending').length,
        consumed: messagesData.messages.filter(m => m.status === 'consumed').length,
        last_id: messagesData.last_id
    };

    return stats;
} 