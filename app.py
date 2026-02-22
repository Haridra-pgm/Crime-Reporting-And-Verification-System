import subprocess
import sys
import os
import signal

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Run admin app on port 8000
admin_process = subprocess.Popen(
    [sys.executable, "app_admin.py"],
)

# Run public app on port 5000
public_process = subprocess.Popen(
    [sys.executable, "app_public.py"],
)

# Run staff app on port 7000
staff_process = subprocess.Popen(
    [sys.executable, "staff_app.py"],
)

print("All Flask apps have started in the same terminal!")
print("Public App running on http://127.0.0.1:5000")
print("Admin App running on http://127.0.0.1:8000")
print("Staff App running on http://127.0.0.1:7000")

try:
    # Wait for all processes to finis
    admin_process.wait()
    public_process.wait()
    staff_process.wait()

except KeyboardInterrupt:
    print("\nInterrupt received, stopping all Flask and apps...")
    
    # Kill the Flask apps (if running)
    admin_process.terminate()
    public_process.terminate()
    staff_process.terminate()

    # Wait for them to terminate gracefully
    admin_process.wait()
    public_process.wait()
    staff_process.wait()

    print("All apps have been stopped.")
