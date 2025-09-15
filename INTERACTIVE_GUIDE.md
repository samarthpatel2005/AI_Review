# 🎯 Interactive AI PR Review Guide

## 🚀 How to Run Interactive PR Reviews

### Method 1: Automatic Mode (Default)
- **When**: Runs automatically when PRs are created/updated
- **Prompt**: Uses smart language-specific prompts
- **Setup**: No additional setup required

### Method 2: Interactive Mode (Custom Prompts)
1. **Go to Actions Tab**
   - Navigate to your repository's "Actions" tab
   - Find "Enhanced AI PR Review (Copilot Style)" workflow

2. **Click "Run workflow"**
   - Click the "Run workflow" button (top right)
   - A form will appear with options

3. **Fill in the Form**:
   - **PR Number**: Enter the PR number you want to analyze
   - **Custom Prompt**: Enter your custom analysis instructions (optional)
   - **Use Default**: Check this to ignore custom prompt and use defaults

## 📝 Interactive Form Options

### 🔢 PR Number (Required)
```
Example: 123
```
The number of the Pull Request you want to analyze.

### 🎯 Custom AI Analysis Prompt (Optional)
```
Example: "Focus on security vulnerabilities and authentication flaws only"
```
Your custom instructions for the AI analysis.

### 🔧 Use Default Prompts (Checkbox)
- ✅ **Checked**: Ignore custom prompt, use smart language detection
- ❌ **Unchecked**: Use custom prompt if provided

## 💡 Custom Prompt Examples

### Security-Focused Analysis
```
Focus exclusively on security vulnerabilities. Check for:
- Hardcoded credentials and API keys
- SQL injection and XSS vulnerabilities
- Authentication and authorization flaws
- Command injection risks
Ignore style and performance issues.
```

### Performance Review
```
Analyze this code for performance issues only:
- Memory leaks and resource management
- Inefficient algorithms and loops
- Database query optimization
- Caching opportunities
Skip security and style checks.
```

### Code Quality Assessment
```
Review for code maintainability and best practices:
- Design patterns and architecture
- Error handling and logging
- Code organization and structure
- Documentation quality
Focus on long-term maintainability.
```

### API Endpoint Review
```
API security and design review:
- Input validation and sanitization
- Error handling and status codes
- Rate limiting and authentication
- Data exposure risks
- RESTful design principles
```

### Database Code Review
```
Database interaction analysis:
- SQL injection prevention
- Query performance and indexing
- Transaction handling
- Data consistency and integrity
- Connection management
```

## 🎛️ Step-by-Step Interactive Usage

### Step 1: Access the Workflow
1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. Find **"Enhanced AI PR Review (Copilot Style)"** in the left sidebar
4. Click on it

### Step 2: Start Interactive Run
1. Click the **"Run workflow"** dropdown button
2. You'll see a form with input fields

### Step 3: Configure Analysis
**Option A: Use Default Prompts**
- Enter PR number: `123`
- Leave custom prompt empty
- Check ✅ "Use Default Prompts"
- Click "Run workflow"

**Option B: Custom Security Focus**
- Enter PR number: `123`
- Custom prompt: `"Security audit: focus on authentication, authorization, and input validation"`
- Leave "Use Default" unchecked
- Click "Run workflow"

**Option C: Performance Analysis**
- Enter PR number: `123`
- Custom prompt: `"Performance review: analyze memory usage, algorithm efficiency, and resource management"`
- Leave "Use Default" unchecked
- Click "Run workflow"

### Step 4: Monitor Results
1. Watch the workflow run in real-time
2. See the prompt configuration in the logs
3. Review AI analysis comments on the PR

## 🔄 Workflow Logic

The workflow decides which prompt to use in this order:

1. **If "Use Default" is checked** → Use default language-specific prompts
2. **If custom prompt provided** → Use the custom prompt
3. **If CUSTOM_PROMPT secret exists** → Use the secret value
4. **Otherwise** → Use default language-specific prompts

## 📊 Prompt Mode Comparison

| Mode | When to Use | Pros | Cons |
|------|-------------|------|------|
| **Default** | General PR reviews | Comprehensive, language-aware | Less focused |
| **Custom Interactive** | Specific analysis needs | Highly targeted, flexible | Requires manual input |
| **Custom Secret** | Consistent custom analysis | Automated, customized | Fixed until changed |

## 🎯 Best Practices

### ✅ DO:
- Use specific, actionable language in custom prompts
- Test custom prompts on sample PRs first
- Be clear about what to focus on and what to ignore
- Use interactive mode for special reviews (security audits, performance analysis)

### ❌ DON'T:
- Make prompts too vague ("check everything")
- Include conflicting instructions
- Make prompts excessively long
- Forget to specify the PR number

## 🚀 Quick Examples

### Security Audit
```yaml
PR Number: 456
Custom Prompt: "Security-only audit: Check for hardcoded secrets, SQL injection, XSS, authentication bypasses, and authorization flaws. Ignore style issues."
Use Default: ❌ Unchecked
```

### Performance Review
```yaml
PR Number: 789
Custom Prompt: "Performance analysis: Focus on memory leaks, algorithm efficiency, database queries, and resource management. Skip security checks."
Use Default: ❌ Unchecked
```

### Quick Default Review
```yaml
PR Number: 321
Custom Prompt: (leave empty)
Use Default: ✅ Checked
```

---

**🎉 Now you have full interactive control over your AI PR reviews!** Use automatic mode for regular reviews and interactive mode when you need focused analysis.