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
- **Version Control**: `commit` for standardized Git commits
- **Memory System**: `remember` for state recording, `next_rule` for workflow navigation

#### ToolsMCP Server (`mcp_ToolsMCP_*`)
System interaction server:
- **Terminal Operations**: `execute_command`, `get_terminal_status`, `get_terminal_output`, `stop_terminal_command`
- **Visual Processing**: `consult_image`, `take_webpage_screenshot`
- **File Manipulation**: `regex_edit` for precise file modifications with enhanced MCP communication

### Workflow System
Located in `.cursor/workflow-steps/`:
- **Autonomous Loop**: `start-workflow` → `next_rule` → `execute` → `remember` → repeat
- **Step Types**: `task-decomposition`, `implementation`, `fix`, `context-update`, `experience-execution`
- **Rule Files**: `.mdc` files in `.cursor/rules/` (e.g., `start.mdc`)

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
│   ├── mcp-commit-server/  # Git commit server (legacy)
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

### User Interface Improvements
- **Clickable Notification Indicator**: The red notification alert in the sidebar is now interactive, providing one-click navigation to the Review & Communication page with intelligent tab selection (Agent Messages prioritized over Tasks to Review)
- **Form Field Management**: Fixed text area clearing issue in the Add Request tab - form fields now properly reset after successful submission, preventing accidental duplicate submissions
- **Navigation Intelligence**: Implemented smart redirection logic that automatically opens the most relevant tab based on notification content

### MCP Tool Enhancements
- **Enhanced regex_edit Communication**: The regex_edit tool now returns properly structured MCP responses with detailed operation status, file information, change statistics, and error handling
- **Improved Error Reporting**: Better structured error messages and success indicators for all MCP operations
- **Streamlined User Experience**: Reduced friction in common workflows through intelligent defaults and automatic form management

## Known Issues & Workarounds

### Tool Reliability
- **`edit_file` Instability**: Unreliable for large changes. Use `regex_edit` for precise modifications
- **Binary File Handling**: Standard tools cannot delete binary files; use terminal commands instead

### MCP Server Management
- **Tool Discovery**: New tools require full Cursor IDE restart to appear
- **Debug Logging**: Any non-JSON output breaks MCP communication
- **Server Restart**: Modify `mcp.json` temporarily to force server restart

### Development Practices
- **MDC File Editing**: Rename to `.md`, edit, rename back to `.mdc` for Git tracking
- **Memory Bank**: Automatic archive cleanup (25 max entries) prevents data bloat
- **Pre-commit Hooks**: Warn on files >500 lines but don't block commits

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
- **Archive Management**: Automatic limitation of stored memories and tasks

### Monitoring
- **Work Queue**: Real-time task and request counting in UI
- **Workflow Visibility**: Current workflow step/rule displayed in sidebar for transparency
- **Interactive Notification System**: Clickable red alert indicators for tasks requiring review and agent messages with smart navigation
- **Memory Usage**: Automatic semantic search and long-term memory management
- **Error Handling**: Comprehensive error reporting through enhanced MCP tools

## Security Considerations
- **File Access**: MCP servers operate within workspace boundaries
- **Command Execution**: Terminal access limited to project directory
- **Data Persistence**: User data preserved during updates and maintenance