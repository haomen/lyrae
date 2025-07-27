#!/usr/bin/env python3
"""
Test script for the OpenAI MCP Server
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if the environment is properly set up"""
    print("Testing environment setup...")
    
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return False
    else:
        print("✅ OPENAI_API_KEY found")
    
    # Check if required packages are installed
    try:
        import openai
        print("✅ openai package installed")
    except ImportError:
        print("❌ openai package not installed")
        return False
    
    try:
        import mcp
        print("✅ mcp package installed")
    except ImportError:
        print("❌ mcp package not installed")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv package installed")
    except ImportError:
        print("❌ python-dotenv package not installed")
        return False
    
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test message."}],
            max_tokens=10
        )
        
        print("✅ OpenAI API connection successful")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("OpenAI MCP Server Test")
    print("=" * 30)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment setup failed. Please fix the issues above.")
        sys.exit(1)
    
    # Test OpenAI connection
    if not test_openai_connection():
        print("\n❌ OpenAI API test failed. Please check your API key.")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("\nYou can now run the MCP server with:")
    print("python mcp_server.py")

if __name__ == "__main__":
    main() 