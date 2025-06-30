# Technical Context

## Project Overview
This project is an autonomous AI agent operating within the Cursor IDE. Its primary goal is to manage software development tasks, interact with the user via a Streamlit interface, and maintain a persistent memory of its operations.

## Core Technologies
- **AI Agent**: Custom-built agent running within Cursor IDE
- **Workflow Engine**: Rule-based system using `.md` files that dictate agent behavior
- **Memory System**: Custom "Memory Bank" for persistent state, tasks, and knowledge storage
- **MCP Tooling**: Custom Model Context Protocol servers for system interactions
- **Frontend**: Streamlit application for user interaction and monitoring
- **Development**: Node.js (MCP servers), Python (Streamlit), Bash (installation)

## Architecture Overview

### Streamlit Application
The primary user interface for the agent, located in `.cursor/streamlit_app/`.

### MCP Server Architecture
- **MemoryBankMCP Server (`mcp_MemoryBankMCP_*`)**: Core server for agent state and workflow management.
- **ToolsMCP Server (`mcp_ToolsMCP_*`)**: System interaction server.

### Workflow System
Located in `.cursor/workflow-steps/`, this system defines the agent's behavior through a series of rules and steps.
- **Dynamic Tool Selection**: The workflow rules provide high-level goals. The agent dynamically selects the most appropriate tool from its toolkit at runtime to achieve these goals, rather than having tools hardcoded in the rules.

## Known Issues & Workarounds

### Workflow & Dependency Management
- **Instability**: The workflow is prone to deadlocks and infinite loops, especially concerning task dependencies and `experience-execution` edge cases. The `remember` tool's logic for recommending the next step is not yet fully robust and has been a source of significant instability.
- **Task State Management**: The implementation rule was recently refactored to enforce immediate `IN_PROGRESS` status marking to prevent task loss, but the overall system for tracking task state across complex workflows remains fragile.

### MCP Server Management
- **Tool Loading Inconsistency**: There is a critical, unresolved issue where the MCP server does not reliably load the latest version of tool files (e.g., `update_task.js`) after modification, even with a server restart. This makes debugging and implementing new features extremely difficult and unpredictable. All development on MCP tools is currently unreliable due to this issue.
- **Comment Validation Failure**: A key feature designed to enforce critical feedback from the agent (by validating comment length in `update_task.js`) is currently inoperative due to the server's inability to load the updated tool code.
- **Debug Logging**: Any non-JSON output from an MCP tool (e.g., `console.log`) will break the JSON-RPC communication and cause the tool to fail silently or crash the server.

### Tool Reliability
- **`edit_file` Instability**: Unreliable for large or complex changes. `regex_edit` should be preferred for precise modifications.

## Dependencies & Requirements
- **Node.js**: v18+ for MCP servers
- **Python**: 3.8+ for Streamlit application
- **Cursor IDE**: Latest version for agent execution
- **Core MCP Dependencies**: `@modelcontextprotocol/sdk`, `zod`

## Installation & Configuration

### Installation Script (`install.sh`)
Comprehensive bash script supporting:
- **Download Methods**: Git clone or curl-based file download
- **MCP Server Setup**: Automatic installation and dependency management
- **Memory Preservation**: Protects existing `.cursor/memory-bank` data
- **Git Integration**: Pre-commit hooks and automatic configuration

### File Structure
```
.cursor/
├── mcp/                    # MCP servers
│   ├── memory-bank-mcp/    # Core memory and workflow server
│   ├── mcp-commit-server/  # Enhanced commit server with terminal tools
│   └── tools-mcp/          # System tools server (planned)
├── memory-bank/            # Persistent agent memory
│   ├── context/            # Project context files
│   └── workflow/           # Tasks and user requests
├── streamlit_app/          # User interface
├── workflow-steps/         # Workflow rule definitions
├── rules/                  # Cursor agent rules
├── run_ui.sh              # Streamlit launcher
└── mcp.json               # MCP server configuration
```

## Recent Enhancements

### Critical Workflow Loop Prevention (Latest)
- **Remember Tool Logic Fix**: Implemented comprehensive logic to prevent infinite loops in the autonomous workflow
  - **Core Problem Resolved**: The `remember` tool could incorrectly recommend `experience-execution` immediately after an `experience-execution` step, creating forbidden infinite loops
  - **New getRecommendedNextStep Function**: Added sophisticated routing logic that explicitly forbids experience-execution → experience-execution transitions
  - **Smart State-Based Routing**: 
    - If task remains IN_PROGRESS after experience-execution → routes to `fix` for issue resolution
    - If task is completed (no IN_PROGRESS) → routes to `context-update` or `task-decomposition` (if new requests exist)
    - Preserves all other valid workflow transitions
  - **Comprehensive Validation**: Created and executed validation script with 6 critical tests, all passing
  - **Impact**: Eliminates the possibility of workflow infinite loops, ensuring robust autonomous operation

### Dependency System Enhancement (Latest)
- **Automatic Task Unblocking**: Comprehensive implementation of automatic dependency resolution system to prevent permanent task blocking
  - **Core Problem Resolved**: Tasks with dependencies were not automatically unblocked when their dependencies completed (REVIEW/DONE status), causing permanent workflow stalls
  - **New Functions Implemented**:
    - `areAllDependenciesCompleted()`: Validates completion status of all task dependencies
    - `checkAndUnblockDependentTasks()`: Automatically finds and unblocks tasks waiting on completed dependencies
    - `cleanupOrphanedDependencies()`: Removes dependencies to non-existent tasks to prevent permanent blocking
  - **Integration**: Seamlessly integrated into `handleUpdateTask()` workflow for automatic triggering on task status changes
  - **Validation**: Comprehensive testing with multiple scenarios (simple dependency, multiple dependencies, orphaned dependencies) - all tests passed
  - **Impact**: Eliminates permanent task blocking in autonomous workflow, ensures smooth task progression without manual intervention
  - **File Modified**: `.cursor/mcp/memory-bank-mcp/mcp_tools/update_task.js`

### Experience-Execution Rule Enhancement (In Review)
- **Workflow Rule Hardening**: Comprehensive modifications to the experience-execution rule to prevent infinite loops at the rule level
  - **Critical Anti-Loop Protection**: Added explicit "CRITICAL ANTI-LOOP PROTECTION" warning section at the top of instructions
  - **Mandatory Sequence**: Made task status update to REVIEW mandatory BEFORE any other action (1. Update task → REVIEW, 2. Commit, 3. Remember)
  - **Visual Warnings**: Added 🚨 MANDATORY FIRST STEP warnings throughout the rule to prevent oversight
  - **Enhanced Examples**: Updated all examples to reflect the new mandatory sequence, ensuring consistent implementation
  - **Think Block Improvements**: Enhanced `<think>` sections with critical reminders about loop prevention requirements
  - **Architectural Impact**: This modification affects a core workflow file, providing double protection against infinite loops (remember tool + rule level)
  - **Impact**: Guarantees that experience-execution steps always mark tasks as REVIEW before calling remember, preventing any possibility of rule-level infinite loops

### ID Generation System Enhancement (In Review)
- **Robust ID Generation**: Comprehensive improvements to prevent duplicate ID issues that cause StreamlitDuplicateElementKey errors
  - **Enhanced create_task.js**: Added `generateUniqueTaskId()` function with collision detection, retry logic, and timestamp fallback
  - **Enhanced userbrief_manager.js**: Added `generateUniqueRequestId()` and `validateUserbriefIntegrity()` functions for robust ID generation
  - **Validation Functions**: Implemented `validateTaskIntegrity()` and `validateUserbriefIntegrity()` to detect and prevent duplicate IDs
  - **Maintenance Tool**: Created `id_integrity_checker.js` utility for detecting and repairing duplicate IDs with automatic backup
  - **Comprehensive Testing**: All validation tests passed, confirming protection against race conditions and ID collisions
  - **Impact**: Resolves StreamlitDuplicateElementKey errors in client projects and ensures bulletproof ID generation system

### Workflow Rule Improvements
- **Implementation Rule Refactoring**: Major restructuring of the implementation workflow rule to guarantee systematic task marking
  - Step 1 renamed: "Task analysis" → "Task analysis and status update"
  - Mandatory IN_PROGRESS marking: Tasks must be marked immediately upon identification at step 1
  - RULE #3 added: "MARQUER IMMÉDIATEMENT la tâche comme IN_PROGRESS dès l'étape 1 - AUCUNE EXCEPTION"
  - Enhanced anti-drift warnings: Explicit prohibitions against forgetting task marking
  - Updated example workflow: Reflects new process with systematic marking at step 1
  - **Impact**: Eliminates task loss during transitions to experience-execution, ensures robust workflow consistency

### Terminal Tools Improvements
- **Enhanced get_terminal_output**: Added `from_beginning` parameter for flexible output reading
  - Default mode: Incremental reading (only new output since last call)
  - `from_beginning: true`: Complete output from process start
- **Comprehensive Documentation**: Created `TERMINAL_TOOLS_GUIDE.md` with usage patterns and troubleshooting
- **Backward Compatibility**: All existing functionality preserved with new optional parameters

### Commit Tool Enhancements
- **Refactoring Task Deduplication**: Automatic prevention of duplicate refactoring tasks for the same file
- **Smart Task Management**: Added `refactoring_target_file` field for precise task identification
- **Cleanup Logic**: Automatically removes existing refactoring tasks before creating new ones

### User Interface Improvements
- **Clickable Notification Indicator**: The red notification alert in the sidebar is now interactive, providing one-click navigation to the Review & Communication page with intelligent tab selection (Agent Messages prioritized over Tasks to Review)
- **Form Field Management**: Fixed text area clearing issue in the Add Request tab - form fields now properly reset after successful submission, preventing accidental duplicate submissions
- **Navigation Intelligence**: Implemented smart redirection logic that automatically opens the most relevant tab based on notification content
- **Workflow Integrity**: Replaced the "Reactivate" button for archived requests with a feedback form. This prevents the old bug where reactivated requests would create duplicate tasks and cause workflow loops. The new system creates a new, distinct request for follow-up, preserving the integrity of the archive.

### MCP Tool Enhancements
- **Enhanced regex_edit Communication**: The regex_edit tool now returns properly structured MCP responses with detailed operation status, file information, change statistics, and error handling
- **Improved Error Reporting**: Better structured error messages and success indicators for all MCP operations
- **Streamlined User Experience**: Reduced friction in common workflows through intelligent defaults and automatic form management
- **Task Comment System**: Implemented mandatory comment system for task status changes with structured storage and UI display integration
- **Critical Bug Fixes**: Resolved UnboundLocalError in Streamlit UI validation system with improved robustness for legacy task data

## Performance & Maintenance

### Automatic Cleanup
- **Python Cache**: `__pycache__` directories cleaned during maintenance
- **MCP Logs**: Terminal logs and status files cleaned regularly
- **Archive Management**: Automatic limitation of stored memories and tasks (50 max)
- **Repository Maintenance**: Automated cleanup of temporary files during context updates

### Monitoring
- **Work Queue**: Real-time task and request counting in UI
- **Workflow Visibility**: Current workflow step/rule displayed in sidebar for transparency
- **Interactive Notification System**: Clickable red alert indicators for tasks requiring review and agent messages with smart navigation
- **Memory Usage**: Automatic semantic search and long-term memory management
- **Error Handling**: Comprehensive error reporting through enhanced MCP tools
- **Terminal Tools**: Comprehensive guide available for optimal usage patterns

## Security Considerations
- **File Access**: MCP servers operate within workspace boundaries
- **Command Execution**: Terminal access limited to project directory
- **Data Persistence**: User data preserved during updates and maintenance
- **Tool Safety**: Enhanced validation and error handling in all MCP operations