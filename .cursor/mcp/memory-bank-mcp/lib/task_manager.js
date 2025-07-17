import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { markReadmeTaskGenerated } from './workflow_state.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const tasksFilePath = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'tasks.json');

// Archive size limits
const MAX_ARCHIVED_TASKS = 50;

class TaskManager {
    constructor() {
        this.tasks = [];
        this.nextId = 1;
    }

    async loadTasks() {
        try {
            const content = await fs.readFile(tasksFilePath, 'utf8');
            this.tasks = JSON.parse(content);
            // Find the next available ID
            if (this.tasks.length > 0) {
                this.nextId = Math.max(...this.tasks.map(t => t.id)) + 1;
            }
        } catch (error) {
            if (error.code === 'ENOENT') {
                this.tasks = [];
                this.nextId = 1;
            } else {
                throw error;
            }
        }
    }

    async saveTasks() {
        try {
            await fs.mkdir(path.dirname(tasksFilePath), { recursive: true });
            await fs.writeFile(tasksFilePath, JSON.stringify(this.tasks, null, 2), 'utf8');
        } catch (error) {
            throw new Error(`Failed to save tasks: ${error.message}`);
        }
    }

    /**
     * Clean up archived tasks to maintain maximum limit
     * Keeps only the most recent archived tasks based on updated_date
     */
    cleanupArchivedTasks() {
        const archivedTasks = this.tasks.filter(task => task.status === 'DONE' || task.status === 'APPROVED');

        if (archivedTasks.length > MAX_ARCHIVED_TASKS) {
            // Sort archived tasks by updated_date (most recent first)
            archivedTasks.sort((a, b) => new Date(b.updated_date) - new Date(a.updated_date));

            // Keep only the most recent MAX_ARCHIVED_TASKS
            const tasksToKeep = archivedTasks.slice(0, MAX_ARCHIVED_TASKS);
            const tasksToRemove = archivedTasks.slice(MAX_ARCHIVED_TASKS);

            // Remove old archived tasks from the main tasks array
            tasksToRemove.forEach(taskToRemove => {
                const index = this.tasks.findIndex(task => task.id === taskToRemove.id);
                if (index !== -1) {
                    this.tasks.splice(index, 1);
                }
            });

            console.log(`[TaskManager] Cleaned up ${tasksToRemove.length} old archived tasks, keeping ${tasksToKeep.length} most recent`);
        }
    }

    createTask(taskData) {
        const newTask = {
            id: this.nextId++,
            title: taskData.title,
            short_description: taskData.short_description || taskData.description || '',
            detailed_description: taskData.detailed_description || taskData.description || '',
            description: taskData.description || taskData.short_description || '',
            status: taskData.status || 'TODO',
            dependencies: taskData.dependencies || [],
            impacted_files: taskData.impacted_files || [],
            validation_criteria: taskData.validation_criteria || '',
            parent_id: taskData.parent_id || null,
            priority: taskData.priority || 3,
            created_date: new Date().toISOString(),
            updated_date: new Date().toISOString()
        };

        this.tasks.push(newTask);
        this.saveTasks(); // Save asynchronously
        return newTask;
    }

    getTaskById(id) {
        return this.tasks.find(task => task.id === id);
    }

    updateTask(id, updates) {
        const taskIndex = this.tasks.findIndex(task => task.id === id);
        if (taskIndex === -1) {
            throw new Error(`Task with ID ${id} not found`);
        }

        const originalStatus = this.tasks[taskIndex].status;
        const updatedTask = {
            ...this.tasks[taskIndex],
            ...updates,
            updated_date: new Date().toISOString()
        };

        this.tasks[taskIndex] = updatedTask;

        // If task was just marked as DONE or APPROVED, cleanup archived tasks
        const finalStates = ['DONE', 'APPROVED'];
        if (!finalStates.includes(originalStatus) && finalStates.includes(updatedTask.status)) {
            this.cleanupArchivedTasks();
        }

        this.saveTasks(); // Save asynchronously
        return updatedTask;
    }

    getAllTasks(options = {}) {
        let filteredTasks = [...this.tasks];

        // Default to excluding DONE tasks unless explicitly requested
        if (!options.include_done) {
            filteredTasks = filteredTasks.filter(task => task.status !== 'DONE');
        }

        // Filter by parent_id if specified
        if (options.parent_id !== undefined) {
            filteredTasks = filteredTasks.filter(task => task.parent_id === options.parent_id);
        }

        // Sort by priority if requested
        if (options.sort_by === 'priority') {
            filteredTasks.sort((a, b) => (a.priority || 3) - (b.priority || 3));
        }

        // Apply limit if specified
        if (options.limit) {
            filteredTasks = filteredTasks.slice(0, options.limit);
        }

        return filteredTasks;
    }

    getNextTasks(options = {}) {
        // Get tasks that are TODO or IN_PROGRESS and have no unresolved dependencies
        let availableTasks = this.tasks.filter(task => {
            if (task.status === 'DONE' || task.status === 'BLOCKED') {
                return false;
            }

            // Check if all dependencies are completed
            if (task.dependencies && task.dependencies.length > 0) {
                return task.dependencies.every(depId => {
                    const depTask = this.getTaskById(depId);
                    return depTask && depTask.status === 'DONE';
                });
            }

            return true;
        });

        // Sort by priority
        availableTasks.sort((a, b) => (a.priority || 3) - (b.priority || 3));

        // Apply limit if specified
        if (options.limit) {
            availableTasks = availableTasks.slice(0, options.limit);
        }

        return availableTasks;
    }

    /**
     * Generate automatic README update task
     * @param {number} implementationCount - Current implementation count
     * @returns {Object} Created README task
     */
    async generateReadmeTask(implementationCount) {
        const timestamp = new Date().toISOString();
        const readmeTaskData = {
            title: `Mettre à jour le README.md - Cycle d'implémentation #${implementationCount}`,
            short_description: `Mise à jour automatique du README.md après ${implementationCount} étapes d'implémentation pour maintenir la documentation à jour avec les derniers développements du projet.`,
            detailed_description: `## Contexte

Cette tâche est générée automatiquement toutes les 10 étapes d'implémentation pour maintenir la documentation du projet à jour.

**Cycle d'implémentation :** #${implementationCount}
**Date de génération :** ${timestamp}

## Objectif

Mettre à jour le README.md pour refléter les derniers développements, fonctionnalités implémentées, et changements architecturaux depuis la dernière mise à jour de documentation.

## Actions requises

**1. Analyse des changements récents :**
- Examiner les 10 dernières tâches implémentées
- Identifier les nouvelles fonctionnalités ajoutées
- Noter les changements architecturaux significatifs
- Détecter les modifications des dépendances ou de configuration

**2. Mise à jour du README.md :**
- Mettre à jour la section "Features" avec les nouvelles fonctionnalités
- Réviser les instructions d'installation si nécessaire
- Actualiser les exemples d'utilisation
- Corriger toute information obsolète
- Ajouter des notes sur les breaking changes si applicable

**3. Validation :**
- Vérifier que toutes les instructions sont encore valides
- Tester les exemples de code mentionnés
- S'assurer que la documentation est cohérente avec l'état actuel du projet

## Analyse Technique & Points de Vigilance

**Attention : Cohérence documentaire**
- Vérifier que la documentation reflète fidèlement l'état actuel du code
- Éviter les descriptions trop techniques qui deviendraient rapidement obsolètes
- Maintenir un équilibre entre détail et lisibilité

**Attention : Exemples fonctionnels**
- Tous les exemples de code doivent être testés et fonctionnels
- Les chemins de fichiers et noms de variables doivent être à jour
- Les versions des dépendances mentionnées doivent être correctes

**Attention : Structure et navigation**
- Maintenir une structure logique et une navigation claire
- Utiliser des liens internes pour faciliter la navigation
- Organiser l'information par ordre de priorité pour les nouveaux utilisateurs

## Critères de validation

- Le README.md reflète fidèlement l'état actuel du projet
- Toutes les nouvelles fonctionnalités importantes sont documentées
- Les instructions d'installation et d'utilisation sont à jour et testées
- La documentation est claire et accessible aux nouveaux contributeurs
- Aucune information obsolète ne subsiste`,
            status: 'TODO',
            priority: 4, // High priority for documentation maintenance
            dependencies: [],
            impacted_files: ['README.md'],
            validation_criteria: `La tâche est terminée quand : (1) Le README.md a été mis à jour avec les derniers développements, (2) Toutes les nouvelles fonctionnalités sont documentées, (3) Les instructions d'installation et d'utilisation sont validées, (4) La documentation est cohérente avec l'état actuel du projet, (5) Aucune information obsolète ne subsiste dans le document.`
        };

        // Create the task
        const createdTask = this.createTask(readmeTaskData);

        // Mark that we generated a README task at this count
        await markReadmeTaskGenerated();

        console.log(`[TaskManager] Generated automatic README update task #${createdTask.id} for implementation cycle #${implementationCount}`);

        return createdTask;
    }
}

// Create a singleton instance
const taskManager = new TaskManager();

// Initialize tasks on module load
taskManager.loadTasks().catch(error => {
    console.error('Failed to load tasks:', error);
});

export { taskManager };

// Legacy export for compatibility
export async function readTasks() {
    await taskManager.loadTasks();
    return taskManager.getAllTasks();
}
