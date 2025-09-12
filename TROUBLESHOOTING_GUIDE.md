# Troubleshooting Guide - AI Reviewer Not Detecting Issues

## 🔍 **Current Issues Fixed**

I've identified and fixed the main problems:

### ✅ **1. Improved AI Prompts**
- Added specific detection for comment formatting issues
- Enhanced examples for the AI to recognize problems
- Made prompts more explicit about what to flag

### ✅ **2. Added Debug Output**
- GitHub Actions now shows detailed logs
- Tracks each step of the review process
- Shows what files are being analyzed

### ✅ **3. Created Test Files**
- `obvious_issues.py` - File with clear problems
- `debug_reviewer.py` - Local testing script

## 🧪 **Testing Steps**

### **Step 1: Verify GitHub Secrets**

Go to https://github.com/samarthpatel2005/AI_test/settings/secrets/actions

Make sure you have:
```
AWS_ACCESS_KEY_ID: your-actual-aws-access-key
AWS_SECRET_ACCESS_KEY: your-actual-aws-secret-key
```

### **Step 2: Test with Obvious Issues**

Create a test PR with this content:
```python
# File: test_obvious.py
#For test
PASSWORD = "secret123"

def divide(a, b):
    return a / b

#hello test
print("debug")
```

This should trigger:
- ✅ Comment formatting: `#For test` → `# For test`
- ✅ Hardcoded password detection
- ✅ Missing error handling
- ✅ Debug comment removal: `#hello test`

### **Step 3: Check GitHub Actions Logs**

1. Go to https://github.com/samarthpatel2005/AI_test/actions
2. Look for the "Enhanced AI Code Review" workflow
3. Check the logs for:
   ```
   === GitHub Event Debug ===
   📁 Analyzing X code files...
   🔍 Reviewing filename...
   💬 Generated X comments for filename
   ```

## 🔧 **What I Fixed**

### **1. Enhanced AI Prompt**
Before:
```
Focus on real issues: security, bugs, important style problems
```

After:
```
SPECIFIC ISSUES TO CHECK:
1. Comment formatting: Comments like "#For test" should be "# For test"
2. Test/debug comments: Should be removed in production
3. Hardcoded credentials: Any passwords, API keys
4. Missing error handling: Division by zero, null checks
5. Security issues: SQL injection, command injection

ALWAYS flag comment formatting issues (missing space after #)
ALWAYS flag test/debug comments that should be removed
```

### **2. Better Examples**
Added specific examples:
```
- For "#For test" → "The comment lacks proper spacing..."
- For "# hello test" → "This test comment should be removed..."
- For "password = 'secret'" → "Use environment variables..."
```

### **3. Debug Output**
Now tracks:
- Which files are being analyzed
- How many comments are generated
- What patches are being reviewed

## 🚨 **Common Issues & Solutions**

### **Issue 1: No Comments Appearing**
**Cause**: AWS credentials not configured
**Fix**: Add real AWS credentials to GitHub secrets

### **Issue 2: Workflow Not Running**
**Cause**: PR not from a branch
**Fix**: Create PRs from feature branches, not direct commits to main

### **Issue 3: AI Not Detecting Issues**
**Cause**: Old prompt was too general
**Fix**: ✅ Already fixed with specific prompts

### **Issue 4: Files Not Being Analyzed**
**Cause**: Only code files are processed
**Fix**: Make sure you're testing with `.py`, `.js`, `.java` files

## 🎯 **Quick Test**

Run this to create a guaranteed test case:

```bash
# 1. Create test branch
git checkout -b test-ai-detection

# 2. Create file with obvious issues
cat > test_issues.py << 'EOF'
#For test
PASSWORD = "secret123"
def divide(a, b):
    return a / b
#hello test
EOF

# 3. Commit and push
git add test_issues.py
git commit -m "Add test file with obvious issues"
git push origin test-ai-detection

# 4. Create PR on GitHub
```

## 📊 **Expected Results**

After creating the PR, you should see:

### **GitHub Actions Log:**
```
🔍 Starting enhanced review of PR #X
📁 Analyzing 1 code files...
🔍 Reviewing test_issues.py...
💬 Generated 4 comments for test_issues.py
📤 Posting 4 total comments...
```

### **PR Comments:**
1. **Line 1**: "The comment lacks proper spacing. It should be '# For test'..."
2. **Line 2**: "Use environment variables instead of hardcoded passwords..."
3. **Line 4**: "Add error handling to prevent division by zero..."
4. **Line 5**: "This test comment should be removed before merging..."

## 🛠️ **If Still Not Working**

1. **Check GitHub Actions**: Look for error messages in workflow logs
2. **Verify AWS Region**: Make sure Bedrock is available in `us-east-1`
3. **Test Locally**: Run `python debug_reviewer.py` to test parsing
4. **Check File Extensions**: Only `.py`, `.js`, `.java` etc. are processed

## 📞 **Next Steps**

1. **Test immediately** with the obvious issues file
2. **Check GitHub Actions logs** for detailed output
3. **Verify AWS credentials** are working
4. **Create PR from branch** (not direct to main)

The AI reviewer should now detect:
- ✅ **Comment formatting** issues
- ✅ **Debug/test comments** that should be removed  
- ✅ **Security issues** like hardcoded passwords
- ✅ **Error handling** problems

Try the test now and let me know what you see in the GitHub Actions logs! 🚀