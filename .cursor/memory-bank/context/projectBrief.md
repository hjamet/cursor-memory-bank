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

## Current State & Challenges

The project is in a phase of **active development and stabilization**. While significant progress has been made on the autonomous workflow and the agent's core capabilities, several critical issues are currently hindering its reliability and must be addressed.

### Current Challenges
- **Workflow Instability**: The workflow is currently prone to deadlocks and infinite loops, particularly when dealing with task dependencies and edge cases in the `experience-execution` step. The logic for recommending the next step is not yet fully robust.
- **MCP Server Reliability**: There are strong indications that the MCP server does not reliably load the latest versions of tool files after modification, even with a server restart. This makes debugging and implementing new features extremely difficult and unpredictable.
- **Comment Validation Failure**: A key feature designed to enforce critical feedback from the agent (by validating comment length) is currently inoperative due to the aforementioned server issues. This directly impacts the quality of the agent's reasoning.
- **Documentation Overly Positive**: The project's documentation has historically been written from an overly positive perspective, failing to accurately reflect the real-world challenges and instabilities of the system.

The immediate priority is to address these fundamental issues to ensure the stability, reliability, and critical self-awareness of the agent. The system is **not** currently in a state of "complete architectural perfection" and requires significant work to achieve its vision.
