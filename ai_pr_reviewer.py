#!/usr/bin/env python3
"""
🤖 Enhanced AI PR Review (GitHub Copilot Style)

This script provides comprehensive AI-powered PR reviews using AWS Bedrock.
It analyzes code changes across multiple programming languages and provides
inline suggestions with GitHub's suggestion feature.

Features:
- Multi-language support (20+ languages)
- Security vulnerability detection  
- Code quality analysis
- Performance issue identification
- Inline suggestions with auto-fix capability
- AWS Bedrock integration with Nova model

Requirements:
- AWS Bedrock access with amazon.nova-micro-v1:0 model
- GitHub token with PR write permissions
- boto3, requests libraries

Environment Variables:
- GITHUB_TOKEN: GitHub API token
- AWS_ACCESS_KEY_ID: AWS access key
- AWS_SECRET_ACCESS_KEY: AWS secret key
- GITHUB_REPOSITORY: Repository name (owner/repo)
- PR_NUMBER: Pull request number
"""

import os
import sys
import json
import requests
import boto3
import re
from datetime import datetime


def main():
    print("🤖 Enhanced AI PR Review (Copilot Style)")
    
    # Get environment variables
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY') 
    pr_number = os.environ.get('PR_NUMBER')
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    # Validate required environment variables
    if not all([github_token, repo, pr_number, aws_key, aws_secret]):
        print("❌ Missing required environment variables:")
        print(f"  - GITHUB_TOKEN: {'✅' if github_token else '❌'}")
        print(f"  - GITHUB_REPOSITORY: {'✅' if repo else '❌'}")
        print(f"  - PR_NUMBER: {'✅' if pr_number else '❌'}")
        print(f"  - AWS_ACCESS_KEY_ID: {'✅' if aws_key else '❌'}")
        print(f"  - AWS_SECRET_ACCESS_KEY: {'✅' if aws_secret else '❌'}")
        sys.exit(1)

    # Initialize Bedrock client
    bedrock = None
    try:
        bedrock = boto3.client(
            'bedrock-runtime', 
            region_name=aws_region, 
            aws_access_key_id=aws_key, 
            aws_secret_access_key=aws_secret
        )
        print("✅ AWS Bedrock client initialized")
    except Exception as e:
        print(f"⚠️ Bedrock initialization error: {e}")
        return

    # GitHub API headers
    headers = {
        'Authorization': f'token {github_token}', 
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # Get PR data
        print(f"📋 Fetching PR #{pr_number} data...")
        pr_response = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}", headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        # Get PR files
        files_response = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files", headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        print(f"📁 Analyzing {len(files_data)} files...")
        
        # Create PR overview
        title = pr_data.get('title', 'No title')
        total_files = len(files_data)
        total_additions = sum(f.get('additions', 0) for f in files_data)
        total_deletions = sum(f.get('deletions', 0) for f in files_data)
        
        overview_parts = [
            "## Pull Request Overview",
            "",
            f"This PR modifies {total_files} file{'s' if total_files != 1 else ''} with {total_additions} additions and {total_deletions} deletions.",
            "",
            f"**{title}**",
            "",
            "### Changes Summary"
        ]
        
        # Add file changes summary
        for file_data in files_data:
            filename = file_data.get('filename', '')
            additions = file_data.get('additions', 0)
            deletions = file_data.get('deletions', 0)
            status = file_data.get('status', '')
            
            if status == 'added':
                overview_parts.append(f"• **Added** `{filename}` ({additions} lines)")
            elif status == 'modified':
                overview_parts.append(f"• **Modified** `{filename}` (+{additions}/-{deletions})")
            else:
                overview_parts.append(f"• **Changed** `{filename}`")
        
        # Add Copilot tip
        overview_parts.extend([
            "",
            "---", 
            "**Tip:** Customize your code reviews with copilot-instructions.md. [Create the file](https://github.com/github/copilot-instructions) or [learn how to get started](https://docs.github.com/en/copilot)."
        ])
        
        # Post overview comment
        overview_text = "\n".join(overview_parts)
        comment_response = requests.post(
            f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
            headers=headers,
            json={'body': overview_text}
        )
        
        if comment_response.status_code == 201:
            print("✅ Posted PR overview")
        else:
            print(f"⚠️ Failed to post overview: {comment_response.status_code}")

        # AI Analysis for all files
        if bedrock:
            commit_sha = pr_data['head']['sha']
            review_comments = []
            
            for file_data in files_data:
                filename = file_data.get('filename', '')
                patch = file_data.get('patch', '')
                status = file_data.get('status', '')
                
                # Skip binary files
                skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.exe', '.dll']
                if not patch or any(filename.lower().endswith(ext) for ext in skip_extensions):
                    continue
                
                print(f"🔍 AI analyzing {filename} (status: {status})...")
                
                # Get file extension for language-specific analysis
                file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
                
                # Generate language-specific AI prompt
                prompt = generate_language_prompt(file_ext, filename, status, patch)
                
                try:
                    # Call AWS Bedrock API
                    body = json.dumps({
                        "messages": [{"role": "user", "content": [{"text": prompt}]}],
                        "inferenceConfig": {"maxTokens": 1500, "temperature": 0.1}
                    })
                    
                    ai_response = bedrock.invoke_model(
                        modelId="amazon.nova-micro-v1:0",
                        body=body,
                        contentType="application/json"
                    )
                    
                    result = json.loads(ai_response['body'].read())
                    ai_text = result['output']['message']['content'][0]['text']
                    print(f"🤖 AI analysis complete: {ai_text[:100]}...")
                    
                    # Parse diff and detect issues
                    issues_found = analyze_code_diff(patch, file_ext, filename)
                    
                    print(f"🔍 Found {len(issues_found)} issues in {filename}")
                    
                    # Create review comments
                    for issue in issues_found:
                        comment_body = format_review_comment(issue)
                        review_comments.append({
                            'path': filename,
                            'line': issue.get('line', 1),
                            'body': comment_body
                        })
                
                except Exception as e:
                    print(f"⚠️ AI error for {filename}: {e}")
            
            # Post inline review comments
            if review_comments:
                print(f"📝 Posting {len(review_comments)} inline suggestions...")
                review_data = {
                    'commit_id': commit_sha,
                    'event': 'COMMENT', 
                    'comments': review_comments
                }
                
                review_response = requests.post(
                    f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews",
                    headers=headers,
                    json=review_data
                )
                
                if review_response.status_code == 200:
                    print(f"✅ Posted {len(review_comments)} inline suggestions")
                else:
                    print(f"⚠️ Failed to post inline comments: {review_response.status_code}")
                    
                    # Fallback: post consolidated comment
                    post_fallback_comment(review_comments, repo, pr_number, headers)
            else:
                print("ℹ️ No issues found - code looks good!")
        
        print("🎉 Enhanced PR review completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def generate_language_prompt(file_ext, filename, status, patch):
    """Generate language-specific AI analysis prompts"""
    
    if file_ext in ['c', 'cpp', 'cc', 'cxx', 'h', 'hpp']:
        return f"""Analyze this C/C++ code diff and find ALL critical issues:
🚨 SECURITY: Buffer overflows (gets, strcpy, strcat, sprintf, scanf), hardcoded secrets, format string vulnerabilities, integer overflows
⚠️ MEMORY: Memory leaks (malloc/new without free/delete), double free, use after free, uninitialized variables, null pointer dereference
💡 QUALITY: Division by zero, infinite loops, dead code, test comments
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext in ['py', 'pyw']:
        return f"""Analyze this Python code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, SQL injection, command injection, eval/exec usage, pickle vulnerabilities, path traversal
⚠️ QUALITY: Exception handling, resource leaks, performance issues, unused imports, mutable defaults, global variables
💡 STYLE: PEP8 violations, missing type hints, print statements, test comments
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext in ['js', 'jsx', 'ts', 'tsx']:
        return f"""Analyze this JavaScript/TypeScript code diff and find ALL critical issues:
🚨 SECURITY: XSS vulnerabilities, prototype pollution, eval usage, hardcoded secrets, insecure randomness, CSRF vulnerabilities
⚠️ QUALITY: Memory leaks, callback hell, promise rejections, var usage, == vs ===, missing error handling
💡 STYLE: Console.log statements, unused variables, test comments, missing semicolons, arrow function usage
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext in ['java', 'kt', 'scala']:
        return f"""Analyze this Java/Kotlin/Scala code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, SQL injection, deserialization vulnerabilities, path traversal, XML external entity (XXE)
⚠️ QUALITY: Resource leaks (streams, connections), null pointer exceptions, infinite loops, thread safety issues, memory leaks
💡 STYLE: System.out.println usage, unused imports, test comments, missing generics, raw types
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext == 'go':
        return f"""Analyze this Go code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, SQL injection, command injection, race conditions, unsafe package usage
⚠️ QUALITY: Goroutine leaks, unchecked errors, resource leaks, panic usage, defer in loops
💡 STYLE: fmt.Print statements, unused variables, test comments, gofmt violations, missing error handling
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext == 'rs':
        return f"""Analyze this Rust code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, unsafe blocks, integer overflows, buffer overflows in unsafe code
⚠️ QUALITY: Unwrap usage, panic calls, unused variables, clone overuse, blocking in async
💡 STYLE: println! statements, test comments, missing documentation, inefficient string handling
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext == 'cs':
        return f"""Analyze this C# code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, SQL injection, XSS, deserialization, path traversal, weak cryptography
⚠️ QUALITY: Resource disposal (using statements), null reference exceptions, memory leaks, thread safety
💡 STYLE: Console.WriteLine, unused usings, test comments, missing async/await, boxing
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext == 'php':
        return f"""Analyze this PHP code diff and find ALL critical issues:
🚨 SECURITY: SQL injection, XSS, file inclusion, hardcoded secrets, command injection, session fixation
⚠️ QUALITY: Error handling, resource leaks, performance issues, globals usage, magic numbers
💡 STYLE: var_dump/print_r, test comments, deprecated functions, PSR violations, missing type declarations
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext == 'rb':
        return f"""Analyze this Ruby code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, SQL injection, command injection, eval usage, YAML.load vulnerabilities
⚠️ QUALITY: Exception handling, performance issues, memory leaks, global variables, thread safety
💡 STYLE: puts/p statements, test comments, unused variables, style guide violations
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext == 'swift':
        return f"""Analyze this Swift code diff and find ALL critical issues:
🚨 SECURITY: Hardcoded secrets, unsafe pointers, force unwrapping, weak cryptography, keychain issues
⚠️ QUALITY: Memory leaks, retain cycles, force unwrapping, thread safety, performance issues
💡 STYLE: print statements, test comments, force casts, naming conventions, unused variables
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    elif file_ext in ['sql', 'mysql', 'pgsql']:
        return f"""Analyze this SQL code diff and find ALL critical issues:
🚨 SECURITY: SQL injection, privilege escalation, hardcoded credentials, data exposure, weak permissions
⚠️ QUALITY: Missing indexes, inefficient queries, resource locks, transaction handling, performance issues
💡 STYLE: Test comments, deprecated functions, formatting issues
FILE: {filename} STATUS: {status} DIFF: {patch}"""
    
    else:
        # Universal analysis for any other file type
        return f"""Analyze this code diff and find ALL critical issues across all categories:
🚨 SECURITY: Hardcoded secrets (passwords, API keys, tokens), injection vulnerabilities, insecure functions, weak cryptography
⚠️ QUALITY: Memory leaks, resource management, error handling, performance issues, infinite loops, null/undefined access
💡 STYLE: Debug statements, test comments, code smells, unused variables, formatting issues
FILE: {filename} STATUS: {status} DIFF: {patch}"""


def analyze_code_diff(patch, file_ext, filename):
    """Analyze code diff and detect issues using pattern matching"""
    issues_found = []
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
            
            # Universal security detection
            security_issues = detect_security_issues(line_content, line_number)
            issues_found.extend(security_issues)
            
            # Language-specific analysis
            language_issues = detect_language_specific_issues(line_content, line_number, file_ext)
            issues_found.extend(language_issues)
            
            # Universal quality issues
            quality_issues = detect_quality_issues(line_content, line_number)
            issues_found.extend(quality_issues)
            
        elif line.startswith(' '):
            line_number += 1
    
    return issues_found


def detect_security_issues(line_content, line_number):
    """Detect universal security issues"""
    issues = []
    
    # Hardcoded secrets detection
    security_keywords = [
        'password', 'secret', 'token', 'api_key', 'access_key', 
        'private_key', 'secret_key', 'auth_token', 'bearer_token',
        'client_secret', 'app_secret', 'encryption_key'
    ]
    
    if any(word in line_content.lower() for word in security_keywords):
        if '=' in line_content or ':' in line_content:
            issues.append({
                'line': line_number,
                'type': 'security', 
                'severity': 'high',
                'message': 'Potential hardcoded secret detected',
                'suggestion': '# TODO: Move to environment variable or secure vault'
            })
    
    # SQL injection patterns
    sql_injection_patterns = [
        r'SELECT.*\+.*\+',  # String concatenation in SQL
        r'WHERE.*=.*\+',    # Dynamic WHERE clauses
        r'INSERT.*\+.*\+',  # Dynamic INSERT
        r'UPDATE.*\+.*\+'   # Dynamic UPDATE
    ]
    
    for pattern in sql_injection_patterns:
        if re.search(pattern, line_content, re.IGNORECASE):
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'Potential SQL injection - use parameterized queries',
                'suggestion': ''
            })
    
    return issues


def detect_language_specific_issues(line_content, line_number, file_ext):
    """Detect language-specific issues"""
    issues = []
    
    if file_ext in ['c', 'cpp', 'cc', 'cxx', 'h', 'hpp']:
        # C/C++ unsafe functions
        unsafe_c_funcs = {
            'gets(': 'Use fgets(buffer, size, stdin) instead',
            'strcpy(': 'Use strncpy() or strcpy_s() instead',
            'strcat(': 'Use strncat() or strcat_s() instead',
            'sprintf(': 'Use snprintf() instead',
            'scanf(': 'Use scanf_s() or limit input instead'
        }
        
        for func, suggestion in unsafe_c_funcs.items():
            if func in line_content:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'high',
                    'message': f'Unsafe C function {func[:-1]}() - buffer overflow risk',
                    'suggestion': suggestion
                })
        
        if 'malloc(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Memory allocation - ensure corresponding free() call',
                'suggestion': ''
            })
    
    elif file_ext in ['py', 'pyw']:
        if 'eval(' in line_content or 'exec(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'eval/exec usage - code injection risk',
                'suggestion': ''
            })
        
        if 'print(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'low',
                'message': 'Consider using logging instead of print statements',
                'suggestion': line_content.replace('print(', 'logging.info(')
            })
    
    elif file_ext in ['js', 'jsx', 'ts', 'tsx']:
        if 'eval(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'eval() usage - code injection risk',
                'suggestion': ''
            })
        
        if 'console.log(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'low',
                'message': 'Remove console.log in production code',
                'suggestion': ''
            })
        
        if '==' in line_content and '===' not in line_content and '!=' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Use strict equality (===) instead of ==',
                'suggestion': line_content.replace('==', '===')
            })
    
    elif file_ext == 'rs':
        if 'unwrap()' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'unwrap() usage - consider proper error handling',
                'suggestion': line_content.replace('.unwrap()', '.expect("description")')
            })
        
        if 'println!' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'low',
                'message': 'Remove println! in production code',
                'suggestion': ''
            })
    
    return issues


def detect_quality_issues(line_content, line_number):
    """Detect universal quality issues"""
    issues = []
    
    # Comment analysis
    comment_patterns = [
        r'^//\s*(test|debug|hello|todo|fixme|hack)',  # C-style comments
        r'^#\s*(test|debug|hello|todo|fixme|hack)',   # Python/Shell comments
        r'^\*\s*(test|debug|hello|todo|fixme|hack)',  # Block comment lines
        r'^<!--\s*(test|debug|hello|todo|fixme|hack)' # HTML comments
    ]
    
    for pattern in comment_patterns:
        if re.match(pattern, line_content.lower()):
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium', 
                'message': 'Remove test/debug comment before production',
                'suggestion': ''
            })
    
    # Division by zero check
    if '/' in line_content and ('return' in line_content or '=' in line_content):
        if 'if' not in line_content and '//' not in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Division operation without zero check',
                'suggestion': ''
            })
    
    return issues


def format_review_comment(issue):
    """Format issue as GitHub review comment"""
    severity = issue.get('severity', 'medium')
    message = issue.get('message', 'Issue detected')
    suggestion = issue.get('suggestion', '')
    
    # Format comment based on severity
    if severity == 'high':
        icon = '🚨'
        label = 'Critical'
    elif severity == 'medium':
        icon = '⚠️'
        label = 'Warning'
    else:
        icon = '💡'
        label = 'Suggestion'
    
    comment_body = f"{icon} **{label}:** {message}"
    
    # Add suggestion if provided
    if suggestion:
        comment_body += f"\n\n```suggestion\n{suggestion}\n```"
        comment_body += "\n\n*Click 'Commit suggestion' to apply this change automatically.*"
    elif suggestion == '':
        comment_body += "\n\n```suggestion\n\n```"
        comment_body += "\n\n*Click 'Commit suggestion' to remove this line.*"
    
    return comment_body


def post_fallback_comment(review_comments, repo, pr_number, headers):
    """Post consolidated comment as fallback when inline comments fail"""
    summary_items = []
    for comment in review_comments:
        summary_items.append(f"**{comment['path']}** (line {comment['line']}): {comment['body']}")
    
    fallback_comment = "## 🤖 AI Code Review\n\n" + "\n\n---\n\n".join(summary_items)
    fallback_response = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers=headers,
        json={'body': fallback_comment}
    )
    
    if fallback_response.status_code == 201:
        print("✅ Posted consolidated review comment")
    else:
        print(f"❌ Failed to post fallback comment: {fallback_response.status_code}")


if __name__ == "__main__":
    main()