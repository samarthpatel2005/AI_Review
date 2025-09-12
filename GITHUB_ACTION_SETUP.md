# GitHub Actions AI Code Review Setup

This guide will help you set up automated AI code reviews for your GitHub repository using AWS Bedrock.

## 🚀 Quick Setup

### Step 1: Add AWS Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these **Repository Secrets**:

   ```
   AWS_ACCESS_KEY_ID = your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY = your_aws_secret_access_key
   ```

### Step 2: Set Model Configuration (Optional)

1. In the same settings page, go to **Variables** tab
2. Add this **Repository Variable**:

   ```
   BEDROCK_MODEL_ID = amazon.nova-micro-v1:0
   ```

   Available models:
   - `amazon.nova-micro-v1:0` (Fast, lightweight)
   - `amazon.nova-lite-v1:0` (Balanced)
   - `amazon.nova-pro-v1:0` (Most capable)

### Step 3: Copy Workflow Files

Copy the workflow files to your repository:

```bash
mkdir -p .github/workflows
cp ai-code-review.yml .github/workflows/
cp advanced-ai-review.yml .github/workflows/
```

### Step 4: Choose Your Review Type

**Option A: Basic Review** (Uses `ai-code-review.yml`)
- Single comprehensive comment per PR
- Overall assessment and recommendations
- Good for most projects

**Option B: Advanced Review** (Uses `advanced-ai-review.yml`)  
- File-by-file analysis
- Issue categorization and severity levels
- More detailed feedback

To use only one, delete the other workflow file.

## 🔧 How It Works

### Triggers
The AI reviewer automatically runs when:
- ✅ New PR is opened
- ✅ PR is updated (new commits)
- ✅ PR is reopened

### What It Reviews
- 🔍 Python, JavaScript, TypeScript, Java, C/C++, Go, Rust files
- 🔍 Only changed/added lines (not entire files)
- 🔍 Security vulnerabilities
- 🔍 Logic errors and bugs
- 🔍 Code quality and best practices
- 🔍 Performance considerations

### Review Output
The AI will post comments on your PR with:
- 📊 Summary of issues found
- 🎯 Specific line-by-line feedback
- 💡 Improvement suggestions
- ⭐ Overall code quality rating

## 🛡️ Security & Permissions

### AWS IAM Permissions
Your AWS user needs these permissions:
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
                "arn:aws:bedrock:*::foundation-model/amazon.nova-*",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
            ]
        }
    ]
}
```

### GitHub Permissions
The workflow has these permissions:
- `pull-requests: write` - To post review comments
- `contents: read` - To read PR diff content

## 🎛️ Customization

### Change Review Focus
Edit the prompt in the workflow file to focus on specific areas:
- Security-only reviews
- Performance optimization
- Code style consistency
- Documentation quality

### Adjust Model Settings
Modify these parameters in the workflow:
- `maxTokens`: Response length (1000-4000)
- `temperature`: Creativity (0.1 = focused, 0.8 = creative)
- `topP`: Response diversity (0.7-0.9)

### Filter File Types
Add or remove file extensions in the `code_extensions` set:
```python
code_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp'}
```

## 🔍 Testing

### Test with a Sample PR
1. Create a test branch: `git checkout -b test-ai-review`
2. Make some code changes with intentional issues
3. Create a PR to main/master branch
4. Watch the AI reviewer in action! 🤖

### Common Issues
- **No review posted**: Check AWS credentials and Bedrock model access
- **Review too generic**: Adjust temperature to lower value (0.1)
- **Missing some files**: Check file extensions in filter
- **API rate limits**: Add delays between API calls if needed

## 💡 Best Practices

### For Repository Owners
- ✅ Review AI feedback as supplementary, not replacement for human review
- ✅ Train your team to interpret AI suggestions appropriately
- ✅ Customize prompts for your specific coding standards
- ✅ Monitor AWS costs (Nova Micro is very cost-effective)

### For Developers
- ✅ Read AI feedback carefully before dismissing
- ✅ Use AI suggestions to learn best practices
- ✅ Don't rely solely on AI - still do manual reviews
- ✅ Provide feedback on AI review quality

## 📊 Cost Estimation

Using **Amazon Nova Micro**:
- ~$0.00015 per 1000 input tokens
- ~$0.0006 per 1000 output tokens
- Typical PR review: $0.01 - $0.05
- Monthly cost for active repo: $5 - $20

## 🎯 Next Steps

1. Set up the GitHub Action
2. Test with a few PRs
3. Customize prompts for your team's needs
4. Train your team on interpreting AI feedback
5. Consider integrating with your existing CI/CD pipeline

---

🤖 **Happy Automated Reviewing!** Your AI assistant is ready to help improve code quality across all your pull requests.