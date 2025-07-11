import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import nunjucks from 'nunjucks';
import { readMemoryContext } from '../lib/memory_context.js';
import { readUserbriefData } from '../lib/userbrief_manager.js';
import { taskManager } from '../lib/task_manager.js';
import { getPossibleNextSteps, getRecommendedNextStep, analyzeSystemState as centralizedAnalyzeSystemState } from '../lib/workflow_recommendation.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workflowDirPath = path.join(__dirname, '..', '..', '..', 'workflow-steps');

// Configure nunjucks
nunjucks.configure(workflowDirPath, { autoescape: false });

/**
 * Update workflow state file with the current rule
 * @param {string} step_name - The workflow step name being executed
 */
async function updateWorkflowState(step_name) {
    try {
        const workflowStateFile = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'workflow_state.json');

        // Read current workflow state
        let workflowState = {
            current_rule: null,
            status: "idle",
            history: []
        };

        try {
            const existingData = await fs.readFile(workflowStateFile, 'utf8');
            workflowState = JSON.parse(existingData);
        } catch (error) {
            // File doesn't exist or is corrupted, use default structure
        }

        // Update with new rule
        const timestamp = new Date().toISOString();
        workflowState.current_rule = step_name;
        workflowState.status = "active";
        workflowState.last_updated = timestamp;

        // Add to history (keep last 10 entries)
        if (!Array.isArray(workflowState.history)) {
            workflowState.history = [];
        }

        workflowState.history.unshift({
            rule: step_name,
            timestamp: timestamp
        });

        // Keep only last 10 history entries
        if (workflowState.history.length > 10) {
            workflowState.history = workflowState.history.slice(0, 10);
        }

        // Write updated state back to file atomically
        await fs.writeFile(workflowStateFile, JSON.stringify(workflowState, null, 2), 'utf8');

    } catch (error) {
        // Log error but don't fail the workflow
        console.warn(`Could not update workflow state: ${error.message}`);
    }
}

/**
 * Analyze system state to determine optimal next workflow step
 * UPDATED: Now uses centralized workflow recommendation logic
 * @param {Object} context - System context including tasks and requests
 * @returns {Object} Analysis result with recommended step and reasoning
 */
async function analyzeSystemState(context) {
    // Use centralized analysis logic for consistency
    return await centralizedAnalyzeSystemState(context);
}

/**
 * Get optimized context based on workflow step to prevent agent saturation
 * ENHANCED VERSION: Implements specific context filtering per rule according to Task #64 specifications
 * @param {string} step_name - The workflow step name
 * @returns {Object} Optimized context for the specific step
 */
async function getOptimizedContext(step_name) {
    const context = {};

    // Step-specific context loading according to Task #64 specifications
    switch (step_name) {
        case 'start-workflow':
        case 'context-update':
            await loadStartWorkflowContext(context);
            break;
        case 'task-decomposition':
            await loadTaskDecompositionContext(context);
            break;
        case 'implementation':
            await loadImplementationContext(context);
            break;
        case 'experience-execution':
        case 'fix':
            await loadExperienceFixContext(context);
            break;
        default:
            // Fallback for unknown steps - minimal context
            await loadMinimalContext(context);
            break;
    }

    return context;
}

/**
 * Load context for start-workflow and context-update rules
 * Includes: projectbrief + techcontext + current task + 3 oldest unprocessed requests + 3 most urgent tasks
 */
async function loadStartWorkflowContext(context) {
    // Always include project brief and tech context for these rules
    try {
        const contextDir = path.join(__dirname, '..', '..', '..', 'memory-bank', 'context');
        const projectBrief = await fs.readFile(path.join(contextDir, 'projectBrief.md'), 'utf8');
        const techContext = await fs.readFile(path.join(contextDir, 'techContext.md'), 'utf8');

        context.project_brief = projectBrief;
        context.tech_context = techContext;
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load project context: ${error.message}`);
        return null;
    }

    // Load recent memories (standard 10)
    await loadRecentMemories(context, 10);

    // Load long-term memories (standard 3)
    await loadLongTermMemories(context, 3);

    // Load current task if exists
    await loadCurrentTask(context);

    // Load 3 oldest unprocessed requests
    await loadUnprocessedRequests(context, 3);

    // Load 3 most urgent tasks (titles and short descriptions only)
    await loadUrgentTasks(context, 3);

    // Load user preferences (limited to 3)
    await loadUserPreferences(context, 3);
}

/**
 * Load context for task-decomposition rule
 * Includes: 1 oldest unprocessed request + complete task list (titles/IDs/descriptions only)
 */
async function loadTaskDecompositionContext(context) {
    // Load recent memories (standard 10)
    await loadRecentMemories(context, 10);

    // Load long-term memories (standard 3)
    await loadLongTermMemories(context, 3);

    // Load only 1 oldest unprocessed request
    await loadUnprocessedRequests(context, 1);

    // Load complete task list with minimal info (titles, IDs, descriptions only)
    await loadCompleteTaskList(context);

    // Load user preferences (limited to 3)
    await loadUserPreferences(context, 3);
}

/**
 * Load context for implementation rule
 * Includes: only the most urgent task with full details
 */
async function loadImplementationContext(context) {
    // Load recent memories (standard 10)
    await loadRecentMemories(context, 10);

    // Load long-term memories (standard 3)
    await loadLongTermMemories(context, 3);

    // Load only the most urgent task with full details
    await loadMostUrgentTask(context);

    // No userbrief data needed for implementation - agent should focus on tasks only
    context.unprocessed_requests = [];
    context.userbrief = { requests: [], summary: "Focus on task implementation" };

    // Load user preferences (limited to 3)
    await loadUserPreferences(context, 3);
}

/**
 * Load context for experience-execution and fix rules
 * Includes: 10 long-term memories + current task if applicable
 */
async function loadExperienceFixContext(context) {
    // Load recent memories (standard 10)
    await loadRecentMemories(context, 10);

    // Load MORE long-term memories for debugging/testing (10 instead of 3)
    await loadLongTermMemories(context, 10);

    // Load current task if exists
    await loadCurrentTask(context);

    // No userbrief data needed for experience-execution/fix - focus on debugging/testing
    context.unprocessed_requests = [];
    context.userbrief = { requests: [], summary: "Focus on debugging and testing" };

    // Load user preferences (limited to 3)
    await loadUserPreferences(context, 3);
}

/**
 * Load minimal context for unknown steps
 */
async function loadMinimalContext(context) {
    await loadRecentMemories(context, 5);
    await loadLongTermMemories(context, 2);
    await loadUserPreferences(context, 2);
}

/**
 * Helper function to load recent memories
 */
async function loadRecentMemories(context, limit = 10) {
    try {
        const workflowDir = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow');
        const memoryFilePath = path.join(workflowDir, 'agent_memory.json');
        const memoryData = await fs.readFile(memoryFilePath, 'utf8');
        const agentMemory = JSON.parse(memoryData);

        context.recent_memories = agentMemory ? agentMemory.slice(-limit) : [];

        // Get previous rule from last memory
        if (agentMemory && agentMemory.length > 0) {
            const lastMemory = agentMemory[agentMemory.length - 1];
            const futureText = lastMemory.future || '';
            const ruleMatch = futureText.match(/(\w+-\w+|\w+)\s+(rule|step)/i);
            context.previous_rule = ruleMatch ? ruleMatch[1] : 'system';
        } else {
            context.previous_rule = 'system';
        }
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load memory context: ${error.message}`);
        context.recent_memories = [];
        context.previous_rule = 'system';
    }
}

/**
 * Helper function to load long-term memories
 */
async function loadLongTermMemories(context, limit = 3) {
    try {
        const workflowDir = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow');
        const longTermMemoryFilePath = path.join(workflowDir, 'long_term_memory.json');
        const longTermData = await fs.readFile(longTermMemoryFilePath, 'utf8');
        const longTermMemory = JSON.parse(longTermData);

        const memories = Array.isArray(longTermMemory) ? longTermMemory : [longTermMemory];

        // Remove embeddings from memories to prevent context saturation
        // Keep only content and timestamp for agent readability
        const memoriesWithoutEmbeddings = memories.slice(0, limit).map(memory => ({
            content: memory.content,
            timestamp: memory.timestamp
        }));

        context.relevant_long_term_memories = memoriesWithoutEmbeddings;
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load long-term memory: ${error.message}`);
        context.relevant_long_term_memories = [];
    }
}

/**
 * Helper function to load current task (for start-workflow, context-update, experience-execution, fix)
 */
async function loadCurrentTask(context) {
    try {
        const tasks = taskManager.getAllTasks();
        const inProgressTasks = tasks.filter(t => t.status === 'IN_PROGRESS');

        if (inProgressTasks.length > 0) {
            // Return the first in-progress task with full details
            context.current_task = inProgressTasks[0];
        } else {
            context.current_task = null;
        }
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load current task: ${error.message}`);
        context.current_task = null;
    }
}

/**
 * Helper function to load unprocessed requests (limited by count)
 */
async function loadUnprocessedRequests(context, limit = 3) {
    try {
        const userbriefData = readUserbriefData();
        const allUnprocessedRequests = userbriefData.requests ?
            userbriefData.requests.filter(req => req.status === 'new' || req.status === 'in_progress') : [];

        if (allUnprocessedRequests.length > 0) {
            const sortedRequests = allUnprocessedRequests.sort((a, b) =>
                new Date(a.created_at) - new Date(b.created_at)
            );

            context.unprocessed_requests = sortedRequests.slice(0, limit);
            context.userbrief = {
                version: userbriefData.version,
                last_id: userbriefData.last_id,
                requests: sortedRequests.slice(0, limit),
                total_unprocessed_count: allUnprocessedRequests.length
            };
        } else {
            context.unprocessed_requests = [];
            context.userbrief = {
                version: userbriefData.version || "1.0.0",
                last_id: userbriefData.last_id || 0,
                requests: [],
                total_unprocessed_count: 0
            };
        }
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load userbrief in next_rule: ${error.message}`);
        context.userbrief = { requests: [], total_unprocessed_count: 0 };
        context.unprocessed_requests = [];
    }
}

/**
 * Helper function to load 3 most urgent tasks (titles and short descriptions only)
 */
async function loadUrgentTasks(context, limit = 3) {
    try {
        const tasks = taskManager.getAllTasks();
        const activeTasks = tasks.filter(t => t.status === 'TODO' || t.status === 'IN_PROGRESS' || t.status === 'BLOCKED');

        // Sort by priority (higher first) then by creation date
        const sortedTasks = activeTasks.sort((a, b) => {
            if (b.priority !== a.priority) return b.priority - a.priority;
            return new Date(a.created_date) - new Date(b.created_date);
        });

        // Return only titles and short descriptions
        context.urgent_tasks = sortedTasks.slice(0, limit).map(task => ({
            id: task.id,
            title: task.title,
            short_description: task.short_description,
            status: task.status,
            priority: task.priority
        }));

        // Use centralized statistics calculation for consistency
        const centralizedStats = await calculateTaskStatistics(tasks);
        context.current_tasks_summary = centralizedStats.current_tasks_summary;
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load urgent tasks: ${error.message}`);
        context.urgent_tasks = [];
        context.current_tasks_summary = 'Task summary unavailable';
    }
}

/**
 * Helper function to load complete task list for task-decomposition (titles, IDs, descriptions only)
 */
async function loadCompleteTaskList(context) {
    try {
        const tasks = taskManager.getAllTasks();
        const activeTasks = tasks.filter(t => t.status === 'TODO' || t.status === 'IN_PROGRESS');

        // Return minimal task info for task-decomposition
        context.complete_task_list = activeTasks.map(task => ({
            id: task.id,
            title: task.title,
            short_description: task.short_description,
            status: task.status,
            priority: task.priority
        }));

        // Use centralized statistics calculation for consistency
        const centralizedStats = await calculateTaskStatistics(tasks);
        context.current_tasks_summary = centralizedStats.current_tasks_summary;
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load complete task list: ${error.message}`);
        context.complete_task_list = [];
        context.current_tasks_summary = 'Task summary unavailable';
    }
}

/**
 * Helper function to load the most urgent task with full details (for implementation)
 */
async function loadMostUrgentTask(context) {
    try {
        const tasks = taskManager.getAllTasks();
        const activeTasks = tasks.filter(t => t.status === 'TODO' || t.status === 'IN_PROGRESS' || t.status === 'BLOCKED');

        if (activeTasks.length > 0) {
            // Sort by priority (higher first) then by creation date
            const sortedTasks = activeTasks.sort((a, b) => {
                if (b.priority !== a.priority) return b.priority - a.priority;
                return new Date(a.created_date) - new Date(b.created_date);
            });

            // Return the most urgent task with full details
            const mostUrgentTask = sortedTasks.slice(0, 1);
            context.most_urgent_task = mostUrgentTask[0];
        } else {
            context.most_urgent_task = null;
        }

        // Enhance task with image data if available
        if (context.most_urgent_task && context.most_urgent_task.image) {
            const imagePath = path.join('C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\temp\\images', context.most_urgent_task.image);
            try {
                const imageBuffer = await fs.readFile(imagePath);
                context.most_urgent_task.image_data = {
                    type: 'image',
                    data: imageBuffer.toString('base64'),
                    mimeType: 'image/jpeg' // Assuming jpeg for now
                };
            } catch (error) {
                // Image not found or could not be read, do not add image_data
            }
        }

        // Use centralized statistics calculation for consistency
        const centralizedStats = await calculateTaskStatistics(tasks);
        context.current_tasks_summary = centralizedStats.current_tasks_summary;
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load most urgent task: ${error.message}`);
        context.most_urgent_task = null;
        context.current_tasks_summary = 'Task summary unavailable';
    }
}

/**
 * Helper function to load user preferences (limited)
 */
async function loadUserPreferences(context, limit = 3) {
    try {
        const userbriefData = readUserbriefData();
        context.user_preferences = userbriefData.requests ?
            userbriefData.requests
                .filter(req => req.status === 'preference' || req.status === 'pinned')
                .slice(0, limit)
                .map(req => req.content) : [];
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load user preferences: ${error.message}`);
        context.user_preferences = [];
    }
}

async function getStep(step_name) {
    const stepFilePath = path.join(workflowDirPath, `${step_name}.md`);
    try {
        const templateContent = await fs.readFile(stepFilePath, 'utf8');

        // Get optimized context for this specific step
        const context = await getOptimizedContext(step_name);

        // Add intelligent system state analysis
        const systemAnalysis = await analyzeSystemState(context);
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

    // Update workflow state
    await updateWorkflowState(step_name);

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