import os
import subprocess
import sys

def get_prompt():
    """Reads prompt from custom.txt, fallback to default.txt."""
    try:
        with open("prompt/custom.txt", "r") as f:
            prompt = f.read().strip()
        if prompt:
            return prompt
    except FileNotFoundError:
        pass  # Fallback to default

    # Fallback to default.txt if custom.txt is not found or empty
    with open("prompt/default.txt", "r") as f:
        return f.read().strip()

def get_pr_changes():
    # This is a simplified mock. In a real scenario, you'd use Git commands.
    # For example: git diff --name-only origin/main...HEAD
    # And then for each file: git diff origin/main...HEAD -- a/path/to/file
    return "mock_pr_changes.diff"

def run_static_analysis(file_path, prompt):
    """Runs static analysis tools on the PR changes."""
    print(f"Running static analysis on {file_path}...")
    # In a real CI/CD pipeline, you'd run tools like Bandit, SonarQube, etc.
    # For this example, we'll run our custom critical words enforcer.
    result = subprocess.run(
        ["python", "scripts/critical_words_enforcer.py", file_path, prompt],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

def main():
    pr_changes_file = get_pr_changes()
    # Create a mock diff file for demonstration
    with open(pr_changes_file, "w") as f:
        f.write("""
+ import os
+ GITHUB_API_KEY = \"ghp_1234567890abcdef\" # This is a mock key
- OLD_CODE
""")

    prompt = get_prompt()
    analysis_result = run_static_analysis(pr_changes_file, prompt)

    if analysis_result:
        print("\n--- AI PR Reviewer ---")
        print(analysis_result)
        print("----------------------\n")
        # In a real scenario, you might comment this on the PR.
        # For now, we just print to console.
    else:
        print("\n--- AI PR Reviewer ---")
        print("✅ All checks passed!")
        print("----------------------\n")

    # Clean up mock file
    os.remove(pr_changes_file)

if __name__ == "__main__":
    main()
