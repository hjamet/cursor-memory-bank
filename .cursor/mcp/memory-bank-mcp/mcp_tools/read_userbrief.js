import { z } from 'zod';
import { readUserbriefData } from '../lib/userbrief_manager.js';

// Schema for the read-userbrief tool parameters
export const readUserbriefSchema = z.object({
    archived_count: z.number().min(0).max(10).default(3).optional()
        .describe('Number of archived entries to include in response (default: 3)')
});

/**
 * Handles the read-userbrief tool call.
 * Returns the first 'in_progress' request, or the first 'new' request from userbrief.json.
 * Also includes a specified number of 'archived' requests for context.
 * 
 * @param {Object} params - Tool parameters
 * @param {number} [params.archived_count=3] - Number of archived entries to include
 * @returns {Object} Tool response with userbrief status and entries
 */
export async function handleReadUserbrief(params) {
    try {
        const { archived_count = 3 } = params;

        console.log(`[ReadUserbrief] Reading userbrief with ${archived_count} archived entries`);

        // Read userbrief data from JSON file
        const userbriefData = readUserbriefData();

        if (!userbriefData || !userbriefData.requests || userbriefData.requests.length === 0) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'empty',
                        message: 'Userbrief is empty or not found',
                        current_request: null,
                        archived_entries: []
                    }, null, 2)
                }]
            };
        }

        const requests = userbriefData.requests;

        // Find current request ('in_progress' takes priority, then first 'new')
        let currentRequest = requests.find(req => req.status === 'in_progress') || requests.find(req => req.status === 'new') || null;

        // Get archived entries for context
        const archivedEntries = requests
            .filter(req => req.status === 'archived')
            .slice(0, archived_count);

        // Prepare response
        const response = {
            status: currentRequest ? 'active' : 'no_pending',
            message: currentRequest
                ? `Found request with status '${currentRequest.status}'`
                : 'No pending requests found',
            current_request: currentRequest,
            archived_entries: archivedEntries,
            total_entries: requests.length,
            summary: {
                new: requests.filter(r => r.status === 'new').length,
                in_progress: requests.filter(r => r.status === 'in_progress').length,
                archived: requests.filter(r => r.status === 'archived').length
            }
        };

        console.log(`[ReadUserbrief] Found ${response.summary.new} new, ${response.summary.in_progress} in progress, ${response.summary.archived} archived requests.`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        console.error('[ReadUserbrief] Error:', error);
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error reading userbrief: ${error.message}`,
                    current_request: null,
                    archived_entries: []
                }, null, 2)
            }]
        };
    }
} 