#!/usr/bin/env python
# SuperElonAI/check_api_key.py
import os
from core.questions import check_api_key_active

def main():
    print("Checking OpenAI API key status...")
    is_active, message = check_api_key_active()
    
    print(f"Status: {'Active' if is_active else 'Inactive'}")
    print(f"Message: {message}")
    
    if not is_active:
        print("\nTroubleshooting tips:")
        print("1. Check if OPENAI_API_KEY environment variable is set")
        print("2. Verify the API key is correct and not expired")
        print("3. Check your OpenAI account billing status")
        print("4. Ensure you have sufficient API credits")
        
        # Check if environment variable exists
        if not os.getenv("OPENAI_API_KEY"):
            print("\nWARNING: OPENAI_API_KEY environment variable is not set!")
            print("Set it using:")
            print("  Windows (Command Prompt): set OPENAI_API_KEY=your_api_key_here")
            print("  Windows (PowerShell): $env:OPENAI_API_KEY = 'your_api_key_here'")

if __name__ == "__main__":
    main()