# Project Brief

## Vision
To create a robust and autonomous AI agent within Cursor that leverages a persistent memory system to manage complex tasks, learn from interactions, and maintain context across sessions.

## Objectives
1.  Define and implement a clear file structure for the agent's memory (Memory Bank).
2.  Develop a set of extensible rules that govern the agent's behavior and workflow.
3.  Enable the agent to autonomously manage tasks, track progress, and update its context.
4.  Facilitate indirect communication between the user and the agent via the Memory Bank files.
5.  Ensure the agent can understand and modify its own operational rules.
6.  Maintain a high level of reliability and error recovery in the agent's operations.

## Constraints
-   Operate within the Cursor extension environment.
-   Rely on available tools and APIs provided by Cursor.
-   Markdown files as the primary medium for memory and rule definitions.

## Stakeholders
-   User (hjamet)
-   Cursor AI Agent

## Success Metrics
-   Agent successfully completes complex multi-step tasks autonomously.
-   Memory Bank accurately reflects the project state and agent's knowledge.
-   Users can effectively guide and interact with the agent through the defined mechanisms.
-   Reduction in manual intervention required for agent operations.

## History and Context
This project involves building and refining an autonomous agent system. Recent enhancements include:
- Agent ability to provide feedback on its work by commenting on archived tasks in `userbrief.md` (Task 8).
- Enhancement of the `fix.mdc` rule to include a `git log --grep` search capability for mysterious problems, improving diagnostic abilities (Task 9).
- Optimization of the testing logic in the rule system to prioritize manual execution via `experience-execution` over systematic automated test creation, reducing complexity and execution time while maintaining code quality (Task 10). 