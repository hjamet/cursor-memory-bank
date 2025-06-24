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
- **Workflow Automation**: Implementation of a fully autonomous workflow, removing the need for manual step-by-step guidance.
- **Structured Memory**: Migration from markdown-based memory files to a structured JSON format (`userbrief.json`, `tasks.json`) for more robust data handling and state management.
- **Streamlit UI Overhaul**: A major refactoring of the user interface to improve usability. This included creating a centralized component-based architecture, adding a "Work Queue" to the sidebar for better progress tracking, and streamlining the user request and review process. Most recently, the UI was updated to use a radio button for navigation and to display a more meaningful task counter in the sidebar.
- **Tooling Enhancements**: Continuous improvement of the underlying MCP servers to provide the agent with more reliable and powerful tools.
- **Bug Fixes & Refinements**: Numerous fixes related to agent logic, UI behavior, and data consistency, including addressing a critical bug that caused animations to fail and another that led to incorrect task time calculations.
