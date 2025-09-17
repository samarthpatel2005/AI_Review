# Test Workflow Validation

This file tests that our three-stage workflow system is properly configured:

## Workflow Sequence
1. **simple-ai-test.yml** (AI PR Reviewer) → runs on pull_request
2. **critical-words-enforcer.yml** (Critical Words) → runs after AI reviewer completes  
3. **generate-summary.yml** (Summary Generator) → runs after critical words completes

## Function Detection Test

```python
def test_function():
    """This function should be detected by our analyzer"""
    # TODO: This should trigger critical words enforcer
    password = "hardcoded_secret"  # This should trigger AI reviewer
    return password

class TestClass:
    def another_function(self, data):
        """Another test function"""
        # HACK: Quick fix needed
        eval(data)  # Security issue for AI reviewer
        return True
```

```javascript
function testJavaScript() {
    // FIXME: Needs proper validation
    var secret = "api_key_123";
    document.write(userInput); // XSS vulnerability
}
```

## Expected Results
- AI Reviewer should detect hardcoded secrets and eval() usage
- Critical Words Enforcer should find TODO, HACK, FIXME comments
- Summary Generator should create comprehensive report