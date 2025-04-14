#!/usr/bin/env python
import sys
import os
import subprocess
import threading
from datetime import datetime
import logging
from flask import Flask, render_template, request, jsonify

# Initialize the Flask app (this is the admin dashboard)
app = Flask(__name__)
app.secret_key = "replace-with-your-secure-secret-key"  # Change this to a secure value

# Global variables for managing the main application process and logs
app.config['APP_RUNNING'] = False
main_app_logs = []  # List to store log lines
app_process = None  # Will hold the subprocess.Popen object

# Ensure we have the correct Python executable
PYTHON_EXEC = sys.executable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AdminDashboard")

# Helper function: Continuously capture stdout from the main app process
def capture_app_logs(process):
    while True:
        line = process.stdout.readline()
        if not line:
            break
        main_app_logs.append(line.rstrip())
    app.config['APP_RUNNING'] = False
    logger.info("Main app process ended.")

# ----------------------------
# Routes for the Admin Dashboard
# ----------------------------

@app.route("/")
def admin_dashboard():
    # Render your admin dashboard (home.html should be in the templates folder)
    return render_template("home.html")

@app.route("/admin/start", methods=["POST"])
def admin_start():
    global app_process
    if not app.config['APP_RUNNING']:
        try:
            # Use Waitress to run the main app instead of running app.py directly.
            # This avoids issues with the debug reloader.
            cmd = [
                PYTHON_EXEC, "-u", "-m", "waitress",
                "--host=127.0.0.1",
                "--port=5000",
                "app:app"
            ]
            # Spawn the process; capture its stdout and stderr.
            app_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            app.config['APP_RUNNING'] = True
            main_app_logs.append(f"{datetime.now()} - Main app started via Waitress.")
            threading.Thread(target=capture_app_logs, args=(app_process,), daemon=True).start()
            logger.info("Main app has been started via Waitress.")
            return jsonify({'status': 'started'}), 200
        except Exception as e:
            logger.error(f"Error starting main app: {str(e)}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'already_running'}), 200

@app.route("/admin/stop", methods=["POST"])
def admin_stop():
    global app_process
    if app.config['APP_RUNNING'] and app_process:
        try:
            app_process.terminate()  # Attempt graceful shutdown
            app_process.wait(timeout=10)
            app.config['APP_RUNNING'] = False
            main_app_logs.append(f"{datetime.now()} - Main app stopped.")
            logger.info("Main app has been stopped.")
            return jsonify({'status': 'stopped'}), 200
        except Exception as e:
            logger.error(f"Error stopping main app: {str(e)}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'not_running'}), 200
    
@app.route('/admin/status')
def admin_status():
    # Return the running status as a JSON object.
    return jsonify({"running": app.config['APP_RUNNING']})


@app.route("/admin/logs_data")
def logs_data():
    # Returns the logs as plain text so the admin page can poll and display them.
    return "\n".join(main_app_logs)

if __name__ == "__main__":
    # Run the admin dashboard on port 5001 (or change to your desired port)
    app.run(debug=True, host="127.0.0.1", port=5001)
