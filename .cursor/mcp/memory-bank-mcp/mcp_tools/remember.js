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

async function getPossibleNextSteps() {
    try {
        const userbrief = await readUserbrief();
        if (userbrief && userbrief.requests && userbrief.requests.some(r => r.status === 'new' || r.status === 'in_progress')) {
            return ['task-decomposition'];
        }

        const tasks = await readTasks();
        if (tasks && tasks.some(t => t.status === 'TODO' || t.status === 'IN_PROGRESS')) {
            return ['implementation'];
        }

        // Default when no work is pending
        return ['context-update', 'system'];

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
        return [];
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
    const possible_next_steps = await getPossibleNextSteps();

    // Find semantically similar long-term memories based on the last "future" 
    let semanticLongTermMemories = [];
    if (lastMemory && lastMemory.future && longTermMemories.length > 0) {
        semanticLongTermMemories = await findSimilarMemories(lastMemory.future, longTermMemories, 3);
    }

    // Determine the most appropriate next step based on current state
    let recommendedNextStep = possible_next_steps[0];
    let workflowInstruction = "";

    if (possible_next_steps.includes('task-decomposition')) {
        recommendedNextStep = 'task-decomposition';

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
            // Debug logging removed to prevent JSON-RPC pollution
            // console.warn(`[Remember] Could not read userbrief for example request: ${error.message}`);
            return null;
        }

        workflowInstruction = `CONTINUE WORKFLOW: New user requests detected. You must now call mcp_MemoryBankMCP_next_rule with 'task-decomposition' to process pending requests. STOPPING IS PROHIBITED.${exampleRequestInfo}`;
    } else if (possible_next_steps.includes('implementation')) {
        recommendedNextStep = 'implementation';
        workflowInstruction = "CONTINUE WORKFLOW: Tasks are available for implementation. You must now call mcp_MemoryBankMCP_next_rule with 'implementation' to continue working on tasks. STOPPING IS PROHIBITED.";
    } else if (possible_next_steps.includes('context-update')) {
        recommendedNextStep = 'context-update';
        workflowInstruction = "CONTINUE WORKFLOW: Context refresh needed. You must now call mcp_MemoryBankMCP_next_rule with 'context-update' to refresh project context. STOPPING IS PROHIBITED.";
    } else {
        workflowInstruction = "CONTINUE WORKFLOW: You must now call mcp_MemoryBankMCP_next_rule to continue the autonomous workflow. STOPPING IS ABSOLUTELY PROHIBITED. Memory recording is a continuation point, not an end point.";
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
        user_message_result: userMessageResult, // Include user message result if provided

        // Enhanced workflow continuation directives
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
    long_term_memory: z.string().optional().describe("MÉMOIRE LONG TERME - Rédigez en français uniquement les informations critiques du projet à conserver de façon persistante (ex: schémas de base de données, décisions architecturales, conventions de code, bugs récurrents à éviter). N'utilisez cet argument QUE pour des informations qui resteront toujours vraies et utiles. Exemple : 'Architecture MCP : Les outils MCP doivent utiliser le format 3-paramètres server.tool(name, schema, handler) avec objets Zod inline pour éviter les erreurs de sérialisation.'"),
    user_message: z.string().optional().describe("MESSAGE UTILISATEUR - Rédigez en français un message facultatif pour communiquer avec l'utilisateur (1-2 phrases max). Utilisez UNIQUEMENT pour des informations importantes : réponses aux questions, problèmes critiques identifiés, décisions importantes prises qui diffèrent des demandes. Exemple : 'La tâche a été complétée avec succès, prête pour votre validation.' ou 'J'ai dû modifier l'approche en raison d'un conflit de dépendances, voir les détails dans les commentaires de la tâche.'"),
};

export { remember as handleRemember }; 