#!/usr/bin/env node

/**
 * Cleanup Test Messages Script
 * This script removes test messages containing "clé secrète : 42" from storage files
 * to prevent them from being repeated in future communications.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// File paths
const USERBRIEF_FILE = path.join(__dirname, '..', '..', 'memory-bank', 'workflow', 'userbrief.json');
const AGENT_MEMORY_FILE = path.join(__dirname, '..', '..', 'memory-bank', 'workflow', 'agent_memory.json');
const USER_MESSAGES_FILE = path.join(__dirname, '..', '..', 'memory-bank', 'workflow', 'user_messages.json');

// Test message patterns to remove
const TEST_MESSAGE_PATTERNS = [
    /voici la clé secrète\s*:\s*42/i,
    /clé secrète.*42/i,
];

/**
 * Check if a message contains test patterns
 * @param {string} content - The content to check
 * @returns {boolean} - True if the content contains test patterns
 */
function containsTestMessage(content) {
    if (!content || typeof content !== 'string') {
        return false;
    }

    const normalizedContent = content.toLowerCase().trim();

    for (const pattern of TEST_MESSAGE_PATTERNS) {
        if (pattern.test(normalizedContent)) {
            return true;
        }
    }

    return false;
}

/**
 * Clean userbrief.json file
 */
async function cleanUserbrief() {
    try {
        const data = await fs.readFile(USERBRIEF_FILE, 'utf8');
        const userbrief = JSON.parse(data);

        let removedCount = 0;

        // Filter out test messages from archived entries
        if (userbrief.archived_entries && Array.isArray(userbrief.archived_entries)) {
            const originalCount = userbrief.archived_entries.length;
            userbrief.archived_entries = userbrief.archived_entries.filter(entry => {
                if (entry.content && containsTestMessage(entry.content)) {
                    removedCount++;
                    return false;
                }
                return true;
            });

            console.log(`Userbrief: Removed ${removedCount} test messages from archived entries`);
        }

        // Update statistics
        if (userbrief.statistics && userbrief.statistics.by_status) {
            userbrief.statistics.by_status.archived = Math.max(0, (userbrief.statistics.by_status.archived || 0) - removedCount);
        }

        if (userbrief.total_requests) {
            userbrief.total_requests = Math.max(0, userbrief.total_requests - removedCount);
        }

        // Save cleaned userbrief
        await fs.writeFile(USERBRIEF_FILE, JSON.stringify(userbrief, null, 2), 'utf8');
        console.log(`✅ Cleaned userbrief.json - Removed ${removedCount} test messages`);

    } catch (error) {
        if (error.code === 'ENOENT') {
            console.log('📁 userbrief.json not found, skipping...');
        } else {
            console.error('❌ Error cleaning userbrief.json:', error.message);
        }
    }
}

/**
 * Clean agent_memory.json file
 */
async function cleanAgentMemory() {
    try {
        const data = await fs.readFile(AGENT_MEMORY_FILE, 'utf8');
        const memories = JSON.parse(data);

        if (!Array.isArray(memories)) {
            console.log('📁 agent_memory.json is not an array, skipping...');
            return;
        }

        let removedCount = 0;
        const originalCount = memories.length;

        // Filter out memories containing test messages
        const cleanedMemories = memories.filter(memory => {
            if (memory.present && containsTestMessage(memory.present)) {
                removedCount++;
                return false;
            }
            if (memory.past && containsTestMessage(memory.past)) {
                removedCount++;
                return false;
            }
            if (memory.future && containsTestMessage(memory.future)) {
                removedCount++;
                return false;
            }
            return true;
        });

        if (removedCount > 0) {
            await fs.writeFile(AGENT_MEMORY_FILE, JSON.stringify(cleanedMemories, null, 2), 'utf8');
            console.log(`✅ Cleaned agent_memory.json - Removed ${removedCount} test memories`);
        } else {
            console.log('✅ agent_memory.json - No test messages found');
        }

    } catch (error) {
        if (error.code === 'ENOENT') {
            console.log('📁 agent_memory.json not found, skipping...');
        } else {
            console.error('❌ Error cleaning agent_memory.json:', error.message);
        }
    }
}

/**
 * Clean user_messages.json file
 */
async function cleanUserMessages() {
    try {
        const data = await fs.readFile(USER_MESSAGES_FILE, 'utf8');
        const userMessages = JSON.parse(data);

        if (!userMessages.messages || !Array.isArray(userMessages.messages)) {
            console.log('✅ user_messages.json - No messages to clean');
            return;
        }

        let removedCount = 0;
        const originalCount = userMessages.messages.length;

        // Filter out test messages
        userMessages.messages = userMessages.messages.filter(msg => {
            if (msg.content && containsTestMessage(msg.content)) {
                removedCount++;
                return false;
            }
            return true;
        });

        if (removedCount > 0) {
            await fs.writeFile(USER_MESSAGES_FILE, JSON.stringify(userMessages, null, 2), 'utf8');
            console.log(`✅ Cleaned user_messages.json - Removed ${removedCount} test messages`);
        } else {
            console.log('✅ user_messages.json - No test messages found');
        }

    } catch (error) {
        if (error.code === 'ENOENT') {
            console.log('📁 user_messages.json not found, skipping...');
        } else {
            console.error('❌ Error cleaning user_messages.json:', error.message);
        }
    }
}

/**
 * Main cleanup function
 */
async function main() {
    console.log('🧹 Starting cleanup of test messages...\n');

    await cleanUserbrief();
    await cleanAgentMemory();
    await cleanUserMessages();

    console.log('\n✅ Cleanup completed successfully!');
    console.log('🔄 Please restart the MCP server for changes to take effect.');
}

// Run the cleanup
main().catch(error => {
    console.error('❌ Cleanup failed:', error);
    process.exit(1);
}); 