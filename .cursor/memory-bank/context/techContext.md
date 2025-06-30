# Technical Context

## Project Overview
This project is an autonomous AI agent operating within the Cursor IDE. Its primary goal is to manage software development tasks, interact with the user via a Streamlit interface, and maintain a persistent memory of its operations.

## Core Technologies
- **AI Agent**: Custom-built agent running within Cursor IDE
- **Workflow Engine**: Rule-based system using `.mdc` files that dictate agent behavior
- **Memory System**: Custom "Memory Bank" for persistent state, tasks, and knowledge storage
- **MCP Tooling**: Custom Model Context Protocol servers for system interactions
- **Frontend**: Streamlit application for user interaction and monitoring
- **Development**: Node.js (MCP servers), Python (Streamlit), Bash (installation)

## Architecture Overview

### Streamlit Application
The primary user interface for the agent, located in `.cursor/streamlit_app/`:

- **Main Entry Point**: `app.py` - Handles user request submission and task review with radio navigation
- **Components**:
  - `components/sidebar.py`: Centralized sidebar with auto-refresh, work queue counter, workflow step indicator, and clickable notification alerts with intelligent navigation
  - `components/task_utils.py`: Helper functions for task/user brief manipulation, workflow state tracking, and notification counting
  - `components/style_utils.py`: UI styling utilities
- **Pages**:
  - `pages/task_status.py`: Dashboard for viewing and tracking all tasks
  - `pages/memory.py`: Interface for inspecting agent's recent memories
- **Data Models**:
  - `tasks.json`: Development tasks with status history tracking
  - `userbrief.json`: User requests, decoupled from task management until conversion

### MCP Server Architecture

#### MemoryBankMCP Server (`mcp_MemoryBankMCP_*`)
Core server for agent state and workflow management:
- **User Request Management**: `read_userbrief`, `update_userbrief`
- **Task Management**: `create_task`, `update_task`, `get_all_tasks`, `get_next_tasks`
- **Version Control**: `commit` for standardized Git commits with refactoring task deduplication
- **Memory System**: `remember` for state recording, `next_rule` for workflow navigation with **critical loop prevention logic**

#### ToolsMCP Server (`mcp_ToolsMCP_*`)
System interaction server:
- **Terminal Operations**: `execute_command`, `get_terminal_status`, `get_terminal_output` (enhanced with `from_beginning` parameter), `stop_terminal_command`
- **Visual Processing**: `consult_image`, `take_webpage_screenshot`
- **File Manipulation**: `regex_edit` for precise file modifications with enhanced MCP communication

### Workflow System
Located in `.cursor/workflow-steps/`:
- **Autonomous Loop**: `start-workflow` → `next_rule` → `execute` → `remember` → repeat
- **Step Types**: `task-decomposition`, `implementation`, `fix`, `context-update`, `experience-execution`
- **Rule Files**: `.mdc` files in `.cursor/rules/` (e.g., `start.mdc`)
- **Implementation Rule Enhancement**: The implementation rule has been refactored to guarantee systematic task marking as IN_PROGRESS at step 1, preventing task loss during transitions to experience-execution
- **Critical Loop Prevention**: The `remember` tool now includes sophisticated logic to prevent infinite loops, especially the critical experience-execution → experience-execution transition
- **Experience-Execution Rule Hardening**: The experience-execution rule itself has been enhanced with mandatory anti-loop protections, ensuring tasks are marked REVIEW before any remember call

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

### MCP Tool Enhancements
- **Enhanced regex_edit Communication**: The regex_edit tool now returns properly structured MCP responses with detailed operation status, file information, change statistics, and error handling
- **Improved Error Reporting**: Better structured error messages and success indicators for all MCP operations
- **Streamlined User Experience**: Reduced friction in common workflows through intelligent defaults and automatic form management
- **Task Comment System**: Implemented mandatory comment system for task status changes with structured storage and UI display integration
- **Critical Bug Fixes**: Resolved UnboundLocalError in Streamlit UI validation system with improved robustness for legacy task data

## Known Issues & Workarounds

### Tool Reliability
- **`edit_file` Instability**: Unreliable for large changes. Use `regex_edit` for precise modifications
- **Binary File Handling**: Standard tools cannot delete binary files; use terminal commands instead

### MCP Server Management
- **Tool Discovery**: New tools require full Cursor IDE restart to appear
- **Debug Logging**: Any non-JSON output breaks MCP communication
- **Server Restart**: Modify `mcp.json` temporarily to force server restart
- **Terminal Tools**: Enhanced tools require MCP server restart to activate new features
- **Tool Loading Inconsistency**: There is a suspected issue where the MCP server does not reliably load the latest version of tool files, even after a restart. This can lead to unpredictable behavior and make debugging extremely difficult.

### Development Practices
- **MDC File Editing**: Rename to `.md`, edit, rename back to `.mdc` for Git tracking
- **Memory Bank**: Automatic archive cleanup (50 max entries) prevents data bloat
- **Pre-commit Hooks**: Warn on files >500 lines but don't block commits

### Workflow & Dependency Management
- **Dependency Logic**: The logic for resolving task dependencies is not functioning correctly, leading to workflow deadlocks. Tasks can remain blocked even when their dependencies are completed.

## Dependencies & Requirements

### Runtime Requirements
- **Cursor IDE**: Latest version for agent execution
- **Node.js**: v18+ for MCP servers
- **Python**: 3.8+ for Streamlit application
- **Git**: For version control and installation (optional with curl fallback)

### MCP Server Dependencies
- **Core**: `@modelcontextprotocol/sdk`
- **Validation**: `zod` for schema validation
- **Visual Tools**: `puppeteer`, `sharp` for image processing
- **Web Framework**: `express`, `cors`, `express-rate-limit`

### Installation Tools
- **Required**: `bash`, `curl` or `git`
- **Optional**: `jq` for JSON processing, `npm` for dependency installation

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