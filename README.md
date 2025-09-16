# 🤖 AI-Powered PR Review System

A comprehensive GitHub Actions-based PR review system that combines AI analysis with critical word enforcement to ensure code quality and security.

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Scripts Overview](#scripts-overview)
- [Setup Requirements](#setup-requirements)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This system provides automated PR reviews through two complementary scripts:

1. **🤖 AI PR Reviewer** - Advanced AI-powered code analysis using AWS Bedrock
2. **🚨 Critical Words Enforcer** - Comment analysis for problematic patterns and words

Both scripts work together to provide comprehensive PR feedback without blocking development workflow.

## 🏗️ System Architecture

```
GitHub PR Created/Updated
         ↓
   GitHub Actions Trigger
         ↓
    ┌─────────────────┬─────────────────┐
    │   AI Reviewer   │ Critical Words  │
    │    (Script 1)   │   (Script 2)    │
    └─────────────────┴─────────────────┘
         ↓                     ↓
   AI Analysis            Comment Analysis
         ↓                     ↓
    Inline Comments      Status Reports
         ↓                     ↓
      GitHub PR Interface
```

## 📜 Scripts Overview

### 🤖 Script 1: AI PR Reviewer (`scripts/ai_pr_reviewer.py`)

**Purpose**: Comprehensive AI-powered code analysis with intelligent prompt handling

**Key Features**:
- **Intelligent Prompt System**: 
  - Uses custom prompt (`prompt/custom.txt`) when available
  - Falls back to default prompt (`prompt/default.txt`) automatically
  - AI response parsing vs pattern matching based on prompt type
- **Multi-Language Support**: 20+ programming languages
- **COMPLETE CODE ANALYSIS**: 
  - **Function calls**: `eval()`, `exec()`, `system()`, `subprocess.call()`
  - **Variable assignments**: `password = "admin123"`, hardcoded secrets
  - **SQL patterns**: String concatenation, injection vulnerabilities
  - **File operations**: `open()`, path traversal risks
  - **Network requests**: `requests.get()`, SSL validation
  - **Memory management**: `malloc()`, buffer overflows
  - **Cryptographic functions**: `md5()`, weak algorithms
  - **Database operations**: `DELETE`, `DROP`, `UPDATE` statements
  - **Language-specific security**: XSS, buffer overflows, injection attacks
  - **Comments and documentation**: As part of comprehensive analysis
- **Inline Suggestions**: GitHub-native suggestion format with auto-apply

**How It Decides Analysis Mode**:
```python
if custom_prompt_exists and has_content:
    # Use AI response from AWS Bedrock
    analysis_mode = "AI_RESPONSE"
else:
    # Use built-in pattern matching
    analysis_mode = "PATTERN_MATCHING"
```

**Output**: Detailed inline PR comments with 4-line format:
- **Risk Level**: Critical/High/Warning/Suggestion
- **Detailed Explanation**: Why the issue is problematic
- **Impact Assessment**: What could go wrong
- **Specific Fix Suggestion**: How to resolve it

### 🚨 Script 2: Critical Words Enforcer (`scripts/critical_words_enforcer.py`)

**Purpose**: Analyze PR comments for problematic words and patterns (COMMENTS ONLY)

**Key Features**:
- **Non-Blocking Analysis**: Reports issues without failing PRs
- **COMMENT EXTRACTION ONLY**: Analyzes comment text, NOT code logic
  - **C-style comments**: `// TODO: fix this hack`
  - **Block comments**: `/* This needs refactoring */`
  - **Python comments**: `# FIXME: security vulnerability`
  - **HTML comments**: `<!-- Remove this debug code -->`
  - **Does NOT analyze**: Function calls, variable names, code patterns
- **Categorized Detection**: 6 categories of critical words
- **Threshold Configuration**: Customizable enforcement levels
- **GitHub Status Integration**: Updates PR status with findings

**Word Categories**:
1. **Security Risks**: password, secret, token, hardcoded credentials
2. **Code Smells**: hack, workaround, technical debt
3. **Development Issues**: todo, fixme, bug, incomplete
4. **Security Vulnerabilities**: injection, xss, unsafe
5. **Performance Issues**: slow, bottleneck, memory leak
6. **Quality Issues**: deprecated, legacy, cleanup needed

**Output**: Status checks and summary comments with categorized findings

## ⚙️ Setup Requirements

### GitHub Secrets Required:
```yaml
AWS_ACCESS_KEY_ID: Your AWS access key
AWS_SECRET_ACCESS_KEY: Your AWS secret key
GITHUB_TOKEN: Auto-provided by GitHub Actions
```

### AWS Requirements:
- AWS Bedrock access enabled
- `amazon.nova-micro-v1:0` model permissions
- Proper IAM policies for Bedrock access

### Repository Structure:
```
your-repo/
├── .github/workflows/
│   ├── simple-ai-test.yml          # AI Reviewer workflow
│   └── critical-words-enforcer.yml # Critical words workflow
├── scripts/
│   ├── ai_pr_reviewer.py           # Main AI analysis script
│   └── critical_words_enforcer.py  # Critical words script
├── prompt/
│   ├── custom.txt                  # Custom AI prompt (optional)
│   └── default.txt                 # Default AI prompt (fallback)
└── requirements.txt                # Python dependencies
```

## 🔄 How It Works

### When a PR is Created/Updated:

#### Step 1: GitHub Actions Trigger
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [ main, master, develop ]
```

#### Step 2: AI Reviewer Execution
1. **Environment Setup**: Validate GitHub and AWS credentials
2. **Prompt Detection**: Check if `prompt/custom.txt` has content
3. **Analysis Mode Selection**:
   - **Custom Prompt Available** → Use AI response from AWS Bedrock
   - **Custom Prompt Empty/Missing** → Use pattern matching analysis
4. **File Analysis**: Process all changed files in the PR
5. **Comment Generation**: Create detailed inline review comments
6. **GitHub Integration**: Post comments directly to PR

#### Step 3: Critical Words Enforcement
1. **Comment Extraction**: Parse comments from changed files
2. **Word Analysis**: Check against categorized critical word lists
3. **Threshold Evaluation**: Compare findings against configured limits
4. **Status Reporting**: Update PR status with results
5. **Summary Generation**: Create detailed findings report

### Intelligent Analysis Mode Selection:

```python
# AI Reviewer Decision Logic
def determine_analysis_mode():
    custom_prompt_path = "prompt/custom.txt"
    
    if file_exists(custom_prompt_path) and file_has_content(custom_prompt_path):
        print("🎯 Using AI response from custom prompt")
        return use_ai_analysis()
    else:
        print("🔍 Using pattern matching analysis")
        return use_pattern_matching()
```

## ⚙️ Configuration

### AI Reviewer Configuration:

#### Custom Prompt (`prompt/custom.txt`):
```
🔧 QUICK-FIX FOCUSED REVIEW

Identify issues with immediate, actionable solutions. For each problem:

1. ⚡ **Quick Fix** (1-line summary of the immediate solution)
2. **Fix Time** (Estimated minutes/hours to implement)
3. **Step-by-Step** (Specific actions to resolve the issue)
4. **Verification** (How to test that the fix works)

🎯 PRIORITIZE EASILY FIXABLE ISSUES:
- Hardcoded values that should be configuration
- Missing error handling around risky operations
- Debug statements and console logs left in code
```

#### Default Prompt (`prompt/default.txt`):
- Comprehensive 4-line analysis format
- Security, quality, and performance focus
- Detailed explanations and impact assessments

### Critical Words Enforcer Configuration:

```python
# Enforcement Thresholds
CRITICAL_THRESHOLD = 1   # Fail if >= 1 critical word found
WARNING_THRESHOLD = 0    # No warnings, only pass/fail

# Word Categories (Customizable)
CRITICAL_WORDS = {
    'security_risks': ['password', 'secret', 'token', 'hardcoded'],
    'code_smells': ['hack', 'workaround', 'technical_debt'],
    'development_issues': ['todo', 'fixme', 'bug', 'incomplete'],
    # ... more categories
}
```

## � **Key Difference: What Each Script Analyzes**

### **Real-World Example to Show the Difference:**

**Developer pushes this code:**
```python
# TODO: fix this hack later - hardcoded password is bad
password = "admin123"  # This is temporary  
subprocess.call(user_input, shell=True)  # Quick fix for now
eval(user_data)  # Dynamic execution
```

### **🤖 AI Reviewer Analysis (ENTIRE CODE):**
```
🔴 Critical: eval() function detected
   ↳ Line 4: eval(user_data) - Code injection risk
🔴 Critical: subprocess.call() with shell=True  
   ↳ Line 3: shell=True enables command injection
🚨 High Risk: Hardcoded secret detected
   ↳ Line 2: password = "admin123" - Move to environment variables
💡 Suggestion: Remove debug comment
   ↳ Line 1: TODO comment indicates incomplete work
```

### **🚨 Critical Words Enforcer Analysis (COMMENTS ONLY):**
```
🚨 CRITICAL WORDS DETECTED - 5 issues found

📋 DETAILED ANALYSIS:
🔴 Development Issues (3 words):
   - Line 1: "todo" in "TODO: fix this hack later"
   - Line 1: "hack" in "TODO: fix this hack later"  
   - Line 2: "temporary" in "This is temporary"

🔴 Security Risks (2 words):
   - Line 1: "hardcoded" in "hardcoded password is bad"
   - Line 1: "password" in "hardcoded password is bad"

⚠️ IMPORTANT: Critical Words Enforcer does NOT detect:
   ❌ The actual password = "admin123" (code)
   ❌ The subprocess.call(shell=True) (code)  
   ❌ The eval(user_data) (code)
   ✅ Only analyzes: Comment text content
```

### **📊 Summary:**
- **AI Reviewer**: Finds **4 actual security vulnerabilities** in the code logic
- **Critical Words Enforcer**: Finds **5 problematic words** in comments
- **Together**: Complete coverage of both code quality AND documentation quality

## �📊 Usage Examples

### Example 1: AI Analysis with Custom Prompt

**Trigger**: PR with custom prompt available
**Input**: Code with hardcoded password
**Output**:
```
⚡ **Quick Fix: Remove hardcoded password**
**Fix Time:** 5 minutes
**Step-by-Step:** Replace hardcoded password with environment variable
**Verification:** Test authentication with environment variable
```

### Example 2: Pattern Matching Analysis

**Trigger**: PR with empty custom prompt
**Input**: Same code with hardcoded password
**Output**:
```
🚨 **High Risk: Potential hardcoded secret detected**
**Detailed Explanation:** This code pattern has been identified as containing hardcoded credentials which creates a serious security vulnerability.
**Impact Assessment:** Attackers could gain unauthorized access to systems using exposed credentials.
**Specific Fix Suggestion:** Move credentials to environment variables or secure vault storage.
```

### Example 3: Critical Words Detection

**Input**: Code comment containing "// TODO: fix this hack later"
**Output**:
```
🚨 CRITICAL WORDS DETECTED - 2 issues found

📋 DETAILED ANALYSIS:
🔴 CRITICAL: Code Smells (2 words found)
   - Line 45: "hack" in comment "// TODO: fix this hack later"
   - Line 45: "todo" in comment "// TODO: fix this hack later"

💡 SUGGESTED ACTIONS:
- Replace "hack" with proper implementation
- Create GitHub issue for "TODO" items
- Add proper documentation for temporary solutions
```

## 🔧 Troubleshooting

### Common Issues:

#### AI Reviewer Not Using Custom Prompt:
```bash
# Check custom prompt content
cat prompt/custom.txt
# Ensure file has > 10 characters of content
```

#### AWS Bedrock Access Issues:
```bash
# Verify AWS credentials in GitHub Secrets
# Check Bedrock model permissions in AWS Console
# Ensure region is correctly set (default: us-east-1)
```

#### Critical Words False Positives:
```python
# Edit critical_words_enforcer.py
# Modify CRITICAL_WORDS dictionary
# Adjust CRITICAL_THRESHOLD value
```

### Debug Mode:
Both scripts include extensive logging. Check GitHub Actions logs for detailed execution information.

## 🎉 Benefits

### For Developers:
- **Immediate Feedback**: Get detailed analysis before code review
- **Learning Tool**: Understand security and quality issues
- **Consistent Standards**: Automated enforcement of coding standards

### For Teams:
- **Quality Assurance**: Catch issues before they reach production
- **Knowledge Sharing**: Consistent feedback across all developers
- **Efficiency**: Reduce time spent on basic code review tasks

### For Projects:
- **Security**: Proactive vulnerability detection
- **Maintainability**: Enforce clean code practices
- **Documentation**: Ensure code is properly documented

## 📈 Metrics and Reporting

The system provides detailed metrics through:
- GitHub PR status checks
- Inline comment statistics
- Critical word frequency analysis
- Security issue categorization

This comprehensive system ensures high code quality while maintaining development velocity and providing educational value to all team members.