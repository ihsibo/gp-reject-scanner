# Workflow Files

## google-play-audit.yml

This is the main scanning workflow that analyzes external Android repositories.

### How to Use

1. Go to **Actions** tab in GitHub
2. Click **"Google Play Pre-Release Audit"**
3. Click **"Run workflow"**
4. Fill in inputs:
   - **Repository URL**: The Android app's git URL
   - **Branch**: Branch to scan (e.g., main, release/v1.0.0)
   - **GitHub Token**: (optional) For private repos

### What It Does

1. Checks out this scanner repository
2. Clones the target Android app repository
3. Analyzes it with Claude AI using the prompt in `.github/prompts/`
4. Generates HTML report
5. Uploads report as artifact
6. Passes or fails based on score and critical issues

### Required Secrets

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `GH_PAT`: GitHub Personal Access Token (optional, for private repos)

### Outputs

- **HTML Report**: Download from Artifacts
- **Job Summary**: Shows score, tier, and issue counts
- **Pass/Fail**: Green ✅ or Red ❌ in Actions list

---

See main **README.md** for full documentation.
