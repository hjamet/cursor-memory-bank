# Emergency Brake Recovery Procedure

## Context
Cette procédure documente la résolution du problème de boucle infinie context-update causé par l'activation de l'Emergency Brake du système de sécurité workflow.

## Problem Analysis
- **Symptom**: Workflow bloqué dans une boucle infinie context-update → context-update
- **Root Cause**: Emergency Brake système activé après dépassement de 50 transitions consécutives
- **Files Affected**: `.cursor/memory-bank/workflow/workflow_safety.json`

## Diagnostic Commands
```bash
# Check emergency brake status
cat ".cursor/memory-bank/workflow/workflow_safety.json"

# Look for:
# - "consecutive_transitions": > 50
# - "emergency_brake_active": true
# - Many "BLOCKED_context-update_TO_context-update" entries
```

## Recovery Procedure

### 1. Create Backup
```bash
cp ".cursor/memory-bank/workflow/workflow_safety.json" ".cursor/memory-bank/workflow/workflow_safety.json.backup"
```

### 2. Reset Emergency Brake
Create new workflow_safety.json with:
```json
{
  "transition_history": [
    {
      "from": "system",
      "to": "emergency_brake_reset",
      "timestamp": "2025-07-14T18:50:00.000Z"
    }
  ],
  "experience_execution_attempts": 0,
  "last_experience_execution": "2025-07-14T10:37:19.120Z",
  "last_implementation": "2025-07-14T18:50:00.000Z",
  "consecutive_transitions": 1,
  "emergency_brake_active": false
}
```

### 3. Verify Anti-Loop Protections Remain
```bash
# Verify task #317 protections in workflow_recommendation.js
grep -n "CRITICAL FIX: Prevent context-update loops" .cursor/mcp/memory-bank-mcp/lib/workflow_recommendation.js

# Verify task #318 optimizations in remember.js
grep -n "limited to 5 for performance" .cursor/mcp/memory-bank-mcp/mcp_tools/remember.js
```

### 4. Test Workflow Operation
The workflow should now operate normally without entering context-update loops.

## Validation Checklist
- [ ] Emergency brake deactivated (`emergency_brake_active: false`)
- [ ] Consecutive transitions reset to low number (< 5)
- [ ] Backup of original state created
- [ ] Anti-loop protections from tasks #317/#318 preserved
- [ ] Workflow operates without loops

## Prevention
- Monitor `consecutive_transitions` count periodically
- Ensure anti-loop protections remain in place
- Regular workflow health checks

## Applied To
- **Repository**: trail-rag (C:\Users\Jamet\code\trail-rag)
- **Date**: 2025-07-14
- **Task**: #321 - Fix persistent context-update loop problem

## Related Tasks
- Task #317: Anti-loop protections in workflow_recommendation.js
- Task #318: Remember tool optimization  
- Task #320: Diagnostic analysis of persistent loop problem 