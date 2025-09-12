# 🤖 AI Code Reviewer - Copy & Use Template

## 📋 **Requirements Checklist:**

For anyone copying this workflow, they need:

### ✅ **GitHub Repository Setup:**
- [ ] Copy `simple-ai-test.yml` to `.github/workflows/` folder
- [ ] Repository must have Actions enabled
- [ ] Write permissions for GitHub Actions

### ✅ **AWS Bedrock Setup:**
- [ ] AWS Account with Bedrock access
- [ ] Enable `amazon.nova-micro-v1:0` model in AWS Bedrock console
- [ ] Create IAM user with Bedrock permissions

### ✅ **GitHub Secrets (Required):**
Go to **Settings → Secrets and variables → Actions**

Add these 3 secrets:
```
AWS_ACCESS_KEY_ID = your_aws_access_key
AWS_SECRET_ACCESS_KEY = your_aws_secret_key  
AWS_DEFAULT_REGION = us-east-1
```

## 🚀 **One-Click AWS IAM Policy:**

Create an IAM user with this policy for Bedrock access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0"
            ]
        }
    ]
}
```

## 🎯 **Testing Your Setup:**

1. **Create a test file** with known issues:
```python
# test_ai_reviewer.py
api_key = "sk-1234567890"  # Should detect hardcoded secret
print("Debug message")     # Should suggest logging
# hello test                # Should detect test comment
```

2. **Create a PR** with this file
3. **Check for AI comments** on the PR

## 🔧 **Customization Options:**

### **Change AI Model:**
Edit this line in the workflow:
```yaml
modelId: "amazon.nova-micro-v1:0"
```

Available models:
- `amazon.nova-micro-v1:0` (cheapest, fast)
- `amazon.nova-lite-v1:0` (better quality)
- `amazon.nova-pro-v1:0` (highest quality)

### **Change Detection Patterns:**
Look for this section in the workflow and modify:
```python
# Add your custom detection patterns
if 'your_pattern' in line_content:
    issues_found.append({...})
```

### **Adjust AI Prompts:**
Find and modify these prompts:
```python
prompt = "Analyze this code diff and find critical issues..."
```

## 💰 **Cost Estimate:**
- **AWS Bedrock**: ~$0.001 per request (very low cost)
- **Typical usage**: $1-5 per month for active development
- **GitHub Actions**: Free for public repos, included in private repo plans

## 🚨 **Important Notes:**

### **Security:**
- ✅ Code analysis happens in your own AWS account
- ✅ No code sent to third parties
- ✅ GitHub secrets are encrypted
- ⚠️ Don't commit AWS keys to code

### **Privacy:**
- Only analyzes changed lines in PRs
- No full file contents sent to AI
- Works entirely within GitHub + AWS ecosystem

### **Permissions:**
- Workflow needs write access to post comments
- AWS user needs only Bedrock invoke permissions
- No admin or broad AWS permissions required

## 🛠️ **Alternative Setups:**

### **Option 1: OpenAI Instead of AWS**
Replace AWS Bedrock calls with OpenAI API (requires OpenAI API key)

### **Option 2: Self-Hosted Model**
Use local AI models instead of cloud services

### **Option 3: Simpler Version**
Use only pattern matching without AI (remove AWS dependency)

## 📞 **Getting Help:**

### **Common Issues:**
1. **"No AI analysis"** → Check AWS secrets and Bedrock model access
2. **"Comments not posting"** → Verify GitHub Actions permissions  
3. **"AWS errors"** → Check IAM policy and region settings

### **Debug Steps:**
1. Check GitHub Actions workflow logs
2. Test AWS credentials locally
3. Verify Bedrock model is enabled in AWS console

---

**🎉 Copy the workflow file and follow this checklist - you'll have AI code reviews in 5 minutes!**