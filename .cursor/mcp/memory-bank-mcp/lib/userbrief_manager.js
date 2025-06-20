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
    let nextId = 1;

    for (const line of lines) {
        if (line.startsWith('- ')) {
            const content = line.substring(2).trim();
            requests.push({
                id: nextId++,
                content: content,
                status: 'in_progress',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                history: []
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
                    id: nextId++,
                    content: requestMatch[2].trim(),
                    status: statusMap[requestMatch[1]] || 'new',
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    history: []
                });
            }
            newLines.push(line);
        }
    }
    return { requests, hasChanges, newLines };
}

function serializeUserbrief(requests) {
    const lines = [];

    for (const request of requests) {
        const statusMap = {
            'preference': '📌',
            'in_progress': '⏳',
            'archived': '🗄️',
            'pinned': '📌'
        };
        const emoji = statusMap[request.status] || '⏳';
        lines.push(`${emoji} - ${request.content}`);
    }

    return lines.join('\n');
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

// Synchronous version for compatibility
export function readUserbriefData() {
    try {
        const content = fs.readFileSync(userbriefFilePath, 'utf8');
        const { requests } = parseUserbrief(content);
        return { requests };
    } catch (error) {
        if (error.code === 'ENOENT') {
            return { requests: [] };
        }
        throw error;
    }
}

export function writeUserbriefData(data) {
    try {
        const content = serializeUserbrief(data.requests);
        fs.writeFileSync(userbriefFilePath, content, 'utf8');
    } catch (error) {
        throw new Error(`Failed to write userbrief: ${error.message}`);
    }
}

export function addUserbriefRequest(content) {
    const data = readUserbriefData();
    const nextId = data.requests.length > 0 ? Math.max(...data.requests.map(r => r.id)) + 1 : 1;

    const newRequest = {
        id: nextId,
        content: content,
        status: 'new',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        history: []
    };

    data.requests.push(newRequest);
    writeUserbriefData(data);
    return newRequest;
} 