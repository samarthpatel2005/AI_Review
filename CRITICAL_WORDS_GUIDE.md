# 🚫 Critical Words Merge Guard - Configuration Guide

## 🎯 **What This Does:**

The Critical Words Merge Guard automatically scans PR comments and **blocks merges** if too many critical words are found, indicating potential code quality or security issues.

## ⚙️ **Configuration Options:**

### **🔢 Thresholds (Customize in workflow file):**
```python
CRITICAL_THRESHOLD = 10  # Block merge if >= 10 critical words found
WARNING_THRESHOLD = 5   # Show warning if >= 5 critical words found
```

### **📝 Critical Words Categories:**

#### **🔒 Security Risks (15 words):**
```python
'security_risks': [
    'password', 'secret', 'token', 'api_key', 'private_key',
    'hardcode', 'hardcoded', 'credential', 'auth_token',
    'access_key', 'secret_key', 'encryption_key', 'bearer_token',
    'client_secret', 'app_secret', 'oauth_secret'
]
```

#### **💩 Code Smells (14 words):**
```python
'code_smells': [
    'hack', 'workaround', 'quick_fix', 'temporary', 'temp_fix',
    'dirty', 'ugly', 'mess', 'broken', 'bad_code',
    'technical_debt', 'debt', 'kludge', 'bodge'
]
```

#### **🐛 Development Issues (14 words):**
```python
'development_issues': [
    'todo', 'fixme', 'bug', 'error', 'issue', 'problem',
    'broken', 'fail', 'crash', 'exception', 'warning',
    'debug', 'test_only', 'not_working', 'incomplete'
]
```

#### **🚨 Security Vulnerabilities (12 words):**
```python
'security_vulnerabilities': [
    'vulnerability', 'exploit', 'injection', 'xss', 'csrf',
    'buffer_overflow', 'sql_injection', 'code_injection',
    'path_traversal', 'unsafe', 'insecure', 'weak'
]
```

#### **⚡ Performance Issues (11 words):**
```python
'performance_issues': [
    'slow', 'performance', 'bottleneck', 'memory_leak',
    'inefficient', 'optimization_needed', 'lag', 'timeout',
    'deadlock', 'race_condition', 'blocking'
]
```

#### **🧹 Quality Issues (11 words):**
```python
'quality_issues': [
    'deprecated', 'obsolete', 'legacy', 'old_code',
    'refactor_needed', 'cleanup', 'messy', 'spaghetti',
    'duplicate', 'redundant', 'unused'
]
```

## 🔧 **Customization Examples:**

### **For Your Company:**
```python
# Add company-specific words
'company_specific': [
    'your_api_name', 'internal_system', 'legacy_database',
    'prod_server', 'staging_issue', 'client_complaint'
]
```

### **For Different Teams:**
```python
# Frontend team
'frontend_issues': [
    'browser_bug', 'ie_compatibility', 'mobile_responsive',
    'accessibility', 'seo_issue', 'loading_time'
]

# Backend team  
'backend_issues': [
    'database_slow', 'api_timeout', 'server_overload',
    'scaling_issue', 'memory_usage', 'cpu_intensive'
]
```

### **Different Thresholds by Team:**
```python
# Strict for production releases
CRITICAL_THRESHOLD = 5  # Very strict

# Relaxed for development branches
CRITICAL_THRESHOLD = 20  # More lenient

# Per-category thresholds
SECURITY_THRESHOLD = 3   # Block after 3 security words
QUALITY_THRESHOLD = 8    # Block after 8 quality words
```

## 📊 **How It Works:**

### **1. Comment Detection:**
Automatically detects comments in all file types:
- `# Python comments`
- `// C/C++/Java/JavaScript comments`
- `/* Block comments */`
- `<!-- HTML comments -->`
- `-- SQL comments`

### **2. Word Matching:**
- Case-insensitive matching
- Whole word detection
- Categorizes by issue type

### **3. Merge Control:**
- **≥10 words**: 🚫 **BLOCKS MERGE** (commit status = failure)
- **5-9 words**: ⚠️ **WARNING** (commit status = success with warning)
- **<5 words**: ✅ **PASSES** (commit status = success)

### **4. Detailed Reporting:**
- Breakdown by category
- File-by-file analysis  
- Line numbers and context
- Actionable recommendations

## 🎯 **Example Triggers:**

### **Will Block Merge (10+ words):**
```python
# TODO: fix this hack - it's broken and insecure
# FIXME: memory leak in authentication token handling  
# WARNING: hardcoded password causes security vulnerability
# debug: temporary workaround for performance issue
# ugly code with technical debt - needs refactoring
```

### **Will Show Warning (5-9 words):**
```python
# TODO: optimize this slow function
# FIXME: handle error case properly
# hack: quick fix for deadline
```

### **Will Pass (<5 words):**
```python
# Calculate user permissions
# Process payment transaction
# Initialize database connection
```

## 🛠️ **Setup Instructions:**

### **1. Add Workflow File:**
Copy `critical-words-guard.yml` to `.github/workflows/`

### **2. Customize Thresholds:**
Edit the threshold values in the workflow file:
```python
CRITICAL_THRESHOLD = 10  # Adjust this number
WARNING_THRESHOLD = 5   # Adjust this number
```

### **3. Add/Remove Words:**
Modify the `CRITICAL_WORDS` dictionary to match your needs.

### **4. Test Setup:**
Create a test PR with the provided `test_critical_words.py` file to verify it works.

## 💡 **Best Practices:**

### **For Development Teams:**
1. **Regular Review** - Periodically review and clean up TODO/FIXME comments
2. **Proper Tickets** - Convert TODO comments to proper issue tracking
3. **Security Focus** - Never commit hardcoded secrets in comments
4. **Documentation** - Replace temporary comments with proper documentation

### **For Code Reviews:**
1. **Pre-merge Cleanup** - Clean up debug comments before PR submission
2. **Meaningful Comments** - Write clear, purposeful comments
3. **Security Awareness** - Avoid mentioning security details in comments
4. **Technical Debt** - Address or properly document technical debt

## 📈 **Expected Benefits:**

- **🔒 Security** - Prevents accidental secret commits
- **🧹 Code Quality** - Encourages clean, professional comments  
- **📝 Documentation** - Promotes proper documentation over TODO comments
- **⚡ Performance** - Flags performance concerns early
- **🛡️ Risk Reduction** - Catches potential issues before merge

---

**🎉 Your merge guard is ready to maintain high code quality standards!**