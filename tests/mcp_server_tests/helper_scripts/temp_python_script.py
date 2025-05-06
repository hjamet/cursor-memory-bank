import time
import signal
import sys
import os

shutdown_message = ""

def graceful_shutdown(signum, frame):
    global shutdown_message
    print(f"Python script (PID: {os.getpid()}) received signal {signum}. Shutting down gracefully.")
    sys.stdout.flush()
    shutdown_message = "GRACEFUL_SHUTDOWN"
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

print(f"Python script (PID: {os.getpid()}) starting. Will run for approx 40 seconds.")
sys.stdout.flush()

for i in range(40):
    if shutdown_message:
        break
    print(f"Python script (PID: {os.getpid()}) alive, iteration {i+1}/40")
    sys.stdout.flush()
    time.sleep(1)

if not shutdown_message:
    print(f"Python script (PID: {os.getpid()}) completed normally without interruption.")
    sys.stdout.flush()
    shutdown_message = "NORMAL_COMPLETION"

# This final print might not be reached if killed forcefully by SIGKILL
# but is useful if it exits via sys.exit(0) in the handler.
print(f"Python script (PID: {os.getpid()}) final status: {shutdown_message}")
sys.stdout.flush() 