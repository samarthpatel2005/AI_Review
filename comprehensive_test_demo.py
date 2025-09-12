#!/usr/bin/env python3
"""
Comprehensive test file to demonstrate AI code reviewer capabilities.
This file contains various types of issues that the AI should detect.
"""

import os
import requests
import json

# Security Issues
API_KEY = "sk-1234567890abcdef"  # Hardcoded API key - SECURITY ISSUE
DATABASE_PASSWORD = "admin123"  # Hardcoded password - SECURITY ISSUE
SECRET_TOKEN = "secret_abc123"  # Hardcoded secret - SECURITY ISSUE

class SecurityDemo:
    def __init__(self):
        self.api_key = "hardcoded_key_here"  # Another security issue
        
    def unsafe_sql_query(self, user_input):
        # SQL injection vulnerability
        query = f"SELECT * FROM users WHERE name = '{user_input}'"
        return query
        
    def unsafe_file_operation(self, filename):
        # Unsafe file operation
        with open(f"/tmp/{filename}", "w") as f:
            f.write("data")

# Code Quality Issues
def bad_function():
    # hello test - this is a test comment that should be removed
    print("Debug output")  # Should use logging instead
    # debug - another test comment
    x = 5  # Unused variable
    # TODO: fix this later
    # FIXME: broken logic here
    
    # Missing error handling
    response = requests.get("https://api.example.com/data")
    data = response.json()
    
    return data

def another_bad_function():
    # test comment here
    password = "secret123"  # Hardcoded credential
    print(f"Password is: {password}")  # Debug print + security issue
    
    # Missing error handling for HTTP requests
    result = requests.post("https://api.test.com", data={"key": password})
    
    return result.text

# Style and Best Practice Issues
def poorlyNamedFunction(a, b, c):  # Poor function naming
    # Missing docstring
    return a + b + c  # No type hints

class badClassName:  # Should be PascalCase
    def __init__(self):
        self.data = None
        
    def longMethodWithTooManyLines(self):
        # This method is too long and does too many things
        print("Starting process")  # Should use logging
        x = 1
        y = 2
        z = 3
        result1 = x + y
        result2 = y + z
        result3 = x + z
        final_result = result1 + result2 + result3
        print(f"Result: {final_result}")  # Should use logging
        return final_result

# Memory and Resource Issues
def resource_leak_demo():
    # File not properly closed
    f = open("test.txt", "w")
    f.write("data")
    # Missing f.close() or context manager

def performance_issue():
    # Inefficient string concatenation
    result = ""
    for i in range(1000):
        result += str(i)  # Should use join()
    return result

# More test patterns
def function_with_issues():
    # hello test comment
    secret_key = "abc123"  # hardcoded secret
    print("Debugging this function")  # print statement
    
    # No error handling
    response = requests.get("https://example.com")
    
    # debug comment
    return response.json()

if __name__ == "__main__":
    # test execution
    print("Running comprehensive test demo")  # Should use logging
    demo = SecurityDemo()
    result = demo.unsafe_sql_query("'; DROP TABLE users; --")
    print(f"Query result: {result}")  # Debug print