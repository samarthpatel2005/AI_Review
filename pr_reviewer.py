#!/usr/bin/env python3
"""
GitHub Pull Request Diff Reviewer using AWS Bedrock
Reviews only the changed code in GitHub Pull Requests.
"""

import json
import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
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


class GitHubPRReviewer:
    def __init__(self, region_name: str = "us-east-1", model_id: str = "amazon.nova-micro-v1:0"):
        """Initialize the GitHub PR Reviewer."""
        self.region_name = region_name
        self.model_id = model_id
        
        try:
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.region_name
            )
            print(f"✅ GitHub PR Reviewer ready! Using: {self.model_id}")
        except NoCredentialsError:
            print("❌ Error: AWS credentials not found!")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def extract_pr_info(self, pr_url: str) -> Optional[Dict]:
        """
        Extract PR information from GitHub URL.
        
        Example: https://github.com/owner/repo/pull/123
        Returns: {'owner': 'owner', 'repo': 'repo', 'pr_number': '123'}
        """
        pr_pattern = r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.match(pr_pattern, pr_url)
        
        if match:
            owner, repo, pr_number = match.groups()
            return {
                'owner': owner,
                'repo': repo,
                'pr_number': pr_number,
                'api_url': f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
            }
        return None

    def get_pr_diff(self, pr_info: Dict) -> Optional[str]:
        """
        Get the diff content from GitHub PR API.
        """
        try:
            # Get PR details
            print(f"🔄 Fetching PR #{pr_info['pr_number']} from {pr_info['owner']}/{pr_info['repo']}")
            
            headers = {
                'Accept': 'application/vnd.github.v3.diff',
                'User-Agent': 'GitHub-PR-Reviewer'
            }
            
            response = requests.get(pr_info['api_url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            diff_content = response.text
            print(f"✅ Retrieved diff ({len(diff_content)} characters)")
            
            return diff_content
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching PR diff: {e}")
            return None

    def get_pr_metadata(self, pr_info: Dict) -> Optional[Dict]:
        """
        Get PR metadata (title, description, etc.)
        """
        try:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-PR-Reviewer'
            }
            
            response = requests.get(pr_info['api_url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'title': data.get('title', 'No title'),
                'body': data.get('body', 'No description'),
                'author': data.get('user', {}).get('login', 'Unknown'),
                'created_at': data.get('created_at', ''),
                'state': data.get('state', 'unknown'),
                'base_branch': data.get('base', {}).get('ref', 'unknown'),
                'head_branch': data.get('head', {}).get('ref', 'unknown'),
                'files_changed': data.get('changed_files', 0),
                'additions': data.get('additions', 0),
                'deletions': data.get('deletions', 0)
            }
            
        except Exception as e:
            print(f"❌ Error fetching PR metadata: {e}")
            return None

    def filter_code_files_diff(self, diff_content: str) -> str:
        """
        Filter diff to include relevant code files (C/C++, Python, etc.).
        """
        code_extensions = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.py', '.java', '.js', '.ts', '.go', '.rs'}
        
        lines = diff_content.split('\n')
        filtered_lines = []
        include_section = False
        
        for line in lines:
            # Check for file headers in diff
            if line.startswith('diff --git'):
                # Extract filename
                parts = line.split(' ')
                if len(parts) >= 4:
                    filename = parts[3]  # b/filename
                    if any(filename.endswith(ext) for ext in code_extensions):
                        include_section = True
                        filtered_lines.append(line)
                    else:
                        include_section = False
            elif include_section:
                filtered_lines.append(line)
            elif line.startswith('@@') and include_section:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def create_pr_review_prompt(self, diff_content: str, metadata: Dict) -> str:
        """
        Create a focused prompt for PR diff review.
        """
        prompt = f"""Review this GitHub Pull Request diff for code changes:

**PR INFORMATION:**
- Title: {metadata.get('title', 'N/A')}
- Author: {metadata.get('author', 'N/A')}
- Branch: {metadata.get('head_branch', 'N/A')} → {metadata.get('base_branch', 'N/A')}
- Files Changed: {metadata.get('files_changed', 0)}
- Lines: +{metadata.get('additions', 0)} -{metadata.get('deletions', 0)}

**DIFF TO REVIEW:**
```diff
{diff_content}
```

**FOCUS ON THESE AREAS:**

1. **LOGIC ERRORS in modifications:**
   - Incorrect algorithms or conditions
   - Off-by-one errors
   - Null/undefined checks

2. **SECURITY ISSUES in changed code:**
   - Input validation problems
   - Authentication/authorization issues
   - Data exposure risks

3. **CODE QUALITY of modifications:**
   - Code readability and style
   - Error handling improvements/regressions
   - Function design changes
   - Performance implications

4. **COMPATIBILITY & INTEGRATION:**
   - Breaking changes
   - API consistency
   - Backward compatibility
   - Dependencies and imports

5. **TESTING & MAINTAINABILITY:**
   - Test coverage for changes
   - Documentation updates needed
   - Code complexity

**PROVIDE:**
- Line-by-line analysis of problematic changes
- Severity: CRITICAL/HIGH/MEDIUM/LOW
- Specific improvement suggestions
- Overall assessment: APPROVE/REQUEST_CHANGES/COMMENT

Focus only on the CHANGED lines (+ and -), not the entire file context."""

        return prompt

    def review_pr_diff(self, diff_content: str, metadata: Dict) -> Optional[str]:
        """
        Review PR diff using AWS Bedrock.
        """
        try:
            # Filter to only code files
            code_diff = self.filter_code_files_diff(diff_content)
            
            if not code_diff.strip():
                return "No code files found in this PR diff. Only documentation or configuration files were changed."
            
            prompt = self.create_pr_review_prompt(code_diff, metadata)
            
            # Limit diff size for API
            if len(prompt) > 50000:
                print("⚠️ Diff is very large, truncating for analysis...")
                prompt = prompt[:50000] + "\n\n[TRUNCATED - Large diff]"
            
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 2500,
                    "temperature": 0.1,  # Very focused for code review
                    "topP": 0.8
                }
            }
            
            print("🔍 Analyzing PR diff with AI...")
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response["body"].read())
            review_text = response_body["output"]["message"]["content"][0]["text"]
            
            return review_text
            
        except Exception as e:
            print(f"❌ Error during PR review: {e}")
            return f"Error occurred during review: {str(e)}"

    def save_pr_review(self, review_text: str, pr_info: Dict, metadata: Dict, output_dir: str = None) -> str:
        """
        Save the PR review to a text file.
        """
        try:
            print(f"🔧 Debug - pr_info keys: {list(pr_info.keys()) if pr_info else 'None'}")
            print(f"🔧 Debug - metadata keys: {list(metadata.keys()) if metadata else 'None'}")
            print(f"🔧 Debug - review_text length: {len(review_text) if review_text else 'None'}")
            
            # Determine output directory
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
            else:
                output_path = Path(".")
            
            # Generate review filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pr_number = pr_info.get('pr_number', 'unknown')
            review_filename = f"PR_{pr_number}_review_{timestamp}.txt"
            review_file_path = output_path / review_filename
            
            # Create header
            description = metadata.get('body') or 'No description'
            if len(description) > 500:
                description = description[:500] + "..."
            
            header = f"""
{'='*80}
                    GITHUB PULL REQUEST REVIEW
{'='*80}
Repository: {pr_info.get('owner', 'N/A')}/{pr_info.get('repo', 'N/A')}
PR Number: #{pr_info.get('pr_number', 'N/A')}
PR Title: {metadata.get('title', 'N/A')}
Author: {metadata.get('author', 'N/A')}
Branch: {metadata.get('head_branch', 'N/A')} → {metadata.get('base_branch', 'N/A')}
Files Changed: {metadata.get('files_changed', 0)}
Lines: +{metadata.get('additions', 0)} -{metadata.get('deletions', 0)}
State: {metadata.get('state', 'unknown').upper()}
Review Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
AI Model: {self.model_id}
{'='*80}

DESCRIPTION:
{description}

{'='*80}
DIFF REVIEW:
{'='*80}

"""
            
            # Write review
            with open(review_file_path, 'w', encoding='utf-8') as file:
                file.write(header)
                file.write(review_text)
                file.write(f"\n\n{'='*80}\n")
                file.write("End of PR Review\n")
                file.write(f"{'='*80}\n")
            
            return str(review_file_path)
            
        except Exception as e:
            print(f"❌ Error saving review: {e}")
            return None

    def review_pull_request(self, pr_url: str, output_dir: str = None) -> bool:
        """
        Review a GitHub Pull Request.
        """
        print(f"\n🔗 Processing PR: {pr_url}")
        
        # Extract PR info
        pr_info = self.extract_pr_info(pr_url)
        if not pr_info:
            print("❌ Invalid GitHub PR URL format!")
            print("Expected format: https://github.com/owner/repo/pull/123")
            return False
        
        # Get PR metadata
        metadata = self.get_pr_metadata(pr_info)
        if not metadata:
            return False
        
        print(f"📋 PR: {metadata['title']}")
        print(f"👤 Author: {metadata['author']}")
        print(f"📊 Changes: {metadata['files_changed']} files, +{metadata['additions']} -{metadata['deletions']} lines")
        
        # Get PR diff
        diff_content = self.get_pr_diff(pr_info)
        if not diff_content:
            return False
        
        # Review the diff
        review = self.review_pr_diff(diff_content, metadata)
        if not review:
            print("❌ Failed to generate review")
            return False
        
        # Save review
        review_file = self.save_pr_review(review, pr_info, metadata, output_dir)
        if review_file:
            print(f"✅ PR review saved to: {review_file}")
            return True
        else:
            print("❌ Failed to save review")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Review GitHub Pull Request diffs using AWS Bedrock",
        epilog="""
Examples:
  %(prog)s https://github.com/owner/repo/pull/123
  %(prog)s https://github.com/owner/repo/pull/456 -o reviews/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("pr_url", help="GitHub Pull Request URL")
    parser.add_argument("-o", "--output", help="Output directory for review files")
    parser.add_argument("--model", default="amazon.nova-micro-v1:0", help="Bedrock model ID")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    
    args = parser.parse_args()
    
    print("🔍 GitHub Pull Request Reviewer")
    print("=" * 50)
    
    # Initialize reviewer
    reviewer = GitHubPRReviewer(region_name=args.region, model_id=args.model)
    
    # Review the PR
    success = reviewer.review_pull_request(args.pr_url, args.output)
    
    if success:
        print("\n🎉 Pull Request review completed successfully!")
    else:
        print("\n❌ Pull Request review failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
