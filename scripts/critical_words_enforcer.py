import sys
import re

CRITICAL_WORDS = ["key", "secret", "password", "token"]

def scan_file_for_critical_words(file_path):
    """Scans a file for critical words."""
    try:
        with open(file_path, "r") as f:
            for line in f:
                # Simple regex to find words, case-insensitive
                if any(re.search(r'\b' + word + r'\b', line, re.IGNORECASE) for word in CRITICAL_WORDS):
                    return True
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        return False
    return False

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file_path> [prompt]")
        sys.exit(1)

    file_to_scan = sys.argv[1]
    # The prompt is passed as the third argument, with a fallback for backward compatibility.
    prompt = sys.argv[2] if len(sys.argv) > 2 else "🚨 High Risk: Potential hardcoded secret detected"

    if scan_file_for_critical_words(file_to_scan):
        print(prompt)

if __name__ == "__main__":
    main()
