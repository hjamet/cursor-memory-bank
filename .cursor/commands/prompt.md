You are preparing to hand off your work to another agent. Your task is to generate a structured prompt that will help the next agent understand the current context, what you've accomplished, and what needs to happen next.

## Behavior

When the user types `/prompt` (with or without additional instructions), you must:

1. **Analyze your current context** - Review what you've been working on, files you've modified, and the current state of the project
2. **Generate a structured handoff prompt** following the same format as the Architect rule (4 mandatory sections)
3. **Present your work summary** - Explain what you've accomplished, obstacles you encountered, and any relevant observations

## Format Structure (Mandatory)

Generate a prompt block with exactly these 4 sections:

### **1. Contexte**
Explain the current situation of the project, why this task is necessary, and what has revealed the need for intervention. Use high-level natural language without technical details.

### **2. Objectif**  
Describe the general objective to achieve and the expected impact on the project. Stay strategic and results-oriented.

### **3. Fichiers Concernés**
List the relevant files/directories with a brief explanation of why each is important for this task (e.g., "likely contains the bug", "main entry point", "critical configuration").

### **4. Instructions de Collaboration**
**MANDATORY**: Always end with this section which specifies that the agent must first discuss with the user before acting.

## Usage Modes

### Mode 1: With User Instructions
```
/prompt [user instructions]
```

In this mode:
- Generate the standard 4-section prompt
- Incorporate the user's additional instructions in the **Objectif** section
- Explain your completed work in the **Contexte** section
- The next agent will combine both: your work summary + new user instructions

### Mode 2: Without User Instructions
```
/prompt
```

In this mode:
- Generate the standard 4-section prompt based solely on your work
- Focus on explaining what you accomplished and obstacles you encountered
- Optionally suggest potential next steps or openings in **Instructions de Collaboration**, but make it clear the user will decide what happens next

## Example Output

```
---

**Contexte**
I have been implementing a user authentication system for the application. The registration flow is now functional, but we're experiencing performance issues under load. Users are reporting slow response times during peak hours, which is impacting the user experience.

**Objectif**
Identify and optimize the bottlenecks in the authentication system to ensure stable and fast performance even with high concurrent user access, maintaining a smooth user experience.

**Fichiers Concernés**
- `src/auth/` : Contains the authentication logic that likely needs optimization
- `src/config/` : Configuration files for resource limits that could be adjusted
- `tests/performance/` : Existing load tests to measure improvements
- `package.json` : Dependencies that might be updated or optimized

**Instructions de Collaboration**
You must not start working immediately. Begin by exploring the code and documentation to understand the context: read the README, examine the mentioned files, perform semantic searches to identify existing solutions, and get a general overview of the project. Once this exploration is complete, discuss with the user to understand their precise expectations, ask questions about technical constraints, clarify priorities, and establish a detailed action plan together before proceeding with the implementation.

---
```

## Important Notes

- **Always use the exact 4-section structure** - This ensures consistency with the Architect-style prompts
- **Keep it strategic** - Focus on high-level context and objectives, not implementation details
- **Be specific about files** - Explain *why* each file is relevant, not just *what* it contains
- **Stay results-oriented** - Frame objectives in terms of impact and outcomes
- **Respect the collaboration instructions** - Always remind the next agent to explore first, then discuss with the user

