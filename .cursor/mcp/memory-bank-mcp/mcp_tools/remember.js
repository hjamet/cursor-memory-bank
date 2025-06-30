import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { readUserbrief } from '../lib/userbrief_manager.js';
import { readTasks } from '../lib/task_manager.js';
import { encodeText, findSimilarMemories } from '../lib/semantic_search.js';
import { UserMessageManager } from '../lib/user_message_manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const memoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'agent_memory.json');
const longTermMemoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'long_term_memory.json');
const MAX_MEMORIES = 100;

// Helper functions
async function getRecentMemories(count = 5) {
    try {
        const data = await fs.readFile(memoryFilePath, 'utf8');
        const memories = JSON.parse(data);
        return memories.slice(-count);
    } catch (error) {
        return [];
    }
}

async function getTotalMemoriesCount() {
    try {
        const data = await fs.readFile(memoryFilePath, 'utf8');
        const memories = JSON.parse(data);
        return memories.length;
    } catch (error) {
        return 0;
    }
}

async function getTotalLongTermMemoriesCount() {
    try {
        const data = await fs.readFile(longTermMemoryFilePath, 'utf8');
        const memories = JSON.parse(data);
        return Array.isArray(memories) ? memories.length : 1;
    } catch (error) {
        return 0;
    }
}

async function getPossibleNextSteps(lastStep = null) {
    let possibleSteps = new Set();

    try {
        const userbrief = await readUserbrief();
        if (userbrief && userbrief.requests && userbrief.requests.some(r => r.status === 'new' || r.status === 'in_progress')) {
            possibleSteps.add('task-decomposition');
        }

        const tasks = await readTasks();
        if (tasks && tasks.some(t => t.status === 'TODO' || t.status === 'IN_PROGRESS')) {
            possibleSteps.add('implementation');
            // ENHANCED: After implementation, prioritize testing more strongly
            if (lastStep === 'implementation') {
                possibleSteps.add('experience-execution');
                // Also check if there are tasks in REVIEW status, which indicates recent implementation
                if (tasks.some(t => t.status === 'REVIEW')) {
                    possibleSteps.add('experience-execution');
                }
            }
            possibleSteps.add('fix');
        }

        // ENHANCED: Also recommend experience-execution if there are tasks in REVIEW status
        // This helps validate completed implementations
        if (tasks && tasks.some(t => t.status === 'REVIEW')) {
            possibleSteps.add('experience-execution');
        }

        // Default steps that are almost always possible
        possibleSteps.add('context-update');
        possibleSteps.add('system');

        if (possibleSteps.size === 0) {
            // Fallback to a safe default if no other steps are identified
            return ['context-update', 'system'];
        }

        return Array.from(possibleSteps);

    } catch (error) {
        // This can happen on first run if no context files exist.
        // In this case, the only valid next step is to start the process.
        if (error.code === 'ENOENT') {
            return ['START'];
        }
        // Debug logging removed to prevent JSON-RPC pollution
        // console.error(`Error determining next steps: ${error.message}`);
        // Fallback to a safe default
        return ['system'];
    }
}

async function getRecommendedNextStep(lastStep, possibleSteps, tasks = null) {
    // CRITICAL FIX: Prevent experience-execution loops
    // Rule: experience-execution can NEVER be followed by experience-execution
    if (lastStep === 'experience-execution') {
        // If coming from experience-execution, we need to determine the next step based on task status

        // Load tasks if not provided
        if (!tasks) {
            try {
                tasks = await readTasks();
            } catch (error) {
                // If we can't load tasks, default to context-update
                return 'context-update';
            }
        }

        // Find the current task (assuming it's the one that was being worked on)
        // Look for tasks that are IN_PROGRESS or recently moved to REVIEW
        const currentTask = tasks && tasks.find(t => t.status === 'IN_PROGRESS');

        if (currentTask) {
            // Task is still IN_PROGRESS, meaning experience-execution failed
            // Next step should be 'fix' to address the issues
            return 'fix';
        } else {
            // No IN_PROGRESS task found, meaning the task was likely completed
            // Check for new user requests first (highest priority)
            if (possibleSteps.includes('task-decomposition')) {
                return 'task-decomposition';
            }
            // Otherwise, default to context-update
            return 'context-update';
        }
    }

    // For all other cases, use the existing logic
    // Prioritize task-decomposition for new user requests (highest priority)
    if (possibleSteps.includes('task-decomposition')) {
        return 'task-decomposition';
    }

    // ENHANCED: Prioritize experience-execution after implementation
    if (lastStep === 'implementation' && possibleSteps.includes('experience-execution')) {
        return 'experience-execution';
    }

    // ENHANCED: Also prioritize experience-execution if there are tasks in REVIEW status
    // BUT: Allow workflow termination if ONLY REVIEW tasks exist (agent work complete)
    if (possibleSteps.includes('experience-execution')) {
        try {
            if (!tasks) {
                tasks = await readTasks();
            }
            if (tasks && tasks.some(t => t.status === 'REVIEW')) {
                // Check if ALL remaining tasks are REVIEW (agent work complete)
                const activeTasks = tasks.filter(t => ['TODO', 'IN_PROGRESS', 'BLOCKED'].includes(t.status));
                const reviewTasks = tasks.filter(t => t.status === 'REVIEW');

                // If no active tasks and only REVIEW tasks exist, prioritize context-update for potential termination
                if (activeTasks.length === 0 && reviewTasks.length > 0) {
                    if (possibleSteps.includes('context-update')) {
                        return 'context-update';
                    }
                }

                // Otherwise, proceed with experience-execution as normal
                return 'experience-execution';
            }
        } catch (error) {
            // If we can't check tasks, fall through to other logic
        }
    }

    // Other priority steps
    if (possibleSteps.includes('implementation')) {
        return 'implementation';
    }

    if (possibleSteps.includes('fix')) {
        return 'fix';
    }

    if (possibleSteps.includes('context-update')) {
        return 'context-update';
    }

    // Fallback to the first available step
    return possibleSteps[0] || 'context-update';
}

/**
 * Records the agent's state and determines the next step in the workflow.
 * This tool is the central nervous system of the autonomous agent, responsible for memory, reflection, and planning.
 *
 * **CRITICAL SELF-REFLECTION IS MANDATORY.**
 * The purpose of `remember` is not just to log what you did, but to perform a critical analysis of your own actions and their outcomes.
 *
 * - **`past`**: State what you *intended* to do.
 * - **`present`**: This is for critical analysis. Do not just say "I completed the task." Analyze the outcome.
 *   - **If successful**: What were the challenges? What trade-offs were made? Are there any weaknesses in the implementation that need to be monitored?
 *   - **If it failed**: What was the root cause of the failure? What were your flawed assumptions? What did you learn from the error?
 *   - **Be transparent about difficulties, mistakes, and imperfect solutions.** This is crucial for learning and improving.
 * - **`future`**: State your plan for the next step, based on your analysis of the present.
 * - **`long_term_memory`**: Use this to store critical, timeless information that will be useful in the future (e.g., architectural decisions, persistent bugs to avoid, core project principles). Do NOT use it for transient state.
 * - **`user_message`**: Use this **only** to report a critical issue that requires immediate user attention (e.g., a security vulnerability, a major blocker, a catastrophic failure). Do NOT use it for routine status updates. Be direct and factual.
 *
 * This tool drives the agent's learning and decision-making loop. High-quality, critical inputs are essential for a high-functioning autonomous system.
 *
 * @param {Object} args - The arguments for the memory tool.
 * @param {string} args.past - A description of what the agent was originally supposed to do.
 * @param {string} args.present - A detailed and **critical** description of what the agent has actually accomplished, the problems encountered, and the decisions made.
 * @param {string} args.future - A description of what the agent plans to do next.
 * @param {string} [args.long_term_memory] - Critical information to be stored in the persistent long-term memory.
 * @param {string} [args.user_message] - A critical message to be surfaced to the user, only for urgent issues.
 * @returns {Object} A response object containing the recorded memory and recommendations for the next step in the workflow.
 */
async function remember(args) {
    const { past, present, future, long_term_memory, user_message } = args;

    // Handle user message if provided
    let userMessageResult = null;
    if (user_message) {
        try {
            const userMessageManager = new UserMessageManager();

            // Get current context for the message
            const context = {
                workflow_rule: 'implementation', // This could be enhanced to detect current rule
                active_task: null, // This could be enhanced to detect current task
                agent_state: 'processing'
            };

            userMessageResult = await userMessageManager.addMessage(user_message, context);
        } catch (error) {
            // Include the error details in the response instead of throwing
            userMessageResult = {
                success: false,
                error: error.message,
                message: `Failed to record user message: ${error.message}`
            };
        }
    }

    // Handle long-term memory with semantic encoding
    let longTermMemories = [];
    let currentLongTermMemory = null;

    // Read existing long-term memories
    try {
        const data = await fs.readFile(longTermMemoryFilePath, 'utf8');
        const parsed = JSON.parse(data);
        longTermMemories = Array.isArray(parsed) ? parsed : [parsed];
    } catch (error) {
        if (error.code !== 'ENOENT') {
            throw new Error(`Failed to read long-term memory file: ${error.message}`);
        }
        // File doesn't exist, start with empty array
        longTermMemories = [];
    }

    // Add new long-term memory if provided
    if (long_term_memory) {
        try {
            // Encode the new memory
            const embedding = await encodeText(long_term_memory);
            const newMemory = {
                content: long_term_memory,
                timestamp: new Date().toISOString(),
                embedding: embedding
            };

            longTermMemories.push(newMemory);
            currentLongTermMemory = long_term_memory;

            // Save updated memories
            await fs.mkdir(path.dirname(longTermMemoryFilePath), { recursive: true });
            await fs.writeFile(longTermMemoryFilePath, JSON.stringify(longTermMemories, null, 2), 'utf8');
        } catch (error) {
            throw new Error(`Failed to write long-term memory file: ${error.message}`);
        }
    }

    // Read preferences from userbrief (status === 'preference')
    let preferences = [];
    try {
        const userbriefData = await readUserbrief();
        if (userbriefData && userbriefData.requests) {
            preferences = userbriefData.requests
                .filter(req => req.status === 'preference')
                .map(req => req.content);
        }
    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.warn(`[Remember] Could not read preferences from userbrief: ${error.message}`);
        // Do not throw; failing to read userbrief should not stop the remember tool.
        preferences = [];
    }

    let memories = [];
    try {
        const data = await fs.readFile(memoryFilePath, 'utf8');
        memories = JSON.parse(data);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            throw new Error(`Failed to read memory file: ${error.message}`);
        }
        // File doesn't exist, will be created.
    }

    const newMemory = {
        timestamp: new Date().toISOString(),
        past,
        present,
        future,
    };

    memories.push(newMemory);

    if (memories.length > MAX_MEMORIES) {
        memories = memories.slice(memories.length - MAX_MEMORIES);
    }

    try {
        await fs.mkdir(path.dirname(memoryFilePath), { recursive: true });
        await fs.writeFile(memoryFilePath, JSON.stringify(memories, null, 2), 'utf8');
    } catch (error) {
        throw new Error(`Failed to write memory file: ${error.message}`);
    }

    const recentMemories = memories.slice(-10); // Get 10 most recent working memories
    const lastMemory = memories[memories.length - 1];

    // Extract the last rule from the 'past' field of the last memory
    let lastStep = null;
    if (lastMemory && lastMemory.past) {
        // Try to find step name in backticks first
        const match = lastMemory.past.match(/`([^`]+)`/);
        if (match && match[1]) {
            lastStep = match[1];
        } else {
            // Fallback: look for common step names in the text
            const stepNames = ['context-update', 'implementation', 'task-decomposition', 'start-workflow', 'experience-execution', 'fix'];
            for (const stepName of stepNames) {
                if (lastMemory.past.toLowerCase().includes(stepName)) {
                    lastStep = stepName;
                    break;
                }
            }
        }
    }

    // CRITICAL: Check for workflow completion when coming from context-update
    if (lastStep === 'context-update') {
        try {
            const userbrief = await readUserbrief();
            const tasks = await readTasks();

            // Check for unprocessed requests (status 'new' or 'in_progress')
            const hasUnprocessedRequests = userbrief.requests && userbrief.requests.some(r =>
                r.status === 'new' || r.status === 'in_progress'
            );

            // Check for active tasks (not completed)
            const hasActiveTasks = tasks && tasks.some(t =>
                ['TODO', 'IN_PROGRESS', 'BLOCKED'].includes(t.status)
            );

            // ENHANCED: Check for REVIEW-only state (agent work complete, user validation pending)
            const hasReviewTasks = tasks && tasks.some(t => t.status === 'REVIEW');
            const isReviewOnlyState = !hasActiveTasks && hasReviewTasks && !hasUnprocessedRequests;

            // DEBUG: Add debug information to understand the state
            const debugInfo = {
                lastStep,
                hasUnprocessedRequests,
                hasActiveTasks,
                hasReviewTasks,
                isReviewOnlyState,
                requestCount: userbrief.requests ? userbrief.requests.length : 0,
                taskCount: tasks ? tasks.length : 0,
                requestStatuses: userbrief.requests ? userbrief.requests.map(r => r.status) : [],
                taskStatuses: tasks ? tasks.map(t => t.status) : []
            };

            // WORKFLOW TERMINATION: Allow termination when no active work remains for agent
            // This includes both complete state (no tasks) and REVIEW-only state (agent work done)
            if (!hasUnprocessedRequests && (!hasActiveTasks || isReviewOnlyState)) {
                // WORKFLOW COMPLETE - Return proper MCP response structure
                const completionMessage = isReviewOnlyState
                    ? "Memory has been saved. Agent work is complete - only user validation remains. The workflow can be stopped."
                    : "Memory has been saved. The workflow is complete and can be stopped.";
                const workflowInstruction = isReviewOnlyState
                    ? "STOP: Agent work complete. Only tasks in REVIEW status remain (user validation required)."
                    : "STOP: All tasks and user requests have been processed.";

                const completionResponse = {
                    message: completionMessage,
                    workflow_status: "WORKFLOW_COMPLETE",
                    next_action_required: "The workflow is complete. Do not call next_rule. You can stop.",
                    workflow_instruction: workflowInstruction,
                    recommended_next_step: null,
                    current_state: future,
                    possible_next_steps: [],
                    user_preferences: preferences,
                    long_term_memory: currentLongTermMemory,
                    recent_working_memories: await getRecentMemories(5),
                    semantic_long_term_memories: [],
                    total_memories_count: await getTotalMemoriesCount(),
                    total_long_term_memories_count: await getTotalLongTermMemoriesCount(),
                    user_message_result: userMessageResult,
                    continuation_mandatory: false,
                    stopping_prohibited: "You are allowed to stop. The workflow is complete.",
                    immediate_next_action: "The workflow is complete. No further action is required.",
                    workflow_cycle_reminder: "The workflow cycle is now complete. Await new user instructions.",
                    debug_info: debugInfo
                };

                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify(completionResponse, null, 2)
                    }]
                };
            }
        } catch (error) {
            // If we can't check the state, fall through to normal workflow continuation
        }
    }

    const possible_next_steps = await getPossibleNextSteps(lastStep);

    // Find semantically similar long-term memories based on the last "future" 
    let semanticLongTermMemories = [];
    if (lastMemory && lastMemory.future && longTermMemories.length > 0) {
        semanticLongTermMemories = await findSimilarMemories(lastMemory.future, longTermMemories, 3);
    }

    // Load tasks for the recommendation logic
    let tasks = null;
    try {
        tasks = await readTasks();
    } catch (error) {
        // Tasks will remain null, handled in getRecommendedNextStep
    }

    // Use the new function to determine the recommended next step
    const recommendedNextStep = await getRecommendedNextStep(lastStep, possible_next_steps, tasks);
    let workflowInstruction = "";

    // Generate appropriate workflow instructions based on the recommended step
    if (recommendedNextStep === 'experience-execution') {
        if (lastStep === 'implementation') {
            workflowInstruction = "CONTINUE WORKFLOW: Implementation complete. You should now test the changes manually using 'experience-execution' to validate the implementation before proceeding.";
        } else if (tasks && tasks.some(t => t.status === 'REVIEW')) {
            workflowInstruction = "CONTINUE WORKFLOW: Tasks in REVIEW status detected. You should validate these implementations using 'experience-execution' to ensure they work correctly.";
        } else {
            workflowInstruction = "CONTINUE WORKFLOW: Manual testing/validation required. You must now call mcp_MemoryBankMCP_next_rule with 'experience-execution'.";
        }
    } else if (recommendedNextStep === 'task-decomposition') {
        // Get example request to provide context
        let exampleRequestInfo = "";
        try {
            const userbriefData = await readUserbrief();
            if (userbriefData && userbriefData.requests) {
                const newRequests = userbriefData.requests.filter(req => req.status === 'new');
                if (newRequests.length > 0) {
                    // Sort by ID to get the oldest unprocessed request
                    newRequests.sort((a, b) => a.id - b.id);
                    const oldestRequest = newRequests[0];
                    const contentPreview = oldestRequest.content.length > 200
                        ? oldestRequest.content.substring(0, 200) + "..."
                        : oldestRequest.content;
                    const createdDate = new Date(oldestRequest.created_at).toLocaleDateString();

                    exampleRequestInfo = `\n\nExample request to process:\nRequest #${oldestRequest.id} (created ${createdDate}):\n"${contentPreview}"`;
                }
            }
        } catch (error) {
            exampleRequestInfo = "";
        }

        workflowInstruction = `CONTINUE WORKFLOW: New user requests detected. You must now call mcp_MemoryBankMCP_next_rule with 'task-decomposition' to process pending requests. STOPPING IS PROHIBITED.${exampleRequestInfo}`;
    } else if (recommendedNextStep === 'implementation') {
        workflowInstruction = "CONTINUE WORKFLOW: Tasks are available for implementation. You must now call mcp_MemoryBankMCP_next_rule with 'implementation' to continue working on tasks. STOPPING IS PROHIBITED.";
    } else if (recommendedNextStep === 'fix') {
        workflowInstruction = "CONTINUE WORKFLOW: Issues detected that need resolution. You must now call mcp_MemoryBankMCP_next_rule with 'fix' to address problems. STOPPING IS PROHIBITED.";
    } else if (recommendedNextStep === 'context-update') {
        workflowInstruction = "CONTINUE WORKFLOW: Context refresh needed. You must now call mcp_MemoryBankMCP_next_rule with 'context-update' to refresh project context. STOPPING IS PROHIBITED.";
    } else {
        workflowInstruction = "CONTINUE WORKFLOW: You must now call mcp_MemoryBankMCP_next_rule to continue the autonomous workflow. STOPPING IS ABSOLUTELY PROHIBITED. Memory recording is a continuation point, not an end point.";
    }

    // Workflow Completion Check: New logic to allow pausing the workflow
    if (lastMemory && lastMemory.future && lastMemory.future.toLowerCase().includes('paused')) {
        const pauseResponse = {
            message: "Memory recorded. Workflow has been instructed to pause.",
            // Keep the status as CONTINUE_REQUIRED to avoid client errors, but use other fields to signal a stop.
            workflow_status: "CONTINUE_REQUIRED",
            next_action_required: "No further action is required. The workflow can be paused.",
            workflow_instruction: "WORKFLOW PAUSED: The autonomous workflow has been intentionally paused. Do not call next_rule.",
            recommended_next_step: null, // No recommendation
            current_state: lastMemory.future,
            possible_next_steps: [],
            user_preferences: preferences,
            long_term_memory: currentLongTermMemory,
            recent_working_memories: recentMemories,
            semantic_long_term_memories: semanticLongTermMemories,
            total_memories_count: memories.length,
            total_long_term_memories_count: longTermMemories.length,
            user_message_result: userMessageResult,
            continuation_mandatory: false, // The key change to allow stopping
            stopping_prohibited: "You may stop.",
            immediate_next_action: null,
            workflow_cycle_reminder: "The workflow is paused. Await new instructions."
        };

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(pauseResponse, null, 2)
            }]
        };
    }

    const response = {
        message: "Memory successfully recorded.",
        workflow_status: "CONTINUE_REQUIRED",
        next_action_required: `You MUST continue the workflow by calling mcp_MemoryBankMCP_next_rule with '${recommendedNextStep}'. Do not stop here.`,
        workflow_instruction: workflowInstruction,
        recommended_next_step: recommendedNextStep,
        current_state: lastMemory ? lastMemory.future : "No current state.",
        possible_next_steps: possible_next_steps,
        user_preferences: preferences, // Always show preferences
        long_term_memory: currentLongTermMemory, // Only the newly added one, if any
        recent_working_memories: recentMemories, // 10 most recent working memories
        semantic_long_term_memories: semanticLongTermMemories, // 3 most semantically relevant long-term memories
        total_memories_count: memories.length,
        total_long_term_memories_count: longTermMemories.length,
        user_message_result: userMessageResult, // Include the result of the user message operation
        continuation_mandatory: true,
        stopping_prohibited: "CRITICAL: Memory recording is NOT a completion signal. You MUST continue the autonomous workflow.",
        immediate_next_action: `Call mcp_MemoryBankMCP_next_rule with parameter: '${recommendedNextStep}'`,
        workflow_cycle_reminder: "Remember: record → next_rule → execute → remember → next_rule (infinite loop)"
    };

    return {
        content: [{
            type: 'text',
            text: JSON.stringify(response, null, 2)
        }]
    };
}

export const rememberSchema = {
    past: z.string().describe("PASSÉ - Rédigez en français une description de ce que l'agent avait initialement prévu de faire. Exemple : 'J'ai été appelé pour implémenter la fonctionnalité d'authentification JWT selon les spécifications de la tâche #15.'"),
    present: z.string().describe("PRÉSENT - Rédigez en français une description détaillée de ce que l'agent a réellement accompli, les problèmes rencontrés et les décisions prises. Exemple : 'J'ai implémenté avec succès le système d'authentification JWT en créant les middlewares de validation, les routes de connexion et les tests unitaires. Quelques ajustements ont été nécessaires pour la gestion des tokens expirés.'"),
    future: z.string().describe("FUTUR - Rédigez en français une description de ce que l'agent prévoit de faire ensuite. Exemple : 'Je vais maintenant passer à l'implémentation des permissions utilisateur selon la tâche #16, en me concentrant sur le système de rôles.'"),
    long_term_memory: z.string().optional().describe("MÉMOIRE LONG TERME - Rédigez en français uniquement les informations critiques du projet à conserver de façon persistante (ex: schémas de base de données, décisions architecturales, conventions de code, bugs récurrents à éviter). N'utilisez cet argument QUE pour des informations qui resteront toujours vraies et utiles. Exemples: 'La BDD utilise PostgreSQL avec une table users (id, email, password_hash)', 'L'authentification utilise des tokens JWT avec une expiration de 24h stockés dans des cookies httpOnly', 'Pattern de bug: le schéma MCP requiert des objets simples, pas des appels z.object().'"),
    user_message: z.string().optional().describe("MESSAGE CRITIQUE POUR L'UTILISATEUR - Message facultatif (1-3 phrases). N'utilisez PAS ce champ pour des mises à jour positives ou banales. Utilisez-le pour signaler un problème, un risque, ou une découverte qui nécessite l'attention de l'utilisateur. Soyez direct et factuel. Exemples : 'L'implémentation actuelle de l'API présente une faille de sécurité potentielle, une revue est nécessaire.', 'Le bug #142 est plus complexe que prévu, l'estimation de temps est revue à la hausse.', 'Je suis bloqué sur la tâche #152 en raison d'une dépendance externe non disponible.'"),
};

export { remember as handleRemember }; 