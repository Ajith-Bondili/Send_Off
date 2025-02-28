#!/usr/bin/env python3

### Configuration
# Logging Options
LOG = True
LOG_FILE = "commit_bot.log"

# Commit Options
NO_COMMIT_CHANCE = 0 # 0% chance of NOT committing to GitHub.
MAX_COMMITS = 10 #Maximum number of commits that can be made.

# Cron job.
CRON_JOB_TIME = "*/15 9-5 * * *" # Every 15 minutes between 12PM-6PM

# Output Filer
OUTPUT_FILE = "commit_bot.txt"

# Git configuration
GIT_CONFIG = "GIT_SSH_COMMAND=\"ssh -i ~/.ssh/id_rsa -o IdentitiesOnly=yes\"\n"

# Imports
from sys import argv
from pathlib import Path
from os import system # Executing the Git commands.
from random import random, randint # Generating a random float between 0 and 1.
from datetime import datetime # Date and time for our file.
import subprocess

# Check if a cronjob exists for this script, if not, create it using crontab.
system("crontab -l > cron.txt")
with open("cron.txt", "r") as f:
    if "commit_bot.py" not in f.read():
        with open("cron.txt", "a") as f:
            f.write(f"{GIT_CONFIG}{CRON_JOB_TIME} cd {Path.cwd()} && python3 commit_bot.py\n")
            f.close()
            system("crontab cron.txt")
            system("rm -f cron.txt")
    else:
        f.close()
        system("rm -f cron.txt")

# Logging.
def log(message):
    if LOG:
        with open(LOG_FILE, "a") as f:
            f.write(f"{message}\n")
            f.close()

# Create our commit.
def create_commit():
    # Assumes commit_bot.py is in the root of the git repo.
    # Path.cwd() should be correctly set by the 'cd' command in the cron job line.
    repo_cwd = Path.cwd()

    output_file_path = repo_cwd / OUTPUT_FILE
    with open(output_file_path, "w") as f:
        f.write(str(datetime.now()))
        f.close()

    # Git add
    # OUTPUT_FILE is relative to the repo_cwd
    add_cmd = ["/usr/bin/git", "add", OUTPUT_FILE]
    log(f"Attempting: {' '.join(add_cmd)} in {str(repo_cwd)}")
    add_result = subprocess.run(add_cmd, capture_output=True, text=True, cwd=repo_cwd)
    if add_result.returncode != 0:
        log(f"Git add FAILED. RC: {add_result.returncode}.")
        if add_result.stdout: log(f"Git add stdout: {add_result.stdout.strip()}")
        if add_result.stderr: log(f"Git add stderr: {add_result.stderr.strip()}")
        return
    log(f"Git add successful for {OUTPUT_FILE}.")

    # Git commit
    commit_msg = f"Update {OUTPUT_FILE}"
    commit_cmd = ["/usr/bin/git", "commit", "-m", commit_msg]
    log(f"Attempting: {' '.join(commit_cmd)} in {str(repo_cwd)}")
    commit_result = subprocess.run(commit_cmd, capture_output=True, text=True, cwd=repo_cwd)

    if commit_result.returncode == 0:
        # Successful commit usually has output, log it.
        if commit_result.stdout:
            log(f"Git commit successful: {commit_result.stdout.strip()}")
        else:
            log("Git commit successful (no specific stdout message).")
    else:
        # Check if it's "nothing to commit"
        is_nothing_to_commit = "nothing to commit" in commit_result.stdout.lower() or \
                               "nothing to commit" in commit_result.stderr.lower()
        if is_nothing_to_commit:
            log("Nothing to commit. Skipping push.")
            if commit_result.stdout: log(f"Commit stdout (nothing to commit): {commit_result.stdout.strip()}")
            if commit_result.stderr: log(f"Commit stderr (nothing to commit): {commit_result.stderr.strip()}")
            return
        else:
            # Other commit error
            log(f"Git commit FAILED. RC: {commit_result.returncode}.")
            if commit_result.stdout: log(f"Git commit stdout: {commit_result.stdout.strip()}")
            if commit_result.stderr: log(f"Git commit stderr: {commit_result.stderr.strip()}")
            return

    # Git push
    push_cmd = ["/usr/bin/git", "push"]
    log(f"Attempting: {' '.join(push_cmd)} in {str(repo_cwd)}")
    # The GIT_SSH_COMMAND is set in the crontab line and should be inherited by subprocess.
    push_result = subprocess.run(push_cmd, capture_output=True, text=True, cwd=repo_cwd)

    if push_result.returncode == 0:
        log("Git push successful.")
        if push_result.stdout: log(f"Git push stdout: {push_result.stdout.strip()}")
        # stderr might contain non-fatal warnings from push (e.g. about default branch policy or refs)
        if push_result.stderr: log(f"Git push stderr (might be non-fatal): {push_result.stderr.strip()}")
    else:
        log(f"Git push FAILED. RC: {push_result.returncode}")
        if push_result.stdout: log(f"Git push stdout: {push_result.stdout.strip()}")
        if push_result.stderr: log(f"Git push stderr: {push_result.stderr.strip()}")

# Check if already committed today
def already_committed_today():
    # Check git log for commits from today
    today = datetime.now().strftime('%Y-%m-%d')
    result = system(f'/usr/bin/git log --since="{today} 00:00:00" --pretty=format:"%h" > /tmp/commit_check')
    
    with open('/tmp/commit_check', 'r') as f:
        content = f.read().strip()
    
    system('rm -f /tmp/commit_check')
    return len(content) > 0
    
# Execute the script.
if not already_committed_today() and (random() > NO_COMMIT_CHANCE):
    commits = randint(1, MAX_COMMITS)
    for i in range(commits):
        create_commit()
    log(f"[{datetime.now()}] Successfully committed {commits} time(s).")
else:
    if already_committed_today():
        log(f"[{datetime.now()}] Already committed today. Skipping.")
    else:
        log(f"[{datetime.now()}] No commits were made due to random chance.")