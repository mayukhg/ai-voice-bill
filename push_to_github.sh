#!/bin/bash

# Script to push ai-voice-bill repository to GitHub

REPO_DIR="/Users/mayukhghosh/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/ai-voice-bill"
cd "$REPO_DIR" || exit 1

echo "📦 AI Voice Bill - GitHub Push Script"
echo "======================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Initializing..."
    git init
fi

# Check current status
echo "📊 Checking git status..."
git status

# Add all files
echo ""
echo "➕ Adding all files..."
git add -A

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit."
else
    echo "💾 Committing changes..."
    git commit -m "Initial commit: AI Voice Bill Payment Service

- Complete backend implementation with Flask
- Flow 1: Voice reminders with AWS Polly
- Flow 2: Voice-based payments with OTP MFA
- AWS integrations (Lex, Polly, DynamoDB, SNS)
- Comprehensive documentation
- Docker support
- Sample data scripts"
fi

# Check for remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [ -z "$REMOTE_URL" ]; then
    echo ""
    echo "⚠️  No GitHub remote configured."
    echo ""
    echo "Please create a repository on GitHub first:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: ai-voice-bill"
    echo "3. Description: AI Voice Bill Payment Service with AWS Lex and Polly"
    echo "4. Choose Public or Private"
    echo "5. DO NOT initialize with README, .gitignore, or license"
    echo "6. Click 'Create repository'"
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/ai-voice-bill.git): " GITHUB_URL
    
    if [ -n "$GITHUB_URL" ]; then
        echo "🔗 Adding remote origin..."
        git remote add origin "$GITHUB_URL"
    else
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
else
    echo "✅ Remote already configured: $REMOTE_URL"
fi

# Set main branch
echo ""
echo "🌿 Setting main branch..."
git branch -M main

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Your repository is now available at:"
    git remote get-url origin
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "1. GitHub repository exists"
    echo "2. You have push permissions"
    echo "3. Your credentials are configured"
    echo ""
    echo "You may need to authenticate:"
    echo "- Use GitHub CLI: gh auth login"
    echo "- Or configure SSH keys"
    echo "- Or use personal access token"
fi

