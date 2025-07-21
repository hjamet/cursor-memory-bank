import { z } from 'zod';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

import { handleRemember, rememberSchema } from './mcp_tools/remember.js';
import handleNextRule, { nextRuleSchema } from './mcp_tools/next_rule.js';
import { handleCommit } from './mcp_tools/commit.js';
import { handleCreateTask } from './mcp_tools/create_task.js';
import { handleUpdateTask } from './mcp_tools/update_task.js';
import { handleGetAllTasks } from './mcp_tools/get_all_tasks.js';
import { handleGetNextTasks } from './mcp_tools/get_next_tasks.js';
import { handleReadUserbrief } from './mcp_tools/read_userbrief.js';
import { handleUpdateUserbrief } from './mcp_tools/update_userbrief.js';
import { handleDeleteLongTermMemory, deleteLongTermMemorySchema } from './mcp_tools/delete_long_term_memory.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import process from 'process';

// Create a new MCP server instance
const server = new McpServer({
    name: 'MemoryBankMCP',
    version: '1.2.0'
});

// Helper function to wrap handlers with error catching
function safeHandler(handler) {
    return async (args, a, b) => {
        try {
            return await handler(args, a, b);
        } catch (error) {
            // Re-throwing the error should be handled by the MCP SDK to create a proper JSON-RPC error response.
            throw new Error(error.message);
        }
    };
}

// Register the tools with the server

server.tool('remember', rememberSchema, safeHandler(handleRemember));

server.tool('next_rule', nextRuleSchema, safeHandler(handleNextRule));

server.tool('commit', {
    emoji: z.string().describe("EMOJI DE COMMIT : Emoji unique qui représente le type de changement effectué. Utilisez les emojis conventionnels : ✨ pour nouvelles fonctionnalités, 🐛 pour corrections de bugs, 📝 pour documentation, ♻️ pour refactoring, ✅ pour tests, 🔧 pour configuration, 🚀 pour améliorations de performance, 🔒 pour corrections de sécurité, 💄 pour UI/styling, 🗃️ pour changements de base de données, 🔥 pour suppression de code/fichiers."),
    type: z.string().describe("TYPE DE COMMIT : Type de commit conventionnel qui catégorise le changement. Utilisez les types standards : 'feat' (nouvelle fonctionnalité), 'fix' (correction de bug), 'docs' (documentation), 'style' (formatage, pas de changement de code), 'refactor' (restructuration de code), 'test' (ajout de tests), 'chore' (maintenance), 'perf' (performance), 'ci' (intégration continue), 'build' (système de build), 'revert' (annulation de changements)."),
    title: z.string().describe("TITRE DE COMMIT - Rédigez en français un résumé concis à l'impératif du changement (50 caractères ou moins). Commencez par un verbe au présent. Exemples : 'Ajouter le système d'authentification utilisateur', 'Corriger le timeout de connexion base de données', 'Mettre à jour la documentation API', 'Refactoriser la logique de traitement des paiements'. Ne terminez pas par un point."),
    description: z.string().describe("DESCRIPTION DE COMMIT - Rédigez en français une explication détaillée de ce qui a été changé, pourquoi cela a été changé, et tous les détails d'implémentation importants. Incluez : (1) Quels changements spécifiques ont été faits, (2) Pourquoi ces changements étaient nécessaires, (3) Tout changement cassant ou notes de migration, (4) Numéros d'issues liés si applicable. Utilisez des puces pour plusieurs changements. Exemple : 'Implémentation du système d'authentification basé sur JWT :\\n\\n- Ajout des endpoints de connexion/déconnexion avec hachage des mots de passe\\n- Création du middleware pour les routes protégées\\n- Mise à jour du modèle utilisateur avec les champs d'authentification\\n- Ajout de la gestion de session avec expiration de token 24h\\n\\nCeci résout les exigences de sécurité et permet les fonctionnalités spécifiques à l'utilisateur.'")
}, safeHandler(handleCommit));

server.tool('create_task', {
    title: z.string().min(1).max(200).describe("TITRE DE TÂCHE - Rédigez en français un titre clair et actionnable qui décrit ce qui doit être accompli (1-200 caractères). Utilisez l'impératif et soyez précis. Exemples : 'Implémenter le système d'authentification utilisateur', 'Corriger les problèmes de timeout de base de données', 'Créer la documentation API pour les endpoints de paiement', 'Refactoriser les composants de l'interface utilisateur'. Évitez les titres vagues comme 'Corriger un bug' ou 'Mettre à jour le code'."),
    short_description: z.string().min(1).max(500).describe("RÉSUMÉ BREF - Rédigez en français un aperçu concis de la tâche qui fournit le contexte et la portée (1-500 caractères). Doit répondre brièvement au 'quoi' et 'pourquoi'. Exemple : 'Créer un système de connexion sécurisé avec des tokens JWT pour remplacer l'authentification actuelle basée sur les sessions. Cela améliorera la sécurité et permettra l'intégration d'applications mobiles.' Incluez l'objectif principal et le bénéfice clé."),
    detailed_description: z.string().min(1).describe("SPÉCIFICATIONS DÉTAILLÉES - Rédigez en français une description complète de ce qui doit être fait, incluant les exigences spécifiques, critères d'acceptation, détails techniques et approche d'implémentation. Structurez en étapes claires ou puces. Incluez : (1) Fonctionnalité spécifique à implémenter, (2) Exigences et contraintes techniques, (3) Entrées et sorties attendues, (4) Points d'intégration avec les systèmes existants, (5) Exigences de performance ou qualité. Exemple : 'Implémenter l'authentification basée sur JWT :\\n\\n**Exigences :**\\n- Connexion utilisateur avec email/mot de passe\\n- Génération de token JWT avec expiration 24h\\n- Middleware de protection des routes\\n- Hachage des mots de passe avec bcrypt\\n\\n**Critères d'acceptation :**\\n- Les utilisateurs peuvent se connecter et recevoir un JWT valide\\n- Les routes protégées rejettent les tokens invalides\\n- Les mots de passe sont hachés de façon sécurisée\\n- Le mécanisme de rafraîchissement de token fonctionne\\n\\n**Notes techniques :**\\n- Utiliser la bibliothèque jsonwebtoken\\n- Stocker les tokens dans des cookies httpOnly\\n- Implémenter la limitation de taux sur les tentatives de connexion'"),
    dependencies: z.array(z.number().int().positive()).optional().default([]).describe("TASK DEPENDENCIES: Array of task IDs that must be completed before this task can start. Only include direct dependencies that block this task's execution. Example: [12, 15] means tasks 12 and 15 must be completed first. Use empty array [] if no dependencies exist."),
    status: z.enum(['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW']).optional().default('TODO').describe("CURRENT STATUS: Task's current state in the workflow. 'TODO' = not started, 'IN_PROGRESS' = currently being worked on, 'DONE' = completed, 'BLOCKED' = waiting for external dependency, 'REVIEW' = completed but needs review/testing. Default is 'TODO' for new tasks."),
    impacted_files: z.array(z.string()).optional().default([]).describe("AFFECTED FILES: List of files that will be created, modified, or deleted during this task. Use relative paths from project root. Examples: ['src/auth/login.js', 'tests/auth.test.js', 'docs/api/auth.md']. This helps with conflict detection and code review planning."),
    validation_criteria: z.string().optional().default('').describe("CRITÈRES DE VALIDATION - Rédigez en français des critères spécifiques et mesurables qui définissent quand cette tâche est considérée comme terminée. Doivent être testables et objectifs. Incluez des tests fonctionnels, benchmarks de performance ou critères de qualité. Exemple : 'La tâche est terminée quand : (1) Tous les tests unitaires passent avec >90% de couverture, (2) Le flux connexion/déconnexion fonctionne dans le navigateur, (3) Les tokens JWT expirent correctement après 24h, (4) Les endpoints API retournent les codes d'erreur appropriés, (5) La documentation est mise à jour avec les nouveaux endpoints.'"),
    parent_id: z.number().int().positive().optional().describe("PARENT TASK ID: ID of the parent task if this is a subtask or component of a larger task. Use this to create hierarchical task structures. Example: If task 10 is 'Implement user management system' and this task is 'Create user login', then parent_id would be 10. Leave empty for top-level tasks."),
    priority: z.number().int().min(1).max(5).optional().default(3).describe("TASK PRIORITY: Urgency and importance level (1=lowest, 5=highest). Use 5 for critical/blocking issues, 4 for high-priority features, 3 for normal work (default), 2 for nice-to-have improvements, 1 for low-priority tasks. Consider business impact, user impact, and technical dependencies when setting priority."),
    image: z.string().optional().describe("IMAGE FACULTATIVE : Chemin relatif vers une image associée à cette tâche (optionnel). Utilisez le chemin relatif depuis la racine du projet vers un fichier image qui illustre, documente ou est nécessaire pour cette tâche. Exemple : '.cursor/temp/images/mockup_login.png' ou 'docs/assets/database_schema.jpg'. L'image sera accessible via l'outil mcp_ToolsMCP_consult_image pour analyse et référence durant l'implémentation.")
}, safeHandler(handleCreateTask));

server.tool('update_task', {
    task_id: z.number().int().positive().describe("IDENTIFIANT DE TÂCHE : Le numéro d'ID unique de la tâche à mettre à jour. Cet ID est assigné lors de la création de la tâche et peut être trouvé dans les listes de tâches. Champ requis - vous devez spécifier quelle tâche modifier."),
    comment: z.string().describe("COMMENTAIRE CRITIQUE OBLIGATOIRE - Rédigez une analyse critique et détaillée. Ne vous contentez pas de décrire le changement de statut. Instructions par statut : (1) BLOCKED : Analysez la cause racine du blocage. Quels sont les obstacles précis ? Quelles sont les dépendances externes ou les problèmes techniques qui empêchent la progression ? Proposez un plan d'action pour débloquer la situation. (2) REVIEW : Ne dites pas seulement ce que vous avez fait. Mettez en évidence les problèmes que vous avez rencontrés, même si vous les avez résolus. Mentionnez les faiblesses potentielles de votre implémentation et les points à surveiller. Quels tests manuels ont été effectués et quels sont leurs limites ? Guidez l'utilisateur sur les points de friction à vérifier. Si il s'agissait d'un bug, expliquez son origine et comment vous l'avez résolu. (3) Pour tout autre changement : Soyez transparent sur l'impact, les risques et les problèmes potentiels. Un commentaire vide n'est accepté que pour le passage à IN_PROGRESS."),
    title: z.string().min(1).max(200).optional().describe("NOUVEAU TITRE DE TÂCHE - Rédigez en français un titre clair et actionnable mis à jour (1-200 caractères). Utilisez l'impératif et soyez précis. Ne fournissez que si vous voulez changer le titre existant. Exemples : 'Implémenter le système d'authentification utilisateur', 'Corriger les problèmes de timeout de base de données'."),
    short_description: z.string().min(1).max(500).optional().describe("NOUVEAU RÉSUMÉ BREF - Rédigez en français un aperçu concis mis à jour (1-500 caractères). Ne fournissez que si vous voulez changer la description existante. Doit répondre brièvement au 'quoi' et 'pourquoi' et inclure l'objectif principal et le bénéfice clé."),
    detailed_description: z.string().min(1).optional().describe("NOUVELLES SPÉCIFICATIONS DÉTAILLÉES - Rédigez en français une description complète mise à jour avec exigences, critères d'acceptation, détails techniques et approche d'implémentation. Ne fournissez que si vous voulez remplacer complètement la description détaillée existante."),
    dependencies: z.array(z.number().int().positive()).optional().describe("NEW TASK DEPENDENCIES: Updated array of task IDs that must be completed before this task. This completely replaces the existing dependencies list. Use empty array [] to remove all dependencies. Example: [12, 15] means tasks 12 and 15 must be completed first."),
    status: z.enum(['IN_PROGRESS', 'BLOCKED', 'REVIEW']).optional().describe("NEW STATUS: Updated task state. 'IN_PROGRESS' = currently being worked on, 'BLOCKED' = waiting for external dependency, 'REVIEW' = completed but needs review/testing. Only provide if status is changing."),
    impacted_files: z.array(z.string()).optional().describe("NEW AFFECTED FILES: Updated list of files that will be created, modified, or deleted. This completely replaces the existing files list. Use relative paths from project root. Examples: ['src/auth/login.js', 'tests/auth.test.js']."),
    validation_criteria: z.string().optional().describe("NOUVEAUX CRITÈRES DE VALIDATION - Rédigez en français des critères spécifiques et mesurables mis à jour qui définissent quand cette tâche est terminée. Doivent être testables et objectifs. Ne fournissez que si vous voulez changer les critères existants."),
    parent_id: z.number().int().positive().nullable().optional().describe("NEW PARENT TASK ID: Updated parent task ID for hierarchical structure, or null to remove parent relationship. Only provide if you want to change the parent-child relationship."),
    priority: z.number().int().min(1).max(5).optional().describe("NEW TASK PRIORITY: Updated urgency level (1=lowest, 5=highest). Use 5 for critical/blocking issues, 4 for high-priority features, 3 for normal work, 2 for nice-to-have improvements, 1 for low-priority tasks. Only provide if priority is changing."),
    image: z.string().optional().describe("NOUVELLE IMAGE FACULTATIVE : Chemin relatif mis à jour vers une image associée à cette tâche (optionnel). Utilisez le chemin relatif depuis la racine du projet vers un fichier image qui illustre, documente ou est nécessaire pour cette tâche. Ne fournissez que si vous voulez changer l'image existante ou en ajouter une nouvelle. Exemple : '.cursor/temp/images/mockup_updated.png'. L'image sera accessible via l'outil mcp_ToolsMCP_consult_image pour analyse et référence durant l'implémentation.")
}, safeHandler(handleUpdateTask));

server.tool('get_all_tasks', {}, safeHandler(handleGetAllTasks));

server.tool('get_next_tasks', {}, safeHandler(handleGetNextTasks));

server.tool('read_userbrief', {
    archived_count: z.number().optional().describe("ARCHIVED COUNT: Number of archived entries to include in the response (optional, default: 3). Use this to control how many completed/archived requests are returned along with the current active request.")
}, safeHandler(handleReadUserbrief));

server.tool('update_userbrief', {
    action: z.enum(['mark_archived', 'add_comment', 'mark_pinned']).describe("ACTION USERBRIEF : L'opération à effectuer sur une entrée de requête utilisateur. 'mark_archived' = déplacer la requête vers le statut terminé/archivé (utiliser quand le travail est fini), 'add_comment' = ajouter une mise à jour de progression ou note à l'historique de la requête (utiliser pour mises à jour de statut, découvertes, ou communication), 'mark_pinned' = marquer la requête comme importante/prioritaire (utiliser pour éléments haute priorité qui doivent rester visibles)."),
    id: z.number().optional().describe("ID DE REQUÊTE : L'identifiant unique de la requête utilisateur spécifique à mettre à jour. Si omis, l'action ciblera la requête actuellement active (in_progress ou new). Utilisez ceci quand vous devez mettre à jour une requête historique spécifique plutôt que la courante."),
    comment: z.string().optional().describe("COMMENTAIRE DE MISE À JOUR - Rédigez en français le texte à ajouter à l'historique de la requête lors de l'utilisation de l'action 'add_comment'. Doit fournir des mises à jour significatives sur les progrès, découvertes, décisions prises, ou prochaines étapes. Exemples : 'Système d'authentification implémenté avec succès, passage à la phase de test', 'Problème de schéma de base de données découvert, investigation d'alternatives en cours', 'Fonctionnalité terminée et déployée en environnement de staging'. Requis quand action est 'add_comment', ignoré pour les autres actions.")
}, safeHandler(handleUpdateUserbrief));

server.tool('delete_long_term_memory', deleteLongTermMemorySchema, safeHandler(handleDeleteLongTermMemory));


// Start the server
async function startServer() {
    try {
        // Initialize server transport
        const transport = new StdioServerTransport();

        // Connect server to transport
        await server.connect(transport);

    } catch (error) {
        // console.error('[MemoryBankMCP] Failed to start server:', error); // Commented to prevent JSON-RPC pollution
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    process.exit(0);
});

process.on('SIGTERM', () => {
    process.exit(0);
});

// Start the server
startServer().catch(error => {
    // console.error('[MemoryBankMCP] Server startup error:', error); // Commented to prevent JSON-RPC pollution
    process.exit(1);
}); 