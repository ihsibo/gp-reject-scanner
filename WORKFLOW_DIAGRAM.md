# 📊 How the Scanner Works

## Visual Flow

```
┌─────────────────────────────────────────────────────────┐
│         YOU (Developer)                                 │
│  "I want to scan my Android app before releasing"       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    GitHub Actions Tab                                   │
│    Click "Run workflow"                                 │
│                                                         │
│    Enter:                                               │
│    • Repository URL: github.com/you/android-app.git     │
│    • Branch: main                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    GitHub Action Starts                                 │
│    ✓ Checkout scanner repo (this repo)                  │
│    ✓ Clone your Android app to temp folder              │
│    ✓ Install Anthropic SDK                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Claude AI Analysis                                   │
│                                                         │
│    Sends to Anthropic API:                              │
│    • Scanning instructions (prompt)                     │
│    • Your app's file structure                          │
│    • build.gradle content                               │
│    • AndroidManifest.xml                                │
│                                                         │
│    Claude scans 7 categories:                           │
│    1. Technical Requirements                            │
│    2. Permissions                                       │
│    3. Privacy & Data Safety                             │
│    4. Security                                          │
│    5. Google Play Billing                               │
│    6. Ads & Third-Party SDKs                            │
│    7. Manifest & Store Listing                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Claude Generates HTML Report                         │
│                                                         │
│    <html data-score="72"                                │
│          data-critical-fails="2"                        │
│          data-warns="5">                                │
│                                                         │
│    Contains:                                            │
│    • Overall score (0-100%)                             │
│    • List of all findings                               │
│    • File paths where issues found                      │
│    • How to fix each issue                              │
│    • Risk tier assessment                               │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Workflow Evaluates Results                           │
│                                                         │
│    IF score < 50% OR critical issues > 0:               │
│       ❌ Mark workflow as FAILED                        │
│    ELSE:                                                │
│       ✅ Mark workflow as PASSED                        │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Workflow Completes                                   │
│                                                         │
│    ✓ Upload HTML report as artifact                     │
│    ✓ Show score in job summary                          │
│    ✓ Display ✅ or ❌ in Actions list                    │
│    ✓ Delete temporary cloned repo                       │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         YOU (Developer)                                 │
│                                                         │
│    See results in Actions tab:                          │
│    • ✅ Green = Safe to release                         │
│    • ❌ Red = Fix issues first                          │
│                                                         │
│    Download HTML report to see:                         │
│    • What issues were found                             │
│    • Where they are (file + line number)                │
│    • How to fix them                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Example: Scanning "MyAwesomeApp"

### Input
```
Repository: https://github.com/company/MyAwesomeApp.git
Branch: release/v2.0.0
```

### What Happens
1. Scanner clones release/v2.0.0 branch
2. Claude analyzes the code
3. Finds 2 critical issues:
   - Hardcoded API key in ApiClient.java
   - Cleartext HTTP allowed
4. Calculates score: 42%

### Output
```
❌ FAILED
Score: 42% (below 50% threshold)
Critical Issues: 2
Warnings: 12

HTML Report Downloaded:
• Issue #1: Hardcoded API key at ApiClient.java:23
  Fix: Move to BuildConfig or use secrets management
  
• Issue #2: Cleartext HTTP at network_security_config.xml:8
  Fix: Set cleartextTrafficPermitted="false"
  
• ... and 12 warnings
```

### Your Action
1. Fix the 2 critical issues
2. Re-run the scan
3. Get ✅ PASS result
4. Safe to release!

---

## Key Points

✅ **Non-Invasive**: Your Android app repo is never modified
✅ **Fast**: Results in 2-5 minutes
✅ **Reusable**: Scan any app, any branch, anytime
✅ **Secure**: Temporary clones deleted after scan
✅ **Actionable**: Clear instructions on what to fix

---

See **README.md** for full documentation.
