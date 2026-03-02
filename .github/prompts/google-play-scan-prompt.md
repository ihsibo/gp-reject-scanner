# Google Play Pre-Release Audit — Claude Code Prompt

You are an expert Android engineer and Google Play policy specialist. Your job is to perform a thorough static analysis of this Android codebase and determine the likelihood that Google Play will **approve or reject** the next release.

Scan the entire repository and evaluate every item listed below. For each item, determine: ✅ PASS, ❌ FAIL, or ⚠️ WARN (cannot determine from static analysis alone — requires runtime/manual check). Every FAIL on a CRITICAL item meaningfully reduces the approval score.

---

## SCANNING INSTRUCTIONS

Work through each category methodically. Search the codebase using file reads, grep patterns, and directory inspection. Do not guess — only flag issues you can confirm or strongly infer from the code.

---

## CATEGORY 1 — Technical Requirements (CRITICAL WEIGHT: HIGH)

Search for and evaluate:

1. **Target SDK** — Check `build.gradle` / `build.gradle.kts` in all modules. `targetSdkVersion` must be ≥ 34 (as of August 2024 Google Play requirement). FAIL if below 34.
2. **Min SDK** — Note `minSdkVersion`. Flag if below 21 (warn only, not critical).
3. **64-bit support** — Check `abiFilters` in `build.gradle`. Must include `arm64-v8a`. FAIL if explicitly excluded or only 32-bit ABIs listed.
4. **App Bundle** — Check CI scripts, `Makefile`, `Fastfile`, GitHub Actions workflows, or README for whether the release build uses `bundleRelease` (`.aab`) vs `assembleRelease` (`.apk`). WARN if only APK release found.
5. **Debug keystore** — Check any signing configs in `build.gradle`. FAIL if `debug.keystore` or `android.keystore` path referenced for release builds.
6. **Version code increment** — Check `versionCode` in `build.gradle`. WARN if it appears hardcoded at 1 or a very low number with no CI-based increment logic.
7. **Deprecated APIs** — Grep for usage of: `AsyncTask`, `onBackPressed()` override without super, `getExternalStorageDirectory()`, `WifiInfo.getSSID()` without permission check.
8. **Play App Signing compatibility** — No issues to flag from code unless signing is misconfigured.
9. **Kotlin/Java compatibility** — Check `kotlinOptions.jvmTarget` and `compileOptions` source/target compatibility for consistency.

---

## CATEGORY 2 — Permissions (CRITICAL WEIGHT: VERY HIGH)

1. **AndroidManifest.xml** — Find and list ALL `<uses-permission>` declarations across all modules/manifests (including merged ones).
2. **Overly broad permissions** — Flag any of these as CRITICAL if present without obvious justification in code:
   - `READ_CALL_LOG`, `WRITE_CALL_LOG`
   - `PROCESS_OUTGOING_CALLS`
   - `SEND_SMS`, `RECEIVE_SMS`, `READ_SMS`
   - `READ_CONTACTS`, `WRITE_CONTACTS` (warn — check if used)
   - `RECORD_AUDIO` (warn — check if used)
   - `CAMERA` (warn — check if used)
   - `ACCESS_BACKGROUND_LOCATION` (CRITICAL — needs strong justification)
   - `MANAGE_EXTERNAL_STORAGE` (CRITICAL — needs declaration approval)
   - `REQUEST_INSTALL_PACKAGES` (CRITICAL)
   - `BIND_ACCESSIBILITY_SERVICE` (CRITICAL — non-accessibility use is banned)
   - `SYSTEM_ALERT_WINDOW` (warn)
3. **Permission usage vs declaration** — For each sensitive permission declared, grep the codebase to verify it's actually called (e.g., `ContextCompat.checkSelfPermission`, `requestPermissions`, relevant API calls). Flag declared-but-unused permissions as WARN.
4. **Runtime rationale** — Check for `shouldShowRequestPermissionRationale` usage or equivalent Jetpack Activity Result API usage for all sensitive permissions. WARN if absent.
5. **Background location** — If `ACCESS_BACKGROUND_LOCATION` is declared, verify there is a foreground location permission also declared. FAIL if not.

---

## CATEGORY 3 — Privacy & Data Safety (CRITICAL WEIGHT: HIGH)

1. **Privacy Policy URL** — Search for a privacy policy URL in: `strings.xml`, `AndroidManifest.xml` (`meta-data`), any settings/about screen layout XML or code. WARN if no URL found anywhere.
2. **Analytics/Tracking SDKs** — Grep `build.gradle` files for common analytics dependencies:
   - Firebase Analytics (`firebase-analytics`)
   - Facebook SDK (`facebook-android-sdk`)
   - AppsFlyer, Adjust, Branch, Mixpanel, Amplitude, Segment
   - Advertising ID usage (`AdvertisingIdClient`)
   Flag each found SDK — they require Data Safety form disclosure.
3. **Advertising ID** — Grep for `AdvertisingIdClient` or `AD_ID` permission. If found, verify `com.google.android.gms.permission.AD_ID` is declared in manifest. FAIL if used but not declared (required for target SDK 33+).
4. **Crash Reporting SDKs** — Grep for Crashlytics, Sentry, Bugsnag, Datadog. Note these collect device data — must be disclosed.
5. **Data transmission** — Grep for hardcoded endpoints, `OkHttpClient`, `Retrofit`, `Volley`, `HttpURLConnection`. Note any that appear to transmit user data.
6. **Local storage of sensitive data** — Grep for `SharedPreferences` storing anything that looks like tokens, passwords, PII. Check for use of `EncryptedSharedPreferences` — WARN if not using encrypted storage for sensitive keys.
7. **Keystore usage** — Check for Android Keystore (`KeyStore.getInstance("AndroidKeyStore")`) for sensitive key storage. WARN if absent but crypto operations are present.

---

## CATEGORY 4 — Security (CRITICAL WEIGHT: VERY HIGH)

1. **Hardcoded secrets** — Grep entire codebase for patterns:
   - API keys: `api_key`, `apiKey`, `API_KEY`, `secret`, `SECRET`, `token`, `TOKEN`
   - Strings matching common key formats: long alphanumeric strings (32+ chars) in source files
   - AWS: `AKIA`, `aws_access_key`
   - Google API keys: `AIza`
   - Private keys: `BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`
   CRITICAL FAIL for any found in non-test source files.
2. **HTTP (non-TLS) usage** — Grep for `http://` in network-related files (exclude localhost/test). Check `network_security_config.xml` for `cleartextTrafficPermitted="true"`. CRITICAL FAIL if cleartext allowed in production config.
3. **Network Security Config** — Find `res/xml/network_security_config.xml`. Check for:
   - `<debug-overrides>` (ok, but note it)
   - `<domain-config cleartextTrafficPermitted="true">` (FAIL if not debug-only)
   - Custom certificate trust anchors that include user certs in release builds (WARN)
4. **WebView security** — Grep for `WebView`. Check for:
   - `setJavaScriptEnabled(true)` (warn — note it)
   - `addJavascriptInterface` (warn — note the interface name and evaluate risk)
   - `setAllowFileAccessFromFileURLs(true)` or `setAllowUniversalAccessFromFileURLs(true)` (CRITICAL FAIL)
5. **Code execution** — Grep for dynamic DEX loading: `DexClassLoader`, `PathClassLoader` with dynamic paths, `Runtime.exec()`, `ProcessBuilder`. CRITICAL if found.
6. **Root detection bypass** — Grep for RootBeer or similar, note if the app explicitly disables security checks.
7. **SSL pinning** — Grep for `CertificatePinner`, `TrustManager` custom implementations, OkHttp `certificatePinner`. Note presence/absence (absence is WARN for financial/health apps).
8. **Exported components** — Parse `AndroidManifest.xml` for `<activity>`, `<service>`, `<receiver>`, `<provider>` with `android:exported="true"` and no `android:permission` set. WARN for each unprotected exported component.

---

## CATEGORY 5 — Google Play Billing (CRITICAL WEIGHT: HIGH — if applicable)

1. **Billing library presence** — Grep `build.gradle` for `billing` dependency (`com.android.billingclient:billing`). If found, this category is applicable.
2. **Billing library version** — Check version. Google requires minimum version 6.x as of certain dates. FAIL if below 5.
3. **Alternative payment methods** — Grep for payment SDK keywords: `stripe`, `braintree`, `paypal`, `square`, `paddle`, `lemonsqueezy`, `chargebee` in dependencies or imports. CRITICAL if found alongside in-app purchase flows (potential policy violation).
4. **Subscription acknowledgement** — Grep for `acknowledgePurchase` or `consumeAsync`. WARN if billing is used but neither found (unacknowledged purchases are refunded after 3 days).
5. **Purchase verification** — Check if purchases are verified server-side (look for backend calls after purchase) or only client-side. WARN if only client-side.

---

## CATEGORY 6 — Ads & Third-Party SDKs (CRITICAL WEIGHT: MEDIUM)

1. **Ad SDKs** — Grep `build.gradle` for:
   - AdMob (`play-services-ads`)
   - Facebook Audience Network
   - AppLovin, ironSource, MoPub, Unity Ads, Vungle
   Note each found — they require Data Safety disclosure.
2. **Ad ID permission** — If ad SDKs are present, verify `AD_ID` permission declared (required for API 33+).
3. **COPPA compliance** — If any ad SDK found, grep for child-directed treatment calls: `setTagForChildDirectedTreatment`, `setTagForUnderAgeOfConsent`. WARN if ad SDKs present but no child-directed handling found.
4. **SDK versions** — For major SDKs (Firebase, Google Play Services), note versions and flag if significantly outdated (>2 major versions behind).

---

## CATEGORY 7 — Manifest & Store Listing Signals (CRITICAL WEIGHT: MEDIUM)

1. **App label & icon** — Verify `android:label` and `android:icon` are set in manifest and not pointing to missing resources.
2. **Backup rules** — Check `android:allowBackup` and `android:fullBackupContent` / `android:dataExtractionRules` (API 31+). WARN if sensitive data could be backed up.
3. **Test/Debug artifacts** — Grep for: `TODO`, `FIXME`, `HACK`, `test123`, `localhost`, `192.168.`, `10.0.0.` in non-test source. WARN if found in production code.
4. **Logging** — Grep for `Log.d`, `Log.v`, `System.out.println` in non-test source files. WARN if PII-adjacent data might be logged.
5. **ProGuard/R8** — Check for `proguard-rules.pro` or R8 config. WARN if no obfuscation config found for a release build.
6. **Internet permission** — Verify `INTERNET` permission is declared if any network calls exist.
7. **Launcher activity** — Verify exactly one activity has `android.intent.action.MAIN` + `android.intent.category.LAUNCHER` intent filter.

---

## SCORING METHODOLOGY

After completing the scan, calculate the **Google Play Approval Score** as follows:

- Start at **100 points**
- Each **CRITICAL FAIL**: subtract **15 points**
- Each **non-critical FAIL**: subtract **5 points**
- Each **WARN**: subtract **2 points**
- Floor at **0 points**

Approval probability tiers:
- **85–100**: 🟢 High — likely to pass automated and manual review
- **65–84**: 🟡 Medium — may pass but has issues that could trigger manual review or future rejection
- **40–64**: 🟠 Risky — multiple policy concerns, likely to be flagged
- **0–39**: 🔴 High Risk — probable rejection, do not release without fixing critical issues

---

## OUTPUT

Generate a single self-contained HTML file at `google-play-audit-report.html` in the repository root.

The HTML file must:

- Be fully self-contained (no external dependencies, all CSS/JS inline)
- Have a clean, professional, dark-themed design
- **CRITICAL**: Include data attributes in the root `<html>` tag:
  ```html
  <html data-score="72" data-critical-fails="2" data-warns="5">
  ```
  These attributes are parsed by the CI workflow to determine pass/fail status.
  
- Show at the top:
  - App name (from `build.gradle` or `strings.xml`)
  - Package ID
  - Version name + version code
  - Scan date
  - **Large approval score percentage with color coding**
  - Count of: Critical FAILs | Non-critical FAILs | WARNs | PASSes
- Have a section per category with:
  - Category name and overall category status
  - Each finding listed with: status badge (✅ PASS / ❌ FAIL / ⚠️ WARN), description of what was found, file path + line number where relevant, and a brief recommended fix for each FAIL/WARN
- End with a **"What to fix before releasing"** prioritized action list (critical items first)
- Include a **"Items requiring manual verification"** section for things static analysis cannot confirm (runtime behavior, actual store listing content, etc.)

### Color Coding for Score:
- **85-100**: Green background (#22c55e)
- **65-84**: Yellow background (#eab308)
- **40-64**: Orange background (#f97316)
- **0-39**: Red background (#ef4444)

Write the file and confirm it has been created successfully. The HTML report IS the primary output.

Do not output the findings as conversation text — the HTML report IS the output. Keep your working notes minimal.
