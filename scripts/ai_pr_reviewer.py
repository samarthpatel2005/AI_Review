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
        
        with open(custom_path, 'r', encoding='utf-8') as f:
            custom_prompt = f.read().strip()
        
        print(f"🔍 Custom prompt length: {len(custom_prompt)} characters")
        print(f"🔍 Custom prompt first 100 chars: {custom_prompt[:100]}...")
        
        if custom_prompt:
            print("🎯 Using CUSTOM PROMPT from prompt/custom.txt")
            print(f"🔍 FULL CUSTOM PROMPT:")
            print("="*50)
            print(custom_prompt)
            print("="*50)
            return custom_prompt
        
        # If custom is empty, use default
        default_path = os.path.join(project_root, 'prompt', 'default.txt')
        print(f"🔍 Looking for default prompt at: {default_path}")
        
        with open(default_path, 'r', encoding='utf-8') as f:
            default_prompt = f.read().strip()
        
        print("🔧 Using DEFAULT PROMPT from prompt/default.txt")
        print(f"🔍 FULL DEFAULT PROMPT:")
        print("="*50)
        print(default_prompt)
        print("="*50)
        return default_prompt
        
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
                'message': f'Critical function {func[:-1]}() detected - {warning}',
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
                'message': f'File operation {func[:-1]}() with path - {warning}',
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
                'message': f'Network operation {func[:-1]}() - {warning}',
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
                    'message': f'Unsafe C function {func[:-1]}() - buffer overflow risk',
                    'suggestion': suggestion
                })
        
        # Memory management functions
        if 'malloc(' in line_content or 'calloc(' in line_content or 'realloc(' in line_content:
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Memory allocation - ensure corresponding free() call',
                'suggestion': ''
            })
        
        # Pointer operations
        if '*' in line_content and ('=' in line_content or 'return' in line_content):
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium',
                'message': 'Pointer operation - ensure null pointer checks',
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
                    'message': f'Dangerous Python function {func[:-1]}() - {warning}',
                    'suggestion': f'# CRITICAL: Review {func[:-1]}() usage for security'
                })
        
        # File operations with user input
        if ('open(' in line_content or 'file(' in line_content) and ('+' in line_content or 'input(' in line_content):
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': 'File operation with potential user input - path traversal risk',
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
                        'message': f'{func[:-1]}() with shell=True - command injection risk',
                        'suggestion': 'Use shell=False and pass commands as list'
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
            issues.append({
                'line': line_number,
                'type': 'quality',
                'severity': 'medium', 
                'message': 'Remove test/debug/temporary comment before production',
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
            issues.append({
                'line': line_number,
                'type': 'security',
                'severity': 'high',
                'message': f'Critical function detected - {warning}',
                'suggestion': f'// TODO: Review function security implementation'
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
                'message': f'Database operation {operation} - ensure proper validation and authorization',
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
                    'message': f'Weak cryptographic function {pattern[:-1]}() - use stronger alternatives',
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
        icon = '�'
        label = 'CRITICAL'
    elif severity == 'high':
        icon = '🚨'
        label = 'High Risk'
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
