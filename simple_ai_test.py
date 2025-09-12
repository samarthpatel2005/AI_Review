"""
Simple test file to verify AI reviewer detection.
"""

import requests

def test_function():
    # hello test - this should be detected
    api_key = "sk-1234567890"  # hardcoded secret
    print("Debug message")  # should suggest logging
    
    # test comment here  
    response = requests.get("https://api.example.com")  # missing error handling
    
    # debug line
    password = "admin123"  # another security issue
    
    return response.json()

class TestClass:
    def __init__(self):
        self.token = "secret_token_abc"  # hardcoded token
        
    def process_data(self):
        # hello test comment
        print("Processing...")  # print statement
        # TODO: implement this
        pass