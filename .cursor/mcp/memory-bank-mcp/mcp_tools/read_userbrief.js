import { z } from 'zod';
import { readUserbriefData } from '../lib/userbrief_manager.js';

/**
 * Handles the read-userbrief tool call.
 * Returns the current request ('in_progress' or 'new'), plus a configurable number of archived entries.
 * 
 * @param {Object} params - Tool parameters
 * @param {number} [params.archived_count=3] - Number of archived entries to include
 * @returns {Object} Tool response with userbrief data
 */
export async function handleReadUserbrief(params) {
    try {
        const { archived_count = 3 } = params || {};

        // Debug logging removed to prevent JSON-RPC pollution
        // console.log(`[ReadUserbrief] Reading userbrief with ${archived_count} archived entries`);

        const userbriefData = readUserbriefData();
        const requests = userbriefData.requests || [];

        if (requests.length === 0) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'success',
                        message: 'Userbrief is empty',
                        current_request: null,
                        archived_entries: [],
                        total_requests: 0
                    }, null, 2)
                }]
            };
        }

        // Find current request (in_progress > new)
        let currentRequest = requests.find(req => req.status === 'in_progress') ||
            requests.find(req => req.status === 'new') ||
            null;

        // Get archived entries (most recent first)
        const archivedEntries = requests
            .filter(req => req.status === 'archived')
            .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
            .slice(0, archived_count);

        // Get preferences
        const preferences = requests
            .filter(req => req.status === 'preference' || req.status === 'pinned')
            .map(req => req.content);

        const response = {
            status: 'success',
            message: `Retrieved userbrief data with ${archived_count} archived entries`,
            current_request: currentRequest,
            archived_entries: archivedEntries,
            preferences: preferences,
            total_requests: requests.length,
            statistics: {
                by_status: requests.reduce((acc, req) => {
                    acc[req.status] = (acc[req.status] || 0) + 1;
                    return acc;
                }, {})
            }
        };

        // Debug logging removed to prevent JSON-RPC pollution  
        // console.log(`[ReadUserbrief] Success: Found ${requests.length} total requests, current: ${currentRequest ? `#${currentRequest.id}` : 'none'}`);

        return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };

    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.error('[ReadUserbrief] Error:', error);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error reading userbrief: ${error.message}`
                }, null, 2)
            }]
        };
    }
} 