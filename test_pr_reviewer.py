#!/usr/bin/env python3
"""
Simple test for PR reviewer functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pr_reviewer import GitHubPRReviewer

def test_pr_extraction():
    """Test PR URL extraction"""
    reviewer = GitHubPRReviewer()
    
    test_url = "https://github.com/Jaimin7364/simple-review/pull/1"
    pr_info = reviewer.extract_pr_info(test_url)
    
    print("🧪 Testing PR URL extraction:")
    print(f"URL: {test_url}")
    print(f"Extracted info: {pr_info}")
    
    if pr_info:
        print("✅ PR extraction successful!")
        return pr_info
    else:
        print("❌ PR extraction failed!")
        return None

def test_metadata_fetch(pr_info):
    """Test metadata fetching"""
    reviewer = GitHubPRReviewer()
    
    print("\n🧪 Testing metadata fetch:")
    metadata = reviewer.get_pr_metadata(pr_info)
    
    if metadata:
        print("✅ Metadata fetch successful!")
        print(f"Title: {metadata.get('title')}")
        print(f"Author: {metadata.get('author')}")
        print(f"Files: {metadata.get('files_changed')}")
        return metadata
    else:
        print("❌ Metadata fetch failed!")
        return None

def test_diff_fetch(pr_info):
    """Test diff fetching"""
    reviewer = GitHubPRReviewer()
    
    print("\n🧪 Testing diff fetch:")
    diff = reviewer.get_pr_diff(pr_info)
    
    if diff:
        print("✅ Diff fetch successful!")
        print(f"Diff length: {len(diff)} characters")
        print("First 200 characters:")
        print(diff[:200] + "...")
        return diff
    else:
        print("❌ Diff fetch failed!")
        return None

if __name__ == "__main__":
    print("🧪 PR Reviewer Component Tests")
    print("=" * 40)
    
    # Test 1: URL extraction
    pr_info = test_pr_extraction()
    if not pr_info:
        sys.exit(1)
    
    # Test 2: Metadata fetch
    metadata = test_metadata_fetch(pr_info)
    if not metadata:
        sys.exit(1)
    
    # Test 3: Diff fetch
    diff = test_diff_fetch(pr_info)
    if not diff:
        sys.exit(1)
    
    print("\n🎉 All component tests passed!")
    print("The issue might be in the AI analysis or file saving step.")
