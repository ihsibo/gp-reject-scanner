# Google Play Release Rejection Scanner

Centralized GitHub Action that scans **any** Android repository for Google Play policy violations and predicts rejection likelihood before submission.

## 🎯 How It Works

This is a **standalone scanner repository**. You don't need to add it to your Android projects. Instead:

1. This repo contains the scanning workflow
2. You trigger it manually and provide your Android app's repository URL
3. It clones your app, scans it with Claude AI, and generates a report
4. You get a pass/fail result based on Google Play compliance

---

## 🚀 Setup (One Time)

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/gp-release-reject-scanner.git
cd gp-release-reject-scanner
```

Push to your GitHub account if you haven't already.

### 2. Add Required Secrets

Go to Settings → Secrets and variables → Actions

**Required Secret #1: Anthropic API Key**
- Click "New repository secret"
- Name: `ANTHROPIC_API_KEY`
- Value: Your Anthropic API key (starts with `sk-ant-...`)

**Required Secret #2: GitHub Token (for private org repos)**
- Click "New repository secret"  
- Name: `GH_ORG_TOKEN`
- Value: Personal Access Token with `repo` scope (starts with `ghp_...`)

**How to create PAT:**
1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Check `repo` scope
4. Copy the token

> 📖 **Detailed instructions:** See [PRIVATE_REPOS_SETUP.md](PRIVATE_REPOS_SETUP.md)

---

## 📋 How to Scan an Android App

### Option 1: Via GitHub UI (Easiest)

1. Go to your scanner repo on GitHub
2. Click **Actions** tab
3. Click **Google Play Pre-Release Audit** workflow
4. Click **Run workflow** button
5. Fill in:
   - **Repository URL**: `https://github.com/your-org/android-app.git`
   - **Branch**: `main` (or `release/v1.0.0`, etc.)
6. Click **Run workflow**
7. Wait 2-5 minutes
8. Download HTML report from Artifacts

> **Note:** For private repos, make sure you've added the `GH_ORG_TOKEN` secret (see setup above).

### Option 2: Via GitHub CLI

```bash
gh workflow run "Google Play Pre-Release Audit" \
  -f repository_url="https://github.com/owner/android-app.git" \
  -f branch="main"
```

### Option 3: Via API/cURL

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/gp-release-reject-scanner/actions/workflows/google-play-audit.yml/dispatches \
  -d '{"ref":"main","inputs":{"repository_url":"https://github.com/owner/android-app.git","branch":"main"}}'
```

---

## 📊 Understanding Results

### ✅ PASS (Green Checkmark)

```
Score: 85%+
Critical Issues: 0
Result: Safe to release
```

### ❌ FAIL (Red X)

```
Score: < 50%  OR  Critical Issues: > 0
Result: Fix issues before releasing
```

### Report Details

Download the HTML report from Artifacts to see:
- Detailed findings for each category
- File paths and line numbers
- Specific fix recommendations
- Risk tier assessment

---

## 🔐 Scanning Private Repositories

The workflow automatically uses the `GH_ORG_TOKEN` secret to access private organization repositories.

**Setup:**
1. Create a GitHub Personal Access Token with `repo` scope
2. Add it as a secret named `GH_ORG_TOKEN`
3. The workflow uses it automatically - no extra input needed!

> 📖 **Full setup guide:** See [PRIVATE_REPOS_SETUP.md](PRIVATE_REPOS_SETUP.md) for step-by-step instructions.

---

## 📝 What Gets Scanned

### 7 Categories, 50+ Checks

1. **Technical Requirements** (HIGH)
   - Target SDK ≥ 34
   - 64-bit support
   - App Bundle format

2. **Permissions** (VERY HIGH)
   - Overly broad permissions
   - Unused permissions
   - Background location

3. **Privacy & Data Safety** (HIGH)
   - Privacy policy URL
   - Analytics/tracking SDKs
   - Encrypted storage

4. **Security** (VERY HIGH)
   - Hardcoded API keys
   - Cleartext HTTP
   - WebView security

5. **Google Play Billing** (HIGH)
   - Billing library version
   - Alternative payments

6. **Ads & Third-Party SDKs** (MEDIUM)
   - Ad SDK declarations
   - COPPA compliance

7. **Manifest & Store Listing** (MEDIUM)
   - App label and icon
   - Debug artifacts

---

## 🎯 Scoring System

**Starting Score**: 100 points

**Deductions**:
- ❌ Critical FAIL: -15 points
- ❌ Regular FAIL: -5 points
- ⚠️ Warning: -2 points

**Thresholds**:
- 🟢 85-100%: High confidence
- 🟡 65-84%: Medium confidence
- 🟠 40-64%: Risky
- 🔴 0-39%: High risk

**Failure Conditions**:
- Score < **50%** → ❌ FAIL
- Critical issues > 0 → ❌ FAIL

---

## 💡 Example Usage

### Scan a Release Branch

```
Repository URL: https://github.com/mycompany/my-android-app.git
Branch: release/v2.1.0
```

Result: 
- Clones the release branch
- Scans for Google Play violations
- Reports if it's safe to submit to Play Store

### Scan Before Creating Release

```
Repository URL: https://github.com/mycompany/my-android-app.git
Branch: develop
```

Result:
- Check if develop branch is ready for release
- Fix issues before creating release branch

---

## 🔄 Integrating with Your Workflow

### Option A: Manual Scanning (Current Setup)
Run the scan manually before each release submission.

### Option B: Automated Scanning (Advanced)

You can trigger this workflow from other repositories using `repository_dispatch` or workflow triggers.

**Example**: Add to your Android repo's workflow:

```yaml
# In your Android repo
name: Trigger Scanner
on:
  push:
    branches:
      - release/**

jobs:
  trigger-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger scanner workflow
        run: |
          gh workflow run "Google Play Pre-Release Audit" \
            --repo YOUR_USERNAME/gp-release-reject-scanner \
            -f repository_url="${{ github.server_url }}/${{ github.repository }}.git" \
            -f branch="${{ github.ref_name }}"
        env:
          GH_TOKEN: ${{ secrets.GH_PAT }}
```

---

## 🐛 Troubleshooting

### "Failed to clone repository"
- Check repository URL is correct
- For private repos, ensure GitHub token has access
- Verify branch name exists

### "ANTHROPIC_API_KEY not set"
- Add the secret in repository Settings → Secrets

### "Could not extract score"
- Check the HTML report manually in artifacts
- Verify prompt file exists in `.github/prompts/`

### Action always passes/fails
- Download HTML artifact and check the score
- Verify data attributes are in the HTML

---

## 📚 Multiple Apps

You can scan as many Android apps as you want from this single scanner repo:

```bash
# Scan App 1
Run workflow with: https://github.com/company/app1.git

# Scan App 2
Run workflow with: https://github.com/company/app2.git

# Scan App 3
Run workflow with: https://github.com/company/app3.git
```

Each scan:
- Creates a separate workflow run
- Generates its own HTML report
- Shows pass/fail independently
- Stores artifact with unique name

---

## 🔐 Security

- ✅ API key stored as encrypted GitHub secret
- ✅ Cloned repos are temporary (deleted after scan)
- ✅ Reports stored 30 days, then auto-deleted
- ✅ Only repo members can access artifacts
- ✅ Code analyzed by SOC 2 certified Anthropic API

---

## 📞 Support

For issues:
1. Check the workflow run logs
2. Download and review the HTML report
3. Verify all secrets are configured
4. Ensure target repository is accessible

---

## 🎉 Benefits

✅ **Centralized**: One scanner for all your Android apps
✅ **No Pollution**: No workflow files added to your app repos
✅ **Reusable**: Scan any branch of any app anytime
✅ **Safe**: Temporary clones, no permanent changes
✅ **Fast**: Results in 2-5 minutes
✅ **Actionable**: Clear reports with fix recommendations

---

**Version**: 2.0 (Standalone Scanner)
**Updated**: 2026-03-02
