import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

// Use the absolute path that we know works
const TASKS_FILE_PATH = 'C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\memory-bank\\streamlit_app\\tasks.json';

async function readTasks() {
    try {
        const data = await fs.readFile(TASKS_FILE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            return [];
        }
        throw error;
    }
}

/**
 * Performs comprehensive dependency graph analysis
 * @param {Array} tasks - All tasks
 * @param {Map} taskMap - Task lookup map
 * @returns {Object} Analysis results with available tasks and dependency insights
 */
function analyzeDependencyGraph(tasks, taskMap) {
    const analysis = {
        availableTasks: [],
        blockedTasks: [],
        circularDependencies: [],
        dependencyChains: new Map(),
        readinessScores: new Map()
    };

    // First pass: identify tasks with satisfied dependencies
    tasks.forEach(task => {
        if (task.status === 'DONE' || task.status === 'APPROVED' || task.status === 'REVIEW') return;

        const dependencyStatus = analyzeDependencies(task, taskMap);

        if (dependencyStatus.isAvailable) {
            analysis.availableTasks.push({
                ...task,
                dependencyStatus,
                readinessScore: calculateReadinessScore(task, taskMap)
            });
        } else {
            analysis.blockedTasks.push({
                ...task,
                dependencyStatus,
                blockingReason: dependencyStatus.blockingReason
            });
        }

        analysis.dependencyChains.set(task.id, dependencyStatus.chain);
        analysis.readinessScores.set(task.id, calculateReadinessScore(task, taskMap));
    });

    // Detect circular dependencies
    analysis.circularDependencies = detectCircularDependencies(tasks, taskMap);

    return analysis;
}

/**
 * Analyzes dependencies for a single task
 * @param {Object} task - Task to analyze
 * @param {Map} taskMap - Task lookup map
 * @returns {Object} Dependency analysis result
 */
function analyzeDependencies(task, taskMap) {
    const result = {
        isAvailable: true,
        completedDependencies: [],
        pendingDependencies: [],
        missingDependencies: [],
        blockingReason: null,
        chain: []
    };

    if (!task.dependencies || task.dependencies.length === 0) {
        result.chain = [`Task ${task.id} has no dependencies`];
        return result;
    }

    task.dependencies.forEach(depId => {
        const depTask = taskMap.get(depId);

        if (!depTask) {
            result.missingDependencies.push(depId);
            result.isAvailable = false;
            result.blockingReason = `Missing dependency: Task ${depId}`;
        } else if (depTask.status === 'DONE' || depTask.status === 'APPROVED' || depTask.status === 'REVIEW') {
            result.completedDependencies.push({
                id: depTask.id,
                title: depTask.title,
                status: depTask.status
            });
        } else {
            result.pendingDependencies.push({
                id: depTask.id,
                title: depTask.title,
                status: depTask.status
            });
            result.isAvailable = false;
            result.blockingReason = `Waiting for Task ${depTask.id}: ${depTask.title} (${depTask.status})`;
        }
    });

    // Build dependency chain description
    result.chain = [
        `Task ${task.id} depends on ${task.dependencies.length} task(s)`,
        `✅ Completed: ${result.completedDependencies.length}`,
        `⏳ Pending: ${result.pendingDependencies.length}`,
        `❌ Missing: ${result.missingDependencies.length}`
    ];

    return result;
}

/**
 * Calculates a readiness score for intelligent task prioritization
 * @param {Object} task - Task to score
 * @param {Map} taskMap - Task lookup map
 * @returns {number} Readiness score (higher = more ready)
 */
function calculateReadinessScore(task, taskMap) {
    let score = 0;

    // Base priority score (priority 5 = 50 points, priority 1 = 10 points)
    score += (task.priority || 3) * 10;

    // Status bonus
    const statusBonus = {
        'IN_PROGRESS': 15, // Currently being worked on
        'TODO': 10,        // Ready to start
        'REVIEW': 5,       // Needs review
        'BLOCKED': 0       // Blocked
    };
    score += statusBonus[task.status] || 0;

    // Dependency readiness bonus
    if (!task.dependencies || task.dependencies.length === 0) {
        score += 20; // No dependencies = immediate availability
    } else {
        const completedDeps = task.dependencies.filter(depId => {
            const depTask = taskMap.get(depId);
            return depTask && (depTask.status === 'DONE' || depTask.status === 'APPROVED' || depTask.status === 'REVIEW');
        });
        score += (completedDeps.length / task.dependencies.length) * 15;
    }

    // Age factor (older tasks get slight priority boost)
    if (task.created_date) {
        const ageInDays = (Date.now() - new Date(task.created_date).getTime()) / (1000 * 60 * 60 * 24);
        score += Math.min(ageInDays * 0.5, 5); // Max 5 points for age
    }

    // Parent task consideration
    if (task.parent_id) {
        const parentTask = taskMap.get(task.parent_id);
        if (parentTask && parentTask.status === 'IN_PROGRESS') {
            score += 10; // Boost subtasks of active parent tasks
        }
    }

    return Math.round(score * 100) / 100; // Round to 2 decimal places
}

/**
 * Detects circular dependencies in the task graph
 * @param {Array} tasks - All tasks
 * @param {Map} taskMap - Task lookup map
 * @returns {Array} List of circular dependency chains
 */
function detectCircularDependencies(tasks, taskMap) {
    const visited = new Set();
    const recursionStack = new Set();
    const cycles = [];

    function dfs(taskId, path = []) {
        if (recursionStack.has(taskId)) {
            // Found a cycle
            const cycleStart = path.indexOf(taskId);
            cycles.push(path.slice(cycleStart).concat([taskId]));
            return;
        }

        if (visited.has(taskId)) return;

        visited.add(taskId);
        recursionStack.add(taskId);
        path.push(taskId);

        const task = taskMap.get(taskId);
        if (task && task.dependencies) {
            task.dependencies.forEach(depId => {
                dfs(depId, [...path]);
            });
        }

        recursionStack.delete(taskId);
    }

    tasks.forEach(task => {
        if (!visited.has(task.id)) {
            dfs(task.id);
        }
    });

    return cycles;
}

/**
 * Applies intelligent task selection with tie-breaking
 * @param {Array} availableTasks - Tasks ready for execution
 * @returns {Object} Selection result with rationale
 */
function selectOptimalTasks(availableTasks) {
    if (availableTasks.length === 0) {
        return {
            selectedTasks: [],
            selectionStrategy: "No tasks available",
            rationale: "All tasks are either completed, blocked by dependencies, or have unresolved issues"
        };
    }

    // Sort by readiness score (highest first), then by priority, then by creation date
    availableTasks.sort((a, b) => {
        // Primary: Readiness score
        const scoreDiff = b.readinessScore - a.readinessScore;
        if (Math.abs(scoreDiff) > 0.1) return scoreDiff;

        // Secondary: Priority
        const priorityDiff = (b.priority || 3) - (a.priority || 3);
        if (priorityDiff !== 0) return priorityDiff;

        // Tertiary: Status importance
        const statusPriority = { 'IN_PROGRESS': 1, 'TODO': 2, 'REVIEW': 3, 'BLOCKED': 4 };
        const statusDiff = (statusPriority[a.status] || 99) - (statusPriority[b.status] || 99);
        if (statusDiff !== 0) return statusDiff;

        // Quaternary: Age (older first)
        const aDate = new Date(a.created_date || 0);
        const bDate = new Date(b.created_date || 0);
        return aDate - bDate;
    });

    const topTask = availableTasks[0];
    const topReadinessScore = topTask.readinessScore;
    const topPriority = topTask.priority || 3;

    // Find all tasks with equivalent readiness scores and priorities
    const equivalentTasks = availableTasks.filter(task =>
        Math.abs(task.readinessScore - topReadinessScore) < 0.1 &&
        (task.priority || 3) === topPriority
    );

    let selectionStrategy;
    let rationale;

    if (equivalentTasks.length === 1) {
        selectionStrategy = "Single highest priority task";
        rationale = [
            `Selected Task ${topTask.id} as the single most urgent task`,
            `Readiness Score: ${topReadinessScore} (Priority: ${topPriority}, Status: ${topTask.status})`,
            `Dependencies: ${topTask.dependencyStatus.completedDependencies.length} completed, ${topTask.dependencyStatus.pendingDependencies.length} pending`,
            `Selection based on: dependency readiness + priority weighting + status importance + age factor`
        ].join('\n');
    } else {
        selectionStrategy = "Multiple equivalent priority tasks";
        rationale = [
            `Found ${equivalentTasks.length} tasks with equivalent urgency (Readiness Score: ${topReadinessScore}, Priority: ${topPriority})`,
            `All tasks have satisfied dependencies and equal priority weighting`,
            `Agent can choose any of these tasks or work on multiple in parallel`,
            `Tasks are sorted by status importance and creation date for consistent ordering`
        ].join('\n');
    }

    return {
        selectedTasks: equivalentTasks,
        selectionStrategy,
        rationale
    };
}

/**
 * Handles the get_next_tasks tool call
 * Returns the most urgent available tasks automatically determined by advanced dependency graph analysis
 * 
 * @param {Object} params - Tool parameters (no parameters needed)
 * @returns {Object} Tool response with intelligently selected highest priority available tasks
 */
export async function handleGetNextTasks(params) {
    try {
        const allTasks = await readTasks();

        // Filter out tasks that are done, approved, or in review
        const activeTasks = allTasks.filter(task => task.status !== 'DONE' && task.status !== 'APPROVED' && task.status !== 'REVIEW');

        if (activeTasks.length === 0) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'success',
                        message: 'No active tasks available to be worked on.',
                        available_tasks: [],
                        statistics: { total_tasks: allTasks.length, active_tasks_count: 0 }
                    }, null, 2)
                }]
            };
        }

        // Create task lookup map for efficient dependency resolution
        const taskMap = new Map(activeTasks.map(task => [task.id, task]));

        // Perform comprehensive dependency graph analysis
        const dependencyAnalysis = analyzeDependencyGraph(activeTasks, taskMap);

        // Apply intelligent task selection with tie-breaking
        const selectionResult = selectOptimalTasks(dependencyAnalysis.availableTasks);

        // Final check for selected tasks
        if (selectionResult.selectedTasks.length === 0 && dependencyAnalysis.availableTasks.length > 0) {
            // Fallback to the highest priority task if selection logic fails
            selectionResult.selectedTasks = [dependencyAnalysis.availableTasks[0]];
            selectionResult.rationale += " | Fallback to highest priority available task.";
        }

        // Enhance tasks with image data if available
        const enhancedTasks = await Promise.all(selectionResult.selectedTasks.map(async (task) => {
            if (task.image) {
                const imagePath = path.join('C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\temp\\images', task.image);
                try {
                    const imageBuffer = await fs.readFile(imagePath);
                    task.image_data = {
                        type: 'image',
                        data: imageBuffer.toString('base64'),
                        mimeType: 'image/jpeg' // Assuming jpeg for now
                    };
                } catch (error) {
                    // Image not found or could not be read, do not add image_data
                }
            }
            return task;
        }));

        // Generate comprehensive statistics
        const statistics = {
            total_tasks: allTasks.length,
            available_tasks_count: dependencyAnalysis.availableTasks.length,
            blocked_tasks_count: dependencyAnalysis.blockedTasks.length,
            tasks_returned: enhancedTasks.length,
            highest_priority_level: enhancedTasks.length > 0 ? enhancedTasks[0].priority : null,
            highest_readiness_score: enhancedTasks.length > 0 ? enhancedTasks[0].readinessScore : null,
            status_breakdown: allTasks.reduce((acc, task) => {
                acc[task.status] = (acc[task.status] || 0) + 1;
                return acc;
            }, {}),
            dependency_analysis: {
                tasks_with_no_dependencies: dependencyAnalysis.availableTasks.filter(t => !t.dependencies || t.dependencies.length === 0).length,
                tasks_blocked_by_dependencies: dependencyAnalysis.blockedTasks.length,
                circular_dependencies_detected: dependencyAnalysis.circularDependencies.length
            }
        };

        const hasTasks = selectionResult.selectedTasks.length > 0;
        const topPriority = hasTasks ? selectionResult.selectedTasks[0].priority : 'N/A';
        const message = hasTasks
            ? `Found ${selectionResult.selectedTasks.length} highest priority available tasks (priority ${topPriority})`
            : 'No available tasks to select.';

        const response = {
            status: 'success',
            message: message,
            workflow_reminder: "IMPORTANT: You are in a workflow. Process ONLY ONE task at a time. After completing this task, you MUST call remember() to continue the workflow.",
            available_tasks: enhancedTasks.map(task => ({
                id: task.id,
                title: task.title,
                short_description: task.short_description,
                status: task.status,
                priority: task.priority,
                dependencies: task.dependencies || [],
                dependency_details: task.dependencyStatus.completedDependencies.concat(
                    task.dependencyStatus.pendingDependencies,
                    task.dependencyStatus.missingDependencies.map(id => ({
                        id,
                        title: 'Unknown Task',
                        status: 'NOT_FOUND'
                    }))
                ),
                is_available: task.dependencyStatus.isAvailable,
                readiness_score: task.readinessScore,
                dependency_chain: task.dependencyStatus.chain,
                parent_id: task.parent_id,
                created_date: task.created_date,
                updated_date: task.updated_date,
                image_data: task.image_data || null
            })),
            statistics,
            selection_analysis: {
                strategy: selectionResult.selectionStrategy,
                rationale: selectionResult.rationale,
                dependency_insights: dependencyAnalysis.circularDependencies.length > 0
                    ? `⚠️ Warning: ${dependencyAnalysis.circularDependencies.length} circular dependencies detected`
                    : "✅ No circular dependencies detected",
                blocked_tasks_summary: dependencyAnalysis.blockedTasks.length > 0
                    ? `${dependencyAnalysis.blockedTasks.length} tasks are blocked by unresolved dependencies`
                    : "No tasks are blocked by dependencies"
            },
            query_info: {
                selection_strategy: selectionResult.selectionStrategy,
                algorithm_used: "Enhanced dependency graph analysis with readiness scoring",
                total_available: dependencyAnalysis.availableTasks.length,
                analysis_timestamp: new Date().toISOString()
            }
        };

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error retrieving next tasks: ${error.message}`,
                    available_tasks: [],
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message,
                        stack_trace: error.stack?.split('\n').slice(0, 5) // First 5 lines of stack trace
                    }
                }, null, 2)
            }]
        };
    }
}