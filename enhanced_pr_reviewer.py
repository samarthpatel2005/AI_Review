#!/usr/bin/env python3
"""
Enhanced GitHub Pull Request Reviewer using AWS Bedrock
Works like GitHub Copilot with inline comments and commit suggestions.
"""

import json
import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from urllib.parse import urlparse

try:
    import boto3
    import requests
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: Required packages not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class EnhancedGitHubPRReviewer:
    def __init__(self, region_name: str = "us-east-1", model_id: str = "amazon.nova-micro-v1:0"):
        """Initialize the Enhanced GitHub PR Reviewer."""
        self.region_name = region_name
        self.model_id = model_id
        self.github_token = os.environ.get('GITHUB_TOKEN')
        
        try:
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.region_name
            )
            print(f"✅ Enhanced GitHub PR Reviewer ready! Using: {self.model_id}")
        except NoCredentialsError:
            print("❌ Error: AWS credentials not found!")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def parse_pr_url(self, pr_url: str) -> Optional[Dict]:
        """Parse GitHub PR URL and extract repository and PR number."""
        pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.match(pattern, pr_url)
        
        if not match:
            print(f"❌ Invalid PR URL format: {pr_url}")
            return None
        
        owner, repo, pr_number = match.groups()
        
        return {
            'owner': owner,
            'repo': repo,
            'pr_number': int(pr_number),
            'full_name': f"{owner}/{repo}",
            'api_url': f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        }

    def get_github_headers(self) -> Dict:
        """Get GitHub API headers with authentication."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Enhanced-GitHub-PR-Reviewer'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        return headers

    def get_pr_files(self, pr_info: Dict) -> List[Dict]:
        """Get list of files changed in the PR with their diffs."""
        try:
            headers = self.get_github_headers()
            
            # Get files changed in PR
            files_url = f"{pr_info['api_url']}/files"
            response = requests.get(files_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            files_data = response.json()
            
            # Filter code files only
            code_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.cs', '.scala', '.sh', '.yml', '.yaml', '.json'}
            
            code_files = []
            for file_data in files_data:
                filename = file_data.get('filename', '')
                if any(filename.endswith(ext) for ext in code_extensions):
                    code_files.append({
                        'filename': filename,
                        'status': file_data.get('status', ''),
                        'additions': file_data.get('additions', 0),
                        'deletions': file_data.get('deletions', 0),
                        'changes': file_data.get('changes', 0),
                        'patch': file_data.get('patch', ''),
                        'sha': file_data.get('sha', ''),
                        'raw_url': file_data.get('raw_url', '')
                    })
            
            return code_files
            
        except Exception as e:
            print(f"❌ Error fetching PR files: {e}")
            return []

    def parse_diff_for_line_numbers(self, patch: str) -> List[Dict]:
        """Parse diff patch to extract line numbers and changes."""
        lines = patch.split('\n')
        changes = []
        old_line = 0
        new_line = 0
        
        for line in lines:
            if line.startswith('@@'):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                hunk_match = re.match(r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if hunk_match:
                    old_line = int(hunk_match.group(1)) - 1
                    new_line = int(hunk_match.group(2)) - 1
            elif line.startswith('-'):
                old_line += 1
                changes.append({
                    'type': 'deleted',
                    'old_line': old_line,
                    'new_line': None,
                    'content': line[1:],  # Remove the - prefix
                    'full_line': line
                })
            elif line.startswith('+'):
                new_line += 1
                changes.append({
                    'type': 'added',
                    'old_line': None,
                    'new_line': new_line,
                    'content': line[1:],  # Remove the + prefix
                    'full_line': line
                })
            elif line.startswith(' '):
                old_line += 1
                new_line += 1
                changes.append({
                    'type': 'context',
                    'old_line': old_line,
                    'new_line': new_line,
                    'content': line[1:],  # Remove the space prefix
                    'full_line': line
                })
        
        return changes

    def analyze_code_with_ai(self, file_changes: List[Dict]) -> List[Dict]:
        """Analyze code changes with AI and return inline comments."""
        all_comments = []
        
        for file_data in file_changes:
            filename = file_data['filename']
            patch = file_data['patch']
            
            if not patch.strip():
                continue
            
            # Parse diff for line analysis
            diff_lines = self.parse_diff_for_line_numbers(patch)
            added_lines = [line for line in diff_lines if line['type'] == 'added']
            
            if not added_lines:
                continue
            
            # Create focused prompt for this file
            prompt = self.create_file_analysis_prompt(filename, patch, added_lines)
            
            try:
                # Get AI analysis
                analysis = self.get_ai_analysis(prompt)
                
                # Parse AI response for specific line comments
                file_comments = self.parse_ai_analysis_for_comments(analysis, filename, added_lines)
                all_comments.extend(file_comments)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {filename}: {e}")
                continue
        
        return all_comments

    def create_file_analysis_prompt(self, filename: str, patch: str, added_lines: List[Dict]) -> str:
        """Create AI prompt for analyzing a specific file."""
        prompt = f"""Analyze this code change in file: {filename}

DIFF PATCH:
```diff
{patch}
```

Focus on these added lines:
{chr(10).join([f"Line {line['new_line']}: {line['content']}" for line in added_lines[:10]])}

Provide analysis in this JSON format:
{{
  "comments": [
    {{
      "line": <line_number>,
      "message": "Brief, clear description of the issue (like GitHub Copilot)",
      "suggested_code": "EXACT single line replacement"
    }}
  ]
}}

RULES:
1. Write messages like GitHub Copilot - simple and direct
2. For "suggested_code", provide ONLY the exact replacement for that line
3. Focus on real issues: security, bugs, important style problems
4. Skip minor issues - only flag meaningful problems
5. Keep messages short and clear

Example good messages:
- "This test comment should be removed before merging to production as it appears to be temporary debugging or testing code that doesn't add value to the codebase."
- "The comment lacks proper spacing. It should be '# For test' with a space after the hash symbol to follow Python commenting conventions."
- "Use environment variables instead of hardcoded passwords."
- "Add error handling to prevent division by zero."

Only comment on actual problems that need fixing."""
        
        return prompt

    def get_ai_analysis(self, prompt: str) -> str:
        """Get AI analysis from AWS Bedrock."""
        try:
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 2000,
                    "temperature": 0.1,
                    "topP": 0.8
                }
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            result = json.loads(response['body'].read())
            return result['output']['message']['content'][0]['text']
            
        except Exception as e:
            print(f"❌ Error getting AI analysis: {e}")
            return ""

    def parse_ai_analysis_for_comments(self, analysis: str, filename: str, added_lines: List[Dict]) -> List[Dict]:
        """Parse AI analysis response and create simple GitHub review comments like Copilot."""
        comments = []
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\n(.*?)\n```', analysis, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    print(f"⚠️ Could not extract JSON from AI response for {filename}")
                    return comments
            
            data = json.loads(json_str)
            
            for comment_data in data.get('comments', []):
                line_num = comment_data.get('line')
                message = comment_data.get('message', '')
                suggested_code = comment_data.get('suggested_code', '')
                
                # Find the corresponding line in our diff
                matching_line = None
                for line in added_lines:
                    if line['new_line'] == line_num:
                        matching_line = line
                        break
                
                if matching_line:
                    # Create simple comment like GitHub Copilot (from your image)
                    comment_body = message
                    
                    # Add GitHub's suggested changes format if we have suggested code
                    if suggested_code:
                        comment_body += f"\n\n**Suggested change**\n```suggestion\n{suggested_code}\n```"
                    
                    comments.append({
                        'filename': filename,
                        'line': line_num,
                        'body': comment_body,
                        'severity': comment_data.get('severity', 'suggestion'),
                        'type': comment_data.get('type', 'general'),
                        'suggested_code': suggested_code,
                        'original_code': matching_line['content']
                    })
        
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing AI JSON response for {filename}: {e}")
        except Exception as e:
            print(f"⚠️ Error processing AI analysis for {filename}: {e}")
        
        return comments

    def get_file_language(self, filename: str) -> str:
        """Get programming language from filename."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
            '.scala': 'scala',
            '.sh': 'bash',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json'
        }
        
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        
        return 'text'

    def post_review_comments(self, pr_info: Dict, comments: List[Dict]) -> bool:
        """Post inline review comments to GitHub PR - NO SUMMARY, only inline suggestions."""
        if not self.github_token:
            print("⚠️ No GitHub token available. Cannot post comments.")
            return False
        
        if not comments:
            print("ℹ️ No issues found. No comments to post.")
            return True
        
        try:
            headers = self.get_github_headers()
            
            # Get PR metadata for commit SHA
            response = requests.get(pr_info['api_url'], headers=headers, timeout=30)
            response.raise_for_status()
            pr_data = response.json()
            commit_sha = pr_data['head']['sha']
            
            # Create a review with ONLY inline comments (no summary)
            review_url = f"{pr_info['api_url']}/reviews"
            
            # Format comments for GitHub review API
            review_comments = []
            for comment in comments:
                review_comments.append({
                    'path': comment['filename'],
                    'line': comment['line'],
                    'body': comment['body']
                })
            
            # NO SUMMARY - just post the inline comments
            review_data = {
                'commit_id': commit_sha,
                'event': 'COMMENT',  # Always use COMMENT to avoid blocking PRs
                'comments': review_comments
            }
            
            response = requests.post(review_url, headers=headers, json=review_data, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Posted {len(comments)} inline suggestions (no summary)")
            return True
            
        except Exception as e:
            print(f"❌ Error posting review comments: {e}")
            return False

    def create_commit_suggestions(self, comments: List[Dict]) -> List[Dict]:
        """Create commit suggestions from AI comments."""
        suggestions = []
        
        for comment in comments:
            if comment.get('suggested_code') and comment['severity'] in ['critical', 'high', 'medium']:
                suggestions.append({
                    'filename': comment['filename'],
                    'line': comment['line'],
                    'original_code': '',  # Would need to get from file
                    'suggested_code': comment['suggested_code'],
                    'reason': f"{comment['type'].title()}: {comment['body'].split('**')[2] if '**' in comment['body'] else comment['body'][:100]}..."
                })
        
        return suggestions

    def review_pull_request(self, pr_url: str) -> bool:
        """Main method to review a GitHub Pull Request with inline comments."""
        print(f"🔍 Starting enhanced review of PR: {pr_url}")
        
        # Parse PR URL
        pr_info = self.parse_pr_url(pr_url)
        if not pr_info:
            return False
        
        print(f"📋 PR #{pr_info['pr_number']} in {pr_info['full_name']}")
        
        # Get PR files and metadata
        files_changed = self.get_pr_files(pr_info)
        
        if not files_changed:
            print("ℹ️ No code files to review in this PR")
            return True
        
        print(f"📁 Found {len(files_changed)} code files to review")
        
        # Analyze files with AI
        comments = self.analyze_code_with_ai(files_changed)
        
        if not comments:
            print("✅ No issues found! Code looks good.")
            # Post a simple approval comment
            if self.github_token:
                self.post_approval_comment(pr_info)
            return True
        
        print(f"📝 Generated {len(comments)} review comments")
        
        # Post inline comments
        success = self.post_review_comments(pr_info, comments)
        
        # Create commit suggestions
        suggestions = self.create_commit_suggestions(comments)
        if suggestions:
            print(f"💡 Generated {len(suggestions)} commit suggestions")
        
        return success

    def post_approval_comment(self, pr_info: Dict):
        """Post a simple inline comment when no issues are found - NO SUMMARY."""
        try:
            headers = self.get_github_headers()
            comment_url = f"https://api.github.com/repos/{pr_info['full_name']}/issues/{pr_info['pr_number']}/comments"
            
            # Simple, short approval message
            comment_body = "✅ No issues found! Code looks good to merge."
            
            response = requests.post(comment_url, headers=headers, json={'body': comment_body}, timeout=30)
            response.raise_for_status()
            print("✅ Posted simple approval comment")
            
        except Exception as e:
            print(f"⚠️ Error posting approval comment: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Enhanced GitHub Pull Request Reviewer with inline comments (like GitHub Copilot)",
        epilog="""
Examples:
  %(prog)s https://github.com/owner/repo/pull/123
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("pr_url", help="GitHub Pull Request URL")
    parser.add_argument("--model", default="amazon.nova-micro-v1:0", help="Bedrock model ID")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    
    args = parser.parse_args()
    
    print("🚀 Enhanced GitHub Pull Request Reviewer")
    print("=" * 50)
    
    # Initialize reviewer
    reviewer = EnhancedGitHubPRReviewer(region_name=args.region, model_id=args.model)
    
    # Review the PR
    success = reviewer.review_pull_request(args.pr_url)
    
    if success:
        print("\n🎉 Enhanced Pull Request review completed successfully!")
        print("💬 Check the PR for inline comments and suggestions!")
    else:
        print("\n❌ Pull Request review failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()