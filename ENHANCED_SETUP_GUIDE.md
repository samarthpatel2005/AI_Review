# GitHub Copilot-Style AI Code Review Setup

This setup creates an automated AI code review system that works just like GitHub Copilot, posting inline comments on pull requests with suggestions and commit recommendations.

## 🚀 Features

✅ **Automatic PR Reviews** - Triggers on every pull request
✅ **Inline Comments** - Posts comments directly on changed lines (like GitHub Copilot)
✅ **Severity Levels** - Critical, High, Medium, Low, Suggestions with color-coded emojis
✅ **Code Suggestions** - Provides exact code fixes when possible
✅ **Smart Analysis** - Focuses only on security, bugs, performance, and critical issues
✅ **Multiple Languages** - Supports Python, JavaScript, Java, C++, Go, Rust, and more
✅ **AWS Bedrock** - Powered by Amazon Nova models

## 📋 Setup Instructions

### 1. GitHub Repository Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

```
AWS_ACCESS_KEY_ID: your-aws-access-key
AWS_SECRET_ACCESS_KEY: your-aws-secret-key
```

**Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions.

### 2. AWS Permissions

Your AWS user/role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:model/amazon.nova-micro-v1:0",
                "arn:aws:bedrock:*:*:model/amazon.nova-lite-v1:0",
                "arn:aws:bedrock:*:*:model/amazon.nova-pro-v1:0"
            ]
        }
    ]
}
```

### 3. Enable GitHub Actions

1. Go to your repository → Settings → Actions → General
2. Under "Actions permissions", select **"Allow all actions and reusable workflows"**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**

### 4. Repository File Structure

Make sure you have these files:

```
.github/
  workflows/
    enhanced-ai-review.yml          # Main workflow file
enhanced_pr_reviewer.py             # Enhanced reviewer (optional for local use)
requirements.txt                    # Python dependencies
```

## 🔧 How It Works

### Automatic Triggering
- Runs on PR opened, updated, or reopened
- Only analyzes code files (skips docs, configs unless they're code)
- Focuses on changed lines only

### AI Analysis Process
1. **File Detection** - Identifies changed code files
2. **Diff Parsing** - Extracts added/modified lines with line numbers
3. **AI Review** - Analyzes each file with AWS Bedrock
4. **Comment Generation** - Creates inline comments with severity and suggestions
5. **Review Posting** - Posts as GitHub review with overall summary

### Comment Format
Each inline comment includes:

🔴 **CRITICAL - SECURITY**
SQL injection vulnerability detected

**💡 Suggestion:** Use parameterized queries
**🔧 Suggested fix:**
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Review Summary
The bot posts an overall review comment with:
- Issue count by severity
- Overall assessment
- Links to inline comments

## 🎯 Severity Levels

| Level | Emoji | Action | Description |
|-------|-------|--------|-------------|
| 🔴 Critical | REQUEST_CHANGES | Security vulnerabilities, major bugs |
| 🟠 High | REQUEST_CHANGES | Logic errors, performance issues |
| 🟡 Medium | COMMENT | Code quality, maintainability |
| 🔵 Low | COMMENT | Minor style, optimization |
| 💡 Suggestion | COMMENT | Improvements, best practices |

## 🧪 Testing

### Create a Test PR

1. Create a new branch:
```bash
git checkout -b test-ai-review
```

2. Add a file with some issues:
```python
# test_file_for_ai_review.py
import os
password = "hardcoded123"  # This should trigger security warning
def divide(a, b):
    return a / b  # This should trigger error handling warning
```

3. Commit and push:
```bash
git add test_file_for_ai_review.py
git commit -m "Add test file for AI review"
git push origin test-ai-review
```

4. Create a pull request and watch the AI reviewer in action!

## 🔄 Workflow File

The workflow (`enhanced-ai-review.yml`) does:

1. **Triggers** on PR events (opened, synchronize, reopened)
2. **Permissions** to read code and write PR comments
3. **Setup** Python environment and dependencies
4. **Analysis** runs the AI reviewer script
5. **Comments** posts inline reviews automatically

## 📊 Expected Results

### ✅ Good Code
- Posts approval comment: "No issues found! Code looks good to merge 🎉"

### ⚠️ Issues Found
- Posts inline comments on specific lines
- Provides severity-based summary
- Requests changes for critical/high issues
- Offers specific fix suggestions

## 🛠️ Customization

### Change AI Model
In the workflow file, modify:
```yaml
BEDROCK_MODEL_ID: amazon.nova-pro-v1:0  # For more detailed analysis
```

### Adjust Sensitivity
Edit the prompt in the reviewer script to focus on different types of issues.

### Add Languages
Update the `code_extensions` set in the reviewer to include more file types.

## 🎉 Demo

Once set up, every pull request will get:

1. **Automatic trigger** within seconds
2. **Inline comments** on problematic lines (just like GitHub Copilot)
3. **Severity indicators** with color-coded emojis
4. **Fix suggestions** with exact code replacements
5. **Overall assessment** and approval/rejection

The AI reviewer will comment on things like:
- Security vulnerabilities
- Logic errors and potential bugs
- Performance issues
- Code quality problems
- Best practice violations

## 📞 Support

If you encounter issues:

1. Check GitHub Actions logs in your repository
2. Verify AWS credentials and permissions
3. Ensure Bedrock model access in your region
4. Check the workflow file syntax

This setup provides a professional AI code review experience similar to GitHub Copilot, helping maintain code quality automatically!