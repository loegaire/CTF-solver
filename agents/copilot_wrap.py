import sys
import subprocess
import os
import re

def run_copilot(prompt):
    """
    Generic wrapper for gh copilot cli.
    It takes the prompt from the orchestrator, runs the actual CLI tool natively,
    and returns the output.
    """
    print(f"[Copilot Wrap Worker] Running gh copilot with prompt...")

    try:
        # Assuming `gh copilot suggest -t script "<prompt>"` or similar
        # We use a placeholder for the actual command.

        # We need to extract the task_id and workspace from the prompt
        # to ensure the worker can automatically run the completion command.
        # The orchestrator formats the prompt as:
        # "You are a Worker Agent. Your task is: [desc]\nYou have full access to [workspace].\nWhen finished, execute: `python ctf_task.py --workspace [workspace] complete [task_id] '[your results]'`"

        # This wrapper should ideally just pass the raw prompt to the LLM and let it execute the python command.
        # However, `gh copilot suggest` only suggests commands, it doesn't run them autonomously.
        # If we expect Copilot to run commands autonomously, we would need a more complex interactive wrapper
        # that parses its suggestions and executes them, or we treat Copilot strictly as an analyzer.

        # For this generic wrapper, we'll just pass the prompt to the CLI.
        # If the user's Copilot setup is autonomous, it will handle it.

        result = subprocess.run(
            ["gh", "copilot", "suggest", "-t", "script", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)

    except FileNotFoundError:
        print("[Copilot Wrap Error] 'gh' command not found. Please ensure GitHub CLI and Copilot extension are installed.")
        print(f"[Simulated Output for Prompt]: {prompt}")
    except subprocess.CalledProcessError as e:
        print(f"[Copilot Wrap Error] gh copilot failed with error: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python copilot_wrap.py '<prompt>'")
        sys.exit(1)

    prompt = sys.argv[1]
    run_copilot(prompt)
