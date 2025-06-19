import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine project root (assuming this file is in .cursor/mcp/memory-bank-mcp/lib/)
const projectRoot = path.resolve(__dirname, '../../../..');
const USERBRIEF_PATH = path.join(projectRoot, '.cursor/memory-bank/userbrief.md');

/**
 * Reads the userbrief.md file and returns its content as an array of lines
 * @returns {string[]} Array of lines from userbrief.md
 */
export function readUserbriefLines() {
    try {
        if (!fs.existsSync(USERBRIEF_PATH)) {
            console.warn(`[UserBriefManager] userbrief.md not found at ${USERBRIEF_PATH}`);
            return [];
        }

        const content = fs.readFileSync(USERBRIEF_PATH, 'utf-8');
        return content.split('\n');
    } catch (error) {
        console.error('[UserBriefManager] Error reading userbrief.md:', error);
        return [];
    }
}

/**
 * Writes content to the userbrief.md file
 * @param {string[]} lines - Array of lines to write to userbrief.md
 */
export function writeUserbriefLines(lines) {
    try {
        const content = lines.join('\n');
        fs.writeFileSync(USERBRIEF_PATH, content, 'utf-8');
        console.log('[UserBriefManager] userbrief.md updated successfully');
    } catch (error) {
        console.error('[UserBriefManager] Error writing userbrief.md:', error);
        throw error;
    }
}

/**
 * Parses userbrief lines into structured entries
 * @param {string[]} lines - Array of lines from userbrief.md
 * @returns {Array} Array of parsed entries with status and content
 */
export function parseUserbriefEntries(lines) {
    const entries = [];
    let currentEntry = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Skip empty lines and headers
        if (!line || line.startsWith('#')) {
            continue;
        }

        // Check if this line starts a new entry
        if (line.match(/^(🆕|⏳|🗄️|-)\s*-\s*/)) {
            // Save previous entry if exists
            if (currentEntry) {
                entries.push(currentEntry);
            }

            // Determine status from emoji
            let status = 'unprocessed';
            if (line.startsWith('🆕')) {
                status = 'new';
            } else if (line.startsWith('⏳')) {
                status = 'in_progress';
            } else if (line.startsWith('🗄️')) {
                status = 'archived';
            } else if (line.startsWith('-')) {
                status = 'unprocessed';
            }

            // Extract content (remove emoji and dash)
            const content = line.replace(/^(🆕|⏳|🗄️|-)\s*-\s*/, '').trim();

            currentEntry = {
                status: status,
                content: content,
                line_number: i + 1,
                full_text: line
            };
        } else if (currentEntry && line) {
            // This is a continuation of the current entry
            currentEntry.content += ' ' + line;
            currentEntry.full_text += '\n' + line;
        }
    }

    // Don't forget the last entry
    if (currentEntry) {
        entries.push(currentEntry);
    }

    return entries;
}

/**
 * Updates the status of a specific entry in userbrief.md
 * @param {number} lineNumber - Line number of the entry to update
 * @param {string} newStatus - New status ('new', 'in_progress', 'archived', 'unprocessed')
 * @returns {boolean} Success status
 */
export function updateEntryStatus(lineNumber, newStatus) {
    try {
        const lines = readUserbriefLines();
        if (lineNumber < 1 || lineNumber > lines.length) {
            throw new Error(`Invalid line number: ${lineNumber}`);
        }

        const lineIndex = lineNumber - 1;
        const line = lines[lineIndex];

        // Map status to emoji
        const statusEmojis = {
            'new': '🆕',
            'in_progress': '⏳',
            'archived': '🗄️',
            'unprocessed': '-'
        };

        const newEmoji = statusEmojis[newStatus];
        if (!newEmoji) {
            throw new Error(`Invalid status: ${newStatus}`);
        }

        // Replace the emoji at the beginning of the line
        const updatedLine = line.replace(/^(🆕|⏳|🗄️|-)\s*-\s*/, `${newEmoji} - `);
        lines[lineIndex] = updatedLine;

        writeUserbriefLines(lines);
        return true;
    } catch (error) {
        console.error('[UserBriefManager] Error updating entry status:', error);
        return false;
    }
}

/**
 * Parses userbrief lines and categorizes them by status
 * @param {string[]} lines Array of lines from userbrief.md
 * @returns {Object} Object with categorized requests
 */
export function parseUserbriefLines(lines) {
    const result = {
        unprocessed: [], // Lines starting with 🆕 or -
        inProgress: [], // Lines starting with ⏳
        preferences: [], // Lines starting with 📌
        archived: [], // Lines starting with 🗄️
        other: [] // All other lines (headers, empty lines, etc.)
    };

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();

        if (trimmedLine.startsWith('🆕 -') || trimmedLine.startsWith('- ')) {
            result.unprocessed.push({ lineIndex: i, content: line });
        } else if (trimmedLine.startsWith('⏳ -')) {
            result.inProgress.push({ lineIndex: i, content: line });
        } else if (trimmedLine.startsWith('📌 -')) {
            result.preferences.push({ lineIndex: i, content: line });
        } else if (trimmedLine.startsWith('🗄️ -')) {
            result.archived.push({ lineIndex: i, content: line });
        } else {
            result.other.push({ lineIndex: i, content: line });
        }
    }

    return result;
}

/**
 * Extracts task text from a userbrief line (removes emoji prefix)
 * @param {string} line The userbrief line
 * @returns {string} The task text without emoji prefix
 */
export function extractTaskText(line) {
    const trimmedLine = line.trim();
    if (trimmedLine.startsWith('🆕 -') || trimmedLine.startsWith('⏳ -') ||
        trimmedLine.startsWith('📌 -') || trimmedLine.startsWith('🗄️ -')) {
        return trimmedLine.substring(4).trim(); // Remove emoji and "- " prefix
    } else if (trimmedLine.startsWith('- ')) {
        return trimmedLine.substring(2).trim(); // Remove "- " prefix
    }
    return trimmedLine;
}

/**
 * Updates a specific line in userbrief.md with new status
 * @param {number} lineIndex Index of the line to update
 * @param {string} newStatus New status emoji ('🆕', '⏳', '📌', '🗄️')
 * @param {string} taskText Task text (without emoji prefix)
 * @param {string} comment Optional comment to append
 * @returns {string} The updated line
 */
export function updateLineStatus(lineIndex, newStatus, taskText, comment = '') {
    const newLine = `${newStatus} - ${taskText}${comment ? ' ' + comment : ''}`;

    const lines = readUserbriefLines();
    if (lineIndex >= 0 && lineIndex < lines.length) {
        lines[lineIndex] = newLine;
        writeUserbriefLines(lines);
        return newLine;
    } else {
        throw new Error(`Invalid line index: ${lineIndex}`);
    }
} 