#!/usr/bin/env python3
"""
Test script for the Enhanced GitHub PR Reviewer
"""

import os
import sys
from pathlib import Path

# Add current directory to path so we can import our reviewer
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_pr_reviewer import EnhancedGitHubPRReviewer
except ImportError:
    print("❌ Could not import enhanced_pr_reviewer. Make sure the file exists.")
    sys.exit(1)

def test_enhanced_reviewer():
    """Test the enhanced reviewer functionality."""
    print("🧪 Testing Enhanced GitHub PR Reviewer")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Set these before running the test:")
        for var in missing_vars:
            print(f"export {var}=your_value")
        return False
    
    # Optional: Check GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("⚠️ No GITHUB_TOKEN found. Reviews will be generated but not posted.")
    else:
        print("✅ GitHub token found - reviews will be posted to GitHub")
    
    try:
        # Initialize the reviewer
        reviewer = EnhancedGitHubPRReviewer()
        print("✅ Enhanced reviewer initialized successfully!")
        
        # Test with a sample PR URL (you can change this to any real PR)
        test_pr_url = input("\n🔗 Enter a GitHub PR URL to test (or press Enter for demo): ").strip()
        
        if not test_pr_url:
            print("📋 Using demo mode - showing reviewer capabilities...")
            
            # Demo the diff parsing functionality
            sample_diff = """@@ -1,3 +1,6 @@
+import os
+password = "hardcoded123"  # Security issue
+
 def calculate(a, b):
-    return a / b
+    if b == 0:
+        return None
+    return a / b"""
            
            print("\n📄 Sample diff analysis:")
            print(sample_diff)
            
            # Parse the diff
            changes = reviewer.parse_diff_for_line_numbers(sample_diff)
            print(f"\n📊 Parsed {len(changes)} line changes:")
            for change in changes[:5]:  # Show first 5
                print(f"  {change['type']}: Line {change.get('new_line', change.get('old_line', 'N/A'))}: {change['content'][:50]}...")
            
            print("\n✅ Demo completed successfully!")
            return True
        else:
            # Test with real PR
            print(f"\n🔍 Testing with PR: {test_pr_url}")
            success = reviewer.review_pull_request(test_pr_url)
            
            if success:
                print("\n🎉 Test completed successfully!")
                if github_token:
                    print("💬 Check the PR for inline comments!")
                return True
            else:
                print("\n❌ Test failed!")
                return False
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

def create_test_file():
    """Create a test file with various code issues for testing."""
    test_content = '''# hello test
"""
Test file for AI code review
This file contains various issues that should be detected by the AI reviewer
"""

import os
import subprocess

# Security issue: hardcoded password
PASSWORD = "secret123"
API_KEY = "abcd1234"

def unsafe_sql_query(user_input):
    """Function with SQL injection vulnerability"""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def divide_numbers(a, b):
    """Function without error handling"""
    return a / b  # Division by zero possible

def execute_command(user_input):
    """Command injection vulnerability"""
    os.system(f"ls {user_input}")

def inefficient_loop():
    """Performance issue"""
    result = []
    for i in range(1000):
        for j in range(1000):
            result.append(i * j)
    return result

class BadClass:
    """Class with various issues"""
    
    def __init__(self):
        self.data = None
    
    def process_data(self, data):
        # No validation
        self.data = data
        return self.data.upper()  # Potential AttributeError

def main():
    """Main function"""
    # Using deprecated function
    user_name = input("Enter name: ")
    result = unsafe_sql_query(user_name)
    print(result)

if __name__ == "__main__":
    main()
'''
    
    test_file_path = Path("test_file_for_ai_review.py")
    test_file_path.write_text(test_content)
    print(f"✅ Created test file: {test_file_path}")
    print("💡 You can now commit this file and create a PR to test the AI reviewer!")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Enhanced GitHub PR Reviewer")
    parser.add_argument("--create-test-file", action="store_true", help="Create a test file with code issues")
    parser.add_argument("--pr-url", help="Test with specific PR URL")
    
    args = parser.parse_args()
    
    if args.create_test_file:
        create_test_file()
        return
    
    if args.pr_url:
        os.environ.setdefault('TEST_PR_URL', args.pr_url)
    
    success = test_enhanced_reviewer()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()