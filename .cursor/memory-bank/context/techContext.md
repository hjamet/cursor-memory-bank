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
- **Tool Usage Constraints**: To enforce specific tool usage patterns, explicit constraints (e.g., forbidding `run_terminal_cmd` in favor of `mcp_ToolsMCP_execute_command`) are added directly into the workflow rule files. This serves as a "soft" directive to the agent.

## CRITICAL SYSTEM FAILURES & CONSTRAINTS

### MCP Server Deployment Constraint (CRITICAL)
**The most critical technical constraint affecting all development:**
- **Manual Restart Required**: ALL modifications to MCP tool code (`.cursor/mcp/memory-bank-mcp/mcp_tools/*.js`) require manual Cursor restart to become effective
- **Server Caching Issue**: MCP server caches tool code and does not reload changes automatically
- **Development Impact**: Creates a gap between implementation success (direct Node.js testing) and deployment failure (MCP testing)
- **Validation Pattern**: Code must be tested via: Implementation → Direct Testing → Manual Restart → MCP Testing → Final Validation

### Validation System Breakdown (DISCOVERED VIA ADVERSARIAL AUDIT)
**Critical data validation systems - MAJOR PROGRESS ACHIEVED:**

#### 1. Duplicate Detection System
- **Status**: ✅ **IMPLEMENTED AND ACTIVE** (as of MCP restart 2025-06-30)
- **Location**: `.cursor/mcp/memory-bank-mcp/mcp_tools/create_task.js`
- **Algorithm**: Levenshtein distance with configurable thresholds (0.85/0.7/0.9)
- **Validation**: Successfully blocks duplicate task creation with detailed error messages
- **Impact**: System now prevents creation of tasks with identical titles

#### 2. Circular Dependency Prevention
- **Status**: ✅ **IMPLEMENTED AND ACTIVE** (as of MCP restart 2025-06-30)
- **Location**: `.cursor/mcp/memory-bank-mcp/mcp_tools/circular_dependency_validator.js`
- **Algorithm**: DFS-based cycle detection with optimized performance
- **Validation**: Successfully prevents circular dependency creation
- **Impact**: Tasks can no longer be created with circular dependencies (A→B→A)

#### 3. Centralized CRUD Validation System (NEW - Task #258)
- **Status**: ✅ **IMPLEMENTED AND ACTIVE** (as of 2025-06-30)
- **Location**: `.cursor/mcp/memory-bank-mcp/lib/task_crud_validator.js`
- **Architecture**: 3-layer validation (Schema → Business Rules → Data Integrity)
- **Features**: 
  - Zod-based schema validation for all data types
  - Business rule enforcement (status transitions, dependencies)
  - Data integrity checks (duplicates, file path safety)
  - Comprehensive error classes with detailed feedback
- **Integration**: Fully integrated into `create_task.js` and `update_task.js`
- **Validation**: Adversarial testing confirms critical functions operational
- **Limitations**: Schema error handling needs refinement (causes interruptions vs clean errors)

#### 4. Data Integrity Issues
- **Duplicate tasks.json files**: 
  - Active: `.cursor/memory-bank/streamlit_app/tasks.json` (709KB, used by MCP)
  - Vestige: `.cursor/memory-bank/workflow/tasks.json` (empty, unused) - **STILL REQUIRES CLEANUP**
- **Statistical inconsistencies**: Partially addressed with centralized statistics module
- **Corrupted test data**: System contains test tasks (#252, #253, #264, #265) with circular dependencies - **CLEANUP IN PROGRESS**

### Workflow & Dependency Management
- **Infinite Loop Prevention**: Recent improvements have addressed some workflow infinite loops, but edge cases remain
- **Task State Management**: Implementation rule enforces immediate `IN_PROGRESS` marking, but overall state tracking across complex workflows remains fragile
- **Dependency Resolution**: Automatic unblocking system exists but may not handle all edge cases

### Tool Reliability Issues
- **`edit_file` Instability**: Unreliable for large or complex changes. `regex_edit` should be preferred for precise modifications
- **Debug Logging Constraint**: Any non-JSON output from MCP tools (e.g., `console.log`) breaks JSON-RPC communication and crashes the server
- **Error Handling**: MCP tools fail silently in many cases, making debugging extremely difficult

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
│   └── workflow/           # Tasks and user requests (DEPRECATED)
│   └── streamlit_app/      # ACTIVE data location
├── streamlit_app/          # User interface
├── workflow-steps/         # Workflow rule definitions
├── rules/                  # Cursor agent rules
├── run_ui.sh              # Streamlit launcher
└── mcp.json               # MCP server configuration
```

## Recent Implementations (WITH CRITICAL CAVEATS)

### Duplicate Detection System (IMPLEMENTED BUT NOT ACTIVE)
- **Implementation**: Complete Levenshtein-based duplicate detection in `create_task.js`
- **Testing**: Direct Node.js tests pass perfectly
- **MCP Status**: FAILS due to server caching - requires manual restart
- **Performance**: O(k×n×m) complexity not tested under realistic load
- **Limitations**: Server-side only, no Streamlit UI integration

### Circular Dependency Prevention (IMPLEMENTED BUT NOT ACTIVE)
- **Implementation**: Complete DFS-based cycle detection with validator module
- **Testing**: 12 tests pass, including performance validation on 1000 tasks
- **MCP Status**: FAILS due to server caching - allows cycle creation (264↔265)
- **Performance**: Sub-1000ms for large datasets in direct testing
- **Integration**: Integrated into both create_task.js and update_task.js

### Workflow Improvements (PARTIALLY EFFECTIVE)
- **Remember Tool Logic**: Improved infinite loop prevention
- **Implementation Rule**: Enhanced task marking requirements
- **Experience-Execution Rule**: Added anti-loop protections
- **Dependency System**: Automatic task unblocking on completion

### User Interface Improvements (STABLE)
- **Clickable Notifications**: Interactive alert system with smart navigation
- **Form Management**: Fixed text area clearing issues
- **Workflow Integrity**: Replaced problematic "Reactivate" button with feedback system
- **Task Comment System**: Mandatory comments for status changes

## Performance & Maintenance

### Automatic Cleanup (IMPLEMENTED)
- **Python Cache**: `__pycache__` directories cleaned during maintenance
- **MCP Logs**: Terminal logs and status files cleaned regularly
- **Archive Management**: Automatic limitation of stored memories and tasks (50 max)
- **Repository Maintenance**: Automated cleanup of temporary files during context updates

### Monitoring (UNRELIABLE)
- **Work Queue**: Real-time task and request counting (may be inaccurate due to statistical inconsistencies)
- **Workflow Visibility**: Current workflow step/rule displayed in sidebar
- **Interactive Notification System**: Clickable red alert indicators
- **Memory Usage**: Automatic semantic search and long-term memory management
- **Error Handling**: Enhanced MCP tool error reporting (when tools don't fail silently)

## Security & Data Integrity Concerns

### Data Integrity (COMPROMISED)
- **Validation Gaps**: Critical validation systems not active in production
- **Corrupted Data**: Test data with circular dependencies polluting production
- **Statistical Unreliability**: Cannot trust system metrics for decision-making
- **Duplicate Architecture**: Two conflicting data sources create confusion

### Security Considerations (BASIC)
- **File Access**: MCP servers operate within workspace boundaries
- **Command Execution**: Terminal access limited to project directory
- **Data Persistence**: User data preserved during updates and maintenance
- **Tool Safety**: Enhanced validation exists but may not be active due to server caching

## Development Workflow Constraints

### Critical Development Pattern
1. **Implementation**: Write code changes
2. **Direct Testing**: Test via Node.js scripts (usually succeeds)
3. **MCP Testing**: Test via MCP tools (often fails due to caching)
4. **Manual Restart**: Restart Cursor to reload MCP server
5. **Final Validation**: Re-test via MCP tools
6. **Deployment**: Changes become effective only after restart

### Known Failure Modes
- **Silent MCP Failures**: Tools fail without clear error messages
- **Caching Issues**: Server uses old code versions despite apparent restart
- **Debug Logging Breaks**: Any console output crashes JSON-RPC communication
- **Inconsistent State**: Direct tests pass while MCP tests fail

## Realistic System Assessment

The system demonstrates sophisticated autonomous capabilities but suffers from fundamental validation and deployment issues. The MCP server caching constraint creates a significant barrier to reliable development and testing. Critical validation systems exist but are not active in the production environment, creating a false sense of security.

The architecture is sound, but the implementation requires significant work to address data integrity issues, deployment constraints, and validation gaps before it can be considered production-ready for autonomous operation.