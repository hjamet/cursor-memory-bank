# Streamlit Auto-refresh Playwright Test Instructions

## Overview
This document provides step-by-step instructions for testing the Streamlit auto-refresh functionality using MCP Playwright tools.

## Prerequisites
1. Streamlit application running on `http://localhost:8501`
2. MCP Playwright tools available
3. Timer component added to the main page (implemented in `app.py`)
4. Auto-refresh configured for 2-second intervals (configured in `sidebar.py`)

## Test Implementation

### Step 1: Navigate to Streamlit Application
```
Use: mcp_playwright_browser_navigate
URL: http://localhost:8501
Purpose: Load the Streamlit app in the browser
```

### Step 2: Wait for Page Load
```
Use: mcp_playwright_browser_wait_for
time: 3
Purpose: Allow page to fully load and initialize
```

### Step 3: Take Initial Snapshot
```
Use: mcp_playwright_browser_snapshot
Purpose: Capture initial state of the page including timer value
Expected: Find text containing "Auto-refresh Test Timer: X.X seconds elapsed since page load"
```

### Step 4: Wait for Auto-refresh Cycles
```
Use: mcp_playwright_browser_wait_for
time: 8
Purpose: Allow 4 auto-refresh cycles (8 seconds / 2 seconds per cycle)
Expected: Page should automatically refresh 4 times during this period
```

### Step 5: Take Final Snapshot
```
Use: mcp_playwright_browser_snapshot
Purpose: Capture final state after auto-refresh cycles
Expected: Timer should show significantly higher value
```

### Step 6: Analyze Results
Compare the initial and final snapshots:
- Extract timer values from both snapshots
- Calculate time difference
- Verify timer increased by at least 6 seconds (allowing 2-second tolerance)

## Success Criteria
1. **Initial snapshot** contains timer with starting value
2. **Final snapshot** contains timer with increased value
3. **Timer increase** is at least 6 seconds (indicating 4 auto-refresh cycles worked)
4. **No errors** in browser console
5. **Page content** refreshes automatically without user intervention

## Timer Component Details
The timer component is located in the main content area and displays:
```
⏱️ **Auto-refresh Test Timer**: X.X seconds elapsed since page load
This timer validates that auto-refresh is working - it should increment automatically every 2 seconds
```

## Pattern Matching for Timer Extraction
Use these regex patterns to extract timer values from snapshots:
- `Auto-refresh Test Timer[:\s]*(\d+\.?\d*)\s*seconds`
- `(\d+\.?\d*)\s*seconds elapsed since page load`
- `Timer[:\s]*(\d+\.?\d*)`

## Expected Test Flow

### Test Execution Sequence
1. **Navigate** → `http://localhost:8501`
2. **Wait** → 3 seconds for load
3. **Snapshot** → Capture initial timer (e.g., "3.2 seconds")
4. **Wait** → 8 seconds for auto-refresh
5. **Snapshot** → Capture final timer (e.g., "11.8 seconds")
6. **Analyze** → Verify 8.6 second increase ✅

### Validation Logic
```python
timer_increase = final_timer - initial_timer
expected_minimum = 6.0  # seconds
success = timer_increase >= expected_minimum
```

## Auto-refresh Configuration
The auto-refresh is configured in `.cursor/streamlit_app/components/sidebar.py`:
- **Interval**: 2000ms (2 seconds)
- **Enabled by default**: Yes
- **Key**: "auto_refresh_2s"
- **Library**: streamlit-autorefresh

## Troubleshooting

### If Test Fails
1. **Check Streamlit app is running**: Verify `http://localhost:8501` is accessible
2. **Verify auto-refresh is enabled**: Check sidebar shows "✅ Actualisation automatique activée"
3. **Check timer visibility**: Ensure timer component appears on main page
4. **Browser console**: Look for JavaScript errors using `mcp_playwright_browser_console_messages`
5. **Manual verification**: Visit page manually and observe timer increments

### Common Issues
- **Timer not found**: Streamlit app may not be running or timer component missing
- **Timer not incrementing**: Auto-refresh might be disabled or malfunctioning
- **Slow increment**: Network issues or high server load
- **JavaScript errors**: Browser compatibility or library issues

## Files Modified for Testing
1. **`.cursor/streamlit_app/app.py`** - Added timer component
2. **`test_auto_refresh_playwright.py`** - Framework test script
3. **`test_auto_refresh_real_playwright.py`** - Real test implementation
4. **`PLAYWRIGHT_TEST_INSTRUCTIONS.md`** - This documentation

## Test Scripts Available
- **`test_auto_refresh_playwright.py`** - Simulation/framework test
- **`test_auto_refresh_real_playwright.py`** - Real implementation guide
- Both scripts provide validation logic and reporting functions

## Expected Output
```
PLAYWRIGHT AUTO-REFRESH TEST REPORT
==================================================
Timestamp: 2025-07-21 16:32:02
Test Result: PASSED

TIMER ANALYSIS:
  Initial Timer: 3.2 seconds
  Final Timer: 11.8 seconds
  Timer Increase: 8.6 seconds
  Expected Minimum: 6.0 seconds

RESULT: Auto-refresh is working correctly!
RECOMMENDATIONS:
  - No further action required
  - Auto-refresh validated via browser testing
==================================================
```

This comprehensive test validates that the Streamlit auto-refresh functionality works as expected with real browser automation. 