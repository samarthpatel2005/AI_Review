"""
Test script to simulate what the AI reviewer will detect in the C file.
"""

# Issues the AI reviewer will detect in unsafe_c_code.c:

security_issues = [
    {
        "line": 5,
        "severity": "high", 
        "type": "security",
        "message": "Potential hardcoded secret detected",
        "code": 'char global_password[20] = "admin123";'
    },
    {
        "line": 9,
        "severity": "high",
        "type": "security", 
        "message": "Unsafe C function gets() detected - buffer overflow risk",
        "code": "gets(buffer);",
        "suggestion": "fgets(buffer, size, stdin)"
    },
    {
        "line": 15,
        "severity": "high",
        "type": "security",
        "message": "Unsafe C function strcpy() detected - buffer overflow risk", 
        "code": "strcpy(greet, \"Hello \");",
        "suggestion": "strncpy() or strcpy_s()"
    },
    {
        "line": 16,
        "severity": "high",
        "type": "security",
        "message": "Unsafe C function strcat() detected - buffer overflow risk",
        "code": "strcat(greet, name);",
        "suggestion": "strncat() or strcat_s()"
    },
    {
        "line": 22,
        "severity": "high", 
        "type": "security",
        "message": "Unsafe C function sprintf() detected - buffer overflow risk",
        "code": "sprintf(query, \"SELECT * FROM users WHERE name = '%s';\", userInput);",
        "suggestion": "snprintf()"
    },
    {
        "line": 14,
        "severity": "high",
        "type": "quality",
        "message": "Potential memory leak - malloc without corresponding free",
        "code": "char *greet = malloc(50);"
    },
    {
        "line": 27,
        "severity": "medium",
        "type": "quality", 
        "message": "Division operation without zero check",
        "code": "return a / b;"
    }
]

print("🤖 AI Code Review Results for unsafe_c_code.c:")
print("=" * 60)

for issue in security_issues:
    icon = "🚨" if issue["severity"] == "high" else "⚠️" if issue["severity"] == "medium" else "💡"
    print(f"\n{icon} **{issue['severity'].upper()}:** {issue['message']}")
    print(f"   Line {issue['line']}: `{issue['code']}`")
    if "suggestion" in issue:
        print(f"   💡 Suggestion: Use `{issue['suggestion']}` instead")

print(f"\n\n✅ **Summary:** Found {len(security_issues)} critical issues")
print("🔒 Security issues: 5 high-severity buffer overflow risks + 1 hardcoded secret")  
print("⚡ Quality issues: 1 memory leak + 1 unsafe division")
print("\n🎯 The AI reviewer will post inline suggestions for each issue!")