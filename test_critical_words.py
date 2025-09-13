"""
Test file with many critical words in comments to trigger the merge guard.
This file is designed to hit the 10+ critical words threshold.
"""

import requests
import os

class TestClass:
    def __init__(self):
        # TODO: This is a temporary hack and needs to be fixed  # Critical words: TODO, temporary, hack
        self.api_key = "sk-test123"  # hardcoded secret - bad practice  # Critical words: hardcoded, secret, bad
        
    def process_data(self, user_input):
        # FIXME: This is broken and has a security vulnerability  # Critical words: FIXME, broken, security, vulnerability
        # WARNING: potential SQL injection here - needs urgent fix  # Critical words: warning, injection, urgent
        query = f"SELECT * FROM users WHERE name = '{user_input}'"
        
        # debug: this is slow and has performance issues  # Critical words: debug, slow, performance
        print("Debug output")  # Remove this debug code
        
        return query
    
    def authenticate_user(self, password):
        # hack: quick workaround for authentication bug  # Critical words: hack, workaround, bug
        # TODO: implement proper error handling and fix memory leak  # Critical words: TODO, error, memory_leak
        
        if password == "admin123":  # hardcoded password - security risk  # Critical words: hardcoded, password, security
            return True
            
        # FIXME: this code is messy and needs refactoring  # Critical words: FIXME, messy, refactoring
        return False
    
    def legacy_function(self):
        # WARNING: this function is deprecated and unsafe  # Critical words: warning, deprecated, unsafe
        # technical debt: old code that should be removed  # Critical words: technical_debt, old_code
        
        # ugly workaround for broken API  # Critical words: ugly, workaround, broken
        try:
            result = eval("some_code")  # insecure eval usage  # Critical words: insecure, eval
        except:
            # TODO: proper exception handling needed  # Critical words: TODO, exception
            pass
            
        return result

# test_only: this entire class is incomplete and has issues  # Critical words: test_only, incomplete
# debug comment: remove before production  # Critical words: debug, production
# temporary fix for crash in main branch  # Critical words: temporary, crash

def main():
    # hack: dirty solution until we fix the real problem  # Critical words: hack, dirty, problem
    # deadlock issue in multi-threading - needs investigation  # Critical words: deadlock, investigation
    
    test = TestClass()
    
    # vulnerability: XSS attack possible here  # Critical words: vulnerability, XSS
    # performance bottleneck - optimize this later  # Critical words: performance, bottleneck, optimize
    
    return test

# Critical words count in this file should be 25+, well above the 10 threshold!
# The merge guard should block this PR and provide detailed analysis.

if __name__ == "__main__":
    # debug: test execution  # Critical words: debug, test
    main()