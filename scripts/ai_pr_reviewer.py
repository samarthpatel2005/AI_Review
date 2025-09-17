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

ENHANCED CODE ANALYSIS:
✅ Critical Function Detection:
   - Command injection risks (system, exec, eval)
   - File operation security (path traversal)
   - Network operation validation
   - Memory management issues
   - Authentication/authorization functions

✅ Language-Specific Security:
   - C/C++: Buffer overflows, unsafe functions, memory leaks
   - Python: Code injection, subprocess risks, file operations
   - JavaScript: XSS, code injection, DOM manipulation
   - Java: Reflection risks, command injection
   - PHP: Code/command injection, file inclusion
   - Rust: Unsafe blocks, error handling
   - Go: Command execution, unsafe operations

✅ Quality & Performance:
   - Database operation validation
   - Cryptographic function assessment
   - Error handling analysis
   - Thread safety checks
   - Hardcoded configuration detection
   - Memory allocation validation

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
- CUSTOM_PROMPT: (Optional) Custom AI analysis prompt - overrides default language-specific prompts
"""

import os
import sys
import json
import requests
import boto3
import re
from datetime import datetime


def load_prompt():
    """Load prompt from files - custom.txt if not empty, otherwise default.txt"""
    try:
        # Get the root directory of the project (where .git folder is located)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up from scripts/ to project root
        
        print(f"🔍 Script directory: {script_dir}")
        print(f"🔍 Project root: {project_root}")
        
        # Try to read custom prompt first
        custom_path = os.path.join(project_root, 'prompt', 'custom.txt')
        print(f"🔍 Looking for custom prompt at: {custom_path}")
        print(f"🔍 Custom file exists: {os.path.exists(custom_path)}")
        
        if os.path.exists(custom_path):
            try:
                with open(custom_path, 'r', encoding='utf-8') as f:
                    custom_prompt = f.read().strip()
                
                print(f"🔍 Custom prompt length: {len(custom_prompt)} characters")
                
                if custom_prompt and len(custom_prompt) > 10:  # Check if meaningful content exists
                    print("🎯 Using CUSTOM PROMPT from prompt/custom.txt")
                    print(f"🔍 Custom prompt preview: {custom_prompt[:100]}...")
                    return custom_prompt
                else:
                    print("⚠️ Custom prompt file is empty or too short, falling back to default")
            except Exception as e:
                print(f"⚠️ Error reading custom prompt file: {e}")
        
        # If custom is not available or empty, use default
        default_path = os.path.join(project_root, 'prompt', 'default.txt')
        print(f"🔍 Looking for default prompt at: {default_path}")
        
        if os.path.exists(default_path):
            with open(default_path, 'r', encoding='utf-8') as f:
                default_prompt = f.read().strip()
            
            print("🔧 Using DEFAULT PROMPT from prompt/default.txt")
            print(f"🔍 Default prompt preview: {default_prompt[:100]}...")
            return default_prompt
        else:
            raise FileNotFoundError("Default prompt file not found")
        
    except Exception as e:
        print(f"⚠️ Error reading prompt files: {e}")
        print("🔧 Using fallback default prompt")
        return """CRITICAL: You MUST provide detailed feedback in EXACTLY this format for EACH issue found:

🚨 **[Risk Level] Risk: [Issue Title]**
**Detailed Explanation:** [2-3 sentences explaining WHY this is problematic]
**Impact Assessment:** [What could go wrong if not fixed - 1 sentence]
**Specific Fix Suggestion:** [Concrete steps to resolve the issue - 1-2 sentences]

FORMAT REQUIREMENTS: Each issue MUST be exactly 4 lines following the format above. Do NOT use single-line responses like "� High Risk: Potential hardcoded secret detected". Always provide the full 4-line detailed analysis."""


def main():
    print("🤖 Enhanced AI PR Review (Copilot Style)")
    
    # Load prompt from files
    prompt_template = load_prompt()
    
    # Get environment variables
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY') 
    pr_number = os.environ.get('PR_NUMBER')
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    # Validate required environment variables
    if not all([github_token, repo, pr_number, aws_key, aws_secret]):
        print("❌ Missing required environment variables for AI PR Review")
        print("Please ensure all required secrets are configured in GitHub Actions:")
        print("  - GITHUB_TOKEN (auto-provided)")
        print("  - AWS_ACCESS_KEY_ID (add to secrets)")
        print("  - AWS_SECRET_ACCESS_KEY (add to secrets)")
        print("  - Repository and PR information (auto-provided)")
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
                
                # Generate language-specific AI prompt using loaded prompt template
                prompt = generate_language_prompt(file_ext, filename, status, patch, prompt_template)
                
                print(f"🔍 FULL PROMPT BEING SENT TO AI:")
                print("="*60)
                print(prompt)
                print("="*60)
                
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
                    print(f"🤖 AI analysis complete:")
                    print("="*60)
                    print(ai_text)
                    print("="*60)
                    
                    # Determine if we should use AI response or pattern matching
                    # Check if we're using custom prompt (which should get AI response)
                    # or default prompt (which should use pattern matching)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(script_dir)  # Go up from scripts/ to project root
                    custom_path = os.path.join(project_root, 'prompt', 'custom.txt')
                    use_ai_response = False
                    
                    if os.path.exists(custom_path):
                        with open(custom_path, 'r', encoding='utf-8') as f:
                            custom_content = f.read().strip()
                        if custom_content and len(custom_content) > 10:
                            use_ai_response = True
                            print("🎯 Using AI response from custom prompt")
                    
                    if use_ai_response and ai_text.strip():
                        # Parse AI response for issues (when using custom prompt)
                        issues_found = parse_ai_response_for_issues(ai_text, filename)
                        print(f"🤖 Found {len(issues_found)} AI-detected issues in {filename}")
                    else:
                        # Use pattern matching approach (when using default prompt or AI response is empty)
                        print("🔍 Using pattern matching analysis")
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


def parse_ai_response_for_issues(ai_text, filename):
    """Parse AI response text to extract issues when using custom prompts"""
    issues = []
    
    # Handle "no issues" response
    if "no issues detected" in ai_text.lower() or "code looks good" in ai_text.lower():
        return issues
    
    # Split the AI response into sections by risk level indicators
    lines = ai_text.split('\n')
    current_issue = {}
    line_counter = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for risk level indicators (support both formats)
        risk_indicators = ['🔴', '🚨', '⚠️', '💡', '⚡', 'CRITICAL', 'High Risk', 'Warning', 'Suggestion', 'Quick Fix']
        if any(indicator in line for indicator in risk_indicators):
            # Save previous issue if exists
            if current_issue and current_issue.get('message'):
                issues.append(current_issue)
                line_counter += 1
            
            # Start new issue
            severity = 'medium'  # default
            if '🔴' in line or 'CRITICAL' in line.upper():
                severity = 'critical'
            elif '🚨' in line or 'HIGH RISK' in line.upper():
                severity = 'high'
            elif '⚠️' in line or 'WARNING' in line.upper():
                severity = 'medium'
            elif '💡' in line or 'SUGGESTION' in line.upper():
                severity = 'low'
            elif '⚡' in line or 'QUICK FIX' in line.upper():
                severity = 'medium'
            
            # Extract message (remove emoji and formatting)
            message = line
            for indicator in risk_indicators:
                message = message.replace(indicator, '').strip()
            message = message.replace('**', '').replace('*', '').replace(':', '').strip()
            
            current_issue = {
                'line': line_counter,
                'type': 'ai_detected',
                'severity': severity,
                'message': message,
                'detailed_explanation': '',
                'impact_assessment': '',
                'fix_suggestion': '',
                'suggestion': ''
            }
        
        # Look for detailed explanation patterns
        elif ('**Detailed Explanation:**' in line or 
              '**Step-by-Step**' in line or 
              '**Fix Time**' in line):
            if current_issue:
                explanation = line.split(':**')[-1].strip() if ':**' in line else line.strip()
                if current_issue.get('detailed_explanation'):
                    current_issue['detailed_explanation'] += ' ' + explanation
                else:
                    current_issue['detailed_explanation'] = explanation
        
        # Look for impact assessment patterns
        elif ('**Impact Assessment:**' in line or 
              '**Verification**' in line):
            if current_issue:
                impact = line.split(':**')[-1].strip() if ':**' in line else line.strip()
                current_issue['impact_assessment'] = impact
        
        # Look for fix suggestion patterns
        elif ('**Specific Fix Suggestion:**' in line or 
              '**Fix Suggestion:**' in line or
              line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
            if current_issue:
                fix_text = line
                if ':**' in line:
                    fix_text = line.split(':**')[-1].strip()
                elif line.startswith(('1.', '2.', '3.')):
                    fix_text = line[2:].strip()
                
                if current_issue.get('fix_suggestion'):
                    current_issue['fix_suggestion'] += ' ' + fix_text
                else:
                    current_issue['fix_suggestion'] = fix_text
        
        # Capture additional context for current issue
        elif current_issue and line and not line.startswith('🎯') and not line.startswith('✅'):
            # Add to detailed explanation if it's descriptive content
            if len(line) > 10 and not current_issue.get('detailed_explanation'):
                current_issue['detailed_explanation'] = line
    
    # Add the last issue if exists
    if current_issue and current_issue.get('message'):
        issues.append(current_issue)
    
    # If no structured issues found, try to extract any feedback as a general issue
    if not issues and ai_text.strip():
        # Check if it's just "no issues" feedback
        if not any(phrase in ai_text.lower() for phrase in ['no issues', 'looks good', 'code analysis complete']):
            issues.append({
                'line': 1,
                'type': 'ai_detected',
                'severity': 'medium',
                'message': 'AI feedback provided',
                'detailed_explanation': ai_text[:300] + '...' if len(ai_text) > 300 else ai_text,
                'impact_assessment': 'Review the AI feedback for potential improvements.',
                'fix_suggestion': 'Consider implementing the suggestions provided by the AI analysis.',
                'suggestion': ''
            })
    
    return issues


def generate_language_prompt(file_ext, filename, status, patch, prompt_template):
    """Generate AI analysis prompt using template from prompt files"""
    
    # Use the provided prompt template (from default.txt or custom.txt)
    return f"""{prompt_template}

FILE: {filename} STATUS: {status} 
DIFF: {patch}"""

def analyze_code_diff(patch, file_ext, filename):
    """Analyze code diff and detect issues using pattern matching"""
    issues_found = []
    lines = patch.split('\n')
    line_number = 0
    current_function = None
    functions_with_issues = []
    
    for line in lines:
        if line.startswith('@@'):
            # Extract starting line number from diff header
            match = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if match:
                line_number = int(match.group(1)) - 1
        elif line.startswith('+') and not line.startswith('+++'):
            line_number += 1
            line_content = line[1:].strip()
            
            # Detect function definitions to track function-level changes
            function_patterns = [
                r'def\s+(\w+)\s*\(',  # Python
                r'function\s+(\w+)\s*\(',  # JavaScript
                r'(\w+)\s*\([^)]*\)\s*{',  # C/C++/Java/C#
                r'func\s+(\w+)\s*\(',  # Go
                r'fn\s+(\w+)\s*\(',  # Rust
                r'sub\s+(\w+)\s*\(',  # Perl
                r'(\w+)\s*:\s*function',  # Object method
            ]
            
            for pattern in function_patterns:
                match = re.search(pattern, line_content, re.IGNORECASE)
                if match:
                    current_function = match.group(1)
                    print(f"🔍 Detected function change: {current_function}() at line {line_number}")
                    break
            
            # Universal security detection
            security_issues = detect_security_issues(line_content, line_number)
            if security_issues and current_function:
                functions_with_issues.append({
                    'function': current_function,
                    'line': line_number,
                    'issues': len(security_issues)
                })
            issues_found.extend(security_issues)
            
            # Language-specific analysis
            language_issues = detect_language_specific_issues(line_content, line_number, file_ext)
            if language_issues and current_function:
                if not any(f['function'] == current_function for f in functions_with_issues):
                    functions_with_issues.append({
                        'function': current_function,
                        'line': line_number,
                        'issues': len(language_issues)
                    })
                else:
                    for f in functions_with_issues:
                        if f['function'] == current_function:
                            f['issues'] += len(language_issues)
            issues_found.extend(language_issues)
            
            # Universal quality issues
            quality_issues = detect_quality_issues(line_content, line_number)
            if quality_issues and current_function:
                if not any(f['function'] == current_function for f in functions_with_issues):
                    functions_with_issues.append({
                        'function': current_function,
                        'line': line_number,
                        'issues': len(quality_issues)
                    })
                else:
                    for f in functions_with_issues:
                        if f['function'] == current_function:
                            f['issues'] += len(quality_issues)
            issues_found.extend(quality_issues)
            
        elif line.startswith(' '):
            line_number += 1
    
    # Log functions with issues
    if functions_with_issues:
        print(f"📊 Functions with issues in {filename}:")
        for func_info in functions_with_issues:
            print(f"  - {func_info['function']}(): {func_info['issues']} issue(s) at line {func_info['line']}")
    
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
            detected_word = next(word for word in security_keywords if word in line_content.lower())
            issues.append({
                'line': line_number,
                'type': 'security', 
                'severity': 'high',
                'message': 'Potential hardcoded secret detected',
                'detailed_explanation': f'This line appears to contain a hardcoded {detected_word} which is a serious security vulnerability. Hardcoded credentials can be easily discovered by anyone with access to the source code, including attackers who compromise your repository.',
                'impact_assessment': 'Exposed credentials could lead to unauthorized access to systems, data breaches, or complete system compromise.',
                'fix_suggestion': f'Move the {detected_word} to environment variables, secure configuration files, or a secrets management system like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault.',
                'suggestion': '# TODO: Move to environment variable or secure vault'
            })
    
    # Critical function patterns - dangerous operations
    critical_functions = {
        'system(': 'Command injection risk - validate input or use safer alternatives',
        'exec(': 'Code injection risk - avoid dynamic code execution',
        'eval(': 'Code injection risk - avoid dynamic code evaluation',
        'subprocess.call(': 'Command injection risk - use subprocess.run() with shell=False',
        'os.system(': 'Command injection risk - use subprocess with proper sanitization',
        'Runtime.getRuntime().exec(': 'Command injection risk in Java - sanitize input',
        'ProcessBuilder(': 'Command injection risk in Java - validate arguments',
        'shell_exec(': 'Command injection risk in PHP - sanitize input',
        'passthru(': 'Command injection risk in PHP - use safer alternatives',
        'popen(': 'Command injection risk - validate input',
        'execvp(': 'Command injection risk in C - validate arguments',
        'CreateProcess(': 'Command injection risk in Windows - validate arguments'
    }
    
    for func, warning in critical_functions.items():
        if func in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'critical',
                'message': f'Critical function {func[:-1]}() detected',
                'detailed_explanation': f'The {func[:-1]}() function is extremely dangerous as it can execute arbitrary system commands or code. This function creates a direct pathway for command injection attacks where malicious input could execute unauthorized commands on the server.',
                'impact_assessment': 'Attackers could gain complete control over your system, steal sensitive data, install malware, or completely compromise your infrastructure.',
                'fix_suggestion': f'Replace {func[:-1]}() with safer alternatives like parameterized queries, input validation, or dedicated libraries that handle user input securely.',
                'suggestion': f'# CRITICAL: Review this {func[:-1]}() call for security implications'
            })
    
    # File operation risks
    file_operations = {
        'open(': 'File operation - ensure proper path validation and access controls',
        'fopen(': 'File operation in C - validate file paths and permissions',
        'file_get_contents(': 'File operation in PHP - validate file paths',
        'readFile(': 'File operation - ensure proper path validation',
        'writeFile(': 'File operation - validate paths and sanitize content',
        'fs.readFile(': 'Node.js file operation - validate file paths',
        'fs.writeFile(': 'Node.js file operation - validate paths and content',
        'File.ReadAllText(': '.NET file operation - validate file paths',
        'File.WriteAllText(': '.NET file operation - validate paths and content'
    }
    
    for func, warning in file_operations.items():
        if func in line_content and ('/' in line_content or '\\' in line_content or '..' in line_content):
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': f'File operation {func[:-1]}() with dynamic path detected',
                'detailed_explanation': f'This {func[:-1]}() operation includes file paths that could be manipulated by user input. This pattern is vulnerable to directory traversal attacks where attackers can access files outside the intended directory using sequences like "../" to navigate the file system.',
                'impact_assessment': 'Attackers could read sensitive configuration files, access user data, or potentially overwrite critical system files.',
                'fix_suggestion': 'Validate and sanitize all file paths, use allowlists for permitted directories, and consider using path normalization functions to prevent directory traversal.',
                'suggestion': '# TODO: Validate file paths to prevent directory traversal'
            })
    
    # Network/HTTP operations
    network_functions = {
        'requests.get(': 'HTTP request - validate URLs and handle SSL properly',
        'requests.post(': 'HTTP request - validate URLs and sanitize data',
        'urllib.request.urlopen(': 'URL operation - validate URLs and handle exceptions',
        'fetch(': 'Network request - validate URLs and handle errors',
        'XMLHttpRequest(': 'AJAX request - validate URLs and sanitize data',
        'HttpClient(': 'HTTP client - ensure proper SSL validation',
        'curl_exec(': 'cURL operation in PHP - validate URLs and options',
        'wget(': 'Network download - validate URLs',
        'curl(': 'Network operation - validate URLs and options'
    }
    
    for func, warning in network_functions.items():
        if func in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'medium',
                'message': f'Network operation {func[:-1]}() detected',
                'detailed_explanation': f'This {func[:-1]}() function makes network requests which can be vulnerable to various attacks including man-in-the-middle attacks, SSL/TLS bypass, and server-side request forgery (SSRF) if URLs are not properly validated.',
                'impact_assessment': 'Attackers could intercept sensitive data, redirect requests to malicious servers, or use your application to attack internal systems.',
                'fix_suggestion': 'Ensure proper SSL certificate validation, validate all URLs against an allowlist, implement timeout controls, and use secure HTTP headers.',
                'suggestion': '# TODO: Ensure proper input validation and SSL verification'
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
                'message': 'Potential SQL injection vulnerability',
                'detailed_explanation': 'This code appears to construct SQL queries using string concatenation which is extremely vulnerable to SQL injection attacks. Attackers can manipulate input to modify the SQL query structure and gain unauthorized access to database.',
                'impact_assessment': 'SQL injection could allow attackers to read, modify, or delete any data in your database, bypass authentication, or even execute administrative operations.',
                'fix_suggestion': 'Use parameterized queries or prepared statements instead of string concatenation. Most database libraries provide safe methods for handling user input in SQL queries.',
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
            'scanf(': 'Use scanf_s() or limit input instead',
            'strncpy(': 'Ensure null termination with strncpy',
            'memcpy(': 'Validate buffer sizes to prevent overflow',
            'memmove(': 'Validate buffer sizes to prevent overflow',
            'alloca(': 'Use malloc() instead - alloca() can cause stack overflow'
        }
        
        for func, suggestion in unsafe_c_funcs.items():
            if func in line_content:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'high',
                    'message': f'Unsafe C function {func[:-1]}() detected',
                    'detailed_explanation': f'The {func[:-1]}() function is unsafe because it does not perform bounds checking, making it vulnerable to buffer overflow attacks. Attackers can exploit this to overwrite memory, execute arbitrary code, or crash the application.',
                    'impact_assessment': 'Buffer overflows can lead to code execution, data corruption, system crashes, or complete system compromise.',
                    'fix_suggestion': suggestion,
                    'suggestion': f'// TODO: Replace {func[:-1]}() with safer alternative'
                })
        
        # Memory management functions
        if 'malloc(' in line_content or 'calloc(' in line_content or 'realloc(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Memory allocation function detected',
                'detailed_explanation': 'This line allocates memory dynamically but every malloc(), calloc(), or realloc() call must have a corresponding free() call to prevent memory leaks. Memory leaks can cause application crashes and performance degradation.',
                'impact_assessment': 'Memory leaks can cause the application to consume increasing amounts of memory, leading to performance issues or system crashes.',
                'fix_suggestion': 'Ensure every memory allocation has a corresponding free() call, consider using smart pointers in C++, or implement proper error handling for allocation failures.',
                'suggestion': '// TODO: Ensure corresponding free() call exists'
            })
        
        # Pointer operations
        if '*' in line_content and ('=' in line_content or 'return' in line_content):
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Pointer operation detected',
                'detailed_explanation': 'This line involves pointer operations which can be dangerous if null pointers are dereferenced. Dereferencing null or invalid pointers leads to segmentation faults and application crashes.',
                'impact_assessment': 'Null pointer dereferences cause immediate application crashes and can potentially be exploited for denial of service attacks.',
                'fix_suggestion': 'Add null pointer checks before dereferencing pointers, use defensive programming practices, and consider using safer alternatives like references in C++.',
                'suggestion': '// TODO: Add null pointer validation'
            })
    
    elif file_ext in ['py', 'pyw']:
        # Python critical functions
        dangerous_python_funcs = {
            'eval(': 'Code injection risk - avoid dynamic code evaluation',
            'exec(': 'Code injection risk - avoid dynamic code execution',
            'compile(': 'Dynamic compilation risk - validate input',
            '__import__(': 'Dynamic import risk - validate module names',
            'getattr(': 'Attribute access risk - validate attribute names',
            'setattr(': 'Attribute modification risk - validate inputs',
            'delattr(': 'Attribute deletion risk - validate operations',
            'hasattr(': 'Attribute check - ensure safe usage'
        }
        
        for func, warning in dangerous_python_funcs.items():
            if func in line_content:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'high',
                    'message': f'Dangerous Python function {func[:-1]}() detected',
                    'detailed_explanation': f'The {func[:-1]}() function can execute arbitrary Python code, making it extremely vulnerable to code injection attacks. This function should never be used with untrusted input as it can execute any Python code string.',
                    'impact_assessment': 'Attackers could execute arbitrary Python code, access sensitive data, modify system files, or completely compromise your application.',
                    'fix_suggestion': f'Remove {func[:-1]}() entirely or replace with safer alternatives like ast.literal_eval() for safe evaluation of Python literals, or implement strict input validation and sandboxing.',
                    'suggestion': f'# CRITICAL: Review {func[:-1]}() usage for security'
                })
        
        # File operations with user input
        if ('open(' in line_content or 'file(' in line_content) and ('+' in line_content or 'input(' in line_content):
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'File operation with potential user input detected',
                'detailed_explanation': 'This file operation appears to use user input directly in file paths, which creates a path traversal vulnerability. Attackers can use sequences like "../" to access files outside the intended directory.',
                'impact_assessment': 'Attackers could read sensitive configuration files, access user data, or potentially write to unauthorized locations.',
                'fix_suggestion': 'Validate and sanitize all user input before using in file paths. Use os.path.join() with proper validation and consider implementing an allowlist of permitted directories.',
                'suggestion': '# TODO: Validate and sanitize file paths'
            })
        
        # Subprocess operations
        subprocess_funcs = ['subprocess.call(', 'subprocess.run(', 'subprocess.Popen(', 'os.system(']
        for func in subprocess_funcs:
            if func in line_content:
                if 'shell=True' in line_content:
                    issues.append({
                        'line': line_number,
                        'type': 'security',
                        'severity': 'critical',
                        'message': f'{func[:-1]}() with shell=True detected',
                        'detailed_explanation': f'Using {func[:-1]}() with shell=True is extremely dangerous as it enables shell injection attacks. The shell interprets special characters and command separators, allowing attackers to execute additional commands.',
                        'impact_assessment': 'Attackers could execute arbitrary system commands, gain shell access, steal sensitive data, or completely compromise the system.',
                        'fix_suggestion': 'Use shell=False and pass commands as a list instead of a string. This prevents shell interpretation and command injection attacks.',
                        'suggestion': 'Use shell=False and pass commands as list'
                    })
        
        if 'print(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'low',
                'message': 'Print statement detected in code',
                'detailed_explanation': 'Print statements are typically used for debugging and should not be left in production code. They can expose sensitive information in logs and indicate incomplete development.',
                'impact_assessment': 'Print statements could leak sensitive information to logs, create performance overhead, or indicate debugging code left in production.',
                'fix_suggestion': 'Replace print statements with proper logging using the logging module, which provides better control over log levels and output destinations.',
                'suggestion': line_content.replace('print(', 'logging.info(')
            })
    
    elif file_ext in ['js', 'jsx', 'ts', 'tsx']:
        # JavaScript/TypeScript dangerous functions
        dangerous_js_funcs = {
            'eval(': 'Code injection risk - avoid dynamic code evaluation',
            'Function(': 'Dynamic function creation - code injection risk',
            'setTimeout(': 'Check if using string instead of function',
            'setInterval(': 'Check if using string instead of function',
            'document.write(': 'XSS risk - use safer DOM manipulation',
            'innerHTML': 'XSS risk - use textContent or sanitize HTML',
            'outerHTML': 'XSS risk - use safer DOM manipulation',
            'insertAdjacentHTML': 'XSS risk - sanitize HTML content'
        }
        
        for func, warning in dangerous_js_funcs.items():
            if func in line_content:
                severity = 'critical' if func in ['eval(', 'Function('] else 'high'
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': severity,
                    'message': f'Dangerous JS function {func} - {warning}',
                    'suggestion': f'// CRITICAL: Review {func} usage for security'
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
    
    elif file_ext in ['java']:
        # Java dangerous functions
        dangerous_java_funcs = {
            'Runtime.getRuntime().exec(': 'Command injection risk - validate input',
            'ProcessBuilder(': 'Command injection risk - validate arguments',
            'Class.forName(': 'Dynamic class loading - validate class names',
            'Method.invoke(': 'Reflection risk - validate method calls',
            'URLClassLoader(': 'Dynamic class loading risk',
            'ScriptEngine.eval(': 'Script injection risk in Java'
        }
        
        for func, warning in dangerous_java_funcs.items():
            if func in line_content:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'high',
                    'message': f'Dangerous Java function {func[:-1]}() - {warning}',
                    'suggestion': f'// TODO: Review {func[:-1]}() for security implications'
                })
    
    elif file_ext in ['php']:
        # PHP dangerous functions
        dangerous_php_funcs = {
            'eval(': 'Code injection risk - avoid dynamic code evaluation',
            'exec(': 'Command injection risk - validate input',
            'shell_exec(': 'Command injection risk - validate input',
            'system(': 'Command injection risk - validate input',
            'passthru(': 'Command injection risk - validate input',
            'file_get_contents(': 'File inclusion risk with user input',
            'include(': 'File inclusion risk - validate file paths',
            'require(': 'File inclusion risk - validate file paths',
            'unserialize(': 'Object injection risk - validate input',
            'create_function(': 'Dynamic function creation - code injection risk'
        }
        
        for func, warning in dangerous_php_funcs.items():
            if func in line_content:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'critical' if func in ['eval(', 'unserialize('] else 'high',
                    'message': f'Dangerous PHP function {func[:-1]}() - {warning}',
                    'suggestion': f'// CRITICAL: Review {func[:-1]}() usage for security'
                })
    
    elif file_ext == 'rs':
        # Rust potentially unsafe patterns
        if 'unwrap()' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'unwrap() usage - consider proper error handling',
                'suggestion': line_content.replace('.unwrap()', '.expect("description")')
            })
        
        if 'unsafe' in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'Unsafe Rust code block - review for memory safety',
                'suggestion': '// TODO: Document why unsafe is necessary and ensure safety'
            })
        
        if 'println!' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'low',
                'message': 'Remove println! in production code',
                'suggestion': ''
            })
    
    elif file_ext in ['go']:
        # Go dangerous patterns
        if 'exec.Command(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'Command execution - validate input to prevent injection',
                'suggestion': '// TODO: Validate command arguments and avoid user input'
            })
        
        if 'unsafe.' in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'Unsafe Go code - review for memory safety',
                'suggestion': '// TODO: Document why unsafe is necessary'
            })
    
    return issues


def detect_quality_issues(line_content, line_number):
    """Detect universal quality issues"""
    issues = []
    
    # Comment analysis - expanded critical patterns
    comment_patterns = [
        r'^//\s*(test|debug|hello|todo|fixme|hack|temp|temporary|remove|delete)',  # C-style comments
        r'^#\s*(test|debug|hello|todo|fixme|hack|temp|temporary|remove|delete)',   # Python/Shell comments
        r'^\*\s*(test|debug|hello|todo|fixme|hack|temp|temporary|remove|delete)',  # Block comment lines
        r'^<!--\s*(test|debug|hello|todo|fixme|hack|temp|temporary|remove|delete)' # HTML comments
    ]
    
    for pattern in comment_patterns:
        if re.match(pattern, line_content.lower()):
            comment_type = re.match(pattern, line_content.lower()).group(1)
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium', 
                'message': f'Temporary {comment_type} comment detected',
                'detailed_explanation': f'This appears to be a {comment_type} comment that indicates incomplete development or testing code. Such comments should be removed before production deployment as they may contain sensitive information or indicate unfinished functionality.',
                'impact_assessment': 'Temporary comments can confuse future developers, expose development practices, or indicate incomplete features that could cause issues.',
                'fix_suggestion': f'Remove this {comment_type} comment or replace it with proper documentation if the information is needed for maintenance.',
                'suggestion': ''
            })
    
    # Function definition patterns - check for critical functions
    function_patterns = {
        'def authenticate(': 'Authentication function - ensure secure implementation',
        'def login(': 'Login function - implement proper security measures',
        'def password(': 'Password function - ensure secure handling',
        'def admin(': 'Admin function - implement proper authorization',
        'def delete(': 'Delete function - implement confirmation and backup',
        'def remove(': 'Remove function - implement safety checks',
        'def drop(': 'Drop function - implement safety measures',
        'def execute(': 'Execute function - validate input to prevent injection',
        'def run(': 'Run function - validate input and implement safety checks',
        'def eval(': 'Eval function - avoid or implement strict validation',
        'function authenticate(': 'Authentication function - ensure secure implementation',
        'function login(': 'Login function - implement proper security measures',
        'function password(': 'Password function - ensure secure handling',
        'function admin(': 'Admin function - implement proper authorization',
        'function delete(': 'Delete function - implement confirmation and backup',
        'function execute(': 'Execute function - validate input to prevent injection'
    }
    
    for pattern, warning in function_patterns.items():
        if pattern in line_content.lower():
            func_name = pattern.split('(')[0].replace('def ', '').replace('function ', '')
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': f'Critical function {func_name}() detected',
                'detailed_explanation': f'This {func_name}() function performs security-sensitive operations that require careful implementation. Such functions are common targets for attackers and must be implemented with proper security controls.',
                'impact_assessment': 'Improperly implemented security functions can lead to authentication bypass, privilege escalation, or unauthorized access to sensitive data.',
                'fix_suggestion': f'Ensure this {func_name}() function implements proper input validation, error handling, logging, and follows security best practices for {func_name.replace("_", " ")} operations.',
                'suggestion': f'// TODO: Review {func_name}() function security implementation'
            })
    
    # Database operation patterns
    db_operations = [
        'DROP TABLE', 'DELETE FROM', 'TRUNCATE', 'ALTER TABLE', 'DROP DATABASE',
        'UPDATE ', 'INSERT INTO', 'CREATE TABLE', 'GRANT ', 'REVOKE ',
        '.execute(', '.query(', '.rawQuery(', 'executeQuery(', 'executeUpdate('
    ]
    
    for operation in db_operations:
        if operation in line_content:
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'medium',
                'message': f'Database operation {operation.strip()} detected',
                'detailed_explanation': f'This line contains a database operation ({operation.strip()}) which requires careful handling to prevent SQL injection and ensure proper authorization. Database operations should always use parameterized queries and proper access controls.',
                'impact_assessment': 'Improper database operations can lead to SQL injection attacks, unauthorized data access, data corruption, or complete database compromise.',
                'fix_suggestion': 'Use parameterized queries or prepared statements, implement proper input validation, and ensure appropriate user permissions for database operations.',
                'suggestion': '// TODO: Validate input and implement proper access controls'
            })
    
    # Cryptographic function usage
    crypto_patterns = [
        'md5(', 'sha1(', 'MD5(', 'SHA1(',  # Weak hashing
        'encrypt(', 'decrypt(', 'hash(', 'crypto.', 'cipher.',
        'AES.', 'DES.', 'RSA.', 'bcrypt.', 'scrypt.',
        'random(', 'Math.random(', 'rand(', 'srand('  # Random number generation
    ]
    
    for pattern in crypto_patterns:
        if pattern in line_content:
            if pattern.lower() in ['md5(', 'sha1(']:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'high',
                    'message': f'Weak cryptographic function {pattern[:-1]}() detected',
                    'detailed_explanation': f'The {pattern[:-1]}() function uses a cryptographically weak hashing algorithm that is vulnerable to collision attacks and rainbow table attacks. MD5 and SHA1 are no longer considered secure for cryptographic purposes.',
                    'impact_assessment': 'Weak hashing algorithms can be broken by attackers, allowing them to forge digital signatures, crack password hashes, or create hash collisions.',
                    'fix_suggestion': 'Replace with stronger hashing algorithms like SHA-256, SHA-3, or use bcrypt/scrypt for password hashing which includes built-in salting and key stretching.',
                    'suggestion': '// TODO: Use SHA-256 or stronger hashing algorithm'
                })
            else:
                issues.append({
                    'line': line_number,
                    'type': 'security',
                    'severity': 'medium',
                    'message': f'Cryptographic operation detected - ensure proper implementation',
                    'suggestion': '// TODO: Review cryptographic implementation for security'
                })
    
    # Error handling patterns
    error_handling = ['try:', 'catch(', 'except:', 'rescue', 'defer', 'finally:']
    if any(pattern in line_content for pattern in error_handling):
        # Check if error is being suppressed
        if ('pass' in line_content or 'continue' in line_content or '// ignore' in line_content.lower()):
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Error suppression detected - ensure proper error handling',
                'suggestion': '// TODO: Implement proper error logging and handling'
            })
    
    # Division by zero check
    if '/' in line_content and ('return' in line_content or '=' in line_content):
        if 'if' not in line_content and '//' not in line_content and '/*' not in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Division operation without zero check',
                'suggestion': '// TODO: Add zero division check'
            })
    
    # Memory allocation without bounds check
    allocation_patterns = ['malloc(', 'calloc(', 'realloc(', 'new ', 'new[]', 'alloc(']
    for pattern in allocation_patterns:
        if pattern in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': f'Memory allocation {pattern[:-1]}() - ensure bounds checking and proper cleanup',
                'suggestion': '// TODO: Validate allocation size and ensure proper deallocation'
            })
    
    # Hardcoded values that might need configuration
    if re.search(r':\s*\d{3,5}\s*[,;}]', line_content):  # Port numbers
        issues.append({
            'line': line_number,
            'type': 'quality',
            'severity': 'low',
            'message': 'Hardcoded port number - consider using configuration',
            'suggestion': '// TODO: Move port number to configuration file'
        })
    
    if re.search(r'(http://|https://)[^\s\'"]+', line_content):  # URLs
        issues.append({
            'line': line_number,
            'type': 'quality',
            'severity': 'low',
            'message': 'Hardcoded URL - consider using configuration',
            'suggestion': '// TODO: Move URL to configuration file'
        })
    
    # Thread/concurrency operations
    thread_patterns = ['Thread(', 'threading.', 'async ', 'await ', 'Promise(', 'Future(', 'goroutine']
    for pattern in thread_patterns:
        if pattern in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': f'Concurrency operation {pattern} - ensure thread safety',
                'suggestion': '// TODO: Review for race conditions and thread safety'
            })
    
    return issues


def format_review_comment(issue):
    """Format issue as GitHub review comment"""
    severity = issue.get('severity', 'medium')
    message = issue.get('message', 'Issue detected')
    suggestion = issue.get('suggestion', '')
    
    # Format comment based on severity
    if severity == 'critical':
        icon = '🔴'
        label = 'CRITICAL Risk'
    elif severity == 'high':
        icon = '🚨'
        label = 'High Risk'
    elif severity == 'medium':
        icon = '⚠️'
        label = 'Warning'
    else:
        icon = '💡'
        label = 'Suggestion'
    
    # Build detailed comment using 4-line format
    detailed_explanation = issue.get('detailed_explanation', '')
    impact_assessment = issue.get('impact_assessment', '')
    fix_suggestion = issue.get('fix_suggestion', '')
    
    comment_body = f"{icon} **{label}: {message}**\n\n"
    
    if detailed_explanation:
        comment_body += f"**Detailed Explanation:** {detailed_explanation}\n\n"
    else:
        comment_body += f"**Detailed Explanation:** This code pattern has been identified as potentially problematic and may introduce security or quality issues.\n\n"
    
    if impact_assessment:
        comment_body += f"**Impact Assessment:** {impact_assessment}\n\n"
    else:
        comment_body += f"**Impact Assessment:** If not addressed, this could lead to security vulnerabilities or code maintainability issues.\n\n"
    
    if fix_suggestion:
        comment_body += f"**Specific Fix Suggestion:** {fix_suggestion}\n\n"
    else:
        comment_body += f"**Specific Fix Suggestion:** Review and refactor this code following security best practices and coding standards.\n\n"
    
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
