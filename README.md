# AWS Bedrock AI Tools

This repository contains AI-powered tools using AWS Bedrock:

1. **Simple Chatbot** - Interactive command-line chatbot
2. **C Code Reviewer** - Automated code review system for C/C++ files
3. **GitHub Code Reviewer** - Review code directly from GitHub URLs
4. **GitHub PR Reviewer** - Review only changed code in Pull Requests
5. **GitHub Actions Integration** - Automated PR reviews via GitHub Actions

## Prerequisites

1. **AWS Account**: You need an AWS account with access to Amazon Bedrock
2. **AWS CLI**: Install and configure AWS CLI with your credentials
3. **Python**: Python 3.7 or higher
4. **Bedrock Model Access**: Request access to Claude or other models in AWS Bedrock console

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials** (choose one method):
   
   **Method 1: AWS CLI**
   ```bash
   aws configure
   ```
   
   **Method 2: Environment Variables**
   Create a `.env` file in this directory:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **Request Model Access**:
   - Go to AWS Bedrock Console
   - Navigate to "Model access" in the left sidebar
   - Request access to "Amazon Titan Text G1 - Express"
   - Wait for approval (usually instant for Titan models)

## Usage

### 1. Chatbot
Run the interactive chatbot:
```bash
python chatbot.py
```

Type your messages and press Enter. Type 'quit', 'exit', or 'bye' to stop the chatbot.

### 2. C Code Reviewer

**Review a single file:**
```bash
python code_reviewer.py example_calculator.c
```

**Review with custom output directory:**
```bash
python code_reviewer.py myfile.c -o reviews/
```

**Review all C files in a directory:**
```bash
python code_reviewer.py src/ -o reviews/
```

**Review recursively (including subdirectories):**
```bash
python code_reviewer.py . -o reviews/ -r
```

**Using the batch script (Windows):**
```cmd
review_code.bat example_calculator.c
review_code.bat src/ reviews/
```

### 3. GitHub Code Reviewer

**Review code directly from GitHub URLs:**
```bash
python github_reviewer.py https://github.com/user/repo/blob/main/file.c
```

**With custom output directory:**
```bash
python github_reviewer.py https://github.com/user/repo/blob/main/src/main.c -o reviews/
```

**Review local files (same as regular reviewer):**
```bash
python github_reviewer.py local_file.c -o reviews/
```

**Using batch script:**
```cmd
github_review.bat https://github.com/user/repo/blob/main/file.c
github_review.bat https://github.com/user/repo/blob/main/file.c reviews/
```

### 4. GitHub Pull Request Reviewer

**Review PR diffs (only changed code):**
```bash
python pr_reviewer.py https://github.com/owner/repo/pull/123
```

**With custom output directory:**
```bash
python pr_reviewer.py https://github.com/owner/repo/pull/456 -o reviews/
```

**Using batch script:**
```cmd
pr_review.bat https://github.com/owner/repo/pull/123
pr_review.bat https://github.com/owner/repo/pull/456 reviews/
```

**Features:**
- ✅ Reviews only changed/diff code (not entire files)
- ✅ Supports multiple languages: C/C++, Python, Java, JavaScript, TypeScript, Go, Rust
- ✅ Extracts PR metadata (title, author, stats)
- ✅ Analyzes security, logic, and quality issues
- ✅ Provides line-by-line feedback
- ✅ Gives overall PR assessment
- ✅ Works with any public GitHub repository

### 5. GitHub Actions - Automated PR Reviews

**Automatically review every pull request:**

1. **Setup (One-time)**:
   - Copy `.github/workflows/` to your repository
   - Add AWS credentials to GitHub Secrets
   - See `GITHUB_ACTION_SETUP.md` for detailed instructions

2. **How it works**:
   - ✅ Triggers on PR open/update
   - ✅ Reviews only changed code  
   - ✅ Posts AI feedback as comments
   - ✅ Supports multiple programming languages
   - ✅ Categorizes issues by severity

3. **Two workflow options**:
   - `ai-code-review.yml` - Basic comprehensive review
   - `advanced-ai-review.yml` - File-by-file detailed analysis

**Example GitHub Action output:**
```
🤖 AI Code Review Report

## Summary
Found 3 issues in 2 files requiring attention.

## Issues Found
- 🔴 High: Potential security vulnerability in auth.py:42
- 🟡 Medium: Performance issue in utils.py:15
- 🟢 Low: Code style inconsistency in main.py:8

See inline comments for detailed feedback.
```
### Code Review Features
- **GitHub Integration** - Direct review from GitHub URLs
- **Comprehensive Analysis**: Code quality, security, performance
- **Issue Detection**: Memory leaks, buffer overflows, logic errors
- **Best Practices**: Coding standards and conventions
- **Detailed Reports**: Line-by-line analysis with suggestions
- **Multiple Formats**: Supports .c, .h, .cpp, .cc, .cxx files
- **Multiple Sources**: Local files or GitHub repositories

## Available Models

The chatbot uses Amazon Titan Text G1 - Express by default. You can modify the model in `chatbot.py`:
- `amazon.titan-text-express-v1` (Default - fast and cost-effective)
- `amazon.titan-text-lite-v1` (Lighter, faster version)
- `amazon.titan-text-premier-v1:0` (Most capable Titan model)

You can also use other models if you have access:
- `anthropic.claude-3-haiku-20240307-v1:0` (Claude Haiku)
- `anthropic.claude-3-sonnet-20240229-v1:0` (Claude Sonnet)

## Troubleshooting

- **AccessDeniedException**: Request model access in Bedrock console
- **CredentialsError**: Check your AWS credentials configuration
- **RegionError**: Ensure Bedrock is available in your region (us-east-1, us-west-2, etc.)
