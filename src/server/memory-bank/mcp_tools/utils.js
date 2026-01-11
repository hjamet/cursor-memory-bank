import fs from 'fs/promises';
import { readFileSync } from 'fs';
import path from 'path';

const userbriefPath = path.join(process.cwd(), '.cursor', 'memory-bank', 'workflow', 'userbrief.json');

/**
 * Reads the userbrief data from the JSON file
 * @returns {Object} The userbrief data
 */
export function readUserbriefData() {
    try {
        const data = readFileSync(userbriefPath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return { requests: [] };
    }
}

/**
 * Loads user preferences from userbrief data
 * @param {Object} context - The context object to populate
 * @param {number} limit - Maximum number of preferences to load
 */
export async function loadUserPreferences(context, limit = 3) {
    try {
        const userbriefData = readUserbriefData();
        context.user_preferences = userbriefData.requests ?
            userbriefData.requests
                .filter(req => req.status === 'preference' || req.status === 'pinned')
                .slice(0, limit)
                .map(req => req.content) : [];
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load user preferences: ${error.message}`);
        context.user_preferences = [];
    }
}

/**
 * Loads user preferences for remember tool (without context parameter)
 * @param {number} limit - Maximum number of preferences to load
 * @returns {Array} Array of user preferences
 */
export async function loadUserPreferencesForRemember(limit = 3) {
    try {
        const userbriefData = readUserbriefData();
        return userbriefData.requests ?
            userbriefData.requests
                .filter(req => req.status === 'preference' || req.status === 'pinned')
                .slice(0, limit)
                .map(req => req.content) : [];
    } catch (error) {
        return [];
    }
} 