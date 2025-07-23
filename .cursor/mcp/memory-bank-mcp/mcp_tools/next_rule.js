import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import nunjucks from 'nunjucks';
import { readMemoryContext } from '../lib/memory_context.js';
import { taskManager } from '../lib/task_manager.js';
import { getPossibleNextSteps, getRecommendedNextStep, analyzeSystemState as centralizedAnalyzeSystemState } from '../lib/workflow_recommendation.js';
import { incrementImplementationCount } from '../lib/workflow_state.js';
import { loadUserPreferences, readUserbriefData } from './utils.js';
import { calculateTaskStatistics } from '../lib/task_statistics.js';

/**
 * Load workflow mode from workflow_state.json
 * @returns {string} - The current workflow mode ('infinite' or 'task_by_task')
 */
async function loadWorkflowMode() {
    try {
        const workflowStateFile = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'workflow_state.json');
        const workflowStateData = await fs.readFile(workflowStateFile, 'utf8');
        const workflowState = JSON.parse(workflowStateData);
        return workflowState.mode || 'infinite'; // Default to infinite if mode is not specified
    } catch (error) {
        // If file doesn't exist or is corrupted, default to infinite mode
        return 'infinite';
    }
}

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

        // Read current workflow state with default structure compatible with workflow_state.js
        let workflowState = {
            version: "1.0.0",
            implementation_count: 0,
            last_readme_task_at: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            current_rule: null,
            status: "idle",
            history: []
        };

        try {
            const existingData = await fs.readFile(workflowStateFile, 'utf8');
            const existingState = JSON.parse(existingData);

            // Preserve all existing fields, especially implementation_count and last_readme_task_at
            workflowState = {
                ...workflowState,
                ...existingState
            };
        } catch (error) {
            // File doesn't exist or is corrupted, use default structure
        }

        // Update with new rule
        const timestamp = new Date().toISOString();
        workflowState.current_rule = step_name;
        workflowState.status = "active";
        workflowState.last_updated = timestamp;
        workflowState.updated_at = timestamp;

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
        // Log error but don't fail the workflow (commented to prevent MCP JSON corruption)
        // console.warn(`Could not update workflow state: ${error.message}`);
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
 * Function to create a README generation task when README.md is missing
 */
async function createReadmeTask() {
    try {
        const readmeTask = {
            title: "Créer le fichier README.md manquant",
            short_description: "Générer automatiquement le fichier README.md du projet avec vue d'ensemble, dépendances, informations techniques et instructions d'installation.",
            detailed_description: "Le fichier README.md est manquant dans le projet. Il doit être créé avec les sections suivantes :\n\n**Sections requises :**\n- Vue d'ensemble du projet et objectifs\n- Instructions d'installation et prérequis\n- Dépendances principales et leur rôle\n- Informations techniques sur l'architecture\n- Guide d'utilisation de base\n- Exemples de configuration\n- Liens vers la documentation détaillée\n\n**Critères d'acceptation :**\n- Le fichier README.md existe à la racine du projet\n- Toutes les sections obligatoires sont présentes\n- Les instructions d'installation sont testables\n- Les informations techniques sont à jour\n- Le format Markdown est correct et lisible\n\n**Notes techniques :**\n- S'inspirer de la structure des projets similaires\n- Utiliser un ton professionnel mais accessible\n- Inclure des badges de statut si approprié\n- Maintenir la cohérence avec le reste de la documentation",
            priority: 4,
            status: "TODO",
            dependencies: [],
            impacted_files: ["README.md"],
            validation_criteria: "Le fichier README.md existe, contient toutes les sections requises, et les instructions d'installation sont fonctionnelles."
        };

        await taskManager.createTask(readmeTask);
        // console.log("Task created for missing README.md"); // Commented to prevent MCP JSON corruption
    } catch (error) {
        // console.error("Failed to create README task:", error.message); // Commented to prevent MCP JSON corruption
    }
}

/**
 * Load context for start-workflow and context-update rules
 * Includes: projectbrief + techcontext + current task + 3 oldest unprocessed requests + 3 most urgent tasks
 */
async function loadStartWorkflowContext(context) {
    // Always include README.md as project context for these rules
    try {
        const readmePath = path.join(__dirname, '..', '..', '..', '..', 'README.md');
        const readmeContent = await fs.readFile(readmePath, 'utf8');
        context.project_context = readmeContent;
    } catch (error) {
        // README.md doesn't exist, create a task to generate it
        await createReadmeTask();
        context.project_context = "README.md is missing and a task has been created to generate it.";
    }

    // Load recent memories (standard 10)
    await loadRecentMemories(context, 10);

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
            context.previous_rule = ruleMatch ? ruleMatch[1] : 'start-workflow';
        } else {
            context.previous_rule = 'start-workflow';
        }
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`Could not load memory context: ${error.message}`);
        context.recent_memories = [];
        context.previous_rule = 'start-workflow';
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
        await taskManager.loadTasks(); // FIX: Load tasks from file first
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
        await taskManager.loadTasks(); // FIX: Load tasks from file first
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
        await taskManager.loadTasks(); // FIX: Load tasks from file first
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
        await taskManager.loadTasks(); // FIX: Load tasks from file first
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
            context.current_task = mostUrgentTask[0];
        } else {
            context.current_task = null;
        }

        // Enhance task with image data if available
        if (context.current_task && context.current_task.image) {
            const imagePath = path.join('C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\temp\\images', context.current_task.image);
            try {
                const imageBuffer = await fs.readFile(imagePath);
                context.current_task.image_data = {
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
        context.current_task = null;
        context.current_tasks_summary = 'Task summary unavailable';
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

        // Add workflow mode information to context
        const workflowMode = await loadWorkflowMode();
        context.workflow_mode = {
            current_mode: workflowMode,
            description: workflowMode === 'infinite'
                ? 'Mode Workflow Infini: L\'agent continue automatiquement le workflow'
                : 'Mode Tâche par Tâche: L\'agent s\'arrêtera à context-update',
            stopping_behavior: workflowMode === 'task_by_task'
                ? 'L\'agent s\'arrêtera à context-update pour permettre un nouveau cycle propre'
                : 'L\'agent continue indéfiniment selon le pattern normal du workflow'
        };

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

    // **AUTOMATIC IMPLEMENTATION COUNTER UPDATE**
    // Increment implementation counter automatically when implementation step is called
    if (step_name === 'implementation') {
        try {
            const incrementResult = await incrementImplementationCount();

            // Log the increment for debugging (commented out to prevent MCP JSON corruption)
            // console.log(`[NextRule] Implementation counter incremented to ${incrementResult.count}`);

            // If README task should be triggered, log it (commented out to prevent MCP JSON corruption)
            if (incrementResult.shouldTriggerReadmeTask) {
                // console.log(`[NextRule] README task trigger condition met: ${incrementResult.triggerReason}`);
            }

            // This is just the automatic counter increment as specified in the task requirements
        } catch (error) {
            // Log error but don't fail the workflow - the counter increment is supplementary (commented out to prevent MCP JSON corruption)
            // console.warn(`[NextRule] Failed to increment implementation counter: ${error.message}`);
        }
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