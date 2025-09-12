# 🔍 AI Detection Debugging - Step by Step

## 🚨 **Current Issue: AI Not Detecting Problems**

The AI reviewer isn't detecting issues like:
- ❌ `#For test` → `# For test` (comment formatting)
- ❌ `PASSWORD = "secret"` → hardcoded credentials  
- ❌ `return a / b` → division by zero
- ❌ `#hello test` → debug comments

## 🧪 **Systematic Testing Plan**

### **Phase 1: Test Credentials & Basic Setup**

1. **Verify AWS Credentials Work:**
```bash
# Test AWS credentials locally (if you have them)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
python test_ai_real.py
```

2. **Check GitHub Secrets:**
- Go to: https://github.com/samarthpatel2005/AI_test/settings/secrets/actions
- Verify you have: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Make sure they're your actual AWS credentials, not placeholder text

### **Phase 2: Test with Simple Workflow**

3. **Create Test PR with Simple Workflow:**
```bash
# Create a test branch
git checkout -b test-simple-ai

# Add a file with OBVIOUS issues
echo "#For test
PASSWORD = 'hardcoded123'  
def divide(a, b):
    return a / b
#hello test" > test_simple.py

# Commit and push
git add test_simple.py
git commit -m "Add file with obvious AI detection issues"
git push origin test-simple-ai
```

4. **Create PR and Check Simple Workflow:**
- Create PR on GitHub
- Go to Actions tab: https://github.com/samarthpatel2005/AI_test/actions
- Look for "Simple AI Review Test" workflow
- Check the logs for:
  ```
  🧪 Simple AI Review Test
  GitHub Token: ✅
  AWS Access Key: ✅
  AWS Secret Key: ✅
  📁 Found X changed files
  🤖 Testing AWS Bedrock...
  🤖 AI Response: ...
  ✅ Posted test comment successfully!
  ```

### **Phase 3: Diagnose Specific Issues**

**If Simple Test WORKS:**
- ✅ AWS credentials are fine
- ✅ GitHub API works
- ✅ AI model is responding
- ❌ Problem is in the main workflow logic

**If Simple Test FAILS:**
Check what fails:

**A. Missing Credentials:**
```
GitHub Token: ❌
AWS Access Key: ❌
```
→ Fix: Add proper secrets to GitHub repository

**B. AWS Bedrock Error:**
```
🤖 Testing AWS Bedrock...
❌ Error: UnauthorizedOperation
```
→ Fix: Check AWS region (use us-east-1) or permissions

**C. No Files Found:**
```
📁 Found 0 changed files
```
→ Fix: Make sure you're creating PR from branch, not direct commit

### **Phase 4: Test Main Workflow**

5. **If Simple Test Works, Test Main Workflow:**
- Same test file, but check "Enhanced AI Code Review" workflow
- Look for detailed logs showing:
  ```
  🔍 Starting enhanced review of PR #X
  📁 Analyzing 1 code files...
  🔍 Reviewing test_simple.py...
  💬 Generated X comments for test_simple.py
  ```

## 🔧 **Most Likely Issues & Fixes**

### **Issue 1: AWS Credentials Missing/Wrong**
**Symptoms:** Simple test fails at AWS step
**Fix:** 
1. Get real AWS credentials from AWS Console
2. Add them to GitHub secrets (not placeholder text)
3. Make sure user has Bedrock permissions

### **Issue 2: AI Model Not Available**
**Symptoms:** AWS error like "ModelNotFound" 
**Fix:** Try different model in workflow:
```yaml
modelId: "amazon.nova-lite-v1:0"  # Instead of nova-micro
```

### **Issue 3: Wrong File Types**
**Symptoms:** "No code files to review"
**Fix:** Make sure test files are `.py`, `.js`, `.java` etc.

### **Issue 4: No Line Changes Detected**  
**Symptoms:** "Found 0 added lines"
**Fix:** Create PR from branch with NEW files, not editing existing files

### **Issue 5: AI Prompt Not Working**
**Symptoms:** AI returns empty or irrelevant response
**Fix:** Already improved prompts, should work now

## 🎯 **Quick Debug Commands**

### **Test AWS Locally:**
```bash
python test_ai_real.py
```

### **Check GitHub API:**
```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/samarthpatel2005/AI_test/pulls/PR_NUMBER/files
```

### **Test AI Prompt:**
```python
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
# Test if AI responds to comment formatting
```

## 🚀 **Expected Working Flow**

When everything works correctly:

1. **Create PR** with `#For test` in file
2. **GitHub Actions** triggers both workflows
3. **Simple Test** posts comment: "🧪 AI Review Test Results ✅"
4. **Enhanced Review** posts inline comments on specific lines
5. **You see** suggestions like:
   ```
   Line 1: The comment lacks proper spacing...
   
   Suggested change:
   # For test
   
   [Commit suggestion] [Add to batch]
   ```

## 📞 **Next Steps**

1. **Run the simple test** with obvious issues file
2. **Check GitHub Actions logs** for both workflows  
3. **Look for error messages** in the logs
4. **If simple test works**, the main workflow should too
5. **If simple test fails**, fix credentials/permissions first

**The key is to test step by step and see exactly where it fails!** 🔍

Let me know what you see in the GitHub Actions logs after creating the test PR!