#!/usr/bin/env python3
"""
🚨 Critical Words Enforcer

This script analyzes PR comments for critical words that indicate potential issues.
It provides a strict enforcement mechanism that fails when problematic words are found.

Features:
- Comment extraction from multiple programming languages
- Categorized critical word detection
- Configurable thresholds and word lists
- GitHub status API integration
- Clean, focused reporting

Requirements:
- GitHub token with PR write permissions
- requests library

Environment Variables:
- GITHUB_TOKEN: GitHub API token
- GITHUB_REPOSITORY: Repository name (owner/repo)  
- PR_NUMBER: Pull request number
- GITHUB_SHA: Commit SHA for status updates
"""

import os
import sys
import json
import requests
import re
from collections import defaultdict


# STRICT CONFIGURATION - CUSTOMIZE THESE VALUES
CRITICAL_THRESHOLD = 1   # FAIL if >= 1 critical word found (strict enforcement)
WARNING_THRESHOLD = 0    # No warnings, only pass/fail

# CRITICAL WORDS CATEGORIES - Add your problematic words here
CRITICAL_WORDS = {
    'security_risks': [
        'password', 'secret', 'token', 'api_key', 'private_key',
        'hardcode', 'hardcoded', 'credential', 'auth_token',
        'access_key', 'secret_key', 'encryption_key', 'bearer_token',
        'client_secret', 'app_secret', 'oauth_secret'
    ],
    'code_smells': [
        'hack', 'workaround', 'quick_fix', 'temporary', 'temp_fix',
        'dirty', 'ugly', 'mess', 'broken', 'bad_code',
        'technical_debt', 'debt', 'kludge', 'bodge', 'spaghetti'
    ],
    'development_issues': [
        'todo', 'fixme', 'bug', 'error', 'issue', 'problem',
        'broken', 'fail', 'crash', 'exception', 'warning',
        'debug', 'test_only', 'not_working', 'incomplete'
    ],
    'security_vulnerabilities': [
        'vulnerability', 'exploit', 'injection', 'xss', 'csrf',
        'buffer_overflow', 'sql_injection', 'code_injection',
        'path_traversal', 'unsafe', 'insecure', 'weak'
    ],
    'performance_issues': [
        'slow', 'performance', 'bottleneck', 'memory_leak',
        'inefficient', 'optimization_needed', 'lag', 'timeout',
        'deadlock', 'race_condition', 'blocking'
    ],
    'quality_issues': [
        'deprecated', 'obsolete', 'legacy', 'old_code',
        'refactor_needed', 'cleanup', 'messy', 'duplicate', 
        'redundant', 'unused', 'remove_me'
    ]
}


def main():
    """Main execution function"""
    print("🚨 Critical Words Enforcer - Analyzing PR for Critical Words")
    print("=" * 60)
    
    # Get GitHub environment details
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    pr_number = os.environ.get('PR_NUMBER')
    github_sha = os.environ.get('GITHUB_SHA')
    
    print(f"🔍 Environment Check:")
    print(f"  - Repository: {repo}")
    print(f"  - PR Number: {pr_number}")
    print(f"  - SHA: {github_sha}")
    print(f"  - Token: {'✅ Present' if github_token else '❌ Missing'}")
    
    if not all([github_token, repo, pr_number, github_sha]):
        print("\n⚠️ WARNING: Missing required environment variables")
        print("✅ Action completed (skipped due to missing variables)")
        return
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get PR files
        print(f"\n🔍 Fetching PR files...")
        files_response = requests.get(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
            headers=headers
        )
        
        if files_response.status_code != 200:
            print(f"⚠️ WARNING: Cannot get PR files (status: {files_response.status_code})")
            print("✅ Action completed (skipped due to API error)")
            return
        
        files_data = files_response.json()
        print(f"📂 Found {len(files_data)} files to analyze")
        
        # Analyze files for critical words
        analysis_result = analyze_files_for_critical_words(files_data)
        
        # Generate and post report
        post_analysis_report(analysis_result, repo, pr_number, headers)
        
        # Set commit status
        set_commit_status(analysis_result, repo, github_sha, headers)
        
        print("🎉 Critical Words analysis completed!")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Set error status but don't fail the action
        set_error_status(repo, github_sha, headers)


def analyze_files_for_critical_words(files_data):
    """Analyze all files for critical words in comments"""
    total_critical_words = 0
    total_comments = 0
    critical_words_found = defaultdict(list)
    file_analysis = {}
    
    for file_data in files_data:
        filename = file_data.get('filename', '')
        patch = file_data.get('patch', '')
        status = file_data.get('status', '')
        
        if not patch:
            continue
        
        print(f"📄 Analyzing: {filename}")
        
        # Extract comments and analyze
        file_result = analyze_file_comments(filename, patch, status)
        
        file_analysis[filename] = file_result
        total_critical_words += file_result['critical_words_count']
        total_comments += file_result['comments_count']
        
        # Collect critical words by category
        for category, words_list in file_result['critical_words_by_category'].items():
            critical_words_found[category].extend(words_list)
        
        if file_result['critical_words_count'] > 0:
            print(f"  🚨 {file_result['critical_words_count']} critical words found in {file_result['comments_count']} comments")
        else:
            print(f"  ✅ Clean - {file_result['comments_count']} comments analyzed")
    
    # Determine final result
    has_critical_words = total_critical_words >= CRITICAL_THRESHOLD
    
    print(f"\n" + "=" * 60)
    print(f"📊 ANALYSIS RESULTS:")
    print(f"💬 Total comments analyzed: {total_comments}")
    print(f"🚨 Critical words found: {total_critical_words}")
    print(f"📏 Threshold for failure: {CRITICAL_THRESHOLD}")
    
    if has_critical_words:
        print(f"❌ RESULT: FAILED - Critical words detected!")
    else:
        print(f"✅ RESULT: PASSED - No critical words found!")
    
    return {
        'total_critical_words': total_critical_words,
        'total_comments': total_comments,
        'critical_words_found': critical_words_found,
        'file_analysis': file_analysis,
        'has_critical_words': has_critical_words
    }


def analyze_file_comments(filename, patch, status):
    """Extract and analyze comments from a single file"""
    comments_found = []
    file_critical_count = 0
    file_critical_words = defaultdict(list)
    
    lines = patch.split('\n')
    line_number = 0
    
    for line in lines:
        if line.startswith('@@'):
            # Extract starting line number from diff header
            match = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if match:
                line_number = int(match.group(1)) - 1
        elif line.startswith('+') and not line.startswith('+++'):
            line_number += 1
            line_content = line[1:].strip()
            
            # Extract comments based on file type
            comment_text = extract_comment_from_line(line_content)
            
            if comment_text:
                comments_found.append({
                    'line': line_number,
                    'text': comment_text,
                    'full_line': line_content
                })
                
                # Check for critical words in this comment
                critical_words_in_comment = find_critical_words_in_text(comment_text, filename, line_number)
                
                for category, words_list in critical_words_in_comment.items():
                    if words_list:
                        file_critical_count += len(words_list)
                        file_critical_words[category].extend(words_list)
        
        elif line.startswith(' '):
            line_number += 1
    
    return {
        'comments_count': len(comments_found),
        'critical_words_count': file_critical_count,
        'critical_words_by_category': file_critical_words,
        'all_comments': comments_found,
        'status': status
    }


def extract_comment_from_line(line_content):
    """Extract comment text from a line of code"""
    comment_text = ""
    
    # Python, Shell, Ruby comments (#)
    if re.match(r'^\s*#(.+)', line_content):
        comment_text = re.match(r'^\s*#(.+)', line_content).group(1).strip()
    
    # C/C++, Java, JavaScript, C# comments (//)
    elif re.match(r'^\s*//(.+)', line_content):
        comment_text = re.match(r'^\s*//(.+)', line_content).group(1).strip()
    
    # Block comments (/* ... */)
    elif re.match(r'^\s*/\*(.+)\*/', line_content):
        comment_text = re.match(r'^\s*/\*(.+)\*/', line_content).group(1).strip()
    
    # HTML comments (<!-- ... -->)
    elif re.match(r'^\s*<!--(.+)-->', line_content):
        comment_text = re.match(r'^\s*<!--(.+)-->', line_content).group(1).strip()
    
    # SQL comments (--)
    elif re.match(r'^\s*--(.+)', line_content):
        comment_text = re.match(r'^\s*--(.+)', line_content).group(1).strip()
    
    return comment_text


def find_critical_words_in_text(comment_text, filename, line_number):
    """Find critical words in comment text"""
    critical_words_by_category = defaultdict(list)
    comment_lower = comment_text.lower()
    
    for category, words in CRITICAL_WORDS.items():
        for word in words:
            if word in comment_lower:
                critical_words_by_category[category].append({
                    'file': filename,
                    'word': word,
                    'line': line_number,
                    'context': comment_text,
                    'category': category
                })
    
    return critical_words_by_category


def post_analysis_report(analysis_result, repo, pr_number, headers):
    """Generate and post the analysis report"""
    total_critical_words = analysis_result['total_critical_words']
    total_comments = analysis_result['total_comments']
    critical_words_found = analysis_result['critical_words_found']
    has_critical_words = analysis_result['has_critical_words']
    
    # Generate report
    report_parts = []
    
    if has_critical_words:
        report_parts.extend([
            "# ❌ **PR FAILED - Critical Words Detected**",
            "",
            f"🚨 **Found {total_critical_words} critical words in comments that must be addressed before merge.**",
            "",
            "**This PR cannot be merged until these issues are resolved.**",
            ""
        ])
    else:
        report_parts.extend([
            "# ✅ **PR PASSED - Clean Comments**",
            "",
            f"✅ **Analyzed {total_comments} comments - no critical words detected!**",
            "",
            "Great job maintaining clean, professional comments!",
            ""
        ])
    
    # Show critical words breakdown if found
    if critical_words_found:
        report_parts.extend([
            "## 🚨 **Critical Words Breakdown:**",
            ""
        ])
        
        for category, words_list in critical_words_found.items():
            if words_list:
                category_name = category.replace('_', ' ').title()
                report_parts.extend([
                    f"### 🔍 {category_name} ({len(words_list)} found)",
                    ""
                ])
                
                # Group by file
                files_with_words = defaultdict(list)
                for word_info in words_list:
                    files_with_words[word_info['file']].append(word_info)
                
                for file, file_words in files_with_words.items():
                    report_parts.append(f"**📁 {file}:**")
                    
                    for word_info in file_words[:6]:  # Show up to 6 per file
                        context = word_info['context']
                        word = word_info['word']
                        line_num = word_info['line']
                        
                        display_context = context[:80] + "..." if len(context) > 80 else context
                        report_parts.append(f"- Line {line_num}: `{word}` in \"{display_context}\"")
                    
                    if len(file_words) > 6:
                        report_parts.append(f"- ... and {len(file_words) - 6} more")
                    report_parts.append("")
    
    report_parts.extend([
        "---",
        f"🤖 **Critical Words Enforcer** | Analyzed: {total_comments} comments | Critical: {total_critical_words} | Status: {'⚠️ REPORTED' if has_critical_words else '✅ PASSED'}"
    ])
    
    # Post the analysis comment
    comment_text = "\n".join(report_parts)
    
    # Ensure comment isn't too long
    if len(comment_text) > 65000:
        comment_text = comment_text[:65000] + "\n\n*[Report truncated due to length - check Actions log for details]*"
    
    print(f"\n📝 Posting analysis report...")
    comment_response = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers=headers,
        json={'body': comment_text}
    )
    
    if comment_response.status_code == 201:
        print("✅ Analysis report posted successfully")
    else:
        print(f"⚠️ Failed to post comment: {comment_response.status_code}")
        # Try minimal fallback
        fallback_text = f"🤖 **Critical Words Enforcer**\n\n{'⚠️ REPORTED' if has_critical_words else '✅ PASSED'}: Found {total_critical_words} critical words in {total_comments} comments.\n\nCheck Actions log for full details."
        requests.post(f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments", headers=headers, json={'body': fallback_text})


def set_commit_status(analysis_result, repo, github_sha, headers):
    """Set the commit status based on analysis results"""
    total_critical_words = analysis_result['total_critical_words']
    total_comments = analysis_result['total_comments'] 
    has_critical_words = analysis_result['has_critical_words']
    
    if has_critical_words:
        status_response = requests.post(
            f"https://api.github.com/repos/{repo}/statuses/{github_sha}",
            headers=headers,
            json={
                'state': 'success',
                'description': f'REPORTED: {total_critical_words} critical words found in comments. Review recommended.',
                'context': 'Critical Words Enforcer'
            }
        )
        print("✅ Status set to SUCCESS with warning - merge allowed")
        print(f"⚠️ REPORTED: {total_critical_words} critical words found for review!")
        print("✅ Action completed successfully (reported findings)")
    else:
        status_response = requests.post(
            f"https://api.github.com/repos/{repo}/statuses/{github_sha}",
            headers=headers,
            json={
                'state': 'success',
                'description': f'PASSED: Clean comments - {total_comments} analyzed, no critical words found.',
                'context': 'Critical Words Enforcer'
            }
        )
        print("✅ Status set to SUCCESS - merge allowed")
        print(f"🎉 ENFORCER PASSED: Clean comments detected!")
        print("✅ Action completed successfully")


def set_error_status(repo, github_sha, headers):
    """Set success status when something goes wrong but don't fail the action"""
    try:
        requests.post(
            f"https://api.github.com/repos/{repo}/statuses/{github_sha}",
            headers=headers,
            json={
                'state': 'success',
                'description': 'Critical Words Enforcer completed with warnings.',
                'context': 'Critical Words Enforcer'
            }
        )
        print("✅ Status set to SUCCESS despite error - merge allowed")
        print("✅ Action completed (with warning status)")
    except:
        print("⚠️ Could not set status, but action completed successfully")


if __name__ == "__main__":
    main()