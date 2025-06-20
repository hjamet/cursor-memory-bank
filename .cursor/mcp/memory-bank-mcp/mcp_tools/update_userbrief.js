import { z } from 'zod';
import { readUserbriefData, writeUserbriefData } from '../lib/userbrief_manager.js';

// Schema for the update-userbrief tool parameters
export const updateUserbriefSchema = z.object({
    action: z.enum(['mark_in_progress', 'mark_archived', 'add_comment'])
        .describe('Action to perform on userbrief entry'),
    id: z.number().optional()
        .describe('ID of the request to update. If not provided, targets the current active request.'),
    comment: z.string().optional()
        .describe('Comment to add to the request history.'),
});

/**
 * Handles the update-userbrief tool call.
 * Can mark requests as 'in_progress', 'archived', or add comments.
 * Targets a request by its unique ID.
 * 
 * @param {Object} params - Tool parameters
 * @param {string} params.action - The action to perform.
 * @param {number} [params.id] - The ID of the request to update.
 * @param {string} [params.comment] - A comment to add to the request's history.
 * @returns {Object} Tool response with update status.
 */
export async function handleUpdateUserbrief(params) {
    try {
        const { action, id, comment } = params;

        console.log(`[UpdateUserbrief] Action: ${action}, ID: ${id || 'auto'}, Comment: ${comment ? 'yes' : 'no'}`);

        const userbriefData = readUserbriefData();
        const requests = userbriefData.requests;

        if (requests.length === 0) {
            return { content: [{ type: 'text', text: JSON.stringify({ status: 'error', message: 'Userbrief is empty.' }, null, 2) }] };
        }

        let targetRequest = null;

        if (id) {
            targetRequest = requests.find(req => req.id === id);
        } else {
            // Auto-detect current request: 'in_progress' > 'new'
            targetRequest = requests.find(req => req.status === 'in_progress') || requests.find(req => req.status === 'new') || null;
        }

        if (!targetRequest) {
            const message = id ? `No request found with ID ${id}` : 'No current active request found to update.';
            return { content: [{ type: 'text', text: JSON.stringify({ status: 'error', message }, null, 2) }] };
        }

        const originalStatus = targetRequest.status;
        let newStatus = originalStatus;
        let actionDescription = '';

        // Initialize history if it doesn't exist
        if (!targetRequest.history) {
            targetRequest.history = [];
        }

        const historyEntry = {
            timestamp: new Date().toISOString(),
            action: action,
        };

        switch (action) {
            case 'mark_in_progress':
                newStatus = 'in_progress';
                targetRequest.status = newStatus;
                actionDescription = 'Marked as in progress.';
                break;

            case 'mark_archived':
                newStatus = 'archived';
                targetRequest.status = newStatus;
                actionDescription = 'Marked as archived.';
                if (comment) {
                    historyEntry.comment = comment;
                    actionDescription += ` With comment: "${comment}"`;
                }
                break;

            case 'add_comment':
                if (!comment) {
                    return { content: [{ type: 'text', text: JSON.stringify({ status: 'error', message: 'Comment text is required for add_comment action.' }, null, 2) }] };
                }
                historyEntry.comment = comment;
                actionDescription = `Added comment: "${comment}"`;
                break;

            default:
                return { content: [{ type: 'text', text: JSON.stringify({ status: 'error', message: `Unknown action: ${action}` }, null, 2) }] };
        }

        targetRequest.history.push(historyEntry);
        targetRequest.updated_at = new Date().toISOString();

        writeUserbriefData(userbriefData);

        const response = {
            status: 'success',
            message: `Successfully updated request #${targetRequest.id}`,
            action_performed: {
                action: action,
                description: actionDescription,
                target_request: {
                    id: targetRequest.id,
                    original_status: originalStatus,
                    new_status: newStatus,
                    content_preview: targetRequest.content.substring(0, 100) + (targetRequest.content.length > 100 ? '...' : '')
                }
            }
        };

        console.log(`[UpdateUserbrief] Success: ${actionDescription} on request #${targetRequest.id}`);

        return { content: [{ type: 'text', text: JSON.stringify(response, null, 2) }] };

    } catch (error) {
        console.error('[UpdateUserbrief] Error:', error);
        return { content: [{ type: 'text', text: JSON.stringify({ status: 'error', message: `Error updating userbrief: ${error.message}` }, null, 2) }] };
    }
} 