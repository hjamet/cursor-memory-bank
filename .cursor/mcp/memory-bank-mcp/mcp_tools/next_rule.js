import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { readUserbrief } from '../lib/userbrief_manager.js';
import { readTasks } from '../lib/task_manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workflowDirPath = path.join(__dirname, '..', '..', '..', 'workflow');

async function getRule(rule_name) {
    const ruleFilePath = path.join(workflowDirPath, `${rule_name}.md`);
    try {
        const data = await fs.readFile(ruleFilePath, 'utf8');
        return {
            rule_name: rule_name,
            instructions: data,
        };
    } catch (error) {
        if (error.code === 'ENOENT') {
            throw new Error(`Rule file not found: ${rule_name}.md`);
        }
        throw new Error(`Failed to read rule file: ${error.message}`);
    }
}

async function next_rule(args) {
    let { rule_name } = args;

    if (!rule_name) {
        // Decide which rule to run next
        const userbrief = await readUserbrief();
        if (userbrief.requests.some(r => r.status === 'new' || r.status === 'in_progress')) {
            rule_name = 'task-decomposition';
        } else {
            const tasks = await readTasks();
            if (tasks.some(t => t.status === 'TODO' || t.status === 'IN_PROGRESS')) {
                rule_name = 'implementation';
            } else {
                rule_name = 'context-update';
            }
        }
    }

    return await getRule(rule_name);
}

export const nextRuleSchema = {
    rule_name: z.string().optional().describe("The name of the rule to execute next (without the .md extension). If not provided, the server will decide the next rule."),
};

export { next_rule as handleNextRule };