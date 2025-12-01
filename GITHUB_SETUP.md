# GitHub Setup Instructions

Follow these steps to push your repository to GitHub.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-voice-bill`
3. Description: `AI Voice Bill Payment Service with AWS Lex and Polly`
4. Choose **Public** or **Private**
5. **IMPORTANT**: Do NOT check "Add a README file", "Add .gitignore", or "Choose a license"
6. Click **"Create repository"**

## Step 2: Run the Push Script

Make the script executable and run it:

```bash
cd "/Users/mayukhghosh/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/ai-voice-bill"
chmod +x push_to_github.sh
./push_to_github.sh
```

The script will:
- Add all files
- Commit changes
- Ask for your GitHub repository URL
- Push to GitHub

## Step 3: Manual Push (Alternative)

If the script doesn't work, run these commands manually:

```bash
cd "/Users/mayukhghosh/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Code/ai-voice-bill"

# Add all files
git add -A

# Commit
git commit -m "Initial commit: AI Voice Bill Payment Service

- Complete backend implementation with Flask
- Flow 1: Voice reminders with AWS Polly
- Flow 2: Voice-based payments with OTP MFA
- AWS integrations (Lex, Polly, DynamoDB, SNS)
- Comprehensive documentation
- Docker support
- Sample data scripts"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-voice-bill.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

## Authentication

If you're prompted for credentials:

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when prompted

### Option 2: SSH Keys
1. Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
2. Use SSH URL: `git@github.com:YOUR_USERNAME/ai-voice-bill.git`

### Option 3: GitHub CLI
```bash
gh auth login
gh repo create ai-voice-bill --public --source=. --remote=origin --push
```

## Verify

After pushing, visit:
```
https://github.com/YOUR_USERNAME/ai-voice-bill
```

You should see all your files there!

