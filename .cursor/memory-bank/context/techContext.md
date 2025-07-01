# Technical Context

## Architecture Overview

### System Components

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Cursor IDE        │    │   Streamlit UI      │    │   MCP Servers       │
│                     │    │                     │    │                     │
│ ┌─────────────────┐ │    │ ┌─────────────────┐ │    │ ┌─────────────────┐ │
│ │ AI Agent        │ │◄──►│ │ Web Interface   │ │◄──►│ │ MemoryBankMCP   │ │
│ │ (Workflow Loop) │ │    │ │ (Monitoring)    │ │    │ │ (Core Logic)    │ │
│ └─────────────────┘ │    │ └─────────────────┘ │    │ └─────────────────┘ │
│                     │    │                     │    │                     │
│ ┌─────────────────┐ │    │ ┌─────────────────┐ │    │ ┌─────────────────┐ │
│ │ File System     │ │    │ │ Request Forms   │ │    │ │ ToolsMCP        │ │
│ │ (Workspace)     │ │    │ │ (User Input)    │ │    │ │ (System Ops)    │ │
│ └─────────────────┘ │    │ └─────────────────┘ │    │ └─────────────────┘ │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Data Flow Architecture

```
User Request → Streamlit UI → userbrief.json → Agent Workflow
                                                      ↓
Task Creation → CRUD Validation → tasks.json → Task Execution
                                                      ↓
Code Changes → File Operations → Git Commits → Memory Update
```

## Core Technologies

### Runtime Environment
- **Cursor IDE**: Primary execution environment with MCP integration
- **Node.js v18+**: MCP server runtime with ES modules support
- **Python 3.8+**: Streamlit application and UI components
- **Git**: Version control with automated commit workflows

### Key Dependencies
```json
{
  "mcp": "@modelcontextprotocol/sdk@latest",
  "validation": "zod@^3.22.0",
  "ui": "streamlit@^1.28.0",
  "nlp": "natural@^6.0.0",
  "file-ops": "fs-extra@^11.0.0"
}
```

## MCP Server Architecture

### MemoryBankMCP Server
**Location**: `.cursor/mcp/memory-bank-mcp/`
**Purpose**: Core workflow and data management

#### Tools Provided:
- `mcp_MemoryBankMCP_create_task`: Task creation with validation
- `mcp_MemoryBankMCP_update_task`: Task modification with business rules
- `mcp_MemoryBankMCP_get_all_tasks`: Task retrieval with filtering
- `mcp_MemoryBankMCP_remember`: Memory management and workflow routing
- `mcp_MemoryBankMCP_next_rule`: Workflow step management
- `mcp_MemoryBankMCP_commit`: Git operations with standardized messages

#### Validation Architecture:
```javascript
// 3-Layer Validation System
Schema Validation (Zod) → Business Rules → Data Integrity Checks
                                                      ↓
                                          Error Classification
                                          ├── ValidationError
                                          ├── BusinessRuleError  
                                          └── DataIntegrityError
```

### ToolsMCP Server
**Location**: `.cursor/mcp/tools-mcp/` (planned)
**Purpose**: System interaction and file operations

## Data Storage Architecture

### File Structure
```
.cursor/memory-bank/
├── streamlit_app/
│   ├── tasks.json          # PRIMARY: All task data (262 tasks, ~1MB)
│   └── userbrief.json      # User requests with status tracking
├── context/
│   ├── projectBrief.md     # Business context and objectives
│   └── techContext.md      # Technical implementation details
└── workflow/
    └── tasks.json          # DEPRECATED: Empty vestige file
```

### Data Models

#### Task Schema
```typescript
interface Task {
  id: number;
  title: string;
  short_description: string;
  detailed_description: string;
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'REVIEW' | 'DONE' | 'APPROVED';
  priority: 1 | 2 | 3 | 4 | 5;
  dependencies: number[];
  impacted_files: string[];
  created_at: string;
  updated_at: string;
  history: TaskHistoryEntry[];
}
```

#### User Request Schema
```typescript
interface UserRequest {
  id: number;
  content: string;
  status: 'new' | 'in_progress' | 'archived';
  image?: string;
  created_at: string;
  updated_at: string;
  history: RequestHistoryEntry[];
}
```

## Validation Systems (ACTIVE)

### 1. Duplicate Detection
**Algorithm**: Levenshtein distance with configurable thresholds
**Implementation**: `create_task.js` line 45-78
**Performance**: O(n×m) where n=existing tasks, m=title length
**Thresholds**: 
- Exact match: 1.0 (blocked)
- High similarity: 0.85 (blocked)
- Medium similarity: 0.7 (warning)

### 2. Circular Dependency Prevention
**Algorithm**: Depth-First Search cycle detection
**Implementation**: `circular_dependency_validator.js`
**Performance**: O(V+E) where V=tasks, E=dependencies
**Features**:
- Real-time cycle detection on task creation/update
- Multi-node cycle identification
- Dependency graph health analysis

### 3. CRUD Validation Framework
**Location**: `lib/task_crud_validator.js`
**Architecture**: Modular validation with error classification
**Capabilities**:
- Schema validation (Zod-based)
- Business rule enforcement
- File path safety validation
- Status transition validation

## Workflow Engine

### Rule-Based System
**Location**: `.cursor/workflow-steps/`
**Pattern**: Markdown files defining agent behavior

#### Available Rules:
- `start-workflow.md`: System initialization and context loading
- `task-decomposition.md`: User request analysis and task creation
- `implementation.md`: Code development and task execution
- `fix.md`: Bug resolution and system repair
- `context-update.md`: Maintenance and cleanup operations
- `experience-execution.md`: Manual testing and validation

#### Workflow Loop:
```
start-workflow → remember → next_rule → [execute step] → remember → next_rule → ...
```

### Intelligent Routing
**Logic**: Context-aware step selection based on:
- Unprocessed user requests (→ task-decomposition)
- Active tasks (→ implementation)
- Blocked tasks (→ fix)
- System maintenance needs (→ context-update)
- Validation requirements (→ experience-execution)

## Performance Characteristics

### Current Scale
- **Tasks**: 262 total (all completed/approved)
- **User Requests**: 53 total (3 pending)
- **Memory Entries**: ~64 long-term memories
- **File Operations**: ~1MB primary data file

### Performance Bottlenecks
1. **Duplicate Detection**: O(n×m) scales poorly with large task counts
2. **File I/O**: Single large JSON file for all tasks
3. **Memory Search**: Linear search through memories
4. **Validation**: Multiple validation passes on each operation

### Optimization Opportunities
- **Database Migration**: Replace JSON files with SQLite
- **Indexing**: Add search indices for common queries
- **Caching**: Cache validation results and duplicate checks
- **Pagination**: Implement lazy loading for large datasets

## Development Constraints

### Critical Limitations

#### MCP Server Caching
- **Issue**: Code changes require manual Cursor restart
- **Impact**: Slow iterative development cycle
- **Workaround**: Batch changes and test directly with Node.js first
- **Timeline for Fix**: Architectural limitation, no immediate solution

#### Tool Reliability
- **edit_file**: Unreliable for large changes (>100 lines)
- **Workaround**: Use `mcp_ToolsMCP_regex_edit` for precise modifications
- **Debug Logging**: Cannot use console.log in MCP tools (breaks JSON-RPC)

#### Error Handling
- **Silent Failures**: MCP tools often fail without clear error messages
- **Debugging**: Limited visibility into tool execution
- **Recovery**: Manual intervention sometimes required

### Development Workflow
```
1. Implementation → 2. Direct Testing → 3. MCP Testing → 4. Manual Restart → 5. Final Validation
```

## Security Model

### Access Controls
- **File System**: Limited to workspace directory
- **Command Execution**: Restricted to project context
- **Network Access**: No external network calls from MCP tools
- **User Data**: All operations logged and auditable

### Data Integrity
- **Validation**: Multi-layer validation prevents data corruption
- **Backup**: Automatic backup creation before major operations
- **Audit Trail**: Complete history tracking for all changes
- **Recovery**: Rollback capabilities for failed operations

## Integration Points

### Streamlit Interface
**Port**: 8501 (default)
**Features**:
- Real-time task monitoring
- User request submission with image support
- Memory browsing and search
- System status dashboard

### Git Integration
**Hooks**: Pre-commit validation and formatting
**Commit Standards**: Conventional commits with emoji prefixes
**Branching**: Single branch workflow with continuous integration

### External Tools
- **Brave Search**: Web search capabilities for research
- **Image Processing**: Screenshot and image analysis support
- **Terminal Operations**: Full shell access within workspace

## Monitoring and Observability

### Health Metrics
- **Task Completion Rate**: Currently 100% (262/262 completed)
- **Request Processing**: 3 pending requests awaiting processing
- **System Uptime**: Autonomous operation since last restart
- **Error Rate**: <1% tool failures (mostly edit_file issues)

### Logging
- **Workflow Steps**: Complete trace of agent decision-making
- **Tool Usage**: Detailed logs of all MCP tool invocations
- **Performance**: Timing data for validation and processing operations
- **Errors**: Comprehensive error tracking with stack traces

## Future Architecture Considerations

### Scalability Improvements
- **Database Backend**: SQLite or PostgreSQL for better performance
- **Microservices**: Split MCP servers by functional domain
- **Async Processing**: Queue-based task execution
- **Load Balancing**: Multiple agent instances for high availability

### Enhanced Capabilities
- **Multi-User Support**: Role-based access and isolation
- **Plugin Architecture**: Extensible tool system
- **Machine Learning**: Improved request understanding and task optimization
- **Real-Time Collaboration**: Live editing and conflict resolution 