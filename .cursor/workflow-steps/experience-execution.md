## TLDR
Manually test and validate the implemented functionality through careful analysis and interaction. Focus on understanding behavior, identifying issues, and documenting results through the remember tool.

## Instructions

1. **Planning & Preparation**: Plan the manual testing approach.
   - `<think>`
     - Identify what functionality needs to be tested based on recent implementations.
     - Determine the best way to test each feature (direct interaction, edge cases, error conditions).
     - Consider what scenarios are most likely to reveal issues.
     - Plan the sequence of tests to perform.
     - Define what constitutes success for each test.
     `</think>`
   - Summarize the testing plan and approach.
   - **(Experience-Execution: 1 - Planning completed)**

2. **Manual Testing Execution**: Execute the planned tests manually.
   - `<think>`
     - Follow the testing plan from step 1.
     - For each test scenario, carefully observe the behavior.
     - Note any unexpected results, errors, or edge cases discovered.
     - Document both successful and failed test cases.
     - Pay attention to performance, usability, and correctness.
     `</think>`
   - Execute each planned test scenario systematically.
   - Use `mcp_ToolsMCP_execute_command` for any command-line testing needed.
   - Document the results of each test with detailed observations.
   - **(Experience-Execution: 2 - Manual testing executed)**

3. **Critical Analysis**: Analyze the test results and overall functionality.
   - `<think>`
     - Review all test results from step 2.
     - Identify patterns in successes and failures.
     - Determine if the functionality meets the original requirements.
     - Consider edge cases that might not have been tested.
     - Evaluate the overall quality and robustness of the implementation.
     - Note any areas that need improvement or further development.
     `</think>`
   - Provide a comprehensive analysis of the testing results.
   - Identify any issues, limitations, or areas for improvement.
   - **(Experience-Execution: 3 - Critical analysis completed)**

4. **Record results and determine next steps**: Use the remember tool to document testing and get next steps.
   - `<think>`
     - Summarize what was tested and the results.
     - Note any issues discovered and their potential solutions.
     - Record lessons learned during the testing process.
     - Document the current state of the functionality.
     `</think>`
   - Use the `mcp_MemoryBankMCP_remember` tool to record:
     - **PAST**: What testing was performed and what was discovered
     - **PRESENT**: Current state of the functionality and any issues
     - **FUTURE**: Next steps needed based on the testing results
   - The remember tool will indicate the appropriate next steps
   - **(Experience-Execution: 4 - Record results and determine next steps)**

## Specifics
- This rule focuses on manual testing and validation rather than automated testing.
- Critical analysis of functionality and behavior is mandatory.
- Use `<think>` blocks for planning, analysis, and decision making.
- Results must be recorded using the `remember` tool rather than creating separate documentation files.
- Testing should be thorough and cover edge cases, error conditions, and normal usage scenarios.
- Use MCP tools for all command execution and state management.

## Next Steps
- `context-update` - If testing was successful and functionality works as expected
- `fix` - If testing revealed significant issues or bugs that need to be resolved
- `task-decomposition` - If testing was successful but revealed areas for improvement or new requirements

## Example (Conceptual)

# Experience-Execution: 1 - Planning & Preparation
<think> Plan: Test the new user authentication feature. Test scenarios: valid login, invalid credentials, edge cases like empty fields, special characters. Expected: proper error messages, successful login flow, security measures working. </think>
I will test the authentication feature with various scenarios to ensure it works correctly and securely.
**(Experience-Execution: 1 - Planning completed)**

# Experience-Execution: 2 - Manual Testing Execution
<think> Testing valid login: works correctly, redirects to dashboard. Testing invalid password: shows appropriate error message. Testing empty fields: validation works. Testing SQL injection attempts: properly sanitized. All tests successful. </think>
I systematically tested all planned scenarios. The authentication feature works as expected with proper validation and security measures.
**(Experience-Execution: 2 - Manual testing executed)**

# Experience-Execution: 3 - Critical Analysis
<think> All tests passed successfully. The authentication feature meets requirements. Security measures are in place. User experience is smooth. No issues found. The implementation is robust and ready for production. </think>
The authentication feature is working correctly and meets all requirements. No issues were discovered during testing.
**(Experience-Execution: 3 - Critical analysis completed)**

# Experience-Execution: 4 - Record results and determine next steps
<think> Testing was successful, no issues found. The functionality is working as expected. Ready to update context and complete this phase. </think>
[...calling `mcp_MemoryBankMCP_remember` tool with PAST: "Tested authentication feature with various scenarios", PRESENT: "Feature working correctly, all tests passed", FUTURE: "Ready for context update and completion"...]
**(Experience-Execution: 4 - Record results and determine next steps)**
