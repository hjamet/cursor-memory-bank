import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const userbriefFilePath = path.join(__dirname, '..', '..', '..', '..', '.cursor', 'memory-bank', 'userbrief.md');

function parseUserbrief(content) {
    const requests = [];
    const lines = content.split('\n');
    let hasChanges = false;
    const newLines = [];

    for (const line of lines) {
        if (line.startsWith('- ')) {
            const content = line.substring(2).trim();
            requests.push({
                content: content,
                status: 'in_progress',
            });
            newLines.push(`⏳ - ${content}`);
            hasChanges = true;
        } else {
            const requestMatch = line.match(/^([📌⏳🗄️])\s*-\s*(.*)/);
            if (requestMatch) {
                const statusMap = {
                    '📌': 'preference',
                    '⏳': 'in_progress',
                    '🗄️': 'archived',
                };
                requests.push({
                    content: requestMatch[2].trim(),
                    status: statusMap[requestMatch[1]] || 'new',
                });
            }
            newLines.push(line);
        }
    }
    return { requests, hasChanges, newLines };
}

export async function readUserbrief() {
    try {
        const content = await fs.readFile(userbriefFilePath, 'utf8');
        const { requests, hasChanges, newLines } = parseUserbrief(content);
        if (hasChanges) {
            await fs.writeFile(userbriefFilePath, newLines.join('\n'), 'utf8');
        }
        return { requests };
    } catch (error) {
        if (error.code === 'ENOENT') {
            return { requests: [] }; // Return empty array if file doesn't exist
        }
        throw error;
    }
} 