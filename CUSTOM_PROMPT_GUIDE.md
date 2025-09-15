# 🎯 Custom Prompt Guide for AI PR Reviewer

## Overview
The AI PR Reviewer now supports **custom prompts**, allowing you to tailor the AI analysis to your specific needs. You can choose between:

1. **Default Prompts** - Smart language-specific analysis (recommended)
2. **Custom Prompts** - Your own AI instructions for focused analysis

## 🔧 How to Use Custom Prompts

### Option 1: Using GitHub Secrets (Recommended)

1. **Go to your repository Settings**
2. **Navigate to**: Settings → Secrets and variables → Actions
3. **Add a new secret**:
   - Name: `CUSTOM_PROMPT`
   - Value: Your custom prompt text

4. **Uncomment the line in your workflow file**:
   ```yaml
   # CUSTOM_PROMPT: ${{ secrets.CUSTOM_PROMPT }}  # Remove the # to enable
   ```
   becomes:
   ```yaml
   CUSTOM_PROMPT: ${{ secrets.CUSTOM_PROMPT }}
   ```

### Option 2: Direct Environment Variable
Set the environment variable directly in your workflow:
```yaml
env:
  CUSTOM_PROMPT: "Focus on security vulnerabilities and performance issues only"
```

## 📝 Custom Prompt Examples

### Security-Focused Analysis
```
Focus exclusively on security vulnerabilities. Check for:
- Hardcoded credentials and API keys
- SQL injection and XSS vulnerabilities  
- Command injection risks
- Authentication and authorization flaws
- Cryptographic weaknesses
Ignore style and formatting issues.
```

### Performance-Focused Analysis
```
Analyze this code for performance issues only:
- Memory leaks and resource management
- Inefficient algorithms and loops
- Database query optimization
- Caching opportunities
- Concurrent programming issues
Skip security and style checks.
```

### Code Quality Focus
```
Review for code maintainability and best practices:
- Design patterns and architecture
- Error handling and logging
- Code organization and structure
- Documentation and comments
- Test coverage and quality
```

### Business Logic Review
```
Focus on business logic correctness:
- Input validation and edge cases
- Business rule implementation
- Data consistency and integrity
- Workflow and process compliance
- Integration points and dependencies
```

## 🔄 Switching Between Modes

### Use Default Prompts
- **Don't set** `CUSTOM_PROMPT` environment variable
- **Comment out** the CUSTOM_PROMPT line in workflow
- AI will automatically detect language and use optimized prompts

### Use Custom Prompts  
- **Set** `CUSTOM_PROMPT` to your desired prompt
- **Uncomment** the CUSTOM_PROMPT line in workflow
- AI will use your prompt for all files

## 🎯 Best Practices for Custom Prompts

### ✅ DO:
- Be specific about what to focus on
- Mention what to ignore if needed
- Use clear, actionable language
- Keep prompts concise but comprehensive
- Test prompts on sample PRs first

### ❌ DON'T:
- Make prompts too vague or generic
- Include conflicting instructions
- Make prompts excessively long (>500 words)
- Forget to specify the analysis scope

## 📊 Prompt Comparison

| Feature | Default Prompts | Custom Prompts |
|---------|----------------|----------------|
| **Language Detection** | ✅ Automatic | ❌ Manual |
| **Security Analysis** | ✅ Comprehensive | 🎯 Configurable |
| **Code Quality** | ✅ Multi-faceted | 🎯 Focused |
| **Performance** | ✅ Included | 🎯 Optional |
| **Customization** | ❌ Fixed | ✅ Full Control |
| **Maintenance** | ✅ Auto-updated | 🔧 Manual |

## 🚀 Quick Start Examples

### Example 1: Security-Only Analysis
```yaml
env:
  CUSTOM_PROMPT: "Security audit only: Find hardcoded secrets, injection vulnerabilities, and authentication flaws. Skip style issues."
```

### Example 2: API Review Focus
```yaml
env:
  CUSTOM_PROMPT: "API endpoint analysis: Check input validation, error handling, rate limiting, authentication, and data exposure risks."
```

### Example 3: Database Code Review
```yaml
env:
  CUSTOM_PROMPT: "Database interaction review: Check for SQL injection, performance issues, transaction handling, and data consistency."
```

## 💡 Tips for Effective Custom Prompts

1. **Start with examples** - Use the provided templates
2. **Test incrementally** - Try prompts on small PRs first  
3. **Be specific** - "Check authentication" vs "Check login security"
4. **Set boundaries** - Specify what to include/exclude
5. **Iterate** - Refine prompts based on results

---

**Need help?** Check the Actions logs to see which prompt mode was used and refine accordingly!