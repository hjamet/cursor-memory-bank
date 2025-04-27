import sys
import time

# Remove delay - testing fast script output capture
# time.sleep(3) 

if len(sys.argv) > 1:
    print(f"Argument received: {sys.argv[1]}")
else:
    print("No argument received.") 