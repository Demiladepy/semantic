# 🔒 Security Checklist - Preventing Secret Leaks

## ✅ Immediate Actions Required

### 1. **Verify .env is NOT in Git History**

```bash
# Check if .env was ever committed
git log --all --full-history -- .env

# If .env appears in history, you MUST:
# 1. Remove it from git history
# 2. Rotate ALL API keys and private keys
# 3. Generate new credentials
```

### 2. **Remove .env from Git (if committed)**

```bash
# Remove .env from git cache
git rm --cached .env

# Remove from entire git history (DANGEROUS - use with caution)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: This rewrites history)
git push origin --force --all
```

### 3. **Rotate ALL Credentials Immediately**

If `.env` was ever committed to git, you MUST rotate:

- ✅ OpenAI API Key
- ✅ Telegram Bot Token
- ✅ Polygon Private Key
- ✅ Solana Private Key
- ✅ Kalshi API Key
- ✅ Polymarket API Key
- ✅ All other private keys

---

## 🔍 Security Audit Checklist

### Files That Should NEVER Be Committed

- [ ] `.env` - Environment variables with secrets
- [ ] `.env.local` - Local environment overrides
- [ ] `*.key` - Private key files
- [ ] `*.pem` - Certificate files
- [ ] `wallet.json` - Wallet files
- [ ] `keypair.json` - Keypair files
- [ ] `credentials.json` - Credential files
- [ ] `secrets.json` - Secret configuration
- [ ] Any file containing private keys
- [ ] Any file containing API keys
- [ ] Any file containing passwords

### Files That SHOULD Be Committed

- [x] `.env.example` - Template without real values
- [x] `.gitignore` - Git ignore rules
- [x] `README.md` - Documentation
- [x] `requirements.txt` - Python dependencies
- [x] `package.json` - Node.js dependencies
- [x] All source code files (`.py`, `.js`)
- [x] Documentation files (`.md`)

---

## 🛡️ Security Best Practices

### 1. **Environment Variables**

✅ **DO:**
- Use `.env` for local development
- Keep `.env.example` with placeholder values
- Use environment variables in production
- Rotate keys regularly
- Use different keys for dev/staging/prod

❌ **DON'T:**
- Commit `.env` to git
- Share `.env` files via email/chat
- Hardcode secrets in source code
- Use production keys in development
- Reuse keys across projects

### 2. **Private Keys**

✅ **DO:**
- Store in secure key management systems
- Use hardware wallets for large amounts
- Encrypt private keys at rest
- Use separate keys for testing
- Back up keys securely offline

❌ **DON'T:**
- Store in plain text files
- Commit to version control
- Share via insecure channels
- Use same key across environments
- Store in cloud storage unencrypted

### 3. **API Keys**

✅ **DO:**
- Use API key rotation
- Set IP restrictions when possible
- Monitor API usage
- Use separate keys per service
- Revoke unused keys

❌ **DON'T:**
- Expose in client-side code
- Log API keys
- Share publicly
- Use root/admin keys unnecessarily
- Store in browser localStorage

---

## 🔐 Recommended Security Tools

### 1. **Git Secrets Scanner**

```bash
# Install git-secrets
# macOS
brew install git-secrets

# Windows (via Git Bash)
git clone https://github.com/awslabs/git-secrets
cd git-secrets
make install

# Configure for your repo
git secrets --install
git secrets --register-aws
```

### 2. **TruffleHog (Scan for Secrets)**

```bash
# Install
pip install truffleHog

# Scan repository
trufflehog --regex --entropy=True .

# Scan git history
trufflehog --regex --entropy=True https://github.com/Demiladepy/semantic.git
```

### 3. **GitGuardian (GitHub Integration)**

- Install GitGuardian GitHub App
- Automatically scans commits for secrets
- Alerts on detected secrets
- Free for public repositories

### 4. **Pre-commit Hooks**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for .env file
if git diff --cached --name-only | grep -q "^.env$"; then
    echo "❌ ERROR: Attempting to commit .env file!"
    echo "This file contains secrets and should not be committed."
    exit 1
fi

# Check for private keys
if git diff --cached --name-only | grep -qE "\.(key|pem)$"; then
    echo "❌ ERROR: Attempting to commit private key file!"
    exit 1
fi

# Check for common secret patterns
if git diff --cached -U0 | grep -qE "(api_key|API_KEY|private_key|PRIVATE_KEY|secret|SECRET).*=.*['\"]?[a-zA-Z0-9]{20,}"; then
    echo "⚠️  WARNING: Possible secret detected in commit!"
    echo "Please review your changes carefully."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 🚨 What to Do If Secrets Are Leaked

### Immediate Response (Within 1 Hour)

1. **Rotate ALL Credentials**
   - Generate new API keys
   - Create new private keys
   - Update all services

2. **Revoke Compromised Keys**
   - Disable old API keys
   - Revoke access tokens
   - Block compromised wallets

3. **Remove from Git History**
   ```bash
   # Use BFG Repo-Cleaner (recommended)
   java -jar bfg.jar --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

4. **Monitor for Abuse**
   - Check API usage logs
   - Monitor wallet transactions
   - Review access logs
   - Set up alerts

### Within 24 Hours

5. **Audit All Access**
   - Review who has access
   - Check for unauthorized usage
   - Verify all API calls

6. **Update Security Measures**
   - Implement stricter controls
   - Add monitoring
   - Update documentation

7. **Notify Stakeholders**
   - Inform team members
   - Report to security team
   - Document incident

---

## 📋 Regular Security Maintenance

### Weekly
- [ ] Review API usage logs
- [ ] Check for unusual activity
- [ ] Verify access controls

### Monthly
- [ ] Rotate API keys
- [ ] Audit permissions
- [ ] Review security logs
- [ ] Update dependencies

### Quarterly
- [ ] Full security audit
- [ ] Penetration testing
- [ ] Review and update policies
- [ ] Train team on security

---

## 🔍 Verify Current Repository Status

Run these commands to check your repository:

```bash
# 1. Check if .env is tracked
git ls-files | grep "\.env$"
# Should return nothing

# 2. Check git history for .env
git log --all --full-history -- .env
# Should return nothing

# 3. Check for hardcoded secrets
grep -r "sk-" . --exclude-dir=node_modules --exclude-dir=.git
grep -r "PRIVATE_KEY.*=" . --exclude-dir=node_modules --exclude-dir=.git

# 4. Verify .gitignore is working
git check-ignore -v .env
# Should show: .gitignore:3:.env    .env

# 5. Check for sensitive files in staging
git status
# .env should NOT appear in "Changes to be committed"
```

---

## ✅ Security Verification Script

Create `verify_security.sh`:

```bash
#!/bin/bash

echo "🔒 Security Verification Script"
echo "================================"
echo ""

# Check 1: .env not tracked
echo "✓ Checking if .env is tracked..."
if git ls-files | grep -q "^\.env$"; then
    echo "❌ FAIL: .env is tracked in git!"
    exit 1
else
    echo "✅ PASS: .env is not tracked"
fi

# Check 2: .env in .gitignore
echo "✓ Checking if .env is in .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "✅ PASS: .env is in .gitignore"
else
    echo "❌ FAIL: .env is not in .gitignore!"
    exit 1
fi

# Check 3: No private keys tracked
echo "✓ Checking for tracked private keys..."
if git ls-files | grep -qE "\.(key|pem)$"; then
    echo "❌ FAIL: Private key files are tracked!"
    exit 1
else
    echo "✅ PASS: No private key files tracked"
fi

# Check 4: .env.example exists
echo "✓ Checking if .env.example exists..."
if [ -f ".env.example" ]; then
    echo "✅ PASS: .env.example exists"
else
    echo "⚠️  WARNING: .env.example not found"
fi

echo ""
echo "================================"
echo "✅ Security verification complete!"
```

Run it:
```bash
chmod +x verify_security.sh
./verify_security.sh
```

---

## 📞 Emergency Contacts

If you discover a security breach:

1. **Immediately** rotate all credentials
2. **Document** what was exposed and when
3. **Review** access logs for unauthorized usage
4. **Report** to your security team
5. **Update** security measures to prevent recurrence

---

## 📚 Additional Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git Secrets Tool](https://github.com/awslabs/git-secrets)
- [TruffleHog](https://github.com/trufflesecurity/truffleHog)
- [GitGuardian](https://www.gitguardian.com/)

---

**Last Updated**: 2026-01-27  
**Status**: ✅ Active Protection
