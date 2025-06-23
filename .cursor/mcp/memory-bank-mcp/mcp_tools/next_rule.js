import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import nunjucks from 'nunjucks';
import { readMemoryContext } from '../lib/memory_context.js';
import { readUserbriefData } from '../lib/userbrief_manager.js';
import { taskManager } from '../lib/task_manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workflowDirPath = path.join(__dirname, '..', '..', '..', 'workflow-steps');

// Configure nunjucks
nunjucks.configure(workflowDirPath, { autoescape: false });

/**
 * Analyze system state to determine optimal next workflow step
 * @param {Object} context - System context including tasks and requests
 * @returns {Object} Analysis result with recommended step and reasoning
 */
function analyzeSystemState(context) {
    const tasks = taskManager.getAllTasks();

    // Count tasks by status
    const taskCounts = {
        TODO: tasks.filter(t => t.status === 'TODO').length,
        IN_PROGRESS: tasks.filter(t => t.status === 'IN_PROGRESS').length,
        BLOCKED: tasks.filter(t => t.status === 'BLOCKED').length,
        REVIEW: tasks.filter(t => t.status === 'REVIEW').length,
        DONE: tasks.filter(t => t.status === 'DONE').length
    };

    // Check for unprocessed requests
    const unprocessedRequests = context.unprocessed_requests || [];
    const hasUnprocessedRequests = unprocessedRequests.length > 0;

    // Determine optimal next step
    let recommendedStep = 'context-update';
    let reasoning = 'Default system analysis and planning';

    if (hasUnprocessedRequests) {
        recommendedStep = 'task-decomposition';
        reasoning = `${unprocessedRequests.length} unprocessed user requests need to be converted to tasks`;
    } else if (taskCounts.IN_PROGRESS > 0) {
        recommendedStep = 'implementation';
        reasoning = `${taskCounts.IN_PROGRESS} tasks currently in progress need completion`;
    } else if (taskCounts.BLOCKED > 0) {
        recommendedStep = 'fix';
        reasoning = `${taskCounts.BLOCKED} blocked tasks need resolution`;
    } else if (taskCounts.TODO > 0) {
        recommendedStep = 'implementation';
        reasoning = `${taskCounts.TODO} TODO tasks ready for execution`;
    } else if (taskCounts.REVIEW > 0) {
        recommendedStep = 'experience-execution';
        reasoning = `${taskCounts.REVIEW} tasks need review and testing`;
    }

    return {
        recommendedStep,
        reasoning,
        systemState: {
            taskCounts,
            unprocessedRequestCount: unprocessedRequests.length,
            totalTasks: tasks.length
        }
    };
}

async function getStep(step_name) {
    const stepFilePath = path.join(workflowDirPath, `${step_name}.md`);
    try {
        const templateContent = await fs.readFile(stepFilePath, 'utf8');

        // Get context for template rendering
        const context = await readMemoryContext();

        // Get userbrief information
        try {
            const userbriefData = readUserbriefData();
            context.userbrief = userbriefData;

            // Extract unprocessed requests for easy access
            // For task-decomposition, return only the oldest unprocessed request to prevent agent saturation
            const allUnprocessedRequests = userbriefData.requests ?
                userbriefData.requests.filter(req => req.status === 'new' || req.status === 'in_progress') : [];

            if (step_name === 'task-decomposition' && allUnprocessedRequests.length > 0) {
                // Sort by creation date (oldest first) and take only the first one
                const sortedRequests = allUnprocessedRequests.sort((a, b) =>
                    new Date(a.created_at) - new Date(b.created_at)
                );
                context.unprocessed_requests = [sortedRequests[0]];
            } else {
                context.unprocessed_requests = allUnprocessedRequests;
            }

            // Extract preferences for easy access
            context.user_preferences = userbriefData.requests ?
                userbriefData.requests.filter(req => req.status === 'preference' || req.status === 'pinned').map(req => req.content) : [];
        } catch (error) {
            console.warn(`Could not load userbrief in next_rule: ${error.message}`);
            context.userbrief = { requests: [] };
            context.unprocessed_requests = [];
            context.user_preferences = [];
        }

        // Add intelligent system state analysis
        const systemAnalysis = analyzeSystemState(context);
        context.system_analysis = systemAnalysis;

        // Add routing decision logging
        if (step_name === 'start-workflow') {
            context.routing_decision = {
                recommended_step: systemAnalysis.recommendedStep,
                reasoning: systemAnalysis.reasoning,
                timestamp: new Date().toISOString()
            };
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