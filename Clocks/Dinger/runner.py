import subprocess
import time
import os
import signal

def start_process(command):
    return subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

def is_process_running(process):
    return process.poll() is None

def stop_process(process):
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

# Commands to start Python and React apps
python_app_command = 'python dinger.py'
react_app_command = 'npm start --prefix taskmaster'

# Start the Python Flask app and the React app
python_process = start_process(python_app_command)
react_process = start_process(react_app_command)

try:
    while True:
        # Check every 30 seconds
        time.sleep(30)

        # Restart Python app if it has stopped
        if not is_process_running(python_process):
            print("Python app stopped. Restarting...")
            python_process = start_process(python_app_command)

        # Restart React app if it has stopped
        if not is_process_running(react_process):
            print("React app stopped. Restarting...")
            react_process = start_process(react_app_command)

except KeyboardInterrupt:
    print("Stopping applications...")
    stop_process(python_process)
    stop_process(react_process)
    print("Applications stopped.")