import argparse
import os
import subprocess
import sqlite3
import time
import threading

from ctf_task import get_pending_tasks, set_in_progress, init_db

DB_FILE = "task_db.sqlite"

def worker_monitor(workspace_dir):
    """
    Background daemon thread that continuously monitors the Task Database
    and spawns Worker Agents when new tasks are created.
    """
    print("[Orchestrator Daemon] Watching for new tasks...")
    while True:
        try:
            pending_tasks = get_pending_tasks(workspace_dir)
            for task_id, description in pending_tasks:
                print(f"\n[Orchestrator Daemon] Detected new pending task #{task_id}.")

                # Lock the task so we don't spawn multiple workers for it
                set_in_progress(task_id, workspace_dir)

                # Spawn a worker agent (e.g., Copilot for quick tasks) in a separate thread/process
                print(f"[Orchestrator Daemon] Spawning Copilot Worker for Task #{task_id}...")

                prompt = (
                    f"You are a Worker Agent. Your task is: {description}\n"
                    f"You have full access to {workspace_dir}.\n"
                    f"When finished, execute: `python ctf_task.py --workspace {workspace_dir} complete {task_id} '[your results]'`"
                )

                # Spawns a dedicated thread for the worker so we can safely use subprocess.run
                # and keep the log file open until the process terminates.
                def run_worker_process(task_id, workspace_dir, prompt):
                    log_file_path = os.path.join(workspace_dir, f"worker_{task_id}.log")
                    # For testing/simulation, we check if an environment variable is set
                    # to use the mock worker, otherwise we use the real wrapper.
                    worker_script = os.getenv("WORKER_SCRIPT", "agents/copilot_wrap.py")

                    with open(log_file_path, "w") as log_file:
                        subprocess.run(
                            ["python", worker_script, prompt],
                            stdout=log_file,
                            stderr=log_file
                        )

                worker_thread = threading.Thread(target=run_worker_process, args=(task_id, workspace_dir, prompt), daemon=True)
                worker_thread.start()
        except sqlite3.OperationalError:
            # Database might be locked briefly, try again later
            pass

        time.sleep(2) # Check every 2 seconds


def start_orchestrator(workspace_dir, category, gemini_model=None, copilot_model=None):
    """
    The main entry point. Initializes the workspace, starts the daemon thread,
    and then spawns the Lead Agent in the foreground.
    """
    if not os.path.exists(workspace_dir):
        print(f"Error: Workspace directory '{workspace_dir}' does not exist.")
        return

    # 1. Initialize the Task DB
    init_db(workspace_dir)
    print(f"[Orchestrator] Initialized Swarm Task DB in {workspace_dir}.")

    # 2. Start the Daemon Watcher
    # Pass models through environment variables
    if gemini_model:
        os.environ["GEMINI_MODEL"] = gemini_model
    if copilot_model:
        os.environ["COPILOT_MODEL"] = copilot_model

    daemon = threading.Thread(target=worker_monitor, args=(workspace_dir,), daemon=True)
    daemon.start()

    # 3. Formulate the initial prompt for the Lead Agent
    files = os.listdir(workspace_dir)
    lead_prompt = (
        f"You are the Lead Investigator for a {category} CTF.\n"
        f"Workspace: {workspace_dir}\n"
        f"Files available: {', '.join(files)}\n"
        f"Goal: Find the flag. You can use native shell commands.\n\n"
        f"SWARM CAPABILITY: If you encounter parallelizable tasks (like fuzzing or deep analysis), "
        f"do NOT do them yourself. Instead, use the task manager: `python ctf_task.py --workspace {workspace_dir} create '[task description]'`.\n"
        f"The orchestrator will spawn a worker. You can check status with `status` and read results with `read <id>`."
    )

    # 4. Spawn the Lead Agent (Foreground process)
    print("\n[Orchestrator] Spawning Lead Agent (Gemini)...")
    try:
        # In a real scenario, this is an interactive session that stays open.
        # For the mock, we just call the script which simulates the interaction.
        subprocess.run(["python", "agents/gemini_wrap.py", lead_prompt])

        # If the orchestrator is run in test mode (no interactive prompt), keep it alive
        # so the daemon thread can process tasks created externally
        if os.getenv("KEEP_ALIVE") == "1":
            print("[Orchestrator] Running in background daemon mode...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Orchestrator] Shutting down.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTF Co-op Solver Orchestrator")
    parser.add_argument("command", choices=["solve"], help="Command to run")
    parser.add_argument("--dir", required=True, help="Path to the challenge workspace directory")
    parser.add_argument("--category", required=True, help="Category of the challenge (e.g., pwn, web)")
    parser.add_argument("--gemini-model", help="Model to use for Gemini Lead Agent")
    parser.add_argument("--copilot-model", help="Model to use for Copilot Worker Agent")

    args = parser.parse_args()

    if args.command == "solve":
        start_orchestrator(args.dir, args.category, args.gemini_model, args.copilot_model)
