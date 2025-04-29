# ToDo

# Done

## 1. Refactor `experience-execution.mdc`: Command Execution & Monitoring [In Progress]
- [x] **1.1 Modify Initial Execution (Step 2)**: Change Step 2 to always use `mcp_MyMCP_execute_command` with a fixed short timeout (e.g., 30 seconds).
    - *Description*: Update the instruction text in Step 2 to mandate the use of `mcp_MyMCP_execute_command` and specify a short initial timeout (30s). Remove mentions of long timeouts in this step.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: Step 2 text reflects the use of a short, fixed timeout (30s) for the initial command execution.
- [x] **1.2 Implement Monitoring Loop (New Step 2.5 / Modify Step 3)**: Add a new step or modify Step 3 to implement the iterative monitoring loop.
    - *Description*: Introduce logic after the initial execution (Step 2) to repeatedly call `mcp_MyMCP_get_terminal_status`. Start with a short timeout (e.g., 15s) and progressively increase it on subsequent calls (e.g., double it, up to 300s max) as long as the command runs without critical errors/anomalies. Ensure the 300s maximum timeout per call is explicit.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.1
    - *Validation Criteria*: The rule includes a new step or modified Step 3 detailing the monitoring loop with `mcp_MyMCP_get_terminal_status`, increasing timeouts, and a 300s max limit per call.
- [x] **1.3 Integrate Analysis within Monitoring (Step 2.5 / Modify Step 3)**: Add analysis using `<think>` within the monitoring loop.
    - *Description*: Within the monitoring loop (Task 1.2), explicitly instruct the agent to use `<think>` blocks after each `get_terminal_status` call to analyze the received status/output. This analysis should check for anomalies or potential issues.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.2
    - *Validation Criteria*: The monitoring loop description includes mandatory `<think>` blocks for intermediate analysis.
- [x] **1.4 Add In-Loop Code Investigation & Decision (Step 2.5 / Modify Step 3)**: Allow code investigation and decision-making during monitoring.
    - *Description*: Enhance the `<think>` block (Task 1.3) to allow optional code investigation (`read_file`, `codebase_search`) if anomalies are suspected, without immediately stopping the command. Add logic for the agent to decide based on this analysis whether to continue monitoring, stop the command (`mcp_MyMCP_stop_terminal_command`), or proceed to the final analysis step.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.3
    - *Validation Criteria*: The monitoring loop's `<think>` block describes the possibility of code investigation and the decision logic (continue/stop/proceed).
- [x] **1.5 Adapt Final Analysis (Step 3/4)**: Adjust the final analysis step (currently Step 3, may become Step 4) to account for the new monitoring loop.
    - *Description*: Ensure the final critical analysis step logically follows the monitoring loop and uses the *final* state/output gathered, incorporating any insights from the intermediate `<think>` analyses.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.2, 1.3, 1.4
    - *Validation Criteria*: The final analysis step is clearly distinct from the monitoring loop analysis and uses the comprehensive final results.

# Done

## 1. Refactor `experience-execution.mdc`: Command Execution & Monitoring
- [x] **1.1 Modify Initial Execution (Step 2)**: Change Step 2 to always use `mcp_MyMCP_execute_command` with a fixed short timeout (e.g., 30 seconds).
    - *Description*: Update the instruction text in Step 2 to mandate the use of `mcp_MyMCP_execute_command` and specify a short initial timeout (30s). Remove mentions of long timeouts in this step.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: Step 2 text reflects the use of a short, fixed timeout (30s) for the initial command execution.
- [x] **1.2 Implement Monitoring Loop (New Step 2.5 / Modify Step 3)**: Add a new step or modify Step 3 to implement the iterative monitoring loop.
    - *Description*: Introduce logic after the initial execution (Step 2) to repeatedly call `mcp_MyMCP_get_terminal_status`. Start with a short timeout (e.g., 15s) and progressively increase it on subsequent calls (e.g., double it, up to 300s max) as long as the command runs without critical errors/anomalies. Ensure the 300s maximum timeout per call is explicit.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.1
    - *Validation Criteria*: The rule includes a new step or modified Step 3 detailing the monitoring loop with `mcp_MyMCP_get_terminal_status`, increasing timeouts, and a 300s max limit per call.
- [x] **1.3 Integrate Analysis within Monitoring (Step 2.5 / Modify Step 3)**: Add analysis using `<think>` within the monitoring loop.
    - *Description*: Within the monitoring loop (Task 1.2), explicitly instruct the agent to use `<think>` blocks after each `get_terminal_status` call to analyze the received status/output. This analysis should check for anomalies or potential issues.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.2
    - *Validation Criteria*: The monitoring loop description includes mandatory `<think>` blocks for intermediate analysis.
- [x] **1.4 Add In-Loop Code Investigation & Decision (Step 2.5 / Modify Step 3)**: Allow code investigation and decision-making during monitoring.
    - *Description*: Enhance the `<think>` block (Task 1.3) to allow optional code investigation (`read_file`, `codebase_search`) if anomalies are suspected, without immediately stopping the command. Add logic for the agent to decide based on this analysis whether to continue monitoring, stop the command (`mcp_MyMCP_stop_terminal_command`), or proceed to the final analysis step.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.3
    - *Validation Criteria*: The monitoring loop's `<think>` block describes the possibility of code investigation and the decision logic (continue/stop/proceed).
- [x] **1.5 Adapt Final Analysis (Step 3/4)**: Adjust the final analysis step (currently Step 3, may become Step 4) to account for the new monitoring loop.
    - *Description*: Ensure the final critical analysis step logically follows the monitoring loop and uses the *final* state/output gathered, incorporating any insights from the intermediate `<think>` analyses.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: 1.2, 1.3, 1.4
    - *Validation Criteria*: The final analysis step is clearly distinct from the monitoring loop analysis and uses the comprehensive final results.