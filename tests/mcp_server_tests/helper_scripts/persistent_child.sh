#!/bin/bash
# tests/helper_scripts/persistent_child.sh

CHILD_LOG_FILE="persistent_child_active.log"

echo "Parent script (PID: $$) starting..."

# Start a child process that runs for a while
( 
  echo "Child process (PID: $$) started at $(date) and will sleep for 20s."
  sleep 20 
  echo "Child process (PID: $$) finished sleep at $(date)."
  # On normal exit, remove the log file. If killed, it remains.
  # However, SIGKILL won't allow this trap to run.
  # The existence of the file post-kill is not a reliable indicator for SIGKILL.
  # The purpose of this script is just to have a child process running.
) &

CHILD_SCRIPT_PID=$!
echo "PARENT_SCRIPT_PID_MARKER:$$"
echo "CHILD_PROCESS_PID_MARKER:$CHILD_SCRIPT_PID" # This is the PID of the subshell/backgrounded group

echo "Parent script (PID: $$) started child process group $CHILD_SCRIPT_PID."
echo "Parent script (PID: $$) will now also sleep for 20s."
echo "Parent: before sleep 20"
sleep 20
S_EXIT_CODE=$?
echo "Parent: after sleep 20 (exit code: $S_EXIT_CODE)"

echo "Parent script (PID: $$) finished." 