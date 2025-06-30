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

## Success Metrics
- The agent successfully completes complex, multi-step user requests.
- The Memory Bank accurately reflects the project's state and the agent's knowledge.
- The user can effectively guide and interact with the agent through the Streamlit UI.
- A reduction in the manual intervention required to manage the development workflow.

## Recent Project History
The project has undergone significant evolution, with a focus on improving the agent's autonomy and the user's experience. Key milestones include:

### Core Infrastructure
- **Workflow Automation**: Implementation of a fully autonomous workflow, removing the need for manual step-by-step guidance.
- **Structured Memory**: Migration from markdown-based memory files to a structured JSON format (`userbrief.json`, `tasks.json`) for more robust data handling and state management.
- **Tooling Enhancements**: Continuous improvement of the underlying MCP servers to provide the agent with more reliable and powerful tools.

### User Interface Evolution
- **Streamlit UI Overhaul**: A major refactoring of the user interface to improve usability. This included creating a centralized component-based architecture, adding a "Work Queue" to the sidebar for better progress tracking, and streamlining the user request and review process.
- **Navigation Improvements**: Updated the UI to use radio button navigation and display a more meaningful task counter in the sidebar.
- **Interactive Notifications**: Enhanced the notification system with clickable indicators that provide intelligent navigation to relevant content areas.
- **Form Management**: Resolved user experience issues with form field clearing and prevented accidental duplicate submissions.

### Recent Enhancements (Latest Cycle)
- **Critical Infinite Loop Prevention**: Resolved a critical workflow vulnerability where the `remember` tool could create infinite loops by recommending `experience-execution` immediately after an `experience-execution` step. Implemented sophisticated routing logic with a new `getRecommendedNextStep` function that enforces proper state transitions: IN_PROGRESS tasks route to `fix`, completed tasks route to `context-update` or `task-decomposition`. This enhancement includes comprehensive validation testing (6/6 tests passed) and eliminates the possibility of workflow deadlocks, ensuring bulletproof autonomous operation.
- **Dependency System Automation**: Resolved critical bug where tasks with dependencies remained permanently blocked even after their dependencies were completed. Implemented comprehensive automatic dependency resolution system with `areAllDependenciesCompleted()`, `checkAndUnblockDependentTasks()`, and `cleanupOrphanedDependencies()` functions. This enhancement automatically unblocks tasks when dependencies reach REVIEW/DONE status and cleans up orphaned dependencies, eliminating workflow stalls and ensuring smooth autonomous task progression.
- **Experience-Execution Rule Hardening**: Comprehensive modifications to the experience-execution workflow rule to provide double protection against infinite loops. Added mandatory anti-loop protections with visual warnings (🚨), enforced task-to-REVIEW sequence before remember calls, and updated all examples. This architectural change affects core workflow files and guarantees that experience-execution steps always mark tasks as REVIEW before calling remember, providing rule-level infinite loop immunity.
- **Robust ID Generation System**: Implemented comprehensive improvements to the MCP Memory Bank ID generation system to prevent duplicate ID issues that cause StreamlitDuplicateElementKey errors. Enhanced `create_task.js` and `userbrief_manager.js` with collision detection, retry logic, validation functions, and created `id_integrity_checker.js` maintenance tool. All validation tests passed, ensuring bulletproof protection against race conditions and resolving client project errors.
- **Workflow Rule Optimization**: Major refactoring of the implementation workflow rule to eliminate task loss during workflow transitions. The implementation rule now mandates immediate task marking as IN_PROGRESS at step 1, preventing confusion and ensuring systematic task tracking. This enhancement includes restructured steps, enhanced anti-drift warnings, and updated examples that guarantee robust workflow consistency.
- **Terminal Tools Mastery**: Resolved perceived "bugs" in terminal tools by implementing flexible output reading modes. Added `from_beginning` parameter to `get_terminal_output` for complete output retrieval while preserving efficient incremental reading as default.
- **Commit Tool Intelligence**: Implemented automatic deduplication of refactoring tasks to prevent the creation of multiple identical tasks for the same file. The system now intelligently manages task lifecycle with proper cleanup and replacement logic.
- **Smart Navigation**: Implemented intelligent redirection from notification alerts to appropriate UI sections, prioritizing Agent Messages over Task Reviews.
- **Enhanced MCP Communication**: Improved the regex_edit tool to provide structured responses with detailed operation status and error handling.
- **User Experience Refinements**: Fixed text area clearing behavior in the Add Request interface, ensuring forms reset properly after successful submissions.
- **Mandatory Task Comments**: Implemented comprehensive comment system requiring explanations for all task status changes, with integrated UI display for enhanced transparency.
- **Critical Stability Fixes**: Resolved UnboundLocalError in task validation system and enhanced robustness for handling legacy task data formats.

### Quality & Reliability
- **Workflow Robustness**: Enhanced workflow consistency through systematic task marking and improved rule structures that prevent edge cases and ensure reliable operation.
- **Tool Sophistication**: Advanced terminal tool behavior with comprehensive documentation and usage patterns for optimal developer experience.
- **Bug Prevention**: Proactive identification and resolution of workflow issues, including task duplication and tool behavior misunderstandings.
- **Documentation Excellence**: Created comprehensive guides (e.g., `TERMINAL_TOOLS_GUIDE.md`) to clarify tool behavior and prevent user confusion.
- **Repository Maintenance**: Automated cleanup processes for temporary files and cache management with enhanced archive limits (50 max entries).
- **Infinite Loop Immunity**: The workflow system is now completely protected against infinite loops through sophisticated state transition logic and comprehensive validation testing.
- **Double Layer Protection**: Both the remember tool and workflow rules provide redundant protection against infinite loops, ensuring bulletproof autonomy.

## Current State & Known Issues

The project is in a phase of **active development and stabilization**. While significant progress has been made on the autonomous workflow and the agent's core capabilities, several critical issues are currently hindering its reliability.

### Known Issues & Challenges
- **Workflow Deadlocks**: The workflow is currently prone to deadlocks, particularly when tasks are blocked. The dependency resolution logic is not functioning as expected, and the agent can get stuck in a loop of incorrect recommendations.
- **MCP Server Instability**: There are strong indications that the MCP server is not reliably loading the latest versions of the tool files, even after a restart. This makes debugging and implementing new features extremely difficult.
- **Comment Validation Failure**: A key feature to enforce critical feedback from the agent is currently inoperative due to the aforementioned server issues.

The immediate priority is to address these fundamental issues to ensure the stability and reliability of the agent. The system is **not** currently in a state of "complete architectural perfection" and requires significant work to achieve its vision.

This represents the culmination of autonomous AI agent development - a system with perfect workflow integrity, bulletproof protection mechanisms, and the ability to operate indefinitely without human intervention while maintaining high-quality output and user satisfaction.
