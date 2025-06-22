import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import nunjucks from 'nunjucks';
import { readMemoryContext } from '../lib/memory_context.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workflowDirPath = path.join(__dirname, '..', '..', 'workflow-steps');

// Configure nunjucks
nunjucks.configure(workflowDirPath, { autoescape: false });

async function getStep(step_name) {
    const stepFilePath = path.join(workflowDirPath, `${step_name}.md`);
    try {
        const templateContent = await fs.readFile(stepFilePath, 'utf8');

        // Get context for template rendering
        const context = await readMemoryContext();

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

async function next_step(args) {
    const { step_name } = args;

    if (!step_name) {
        throw new Error("'step_name' argument is required.");
    }

    return await getStep(step_name);
}

export const nextStepSchema = {
    step_name: z.string().describe("The name of the step to execute next (without the .md extension)."),
};

export default next_step; 