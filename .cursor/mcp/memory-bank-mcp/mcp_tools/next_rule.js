import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import nunjucks from 'nunjucks';
import { readMemoryContext } from '../lib/memory_context.js';
import { handleReadUserbrief } from './read_userbrief.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workflowDirPath = path.join(__dirname, '..', '..', '..', 'workflow-steps');

// Configure nunjucks
nunjucks.configure(workflowDirPath, { autoescape: false });

async function getStep(step_name) {
    const stepFilePath = path.join(workflowDirPath, `${step_name}.md`);
    try {
        const templateContent = await fs.readFile(stepFilePath, 'utf8');

        // Get context for template rendering
        const context = await readMemoryContext();

        // Get userbrief information
        try {
            const userbriefResult = await handleReadUserbrief({ archived_count: 3 });
            if (userbriefResult && userbriefResult.content && userbriefResult.content[0]) {
                const userbriefData = JSON.parse(userbriefResult.content[0].text);
                context.userbrief = userbriefData;

                // Extract unprocessed requests for easy access
                context.unprocessed_requests = userbriefData.requests ?
                    userbriefData.requests.filter(req => req.status === 'new' || req.status === 'in_progress') : [];

                // Extract preferences for easy access
                context.user_preferences = userbriefData.requests ?
                    userbriefData.requests.filter(req => req.status === 'preference').map(req => req.content) : [];
            }
        } catch (error) {
            console.warn(`Could not load userbrief in next_rule: ${error.message}`);
            context.userbrief = null;
            context.unprocessed_requests = [];
            context.user_preferences = [];
        }

        // Render template with Jinja2 (nunjucks)
        const renderedContent = nunjucks.renderString(templateContent, context);

        return {
            step_name: step_name,
            instructions: renderedContent,
            context: context
        };
    } catch (error) {
        if (error.code === 'ENOENT') {
            throw new Error(`Step file not found: ${step_name}.md`);
        }
        throw new Error(`Failed to read step file: ${error.message}`);
    }
}

async function next_rule(args) {
    const { step_name } = args;

    if (!step_name) {
        throw new Error("'step_name' argument is required.");
    }

    const result = await getStep(step_name);

    return {
        content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
        }]
    };
}

export const nextRuleSchema = {
    step_name: z.string().describe("WORKFLOW STEP NAME: The name of the workflow step/rule to execute next (without the .md extension). Available steps include: 'start-workflow' (begin new workflow), 'task-decomposition' (break down user requests into tasks), 'implementation' (execute development tasks), 'fix' (debug and resolve issues), 'context-update' (refresh project context and process userbrief), 'experience-execution' (manual testing and validation). Each step contains specific instructions, context, and automatically includes current userbrief status with unprocessed requests and user preferences."),
};

export default next_rule; 