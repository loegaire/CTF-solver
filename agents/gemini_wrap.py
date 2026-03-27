import sys
import subprocess
import os

def run_gemini(prompt):
    """
    Generic wrapper for geminicli.
    It takes the prompt from the orchestrator, runs the actual CLI tool natively,
    and returns the output.
    """
    print(f"[Gemini Wrap] Running geminicli with prompt...")
    try:
        # In a real setup, this runs the actual geminicli command.
        # Assuming the CLI takes the prompt as a command-line argument or via stdin.
        # Example: geminicli prompt "<prompt>"

        # We use a placeholder here for the actual CLI invocation,
        # but it should be replaced with the exact command for the user's setup.
        # For safety in this environment if the tool isn't installed, we'll try to execute it,
        # and fallback gracefully if it's not found.

        result = subprocess.run(
            ["geminicli", "prompt", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)

    except FileNotFoundError:
        print("[Gemini Wrap Error] 'geminicli' command not found. Please ensure it is installed and in your PATH.")
        # Fallback for demonstration/simulation if the user runs this without the tool installed
        print(f"[Simulated Output for Prompt]: {prompt}")
    except subprocess.CalledProcessError as e:
        print(f"[Gemini Wrap Error] geminicli failed with error: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gemini_wrap.py '<prompt>'")
        sys.exit(1)

    prompt = sys.argv[1]
    run_gemini(prompt)
