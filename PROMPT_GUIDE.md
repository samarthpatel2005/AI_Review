# 🎯 Custom AI Review Prompts Guide

## How to Use Different Review Styles

### 🔄 **Switching Between Prompts:**

1. **Copy the content** from any prompt file below
2. **Paste into** `prompt/custom.txt` 
3. **Commit the change** to activate the new review style
4. **Leave empty** to use the default comprehensive review

---

## 📁 **Available Prompt Styles:**

### 🔧 **default.txt** (Active when custom.txt is empty)
**Best for:** General-purpose reviews with detailed explanations
- **Output:** 3-4 line detailed feedback per issue
- **Covers:** Security, quality, style with specific fix suggestions
- **Good for:** Most development teams and general code reviews

### 🔒 **security-focused.txt**
**Best for:** Security-critical applications and compliance reviews
- **Output:** Detailed security threat analysis with attack vectors
- **Covers:** Only security vulnerabilities and risks
- **Good for:** Financial, healthcare, and high-security applications

### ⚡ **performance-focused.txt**
**Best for:** High-performance systems and optimization reviews
- **Output:** Performance metrics and optimization strategies
- **Covers:** Only performance bottlenecks and efficiency issues
- **Good for:** Gaming, real-time systems, and scalability projects

### 👨‍💻 **beginner-friendly.txt**
**Best for:** Educational environments and junior developer mentoring
- **Output:** Teaching-focused explanations with learning resources
- **Covers:** Code quality with educational context
- **Good for:** Bootcamps, internships, and learning projects

### 🏢 **enterprise-grade.txt**
**Best for:** Large organizations with compliance requirements
- **Output:** Business impact analysis with compliance considerations
- **Covers:** Regulatory compliance, technical debt, business risks
- **Good for:** Enterprise applications and regulated industries

### 🔧 **quick-fix.txt**
**Best for:** Fast iteration and immediate issue resolution
- **Output:** Actionable fixes with time estimates
- **Covers:** Easily fixable issues with step-by-step solutions
- **Good for:** Sprint reviews and rapid development cycles

---

## 🚀 **Quick Setup Examples:**

### Example 1: Security Review
```bash
# Copy security prompt to activate
cp prompt/security-focused.txt prompt/custom.txt
git add prompt/custom.txt
git commit -m "Switch to security-focused AI review"
```

### Example 2: Back to Default
```bash
# Empty custom.txt to use default
echo "" > prompt/custom.txt
git add prompt/custom.txt  
git commit -m "Switch back to default comprehensive review"
```

### Example 3: Performance Focus
```bash
# Copy performance prompt
cp prompt/performance-focused.txt prompt/custom.txt
git add prompt/custom.txt
git commit -m "Focus AI review on performance optimization"
```

---

## 📊 **Expected Output Differences:**

### 🔴 **Old Output (1 line):**
```
🚨 High Risk: Potential hardcoded secret detected
```

### ✅ **New Output (3-4 lines):**
```
🚨 High Risk: Hardcoded Admin Credentials Detected
This exposes administrative access credentials directly in source code, creating a critical security vulnerability.
Impact: Attackers gaining repository access could immediately compromise the entire application with admin privileges.
Fix: Move credentials to environment variables or secure vault (e.g., process.env.ADMIN_PASSWORD) and add .env to .gitignore.
```

**Try the new prompts and see the difference in detail and actionability!**