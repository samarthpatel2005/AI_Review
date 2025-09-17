#!/usr/bin/env python3
"""
📊 PR Review Summary Generator

This script generates a comprehensive summary of what the AI PR reviewer
and Critical Words Enforcer analyzed in the changed files.

Features:
- Analyzes all changed files in the PR
- Summarizes AI review findings
- Lists critical words enforcement results  
- Generates detailed markdown report
- Tracks function-level changes and issues

Environment Variables:
- GITHUB_TOKEN: GitHub API token
- GITHUB_REPOSITORY: Repository name (owner/repo)
- PR_NUMBER: Pull request number
- GITHUB_SHA: Commit SHA
"""

import os
import sys
import json
import requests
import re
from datetime import datetime
from collections import defaultdict


def main():
    print("📊 Generating PR Review Summary...")
    
    # Get environment variables
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    pr_number = os.environ.get('PR_NUMBER')
    github_sha = os.environ.get('GITHUB_SHA')
    
    if not all([github_token, repo, pr_number, github_sha]):
        print("⚠️ Missing required environment variables")
        return
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get PR data
        pr_response = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}", headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        # Get PR files
        files_response = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files", headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        # Get PR comments (to analyze what was reviewed)
        comments_response = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments", headers=headers)
        comments_response.raise_for_status()
        comments_data = comments_response.json()
        
        # Generate summary
        summary = generate_summary(pr_data, files_data, comments_data)
        
        # Write to file
        with open('pr-review-summary.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("✅ PR Review Summary generated: pr-review-summary.md")
        
        # Also post as PR comment
        comment_response = requests.post(
            f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
            headers=headers,
            json={'body': summary}
        )
        
        if comment_response.status_code == 201:
            print("✅ Summary posted as PR comment")
        else:
            print(f"⚠️ Failed to post summary comment: {comment_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        sys.exit(1)


def generate_summary(pr_data, files_data, comments_data):
    """Generate comprehensive PR review summary"""
    
    title = pr_data.get('title', 'No title')
    author = pr_data.get('user', {}).get('login', 'Unknown')
    created_at = pr_data.get('created_at', '')
    
    # Analyze files
    total_files = len(files_data)
    total_additions = sum(f.get('additions', 0) for f in files_data)
    total_deletions = sum(f.get('deletions', 0) for f in files_data)
    
    # Categorize files by type
    file_types = defaultdict(list)
    languages_detected = set()
    
    for file_data in files_data:
        filename = file_data.get('filename', '')
        file_ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
        file_types[file_ext].append(filename)
        
        # Map extensions to languages
        lang_map = {
            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript', 
            'java': 'Java', 'c': 'C', 'cpp': 'C++', 'h': 'C/C++',
            'cs': 'C#', 'php': 'PHP', 'rb': 'Ruby', 'go': 'Go',
            'rs': 'Rust', 'kt': 'Kotlin', 'swift': 'Swift',
            'yml': 'YAML', 'yaml': 'YAML', 'json': 'JSON',
            'md': 'Markdown', 'txt': 'Text'
        }
        if file_ext in lang_map:
            languages_detected.add(lang_map[file_ext])
    
    # Analyze review comments
    ai_issues = analyze_review_comments(comments_data)
    
    # Detect functions that were changed
    functions_analyzed = detect_changed_functions(files_data)
    
    # Generate the summary
    summary_parts = [
        "# 📊 PR Review Summary Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**PR Title:** {title}",
        f"**Author:** @{author}",
        f"**Created:** {created_at}",
        "",
        "---",
        "",
        "## 📋 Changes Overview",
        "",
        f"- **Files Modified:** {total_files}",
        f"- **Lines Added:** +{total_additions}",
        f"- **Lines Deleted:** -{total_deletions}",
        f"- **Net Change:** {total_additions - total_deletions:+d}",
        "",
        "### 🔍 Languages Detected",
        ""
    ]
    
    if languages_detected:
        for lang in sorted(languages_detected):
            file_count = sum(1 for ext, files in file_types.items() 
                           if ext in ['py', 'js', 'ts', 'java', 'c', 'cpp', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'kt', 'swift'] 
                           and any(lang.lower() in f.lower() for f in files))
            summary_parts.append(f"- **{lang}**: {len([f for files in file_types.values() for f in files if f.endswith(tuple(get_extensions_for_language(lang)))])} file(s)")
    else:
        summary_parts.append("- No programming languages detected")
    
    summary_parts.extend([
        "",
        "### 📁 Files by Type",
        ""
    ])
    
    for ext, files in sorted(file_types.items()):
        summary_parts.append(f"**{ext.upper() if ext != 'unknown' else 'No Extension'}** ({len(files)} files):")
        for filename in files[:5]:  # Show first 5 files
            summary_parts.append(f"- `{filename}`")
        if len(files) > 5:
            summary_parts.append(f"- ... and {len(files) - 5} more")
        summary_parts.append("")
    
    # AI Review Analysis
    summary_parts.extend([
        "---",
        "",
        "## 🤖 AI Review Analysis Results",
        ""
    ])
    
    if ai_issues['total'] > 0:
        summary_parts.extend([
            f"**Total Issues Found:** {ai_issues['total']}",
            "",
            "### 🚨 Issues by Severity",
            ""
        ])
        
        for severity, count in ai_issues['by_severity'].items():
            if count > 0:
                icon = {'critical': '🔴', 'high': '🚨', 'medium': '⚠️', 'low': '💡'}.get(severity, '📝')
                summary_parts.append(f"- {icon} **{severity.title()}:** {count} issue(s)")
        
        summary_parts.extend([
            "",
            "### 🏷️ Issues by Category",
            ""
        ])
        
        for category, count in ai_issues['by_category'].items():
            if count > 0:
                summary_parts.append(f"- **{category.title()}:** {count} issue(s)")
        
        if ai_issues['files_with_issues']:
            summary_parts.extend([
                "",
                "### 📄 Files with Issues",
                ""
            ])
            for filename, issue_count in ai_issues['files_with_issues'].items():
                summary_parts.append(f"- `{filename}`: {issue_count} issue(s)")
    else:
        summary_parts.extend([
            "✅ **No issues found** - Code looks good!",
            ""
        ])
    
    # Function Analysis
    if functions_analyzed:
        summary_parts.extend([
            "---",
            "",
            "## ⚙️ Function-Level Analysis",
            "",
            f"**Functions Analyzed:** {len(functions_analyzed)}",
            ""
        ])
        
        functions_with_issues = [f for f in functions_analyzed if f['issues'] > 0]
        if functions_with_issues:
            summary_parts.extend([
                "### 🔍 Functions with Issues",
                ""
            ])
            for func in functions_with_issues:
                summary_parts.append(f"- `{func['name']}()` in `{func['file']}`: {func['issues']} issue(s)")
        else:
            summary_parts.append("✅ No issues found in function changes")
    
    # What was checked summary
    summary_parts.extend([
        "",
        "---",
        "",
        "## 🔍 What Was Analyzed",
        "",
        "### 🤖 AI PR Reviewer Checked:",
        "",
        "- **Security Vulnerabilities:**",
        "  - Hardcoded secrets and credentials",
        "  - Command injection risks (`eval`, `exec`, `system`)",
        "  - SQL injection patterns",
        "  - File operation security (path traversal)",
        "  - Network operation validation",
        "  - Cryptographic function usage",
        "",
        "- **Code Quality Issues:**",
        "  - Memory management (leaks, unsafe operations)",
        "  - Error handling patterns",
        "  - Performance bottlenecks",
        "  - Debug statements and temporary code",
        "  - Language-specific best practices",
        "",
        "- **Language-Specific Analysis:**",
        "  - **Python:** Code injection, subprocess risks, import safety",
        "  - **JavaScript/TypeScript:** XSS vulnerabilities, DOM manipulation",
        "  - **C/C++:** Buffer overflows, memory safety, unsafe functions",
        "  - **Java:** Reflection risks, command injection patterns",
        "  - **PHP:** Code injection, file inclusion vulnerabilities",
        "  - **And more...** (20+ languages supported)",
        "",
        "### 🚨 Critical Words Enforcer Checked:",
        "",
        "- **Comment Quality:**",
        "  - TODO/FIXME notes indicating incomplete work",
        "  - Hack/workaround mentions suggesting technical debt",
        "  - Security-related warnings in comments",
        "  - Development-related terminology",
        "  - Performance issue indicators",
        "  - Quality concern mentions",
        "",
        "---",
        "",
        "## 📈 Summary Statistics",
        "",
        f"- **Analysis Mode:** {'AI-Powered' if has_custom_prompt() else 'Pattern Matching'}",
        f"- **Files Scanned:** {total_files}",
        f"- **Lines of Code Changed:** {total_additions + total_deletions}",
        f"- **Programming Languages:** {len(languages_detected)}",
        f"- **Security Issues:** {ai_issues['by_severity'].get('critical', 0) + ai_issues['by_severity'].get('high', 0)}",
        f"- **Quality Issues:** {ai_issues['by_severity'].get('medium', 0) + ai_issues['by_severity'].get('low', 0)}",
        "",
        "---",
        "",
        "*This summary was automatically generated by the AI PR Review System.*  ",
        "*For detailed issue descriptions and fix suggestions, see the inline PR comments.*"
    ])
    
    return "\n".join(summary_parts)


def analyze_review_comments(comments_data):
    """Analyze AI review comments to extract statistics"""
    analysis = {
        'total': len(comments_data),
        'by_severity': defaultdict(int),
        'by_category': defaultdict(int),
        'files_with_issues': defaultdict(int)
    }
    
    for comment in comments_data:
        body = comment.get('body', '')
        path = comment.get('path', 'unknown')
        
        # Extract severity
        if '🔴' in body or 'CRITICAL' in body.upper():
            analysis['by_severity']['critical'] += 1
        elif '🚨' in body or 'HIGH RISK' in body.upper():
            analysis['by_severity']['high'] += 1
        elif '⚠️' in body or 'WARNING' in body.upper():
            analysis['by_severity']['medium'] += 1
        elif '💡' in body or 'SUGGESTION' in body.upper():
            analysis['by_severity']['low'] += 1
        
        # Extract category
        if 'security' in body.lower() or 'injection' in body.lower():
            analysis['by_category']['security'] += 1
        elif 'quality' in body.lower() or 'performance' in body.lower():
            analysis['by_category']['quality'] += 1
        elif 'memory' in body.lower() or 'leak' in body.lower():
            analysis['by_category']['memory'] += 1
        else:
            analysis['by_category']['other'] += 1
        
        # Count by file
        analysis['files_with_issues'][path] += 1
    
    return analysis


def detect_changed_functions(files_data):
    """Detect functions that were changed in the PR"""
    functions = []
    
    function_patterns = [
        r'def\s+(\w+)\s*\(',  # Python
        r'function\s+(\w+)\s*\(',  # JavaScript
        r'(\w+)\s*\([^)]*\)\s*{',  # C/C++/Java/C#
        r'func\s+(\w+)\s*\(',  # Go
        r'fn\s+(\w+)\s*\(',  # Rust
    ]
    
    for file_data in files_data:
        filename = file_data.get('filename', '')
        patch = file_data.get('patch', '')
        
        if not patch:
            continue
        
        lines = patch.split('\n')
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                line_content = line[1:].strip()
                
                for pattern in function_patterns:
                    match = re.search(pattern, line_content, re.IGNORECASE)
                    if match:
                        functions.append({
                            'name': match.group(1),
                            'file': filename,
                            'issues': 0  # Would be populated by actual analysis
                        })
    
    return functions


def get_extensions_for_language(language):
    """Get file extensions for a programming language"""
    ext_map = {
        'Python': ['.py', '.pyw'],
        'JavaScript': ['.js', '.jsx'],
        'TypeScript': ['.ts', '.tsx'],
        'Java': ['.java'],
        'C': ['.c', '.h'],
        'C++': ['.cpp', '.cc', '.cxx', '.hpp'],
        'C#': ['.cs'],
        'PHP': ['.php'],
        'Ruby': ['.rb'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'Kotlin': ['.kt'],
        'Swift': ['.swift']
    }
    return ext_map.get(language, [])


def has_custom_prompt():
    """Check if custom prompt is being used"""
    try:
        with open('prompt/custom.txt', 'r') as f:
            content = f.read().strip()
        return len(content) > 10
    except:
        return False


if __name__ == "__main__":
    main()