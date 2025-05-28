---
description: Call this rule to create or update unit tests for new or existing features
globs: 
alwaysApply: false
---
## TLDR
Create ONLY essential tests to "freeze" stable behaviors that will never change. Use very few tests, simple execution, focus on outputs not internal behavior, avoid mocks, stay close to real usage.

## Instructions

1.  **Stability Assessment**: Verify that behaviors need to be "frozen".
    * **IMPORTANT**: This rule should ONLY be called for behaviors that are stable and unlikely to change.
    * Examine modified/created files to identify ONLY the core, stable behaviors that need to be preserved.
    * **Principle**: Create very few tests, only for behaviors that are critical and will remain unchanged.
    * **Focus**: Test outputs and results, NOT internal implementation details.
    * After each tool call, write **(Test-implementation - 1.[Feature name] in progress...)**

2.  **Minimal Test Creation**: Create only essential tests.
    * **Identify Existing Tests**: Check if relevant tests already exist for the stable behavior.
    * **Decision and Action**:
        * If existing tests adequately cover the stable behavior: Skip test creation.
        * If no relevant test exists for a truly stable behavior: Create a minimal test.
    * **Implementation Principles**:
        * **Very few tests**: Only test the most critical, stable behaviors.
        * **Simple execution**: Use straightforward test logic, avoid complex setups.
        * **Output-focused**: Test what the function/feature produces, not how it works internally.
        * **No mocks**: Use real data and real execution paths when possible.
        * **Real usage**: Test scenarios that mirror actual usage patterns.
        * **Minimal scope**: Each test should verify one specific, stable output or behavior.
    * Use the format defined in the test-files editing rule.
    * After each tool call (creation or modification), write **(Test-implementation - 2.[Test name] in progress...)**

3.  **Call Next Rule**: Mandatory call to `test-execution`.

## Specifics

* **RESTRICTION**: Only create tests for behaviors that are stable and will NOT change.
* **Simplicity**: Prefer simple, direct tests over comprehensive test suites.
* **Output verification**: Test what the code produces, not how it produces it.
* **Real usage**: Tests should mirror actual usage scenarios, not artificial test cases.
* **No mocks**: Avoid mocking unless absolutely necessary; use real data and execution.
* **Minimal coverage**: Better to have few, reliable tests than many complex ones.
* When creating *new* test files, they must begin with `test_` and be placed in the `tests/` folder.
* Use descriptive names that clearly indicate the stable behavior being preserved.
* Include logging using `src/utils/logger.py` if the code is in Python.
* To avoid losing the workflow, systematically write `Test-implementation - [number].[Name] in progress...` between each step.

## Next Rules
* `test-execution` - To execute created tests and analyze results.

## Example

# Test-implementation: 1 - Feature analysis
I start by identifying features to test or tests to enrich. **(Test-implementation: 1 - Feature analysis)**
[...analysis of modified files...]
**(Test-implementation - 1.Authentication in progress...)**
[...identification of behaviors to test or tests to complete...]
**(Test-implementation: 1 - Feature analysis)**

# Test-implementation: 2 - Test creation or modification
I will create or modify tests for each identified item. **(Test-implementation: 2 - Test creation or modification)**
[...modification of an existing test for login...]
**(Test-implementation - 2.Enrichment_TestLogin in progress...)**
[...creation of a new test file for a new feature...]
**(Test-implementation - 2.TestNewValidation in progress...)**
**(Test-implementation: 2 - Test creation or modification)**

# Test-implementation: 3 - Call next rule
I must now call the test-execution rule to execute the tests.
The test-execution rule must be called to execute and analyze the tests. **(Test-implementation: 3 - Call next rule)**

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)
