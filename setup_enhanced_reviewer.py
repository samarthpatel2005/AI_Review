#!/usr/bin/env python3
"""
Quick setup script for Enhanced GitHub PR Reviewer
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import boto3
        import requests
        print("✅ Required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing packages: {e}")
        return False

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def check_aws_credentials():
    """Check AWS credentials."""
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    if aws_key and aws_secret:
        print("✅ AWS credentials found")
        return True
    else:
        print("⚠️ AWS credentials not found in environment variables")
        print("Set them with:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        return False

def check_github_token():
    """Check GitHub token."""
    token = os.environ.get('GITHUB_TOKEN')
    
    if token:
        print("✅ GitHub token found")
        return True
    else:
        print("⚠️ GitHub token not found (optional for local testing)")
        print("Set it with: export GITHUB_TOKEN=your_github_token")
        return False

def verify_setup():
    """Verify the setup is working."""
    print("\n🧪 Testing AWS Bedrock connection...")
    try:
        import boto3
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ AWS Bedrock client created successfully")
        return True
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
        return False

def show_next_steps():
    """Show what to do next."""
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. 📂 Copy the enhanced-ai-review.yml to .github/workflows/")
    print("2. 🔑 Add AWS secrets to your GitHub repository:")
    print("   - Go to Settings → Secrets and variables → Actions")
    print("   - Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    print("3. 🧪 Test locally:")
    print("   python test_enhanced_reviewer.py --create-test-file")
    print("4. 🚀 Create a pull request to see it in action!")
    print("\n📖 Read ENHANCED_SETUP_GUIDE.md for detailed instructions")

def main():
    """Main setup function."""
    print("🚀 Enhanced GitHub PR Reviewer Setup")
    print("=" * 50)
    
    # Check and install requirements
    if not check_requirements():
        if not install_requirements():
            sys.exit(1)
    
    # Check credentials
    aws_ok = check_aws_credentials()
    github_ok = check_github_token()
    
    # Test connection
    if aws_ok:
        bedrock_ok = verify_setup()
    else:
        bedrock_ok = False
    
    # Show status
    print("\n📊 Setup Status:")
    print(f"{'✅' if check_requirements() else '❌'} Python packages")
    print(f"{'✅' if aws_ok else '⚠️'} AWS credentials")
    print(f"{'✅' if github_ok else '⚠️'} GitHub token (optional)")
    print(f"{'✅' if bedrock_ok else '❌'} AWS Bedrock connection")
    
    if aws_ok and bedrock_ok:
        show_next_steps()
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()