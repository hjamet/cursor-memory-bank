# Project Brief

## Vision
To create a robust and autonomous AI agent within the Cursor IDE. This agent will leverage a persistent memory system to manage complex software development tasks, learn from interactions, and maintain context across coding sessions.

## Core Mandate
The agent's primary function is to assist a user (`hjamet`) by autonomously breaking down user requests into actionable development tasks, implementing solutions, and maintaining the project's health.

## Key System Components
- **Autonomous Workflow**: The agent operates on a continuous loop of `remember -> next_rule -> execute`, allowing it to move between states like task decomposition, implementation, and context updates without manual intervention.
- **Memory Bank**: A persistent storage system (`tasks.json`, `userbrief.json`, context files) that acts as the agent's long-term memory.
- **Streamlit UI**: A web-based interface for the user to submit requests, monitor the agent's progress, and review completed work.
- **MCP Tooling**: A set of custom servers that provide the agent with the necessary capabilities (e.g., terminal access, file system manipulation, Git operations) to perform its tasks.

## Current State & Critical Reality Check

The project is in a phase of **active development with significant systemic instabilities**. Despite progress on the autonomous workflow and core capabilities, the system suffers from fundamental architectural flaws that severely impact reliability and production readiness.

### Critical System Failures (Discovered via Adversarial Audit)

**🚨 VALIDATION SYSTEM BREAKDOWN:**
- **Complete absence of duplicate detection**: The system allows creation of tasks with identical titles without any validation
- **No circular dependency prevention**: Tasks can be created with circular dependencies (A→B→A) that permanently block workflow progression
- **Inconsistent task statistics**: Displayed task counts don't match actual task states, making system monitoring unreliable
- **Insufficient CRUD validation**: Basic data integrity checks are missing across all task operations

**🚨 DEPLOYMENT CONSTRAINT CRITICAL:**
- **MCP Server Restart Requirement**: All modifications to MCP tool code (`.cursor/mcp/memory-bank-mcp/mcp_tools/*.js`) require manual Cursor restart to become effective
- **Implementation-Deployment Gap**: Code can pass direct testing but fail in MCP environment due to server caching
- **Unpredictable Development Cycle**: This constraint makes iterative development extremely difficult and unreliable

**🚨 DATA INTEGRITY ISSUES:**
- **Duplicate architecture files**: Two `tasks.json` files exist in different locations, creating confusion about data source
- **Corrupted test data**: System contains test tasks with circular dependencies that pollute production data
- **Statistical inconsistencies**: Task counters and status reports are unreliable due to synchronization issues

### Architectural Debt & Technical Challenges

**Workflow Instability**: The autonomous workflow remains prone to edge cases and infinite loops. While recent improvements have addressed some issues, the system lacks comprehensive error handling and recovery mechanisms.

**Tool Reliability**: Critical tools like `edit_file` are unreliable for complex operations, forcing workarounds that add complexity and potential failure points.

**Validation Gaps**: The system was built with an assumption of reliable input validation, but the adversarial audit revealed this assumption is fundamentally flawed.

**Performance Unknowns**: Systems like duplicate detection using Levenshtein distance (O(k×n×m) complexity) have not been tested under realistic load conditions.

### Development Process Issues

**Overly Optimistic Documentation**: Previous documentation failed to capture the real-world challenges and instabilities, leading to unrealistic expectations about system reliability.

**Insufficient Testing**: The system lacks comprehensive adversarial testing, allowing critical flaws to persist in production.

**Deployment Friction**: The MCP server restart requirement creates significant friction in the development and validation process.

## Immediate Priorities

1. **System Validation Overhaul**: Implement comprehensive duplicate detection, circular dependency prevention, and data integrity validation
2. **Data Cleanup**: Remove corrupted test data and resolve architectural file duplication
3. **Monitoring Improvement**: Fix statistical inconsistencies and implement reliable system health monitoring
4. **Process Documentation**: Clearly document the MCP server restart constraint and its impact on development workflows

## Realistic Assessment

The system is **not production-ready** and requires significant investment in validation, testing, and architectural improvements before it can be considered reliable for autonomous operation. The recent adversarial audit has revealed that the system's apparent stability was built on untested assumptions about data integrity and validation.

The vision remains achievable, but the path requires acknowledging these fundamental issues and addressing them systematically rather than continuing to build features on an unstable foundation.
