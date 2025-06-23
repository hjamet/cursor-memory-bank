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
    emoji: z.string().describe("COMMIT EMOJI: Single emoji that represents the type of change made. Use conventional commit emojis: ✨ for new features, 🐛 for bug fixes, 📝 for documentation, ♻️ for refactoring, ✅ for tests, 🔧 for configuration, 🚀 for performance improvements, 🔒 for security fixes, 💄 for UI/styling, 🗃️ for database changes, 🔥 for removing code/files."),
    type: z.string().describe("COMMIT TYPE: Conventional commit type that categorizes the change. Use standard types: 'feat' (new feature), 'fix' (bug fix), 'docs' (documentation), 'style' (formatting, no code change), 'refactor' (code restructuring), 'test' (adding tests), 'chore' (maintenance), 'perf' (performance), 'ci' (continuous integration), 'build' (build system), 'revert' (reverting changes)."),
    title: z.string().describe("COMMIT TITLE: Concise, imperative mood summary of the change (50 characters or less). Start with a verb in present tense. Examples: 'Add user authentication system', 'Fix database connection timeout', 'Update API documentation', 'Refactor payment processing logic'. Do not end with a period."),
    description: z.string().describe("COMMIT DESCRIPTION: Detailed explanation of what was changed, why it was changed, and any important implementation details. Include: (1) What specific changes were made, (2) Why these changes were necessary, (3) Any breaking changes or migration notes, (4) Related issue numbers if applicable. Use bullet points for multiple changes. Example: 'Implemented JWT-based authentication system:\\n\\n- Added login/logout endpoints with password hashing\\n- Created middleware for protected routes\\n- Updated user model with authentication fields\\n- Added session management with 24h token expiry\\n\\nThis resolves the security requirements and enables user-specific features.'")
}, safeHandler(handleCommit));

server.tool('create_task', {
    title: z.string().min(1).max(200).describe("TASK TITLE: Clear, actionable title that describes what needs to be accomplished (1-200 characters). Use imperative mood and be specific. Examples: 'Implement user authentication system', 'Fix database connection timeout issues', 'Create API documentation for payment endpoints', 'Refactor user interface components'. Avoid vague titles like 'Fix bug' or 'Update code'."),
    short_description: z.string().min(1).max(500).describe("BRIEF SUMMARY: Concise overview of the task that provides context and scope (1-500 characters). Should answer 'what' and 'why' briefly. Example: 'Create a secure login system with JWT tokens to replace the current session-based authentication. This will improve security and enable mobile app integration.' Include the main objective and key benefit."),
    detailed_description: z.string().min(1).describe("DETAILED SPECIFICATIONS: Comprehensive description of what needs to be done, including specific requirements, acceptance criteria, technical details, and implementation approach. Break down into clear steps or bullet points. Include: (1) Specific functionality to implement, (2) Technical requirements and constraints, (3) Expected inputs and outputs, (4) Integration points with existing systems, (5) Performance or quality requirements. Example: 'Implement JWT-based authentication:\\n\\n**Requirements:**\\n- User login with email/password\\n- JWT token generation with 24h expiry\\n- Protected route middleware\\n- Password hashing with bcrypt\\n\\n**Acceptance Criteria:**\\n- Users can log in and receive valid JWT\\n- Protected routes reject invalid tokens\\n- Passwords are securely hashed\\n- Token refresh mechanism works\\n\\n**Technical Notes:**\\n- Use jsonwebtoken library\\n- Store tokens in httpOnly cookies\\n- Implement rate limiting on login attempts'"),
    dependencies: z.array(z.number().int().positive()).optional().default([]).describe("TASK DEPENDENCIES: Array of task IDs that must be completed before this task can start. Only include direct dependencies that block this task's execution. Example: [12, 15] means tasks 12 and 15 must be completed first. Use empty array [] if no dependencies exist."),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().default('TODO').describe("CURRENT STATUS: Task's current state in the workflow. 'TODO' = not started, 'IN_PROGRESS' = currently being worked on, 'DONE' = completed, 'BLOCKED' = waiting for external dependency, 'REVIEW' = completed but needs review/testing. Default is 'TODO' for new tasks."),
    impacted_files: z.array(z.string()).optional().default([]).describe("AFFECTED FILES: List of files that will be created, modified, or deleted during this task. Use relative paths from project root. Examples: ['src/auth/login.js', 'tests/auth.test.js', 'docs/api/auth.md']. This helps with conflict detection and code review planning."),
    validation_criteria: z.string().optional().default('').describe("COMPLETION CRITERIA: Specific, measurable criteria that define when this task is considered complete. Should be testable and objective. Include functional tests, performance benchmarks, or quality gates. Example: 'Task is complete when: (1) All unit tests pass with >90% coverage, (2) Login/logout flow works in browser, (3) JWT tokens expire correctly after 24h, (4) API endpoints return proper error codes, (5) Documentation is updated with new endpoints.'"),
    parent_id: z.number().int().positive().optional().describe("PARENT TASK ID: ID of the parent task if this is a subtask or component of a larger task. Use this to create hierarchical task structures. Example: If task 10 is 'Implement user management system' and this task is 'Create user login', then parent_id would be 10. Leave empty for top-level tasks."),
    priority: z.number().int().min(1).max(5).optional().default(3).describe("TASK PRIORITY: Urgency and importance level (1=lowest, 5=highest). Use 5 for critical/blocking issues, 4 for high-priority features, 3 for normal work (default), 2 for nice-to-have improvements, 1 for low-priority tasks. Consider business impact, user impact, and technical dependencies when setting priority.")
}, safeHandler(handleCreateTask));

server.tool('update_task', {
    task_id: z.number().int().positive().describe("TASK IDENTIFIER: The unique ID number of the task to update. This ID is assigned when the task is created and can be found in task listings. Required field - you must specify which task to modify."),
    title: z.string().min(1).max(200).optional().describe("NEW TASK TITLE: Updated clear, actionable title (1-200 characters). Use imperative mood and be specific. Only provide if you want to change the existing title. Examples: 'Implement user authentication system', 'Fix database connection timeout issues'."),
    short_description: z.string().min(1).max(500).optional().describe("NEW BRIEF SUMMARY: Updated concise overview (1-500 characters). Only provide if you want to change the existing description. Should answer 'what' and 'why' briefly and include the main objective and key benefit."),
    detailed_description: z.string().min(1).optional().describe("NEW DETAILED SPECIFICATIONS: Updated comprehensive description with requirements, acceptance criteria, technical details, and implementation approach. Only provide if you want to replace the existing detailed description completely."),
    dependencies: z.array(z.number().int().positive()).optional().describe("NEW TASK DEPENDENCIES: Updated array of task IDs that must be completed before this task. This completely replaces the existing dependencies list. Use empty array [] to remove all dependencies. Example: [12, 15] means tasks 12 and 15 must be completed first."),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe("NEW STATUS: Updated task state. 'TODO' = not started, 'IN_PROGRESS' = currently being worked on, 'DONE' = completed, 'BLOCKED' = waiting for external dependency, 'REVIEW' = completed but needs review/testing. Only provide if status is changing."),
    impacted_files: z.array(z.string()).optional().describe("NEW AFFECTED FILES: Updated list of files that will be created, modified, or deleted. This completely replaces the existing files list. Use relative paths from project root. Examples: ['src/auth/login.js', 'tests/auth.test.js']."),
    validation_criteria: z.string().optional().describe("NEW COMPLETION CRITERIA: Updated specific, measurable criteria that define when this task is complete. Should be testable and objective. Only provide if you want to change the existing criteria."),
    parent_id: z.number().int().positive().nullable().optional().describe("NEW PARENT TASK ID: Updated parent task ID for hierarchical structure, or null to remove parent relationship. Only provide if you want to change the parent-child relationship."),
    priority: z.number().int().min(1).max(5).optional().describe("NEW TASK PRIORITY: Updated urgency level (1=lowest, 5=highest). Use 5 for critical/blocking issues, 4 for high-priority features, 3 for normal work, 2 for nice-to-have improvements, 1 for low-priority tasks. Only provide if priority is changing.")
}, safeHandler(handleUpdateTask));

server.tool('get_all_tasks', {}, safeHandler(handleGetAllTasks));

server.tool('get_next_tasks', {}, safeHandler(handleGetNextTasks));

server.tool('read_userbrief', {
    archived_count: z.number().optional().describe("ARCHIVED COUNT: Number of archived entries to include in the response (optional, default: 3). Use this to control how many completed/archived requests are returned along with the current active request.")
}, safeHandler(handleReadUserbrief));

server.tool('update_userbrief', {
    action: z.enum(['mark_archived', 'add_comment', 'mark_pinned']).describe("USERBRIEF ACTION: The operation to perform on a user request entry. 'mark_archived' = move request to completed/archived status (use when work is finished), 'add_comment' = append a progress update or note to the request history (use for status updates, findings, or communication), 'mark_pinned' = mark request as important/priority (use for high-priority items that should stay visible)."),
    id: z.number().optional().describe("REQUEST ID: The unique identifier of the specific user request to update. If omitted, the action will target the currently active (in_progress or new) request. Use this when you need to update a specific historical request rather than the current one."),
    comment: z.string().optional().describe("UPDATE COMMENT: Text to add to the request's history when using 'add_comment' action. Should provide meaningful updates about progress, findings, decisions made, or next steps. Examples: 'Successfully implemented authentication system, moving to testing phase', 'Discovered database schema issue, investigating alternatives', 'Feature completed and deployed to staging environment'. Required when action is 'add_comment', ignored for other actions.")
}, safeHandler(handleUpdateUserbrief));


// Start the server
async function startServer() {
    try {
        // Initialize server transport
        const transport = new StdioServerTransport();

        // Connect server to transport
        await server.connect(transport);

    } catch (error) {
        console.error('[MemoryBankMCP] Failed to start server:', error);
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
    console.error('[MemoryBankMCP] Server startup error:', error);
}); 