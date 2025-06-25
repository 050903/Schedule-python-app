#!/usr/bin/env python
# SuperElonAI/check_api_key_simple.py
from dotenv import load_dotenv
import os
import openai

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("API key not found in environment variables")
        return
    
    print(f"API key found: {api_key[:10]}...")
    
    # Set the API key
    openai.api_key = api_key
    
    try:
        # Make a minimal API call to test the key
        response = openai.Model.list(limit=1)
        print("API key is active and working!")
        print(f"Available models: {[model.id for model in response.data[:3]]}")
    except openai.error.AuthenticationError:
        print("API key is invalid or expired")
    except openai.error.RateLimitError:
        print("Rate limit exceeded")
    except Exception as e:
        print(f"Error checking API key: {str(e)}")

if __name__ == "__main__":
    main()