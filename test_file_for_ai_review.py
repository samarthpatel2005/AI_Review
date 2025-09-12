# Test file for AI code review
"""
Test file for AI code review
This file contains various issues that should be detected by the AI reviewer
and generate GitHub-style commit suggestions
"""

import os
import subprocess

# Security issue: hardcoded password (should get suggestion)
PASSWORD = "secret123"
API_KEY = "abcd1234"

def unsafe_sql_query(user_input):
    """Function with SQL injection vulnerability"""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def divide_numbers(a, b):
    """Function without error handling (should get suggestion)"""
    return a / b

def execute_command(user_input):
    """Command injection vulnerability (should get suggestion)"""
    os.system(f"ls {user_input}")

def inefficient_loop():
    """Performance issue"""
    result = []
    for i in range(1000):
        for j in range(1000):
            result.append(i * j)
    return result

#For test
def missing_space_comment():
    """Comment formatting issue (should get suggestion)"""
    pass

class BadClass:
    """Class with various issues"""
    
    def __init__(self):
        self.data = None
    
    def process_data(self, data):
        # No validation (should get suggestion)
        self.data = data
        return self.data.upper()

def main():
    """Main function"""
    user_name = input("Enter name: ")
    result = unsafe_sql_query(user_name)
    print(result)

if __name__ == "__main__":
    main()
