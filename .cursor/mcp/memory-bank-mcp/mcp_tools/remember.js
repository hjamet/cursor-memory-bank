import { z } from 'zod';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { readUserbrief } from '../lib/userbrief_manager.js';
import { readTasks } from '../lib/task_manager.js';
import { encodeText, findSimilarMemories } from '../lib/semantic_search.js';
import { UserMessageManager } from '../lib/user_message_manager.js';
import { getPossibleNextSteps, getRecommendedNextStep } from '../lib/workflow_recommendation.js';
import { resetTransitionCounter } from '../lib/workflow_safety.js';
import { readUserMessages, getPendingMessages, markMessageAsConsumed, cleanupConsumedMessages } from '../lib/user_message_storage.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const memoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'agent_memory.json');
const longTermMemoryFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'long_term_memory.json');
const MAX_MEMORIES = 100;

// Test message patterns to filter out
const TEST_MESSAGE_PATTERNS = [
    /voici la clé secrète\s*:\s*42/i,
    /clé secrète.*42/i,
    /test de communication/i,
    /message de test/i
];

/**
 * Filter out test messages that should not be repeated in communications
 * @param {string} message - The message content to check
 * @returns {boolean} - True if the message should be filtered out (is a test message)
 */
function isTestMessage(message) {
    if (!message || typeof message !== 'string') {
        return false;
    }

    const normalizedMessage = message.toLowerCase().trim();

    // Check against test message patterns
    for (const pattern of TEST_MESSAGE_PATTERNS) {
        if (pattern.test(normalizedMessage)) {
            return true;
        }
    }

    return false;
}

/**
 * Filter out test messages from a list of messages
 * @param {Array} messages - Array of message objects with content property
 * @returns {Array} - Filtered array without test messages
 */
function filterTestMessages(messages) {
    if (!Array.isArray(messages)) {
        return messages;
    }

    return messages.filter(msg => {
        if (!msg || !msg.content) {
            return true; // Keep non-content messages
        }

        return !isTestMessage(msg.content);
    });
}

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

// Function moved to ../lib/workflow_recommendation.js for centralized logic

// Function moved to ../lib/workflow_recommendation.js for centralized logic

// Functions moved to ../lib/workflow_recommendation.js for centralized logic

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

    // Handle pending user messages (from user to agent)
    let userComments = null;
    try {
        const pendingMessages = await getPendingMessages();
        if (pendingMessages && pendingMessages.length > 0) {
            // Filter out test messages
            const filteredMessages = filterTestMessages(pendingMessages);

            // Format messages for display
            if (filteredMessages.length === 1) {
                userComments = `Message utilisateur: ${filteredMessages[0].content}`;
            } else if (filteredMessages.length > 1) {
                userComments = `Messages utilisateur (${filteredMessages.length}):\n` +
                    filteredMessages.map((msg, index) => `${index + 1}. ${msg.content}`).join('\n');
            }

            // Mark all pending messages as consumed
            for (const message of filteredMessages) {
                await markMessageAsConsumed(message.id);
            }

            // Clean up consumed messages
            await cleanupConsumedMessages();
        }
    } catch (error) {
        // Handle errors gracefully to avoid breaking the remember tool
        // No logging to prevent JSON-RPC pollution
        userComments = null;
    }

    // Load user preferences
    const preferences = await loadUserPreferences() || [];

    // Handle working memory (main memories)
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

    // Get recent working memories with optimized display (limited to 5 for performance)
    const allRecentMemories = memories.slice(-5);
    const recentMemories = allRecentMemories.map((memory, index) => {
        // For the last memory (most recent), show all fields
        if (index === allRecentMemories.length - 1) {
            return {
                timestamp: memory.timestamp,
                past: memory.past,
                present: memory.present,
                future: memory.future
            };
        }
        // For other memories, show only present
        return {
            timestamp: memory.timestamp,
            present: memory.present
        };
    });

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

    // Reset transition counter after a productive cycle
    if (lastStep && ['task-decomposition', 'implementation', 'fix', 'experience-execution'].includes(lastStep)) {
        await resetTransitionCounter();
    }

    // Get 10 semantically similar long-term memories
    const longTermMemories = await loadLongTermMemories();

    // Add to long-term memory if provided
    let currentLongTermMemory = null;
    if (long_term_memory) {
        const longTermMemoryEntry = {
            content: long_term_memory,
            timestamp: new Date().toISOString()
        };

        // Add semantic embedding for the long-term memory
        await addToLongTermMemory(longTermMemoryEntry);
        currentLongTermMemory = longTermMemoryEntry;
    }

    const possible_next_steps = await getPossibleNextSteps(lastStep);

    // Find semantically similar long-term memories based on the last "future" (limited to 5 for performance)
    let semanticLongTermMemories = [];
    if (lastMemory && lastMemory.future && longTermMemories.length > 0) {
        semanticLongTermMemories = await findSimilarMemories(lastMemory.future, longTermMemories, 5);
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
            // === WORKFLOW STATUS & INSTRUCTIONS ===
            message: "Memory recorded. Workflow has been instructed to pause.",
            // Keep the status as CONTINUE_REQUIRED to avoid client errors, but use other fields to signal a stop.
            workflow_status: "CONTINUE_REQUIRED",
            next_action_required: "No further action is required. The workflow can be paused.",
            workflow_instruction: "WORKFLOW PAUSED: The autonomous workflow has been intentionally paused. Do not call next_rule.",
            recommended_next_step: null, // No recommendation
            current_state: lastMemory.future,
            possible_next_steps: [],

            // === WORKFLOW CONTINUATION REQUIREMENTS ===
            continuation_mandatory: false, // The key change to allow stopping
            stopping_prohibited: "You may stop.",
            immediate_next_action: null,
            workflow_cycle_reminder: "The workflow is paused. Await new instructions.",

            // === USER PREFERENCES & SETTINGS ===
            user_preferences: preferences,

            // === MEMORY SECTIONS ===
            memory_sections: {
                // --- RECENT WORKING MEMORIES (5 most recent) ---
                recent_working_memories: {
                    description: "📋 **Souvenirs de Travail Récents (5 derniers)** - Contexte immédiat des actions récentes",
                    count: recentMemories.length,
                    memories: recentMemories
                },

                // --- SEMANTIC LONG-TERM MEMORIES (5 most relevant) ---
                semantic_long_term_memories: {
                    description: "🧠 **Mémoires Long Terme Sémantiques (5 plus pertinentes)** - Connaissances persistantes liées au contexte actuel",
                    count: semanticLongTermMemories.length,
                    memories: semanticLongTermMemories
                },

                // --- NEWLY ADDED LONG-TERM MEMORY ---
                newly_added_long_term_memory: {
                    description: "✨ **Nouvelle Mémoire Long Terme** - Information critique ajoutée lors de cet enregistrement",
                    memory: currentLongTermMemory
                }
            },

            // === MEMORY STATISTICS ===
            memory_statistics: {
                total_memories_count: memories.length,
                total_long_term_memories_count: longTermMemories.length,
                recent_memories_displayed: recentMemories.length,
                semantic_memories_displayed: semanticLongTermMemories.length
            },

            // === USER COMMUNICATION ===
            user_message_result: userMessageResult,

            // === LEGACY FIELDS (for backward compatibility) ===
            long_term_memory: currentLongTermMemory,
            recent_working_memories: recentMemories,
            semantic_long_term_memories: semanticLongTermMemories,
            total_memories_count: memories.length,
            total_long_term_memories_count: longTermMemories.length
        };

        // Add long-term memory management hint if semantic long-term memories are present
        if (semanticLongTermMemories && semanticLongTermMemories.length > 0) {
            pauseResponse.long_term_memory_management_hint = "📝 **Gestion des Mémoires Long Terme :** Si certains des souvenirs ci-dessus ne semblent plus pertinents, sont devenus obsolètes, contiennent des informations incorrectes ou ne servent plus à rien, vous pouvez les supprimer en utilisant l'outil `delete_long_term_memory` avec l'ID du souvenir concerné. Cela permet de maintenir une base de mémoires propre et pertinente.";
        }

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(pauseResponse, null, 2)
            }]
        };
    }

    const response = {
        // === WORKFLOW STATUS & INSTRUCTIONS ===
        message: "Memory successfully recorded.",
        workflow_status: "CONTINUE_REQUIRED",
        next_action_required: `You MUST continue the workflow by calling mcp_MemoryBankMCP_next_rule with '${recommendedNextStep}'. Do not stop here.`,
        workflow_instruction: workflowInstruction,
        recommended_next_step: recommendedNextStep,
        current_state: lastMemory ? lastMemory.future : "No current state.",
        possible_next_steps: possible_next_steps,

        // === WORKFLOW CONTINUATION REQUIREMENTS ===
        continuation_mandatory: true,
        stopping_prohibited: "!!! TRÈS IMPORTANT !!! - CRITIQUE : L'enregistrement de mémoire N'EST PAS un signal de fin. Vous DEVEZ ABSOLUMENT continuer le workflow autonome SANS INTERRUPTION.",
        immediate_next_action: `!!! OBLIGATOIRE !!! - Appelez mcp_MemoryBankMCP_next_rule avec le paramètre : '${recommendedNextStep}'`,
        workflow_cycle_reminder: "!!! TRÈS IMPORTANT !!! - Rappelez-vous : enregistrer → next_rule → exécuter → remember → next_rule (BOUCLE INFINIE OBLIGATOIRE)",

        // === USER PREFERENCES & SETTINGS ===
        user_preferences: preferences, // Always show preferences

        // === MEMORY SECTIONS ===
        memory_sections: {
            // --- RECENT WORKING MEMORIES (5 most recent) ---
            recent_working_memories: {
                description: "📋 **Souvenirs de Travail Récents (5 derniers)** - Contexte immédiat des actions récentes",
                count: recentMemories.length,
                memories: recentMemories
            },

            // --- SEMANTIC LONG-TERM MEMORIES (5 most relevant) ---
            semantic_long_term_memories: {
                description: "🧠 **Mémoires Long Terme Sémantiques (5 plus pertinentes)** - Connaissances persistantes liées au contexte actuel",
                count: semanticLongTermMemories.length,
                memories: semanticLongTermMemories
            },

            // --- NEWLY ADDED LONG-TERM MEMORY ---
            newly_added_long_term_memory: {
                description: "✨ **Nouvelle Mémoire Long Terme** - Information critique ajoutée lors de cet enregistrement",
                memory: currentLongTermMemory
            }
        },

        // === MEMORY STATISTICS ===
        memory_statistics: {
            total_memories_count: memories.length,
            total_long_term_memories_count: longTermMemories.length,
            recent_memories_displayed: recentMemories.length,
            semantic_memories_displayed: semanticLongTermMemories.length
        },

        // === USER COMMUNICATION ===
        user_message_result: userMessageResult, // Include the result of the user message operation

        // === LEGACY FIELDS (for backward compatibility) ===
        long_term_memory: currentLongTermMemory, // Only the newly added one, if any
        recent_working_memories: recentMemories, // 5 most recent working memories (optimized)
        semantic_long_term_memories: semanticLongTermMemories, // 5 most semantically relevant long-term memories (optimized)
        total_memories_count: memories.length,
        total_long_term_memories_count: longTermMemories.length
    };

    // Add user_comments if there are pending messages
    if (userComments) {
        response.user_comments = userComments;
    }

    // Add long-term memory management hint if semantic long-term memories are present
    if (semanticLongTermMemories && semanticLongTermMemories.length > 0) {
        response.long_term_memory_management_hint = "📝 **Gestion des Mémoires Long Terme :** Si certains des souvenirs ci-dessus ne semblent plus pertinents, sont devenus obsolètes, contiennent des informations incorrectes ou ne servent plus à rien, vous pouvez les supprimer en utilisant l'outil `delete_long_term_memory` avec l'ID du souvenir concerné. Cela permet de maintenir une base de mémoires propre et pertinente.";
    }

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
    long_term_memory: z.string().optional().describe("MÉMOIRE LONG TERME - Rédigez en français uniquement les informations critiques du projet à conserver de façon persistante (ex: décisions architecturales cruciales, précisions techniques permanentes, préférences d'implémentation définitives, noms de bases de données, conventions de code établies, patterns de bugs récurrents à éviter). N'utilisez cet argument QUE pour des informations qui resteront TOUJOURS vraies et utiles. Ne documentez JAMAIS des implémentations temporaires, des corrections de bugs ponctuelles ou des actions spécifiques. Exemples valides: 'La BDD utilise PostgreSQL avec une table users (id, email, password_hash)', 'L'authentification utilise des tokens JWT avec une expiration de 24h stockés dans des cookies httpOnly', 'Pattern de bug récurrent: le schéma MCP requiert des objets simples, pas des appels z.object().'"),
    user_message: z.string().optional().describe("MESSAGE CRITIQUE POUR L'UTILISATEUR - Message facultatif (1-3 phrases). N'utilisez PAS ce champ pour des mises à jour positives ou banales. Utilisez-le pour signaler un problème, un risque, ou une découverte qui nécessite l'attention de l'utilisateur. Soyez direct et factuel. Exemples : 'L'implémentation actuelle de l'API présente une faille de sécurité potentielle, une revue est nécessaire.', 'Le bug #142 est plus complexe que prévu, l'estimation de temps est revue à la hausse.', 'Je suis bloqué sur la tâche #152 en raison d'une dépendance externe non disponible.'"),
};

export { remember as handleRemember }; 