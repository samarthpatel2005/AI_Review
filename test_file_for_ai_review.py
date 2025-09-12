#!/usr/bin/env python3
"""
Test script to verify GitHub Action setup
This file contains intentional issues for testing the AI reviewer
"""

import os
import subprocess

def unsafe_function(user_input):
    # SECURITY ISSUE: Command injection vulnerability
    command = f"echo {user_input}"
    os.system(command)  # Unsafe! Should use subprocess with shell=False

def memory_leak_example():
    # MEMORY ISSUE: Potential memory leak in C-style thinking
    large_list = []
    for i in range(1000000):
        large_list.append(f"Item {i}")
    # Missing cleanup - not a real issue in Python but demonstrates the concept

def division_error(a, b):
    # LOGIC ERROR: No zero division check
    return a / b  # What if b is 0?

def inefficient_algorithm(items):
    # PERFORMANCE ISSUE: O(n²) when O(n) is possible
    result = []
    for item in items:
        if item not in result:  # This is O(n) for each iteration
            result.append(item)
    return result

def better_algorithm(items):
    # IMPROVEMENT: O(n) solution
    return list(set(items))

def unvalidated_input(data):
    # SECURITY ISSUE: No input validation
    return eval(data)  # Dangerous! Should never use eval on user input

def main():
    # STYLE ISSUE: Inconsistent naming
    user_Data = input("Enter some data: ")
    
    # LOGIC ISSUE: Unhandled exception
    result = division_error(10, 0)  # This will crash
    
    print(f"Result: {result}")

if __name__ == "__main__":
    main()