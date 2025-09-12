#!/usr/bin/env python3
"""
Quick test to debug the AI reviewer
"""

import os
import sys
import json
from pathlib import Path

# Set up environment for testing
os.environ['AWS_ACCESS_KEY_ID'] = 'test'  # You'll need real AWS credentials
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'

sys.path.append(str(Path(__file__).parent))

from enhanced_pr_reviewer import EnhancedGitHubPRReviewer

def test_diff_parsing():
    """Test the diff parsing functionality."""
    print("🧪 Testing Diff Parsing")
    print("=" * 30)
    
    reviewer = EnhancedGitHubPRReviewer()
    
    # Test diff with comment issues
    sample_diff = """@@ -3,6 +3,7 @@ GitHub Pull Request Diff Reviewer using AWS Bedrock
 Reviews only the changed code in GitHub Pull Requests.
 \"\"\"
 
+#For test
 def unsafe_function():
     password = "hardcoded123"
     return password"""
    
    print("📄 Sample diff:")
    print(sample_diff)
    
    # Parse the diff
    changes = reviewer.parse_diff_for_line_numbers(sample_diff)
    print(f"\n📊 Parsed {len(changes)} line changes:")
    for change in changes:
        if change['type'] == 'added':
            print(f"  Added Line {change['new_line']}: '{change['content']}'")
    
    return changes

def test_ai_prompt():
    """Test the AI prompt generation."""
    print("\n🤖 Testing AI Prompt")
    print("=" * 30)
    
    reviewer = EnhancedGitHubPRReviewer()
    
    added_lines = [
        {'new_line': 6, 'content': '#For test', 'type': 'added'},
        {'new_line': 8, 'content': '    password = "hardcoded123"', 'type': 'added'}
    ]
    
    prompt = reviewer.create_file_analysis_prompt('test.py', '#For test\npassword = "hardcoded123"', added_lines)
    print("Generated prompt:")
    print(prompt[:500] + "...")
    
    return prompt

if __name__ == "__main__":
    try:
        changes = test_diff_parsing()
        prompt = test_ai_prompt()
        
        print(f"\n✅ Found {len([c for c in changes if c['type'] == 'added'])} added lines to analyze")
        print("✅ AI prompt generated successfully")
        
        print("\n💡 The issue might be:")
        print("1. AWS credentials not properly configured")
        print("2. AI model not detecting the comment issues") 
        print("3. GitHub API not posting the suggestions correctly")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()