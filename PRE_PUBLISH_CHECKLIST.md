# Pre-Publish Security Checklist

Before pushing this repository to public GitHub, verify all items below:

## ✅ Credentials Removed

- [ ] No OAuth client IDs in code
- [ ] No OAuth client secrets in code
- [ ] No AWS account IDs in code
- [ ] No hardcoded passwords or tokens
- [ ] No API keys in code

## ✅ Internal Information Removed

- [ ] No internal domain names (replace with example.com)
- [ ] No specific gateway IDs (use placeholders or env vars)
- [ ] No target IDs hardcoded
- [ ] No internal IP addresses
- [ ] No employee names or emails

## ✅ Configuration Files

- [ ] `.env` file is in `.gitignore`
- [ ] `.env.example` has placeholder values only
- [ ] No real credentials in example files
- [ ] All sensitive config uses environment variables

## ✅ Documentation

- [ ] README.md has no sensitive information
- [ ] SECURITY.md is present
- [ ] LICENSE file is present
- [ ] CONTRIBUTING.md is present
- [ ] All docs use placeholder values

## ✅ Code Review

- [ ] All Python files reviewed for secrets
- [ ] All scripts use environment variables
- [ ] No debug print statements with sensitive data
- [ ] Error messages don't expose internal details

## ✅ Git History

- [ ] No sensitive data in commit messages
- [ ] No sensitive data in previous commits
- [ ] Consider using `git filter-branch` if needed
- [ ] Or start fresh repository if history is compromised

## ✅ Dependencies

- [ ] `requirements.txt` has no internal packages
- [ ] All dependencies are from public PyPI
- [ ] No references to internal package repositories

## ✅ Testing

- [ ] Test scripts use environment variables
- [ ] No hardcoded test credentials
- [ ] Example values are clearly placeholders

## Commands to Check

```bash
# Search for potential secrets
grep -r "client_secret" .
grep -r "password" .
grep -r "api_key" .
grep -r "token" .

# Search for internal domains
grep -r "presidio-labs.com" .
grep -r ".internal" .

# Search for AWS account IDs (12 digits)
grep -rE "[0-9]{12}" .

# Search for specific gateway IDs
grep -r "yhoea9a1bw" .

# Check git history for secrets
git log -p | grep -i "secret"
git log -p | grep -i "password"
```

## If Secrets Found in Git History

If you find secrets in git history:

### Option 1: BFG Repo-Cleaner (Recommended)
```bash
# Install BFG
brew install bfg  # macOS
# or download from https://rtyley.github.io/bfg-repo-cleaner/

# Remove secrets
bfg --replace-text passwords.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Option 2: Start Fresh
```bash
# Create new repo without history
rm -rf .git
git init
git add .
git commit -m "Initial commit"
```

## Final Verification

Before pushing:

```bash
# Review all changes
git diff

# Check what will be pushed
git log --oneline

# Verify .gitignore is working
git status

# Double-check no secrets
git grep -i "secret"
git grep -i "password"
```

## After Publishing

- [ ] Enable GitHub security features
- [ ] Enable Dependabot alerts
- [ ] Enable secret scanning
- [ ] Set up branch protection
- [ ] Review repository settings
- [ ] Add security policy
- [ ] Monitor for exposed secrets

## Emergency Response

If secrets are accidentally published:

1. **Immediately** rotate all exposed credentials
2. Remove secrets from repository
3. Force push cleaned history (if possible)
4. Notify security team
5. Review access logs for unauthorized use
6. Update incident response documentation

## Contact

Security concerns: security@example.com
