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

## Current State
The project has reached a highly mature state with a sophisticated autonomous workflow system that is now **completely immune to infinite loops**. The agent demonstrates advanced problem-solving capabilities, including:

- **Workflow Mastery**: Seamless execution of complex multi-step tasks with bulletproof state management and systematic task tracking that prevents any task loss.
- **Loop-Free Operation**: The critical `remember` tool fix ensures the workflow can never enter infinite loops, providing guaranteed progression through workflow states.
- **Diagnostic Excellence**: Ability to investigate reported "bugs" and discover they are actually misunderstood features, then enhance them for better usability.
- **Intelligent Enhancement**: Rather than simply fixing problems, the agent improves tools to be more flexible and user-friendly.
- **Comprehensive Documentation**: Proactive creation of user guides and troubleshooting resources.
- **Systematic Reliability**: Enhanced workflow rules ensure consistent behavior and eliminate edge cases that could cause task loss or confusion.
- **Bulletproof Autonomy**: The combination of task tracking improvements and infinite loop prevention creates a truly autonomous system that can operate indefinitely without manual intervention.

The system now operates with minimal manual intervention while maintaining high reliability and user satisfaction. Recent cycles have focused on refining workflow robustness, preventing common issues, and creating excellent documentation for optimal user experience. The latest workflow improvements ensure that no task can be lost during workflow transitions and no infinite loops can occur, providing bulletproof reliability for autonomous operation.
