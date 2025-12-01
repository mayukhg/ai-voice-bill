#!/usr/bin/env python3
"""
Python script to push ai-voice-bill repository to GitHub.
This script can be run directly and will guide you through the process.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    # Get the repository directory
    repo_dir = Path(__file__).parent.absolute()
    os.chdir(repo_dir)
    
    print("📦 AI Voice Bill - GitHub Push Script")
    print("=" * 50)
    print(f"Repository directory: {repo_dir}")
    print()
    
    # Check if git is available
    success, _, _ = run_command("git --version", check=False)
    if not success:
        print("❌ Git is not installed or not in PATH")
        sys.exit(1)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("ℹ️  Initializing git repository...")
        run_command("git init")
    
    # Check current status
    print("📊 Checking git status...")
    success, stdout, _ = run_command("git status --short")
    if stdout.strip():
        print("Files to be committed:")
        print(stdout)
    else:
        print("No changes detected.")
    
    # Add all files
    print("\n➕ Adding all files...")
    run_command("git add -A")
    
    # Check if there are changes to commit
    success, stdout, _ = run_command("git diff --staged --name-only")
    if stdout.strip():
        print("\n💾 Committing changes...")
        commit_message = """Initial commit: AI Voice Bill Payment Service

- Complete backend implementation with Flask
- Flow 1: Voice reminders with AWS Polly
- Flow 2: Voice-based payments with OTP MFA
- AWS integrations (Lex, Polly, DynamoDB, SNS)
- Comprehensive documentation
- Docker support
- Sample data scripts"""
        
        run_command(f'git commit -m "{commit_message}"')
        print("✅ Changes committed")
    else:
        print("ℹ️  No changes to commit.")
    
    # Check for remote
    success, stdout, _ = run_command("git remote get-url origin", check=False)
    if not success or not stdout.strip():
        print("\n⚠️  No GitHub remote configured.")
        print("\nPlease create a repository on GitHub first:")
        print("1. Go to https://github.com/new")
        print("2. Repository name: ai-voice-bill")
        print("3. Description: AI Voice Bill Payment Service with AWS Lex and Polly")
        print("4. Choose Public or Private")
        print("5. DO NOT initialize with README, .gitignore, or license")
        print("6. Click 'Create repository'")
        print()
        
        github_url = input("Enter your GitHub repository URL (e.g., https://github.com/username/ai-voice-bill.git): ").strip()
        
        if not github_url:
            print("❌ No URL provided. Exiting.")
            sys.exit(1)
        
        if not github_url.startswith("http") and not github_url.startswith("git@"):
            print("⚠️  URL doesn't look valid. Adding https:// prefix...")
            if "github.com" not in github_url:
                github_url = f"https://github.com/{github_url}"
            if not github_url.endswith(".git"):
                github_url = f"{github_url}.git"
            if not github_url.startswith("http"):
                github_url = f"https://{github_url}"
        
        print(f"\n🔗 Adding remote origin: {github_url}")
        run_command(f'git remote add origin "{github_url}"')
    else:
        print(f"✅ Remote already configured: {stdout.strip()}")
    
    # Set main branch
    print("\n🌿 Setting main branch...")
    run_command("git branch -M main", check=False)
    
    # Push to GitHub
    print("\n🚀 Pushing to GitHub...")
    print("(You may be prompted for credentials)")
    print()
    
    success, stdout, stderr = run_command("git push -u origin main", check=False)
    
    if success:
        print("\n✅ Successfully pushed to GitHub!")
        success, url, _ = run_command("git remote get-url origin", check=False)
        if success:
            print(f"\nYour repository is now available at:")
            print(url.strip())
    else:
        print("\n❌ Push failed. Error details:")
        print(stderr)
        print("\nTroubleshooting:")
        print("1. Verify GitHub repository exists")
        print("2. Check you have push permissions")
        print("3. Authenticate using one of these methods:")
        print("   - GitHub CLI: gh auth login")
        print("   - Personal Access Token: https://github.com/settings/tokens")
        print("   - SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh")
        sys.exit(1)

if __name__ == "__main__":
    main()

