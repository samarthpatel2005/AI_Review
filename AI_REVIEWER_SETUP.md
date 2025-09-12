# 🤖 AI Code Reviewer Setup Guide

This GitHub Actions workflow provides **GitHub Copilot-style AI code reviews** with inline suggestions and commit buttons.

## ✅ **What You Get:**
- 🔍 **Comprehensive Code Analysis** for all languages (Python, C/C++, JavaScript, etc.)
- 🚨 **Security Issue Detection** (hardcoded secrets, buffer overflows, SQL injection)
- ⚠️ **Code Quality Checks** (test comments, debug code, memory leaks)
- 💡 **Inline Suggestions** with clickable commit buttons
- 📝 **Detailed PR Overviews** with diff summaries

## 🚀 **Quick Setup (3 Steps):**

### 1. **Copy the Workflow File**
Copy `simple-ai-test.yml` to your repository:
```
your-repo/.github/workflows/simple-ai-test.yml
```

### 2. **Set Up AWS Bedrock (Required)**
Add these secrets to your GitHub repository:

**Go to: Settings → Secrets and variables → Actions → New repository secret**

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key  
- `AWS_DEFAULT_REGION`: `us-east-1` (or your preferred region)

### 3. **Enable AWS Bedrock Model**
Ensure the `amazon.nova-micro-v1:0` model is enabled in your AWS Bedrock console.

## 🔧 **Supported Languages:**
- ✅ **Python** (.py) - Security, quality, style issues
- ✅ **C/C++** (.c, .cpp, .h) - Buffer overflows, memory leaks, unsafe functions
- ✅ **JavaScript/TypeScript** (.js, .ts) - Security patterns, best practices
- ✅ **All text files** - Basic security and quality checks

## 🎯 **What It Detects:**

### 🚨 **Security Issues (High Priority):**
- Hardcoded passwords, API keys, tokens
- Buffer overflow risks (`gets`, `strcpy`, `sprintf`)
- SQL injection vulnerabilities
- Unsafe file operations

### ⚠️ **Code Quality Issues:**
- Test/debug comments (`# hello test`, `// debug`)
- Memory leaks (malloc without free)
- Missing error handling
- Print statements vs logging

### 💡 **Best Practices:**
- Code style improvements
- Performance optimizations
- Type hints and documentation

## 📋 **Example Output:**

When you create a PR, you'll see:

1. **PR Overview Comment** with file changes summary
2. **Inline Suggestions** on specific lines:

```markdown
🚨 **Critical:** Unsafe C function gets() detected - buffer overflow risk

```suggestion
fgets(buffer, sizeof(buffer), stdin)
```

*Click 'Commit suggestion' to apply this change automatically.*
```

## 🛠️ **Customization Options:**

### **Change AI Model:**
Edit line 175 in the workflow:
```yaml
modelId: "amazon.nova-micro-v1:0"  # Change to your preferred model
```

### **Adjust Detection Sensitivity:**
Edit the detection patterns starting at line 200 in the workflow.

### **Add More Languages:**
Extend the file extension checks and add language-specific patterns.

## 🔐 **Security Notes:**
- The workflow only analyzes code diffs (changed lines)
- AWS credentials are stored securely in GitHub Secrets
- No code is sent outside GitHub and AWS
- All analysis happens in your GitHub Actions runner

## 🆘 **Troubleshooting:**

### **No AI Analysis:**
- Check AWS credentials in repository secrets
- Verify Bedrock model access in AWS console
- Ensure region matches your AWS setup

### **No Inline Comments:**
- Check if you have write permissions to the repository
- Verify the GitHub token has proper scopes
- Look at the workflow logs for API errors

### **Too Many/Few Detections:**
- Adjust the detection patterns in the workflow
- Modify the AI prompt for your needs
- Change the severity thresholds

## 💡 **Pro Tips:**
1. **Test First:** Create a test PR with known issues to verify setup
2. **Customize Prompts:** Tailor the AI prompts for your coding standards
3. **Team Setup:** Each team member needs the same AWS access
4. **Cost Control:** Monitor AWS Bedrock usage (very low cost for typical use)

## 📞 **Support:**
- Check GitHub Actions logs for detailed error messages
- Verify AWS Bedrock permissions and quotas
- Test with a simple file first (like the included test files)

---

**🎉 Ready to use!** Create a PR and watch the AI reviewer in action!