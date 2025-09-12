#!/usr/bin/env python3
"""
Test the AI reviewer with real AWS credentials
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_with_real_aws():
    """Test with actual AWS credentials if available."""
    
    # Check for AWS credentials
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    if not aws_key or not aws_secret:
        print("❌ No AWS credentials found. Set these environment variables:")
        print("export AWS_ACCESS_KEY_ID=your_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret")
        return False
    
    try:
        from enhanced_pr_reviewer import EnhancedGitHubPRReviewer
        
        print("🧪 Testing AI with real AWS credentials")
        print("=" * 50)
        
        reviewer = EnhancedGitHubPRReviewer()
        
        # Create a test diff that should trigger AI detection
        test_patch = """@@ -1,3 +1,8 @@
 # Simple test with obvious issues for AI to detect
 import os
 
+#For test
+PASSWORD = "hardcoded123"
+
+def divide(a, b):
+    return a / b"""
        
        print("📄 Test patch:")
        print(test_patch)
        
        # Parse the diff
        added_lines = reviewer.parse_diff_for_line_numbers(test_patch)
        print(f"\n📊 Found {len(added_lines)} changes:")
        for line in added_lines:
            if line['type'] == 'added':
                print(f"  + Line {line['new_line']}: '{line['content']}'")
        
        # Test AI analysis
        filename = "simple_test.py"
        added_only = [line for line in added_lines if line['type'] == 'added']
        
        if added_only:
            print(f"\n🤖 Testing AI analysis on {len(added_only)} added lines...")
            
            # Create prompt
            prompt = reviewer.create_file_analysis_prompt(filename, test_patch, added_only)
            print(f"\n📝 Prompt length: {len(prompt)} characters")
            print("📝 Prompt preview:")
            print(prompt[:500] + "...")
            
            # Get AI response
            try:
                ai_response = reviewer.get_ai_analysis(prompt)
                print(f"\n🤖 AI Response ({len(ai_response)} chars):")
                print(ai_response)
                
                # Parse response
                comments = reviewer.parse_ai_analysis_for_comments(ai_response, filename, added_only)
                print(f"\n💬 Parsed {len(comments)} comments:")
                for i, comment in enumerate(comments, 1):
                    print(f"  {i}. Line {comment['line']}: {comment['body'][:100]}...")
                
                return len(comments) > 0
                
            except Exception as e:
                print(f"❌ AI analysis failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ No added lines found in test patch")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_real_aws()
    if success:
        print("\n✅ AI detection is working!")
    else:
        print("\n❌ AI detection failed!")
    sys.exit(0 if success else 1)