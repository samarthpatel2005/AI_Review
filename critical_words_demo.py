"""
Critical Words Merge Guard - Demonstration Script
Shows exactly how the detection and blocking works
"""

# Simulate the critical words detection
CRITICAL_WORDS = {
    'security_risks': [
        'password', 'secret', 'token', 'api_key', 'private_key',
        'hardcode', 'hardcoded', 'credential', 'auth_token',
        'access_key', 'secret_key', 'encryption_key', 'bearer_token',
        'client_secret', 'app_secret', 'oauth_secret'
    ],
    'code_smells': [
        'hack', 'workaround', 'quick_fix', 'temporary', 'temp_fix',
        'dirty', 'ugly', 'mess', 'broken', 'bad_code',
        'technical_debt', 'debt', 'kludge', 'bodge'
    ],
    'development_issues': [
        'todo', 'fixme', 'bug', 'error', 'issue', 'problem',
        'broken', 'fail', 'crash', 'exception', 'warning',
        'debug', 'test_only', 'not_working', 'incomplete'
    ],
    'security_vulnerabilities': [
        'vulnerability', 'exploit', 'injection', 'xss', 'csrf',
        'buffer_overflow', 'sql_injection', 'code_injection',
        'path_traversal', 'unsafe', 'insecure', 'weak'
    ],
    'performance_issues': [
        'slow', 'performance', 'bottleneck', 'memory_leak',
        'inefficient', 'optimization_needed', 'lag', 'timeout',
        'deadlock', 'race_condition', 'blocking'
    ],
    'quality_issues': [
        'deprecated', 'obsolete', 'legacy', 'old_code',
        'refactor_needed', 'cleanup', 'messy', 'spaghetti',
        'duplicate', 'redundant', 'unused'
    ]
}

CRITICAL_THRESHOLD = 10
WARNING_THRESHOLD = 5

# Test comments from different file types
test_comments = {
    "clean_code.py": [
        "# Calculate the monthly payment amount",
        "# Validate user input parameters", 
        "# Return the processed result",
    ],
    "warning_level.js": [
        "// TODO: optimize this function later",
        "// FIXME: handle edge case",
        "// debug: remove this console.log",
        "// hack: quick workaround",
        "// performance issue here",
        "// bug in error handling"
    ],
    "blocked_code.cpp": [
        "// TODO: fix this hack - it's broken and insecure",
        "// FIXME: memory leak in authentication token handling",
        "// WARNING: hardcoded password causes security vulnerability", 
        "// debug: temporary workaround for performance issue",
        "// ugly code with technical debt - needs refactoring",
        "// deprecated function with injection vulnerability",
        "// crash occurs when error handling fails",
        "// slow bottleneck in legacy database code",
        "// unsafe buffer overflow in obsolete function",
        "// technical debt: cleanup this messy workaround",
        "// broken API with deadlock race condition"
    ]
}

def analyze_comments(filename, comments):
    critical_count = 0
    found_words = []
    
    for comment in comments:
        comment_lower = comment.lower()
        
        for category, words in CRITICAL_WORDS.items():
            for word in words:
                if word in comment_lower:
                    critical_count += 1
                    found_words.append({
                        'word': word,
                        'category': category,
                        'comment': comment
                    })
    
    return critical_count, found_words

print("🚫 CRITICAL WORDS MERGE GUARD - DEMONSTRATION")
print("=" * 60)
print()

total_critical_words = 0
all_files_analysis = {}

for filename, comments in test_comments.items():
    print(f"📄 **Analyzing: {filename}**")
    print("-" * 40)
    
    critical_count, found_words = analyze_comments(filename, comments)
    total_critical_words += critical_count
    all_files_analysis[filename] = {
        'count': critical_count,
        'words': found_words,
        'total_comments': len(comments)
    }
    
    print(f"📊 Comments: {len(comments)} | Critical words: {critical_count}")
    
    if found_words:
        print("🔍 Found critical words:")
        for word_info in found_words[:5]:  # Show first 5
            category = word_info['category'].replace('_', ' ').title()
            print(f"  • '{word_info['word']}' ({category})")
            print(f"    └─ \"{word_info['comment'][:60]}...\"")
        
        if len(found_words) > 5:
            print(f"  • ... and {len(found_words) - 5} more")
    
    print()

# Overall analysis
print("📋 **OVERALL ANALYSIS:**")
print("-" * 30)
print(f"🔍 Total critical words found: {total_critical_words}")
print(f"🚨 Critical threshold: {CRITICAL_THRESHOLD}")
print(f"⚠️ Warning threshold: {WARNING_THRESHOLD}")
print()

# Determine action
if total_critical_words >= CRITICAL_THRESHOLD:
    status = "🚫 MERGE BLOCKED"
    action = "FAILURE"
    color = "RED"
elif total_critical_words >= WARNING_THRESHOLD:
    status = "⚠️ WARNING"
    action = "SUCCESS WITH WARNING"
    color = "YELLOW"
else:
    status = "✅ PASSED"
    action = "SUCCESS"
    color = "GREEN"

print(f"🎯 **RESULT: {status}**")
print(f"⚙️ Action: {action}")
print()

# File-by-file breakdown
print("📁 **FILE BREAKDOWN:**")
print("-" * 25)

for filename, analysis in all_files_analysis.items():
    if analysis['count'] >= 5:
        icon = "🚨"
    elif analysis['count'] >= 2:
        icon = "⚠️"
    else:
        icon = "✅"
    
    print(f"{icon} {filename}: {analysis['count']} critical words in {analysis['total_comments']} comments")

print()

# Category breakdown
print("📊 **CATEGORY BREAKDOWN:**")
print("-" * 30)

category_counts = {}
for analysis in all_files_analysis.values():
    for word_info in analysis['words']:
        category = word_info['category']
        category_counts[category] = category_counts.get(category, 0) + 1

for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    category_name = category.replace('_', ' ').title()
    if count >= 3:
        icon = "🚨"
    elif count >= 1:
        icon = "⚠️"
    else:
        icon = "💡"
    print(f"{icon} {category_name}: {count} words")

print()

# Recommendations
print("💡 **RECOMMENDATIONS:**")
print("-" * 25)

if total_critical_words >= CRITICAL_THRESHOLD:
    print("1. 🔍 Review all flagged comments immediately")
    print("2. 🧹 Remove TODO/FIXME comments or create proper tickets")
    print("3. 🔒 Address any security-related comments")
    print("4. 🚀 Fix hacks and workarounds with proper solutions")
    print("5. 📝 Replace temporary comments with documentation")
elif total_critical_words >= WARNING_THRESHOLD:
    print("1. 📋 Review flagged comments before merging")
    print("2. 🧹 Clean up development-related comments")
    print("3. 📝 Consider proper documentation")
else:
    print("1. ✅ Great job! Comments look professional")
    print("2. 📝 Keep writing clear, meaningful comments")

print()
print("🎉 **MERGE GUARD DEMONSTRATION COMPLETE!**")
print(f"The system would {action.lower()} this PR based on {total_critical_words} critical words found.")