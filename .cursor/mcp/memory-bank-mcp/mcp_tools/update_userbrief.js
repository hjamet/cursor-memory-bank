import { z } from 'zod';
import { readUserbriefLines, parseUserbriefEntries, updateEntryStatus, writeUserbriefLines } from '../lib/userbrief_manager.js';

// Schema for the update-userbrief tool parameters
export const updateUserbriefSchema = z.object({
    action: z.enum(['mark_in_progress', 'mark_archived', 'add_comment']).describe('Action to perform on userbrief entry'),
    line_number: z.number().min(1).optional().describe('Line number of the entry to update (optional if auto-detecting current request)'),
    comment: z.string().optional().describe('Comment to add when archiving a task or adding notes'),
    auto_current: z.boolean().default(true).optional().describe('Automatically find and update the current unprocessed/in-progress request (default: true)')
});

/**
 * Handles the update-userbrief tool call
 * Can mark entries as in-progress, archived, or add comments
 * 
 * @param {Object} params - Tool parameters
 * @param {string} params.action - Action to perform ('mark_in_progress', 'mark_archived', 'add_comment')
 * @param {number} [params.line_number] - Specific line number to update
 * @param {string} [params.comment] - Comment to add
 * @param {boolean} [params.auto_current=true] - Auto-detect current request
 * @returns {Object} Tool response with update status
 */
export async function handleUpdateUserbrief(params) {
    try {
        const { action, line_number, comment, auto_current = true } = params;

        console.log(`[UpdateUserbrief] Action: ${action}, Line: ${line_number || 'auto'}, Comment: ${comment ? 'yes' : 'no'}`);

        // Read userbrief file
        const lines = readUserbriefLines();
        if (lines.length === 0) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: 'Userbrief file is empty or not found',
                        action_performed: null
                    }, null, 2)
                }]
            };
        }

        // Parse entries to find target
        const entries = parseUserbriefEntries(lines);
        let targetEntry = null;
        let targetLineNumber = line_number;

        // Auto-detect current request if needed
        if (auto_current && !line_number) {
            // Find current request (in progress ⏳ takes priority, then first unprocessed 🆕 or -)
            const inProgressEntry = entries.find(entry => entry.status === 'in_progress');
            if (inProgressEntry) {
                targetEntry = inProgressEntry;
                targetLineNumber = inProgressEntry.line_number;
            } else {
                const unprocessedEntry = entries.find(entry =>
                    entry.status === 'new' || entry.status === 'unprocessed'
                );
                if (unprocessedEntry) {
                    targetEntry = unprocessedEntry;
                    targetLineNumber = unprocessedEntry.line_number;
                }
            }
        } else if (line_number) {
            // Find specific entry by line number
            targetEntry = entries.find(entry => entry.line_number === line_number);
        }

        if (!targetEntry || !targetLineNumber) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: auto_current
                            ? 'No current unprocessed or in-progress request found'
                            : `No entry found at line ${line_number}`,
                        action_performed: null
                    }, null, 2)
                }]
            };
        }

        let newStatus = targetEntry.status;
        let actionDescription = '';
        let success = false;

        // Perform the requested action
        switch (action) {
            case 'mark_in_progress':
                newStatus = 'in_progress';
                success = updateEntryStatus(targetLineNumber, newStatus);
                actionDescription = 'Marked as in progress (⏳)';
                break;

            case 'mark_archived':
                newStatus = 'archived';
                success = updateEntryStatus(targetLineNumber, newStatus);
                actionDescription = 'Marked as archived (🗄️)';

                // Add comment if provided
                if (success && comment) {
                    const updatedLines = readUserbriefLines();
                    const commentLine = `    ${comment}`;
                    updatedLines.splice(targetLineNumber, 0, commentLine);
                    writeUserbriefLines(updatedLines);
                    actionDescription += ` with comment: "${comment}"`;
                }
                break;

            case 'add_comment':
                // Add comment without changing status
                if (comment) {
                    const updatedLines = readUserbriefLines();
                    const commentLine = `    ${comment}`;
                    updatedLines.splice(targetLineNumber, 0, commentLine);
                    writeUserbriefLines(updatedLines);
                    success = true;
                    actionDescription = `Added comment: "${comment}"`;
                } else {
                    return {
                        content: [{
                            type: 'text',
                            text: JSON.stringify({
                                status: 'error',
                                message: 'Comment text is required for add_comment action',
                                action_performed: null
                            }, null, 2)
                        }]
                    };
                }
                break;

            default:
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify({
                            status: 'error',
                            message: `Unknown action: ${action}`,
                            action_performed: null
                        }, null, 2)
                    }]
                };
        }

        if (!success && action !== 'add_comment') {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Failed to update entry status to ${newStatus}`,
                        action_performed: null
                    }, null, 2)
                }]
            };
        }

        // Prepare response
        const response = {
            status: 'success',
            message: `Successfully updated userbrief entry`,
            action_performed: {
                action: action,
                description: actionDescription,
                target_entry: {
                    line_number: targetLineNumber,
                    original_status: targetEntry.status,
                    new_status: newStatus,
                    content_preview: targetEntry.content.substring(0, 100) + (targetEntry.content.length > 100 ? '...' : '')
                }
            }
        };

        console.log(`[UpdateUserbrief] Success: ${actionDescription} on line ${targetLineNumber}`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        console.error('[UpdateUserbrief] Error:', error);
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error updating userbrief: ${error.message}`,
                    action_performed: null
                }, null, 2)
            }]
        };
    }
} 