# API Permission Error - Quick Fix Guide

## The Problem

You provided your API key: `AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY`

When we tested it, we got:
```json
{
    "error": {
        "code": 403,
        "message": "Method doesn't allow unregistered callers...",
        "status": "PERMISSION_DENIED"
    }
}
```

**This means**: Your API key is valid, but the **Custom Search API is not enabled** on your Google Cloud project.

---

## The Solution (2 minutes)

### Step 1: Enable Custom Search API

**Option A: Via Console (Easiest)**
1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. Make sure you're in the correct project (the one where you created the API key)
3. Click the blue **"ENABLE"** button
4. Wait 1-2 minutes for the API to activate

**Option B: Via gcloud CLI**
```bash
gcloud services enable customsearch.googleapis.com
```

### Step 2: Test the API

After enabling, wait 2 minutes, then test:

```bash
# Set your credentials
export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"

# Test query
curl -s "https://www.googleapis.com/customsearch/v1?key=$GOOGLE_API_KEY&cx=$GOOGLE_CSE_ID&q=test&num=1"
```

**Success looks like**:
```json
{
  "kind": "customsearch#search",
  "queries": {...},
  "items": [...]
}
```

**Still getting PERMISSION_DENIED?**
- Wait another 2 minutes (API activation can take up to 5 minutes)
- Verify you're enabling the API on the same project where the API key was created
- Check that the API key hasn't been restricted to other APIs only

---

## Step 3: Run Your First Verification

Once the API test succeeds:

```bash
cd /home/setup/infrafabric/marketing/page-zero

# Load environment variables
export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"

# Verify 5 test contacts (safe, uses ~55 queries)
python3 safe_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-test.csv \
  --max 5
```

Expected output:
```
================================================================================
SAFE VERIFICATION MODE - FREE TIER PROTECTION
================================================================================
Maximum contacts per run: 9
Estimated API queries: ~99
Free tier daily limit: 100 queries
Safety margin: 1 queries
================================================================================

No --max specified. Using safe default: 5 contacts

✅ Proceeding with 5 contacts
Estimated API usage: ~55 queries

[Processing contacts...]

================================================================================
✅ SAFE VERIFICATION COMPLETE
================================================================================
No billing risk - stayed within free tier limits!
================================================================================
```

---

## What This Test Will Do

For each of your top 5 contacts, the system will:

1. **Search Google** for their name + current role (5 queries)
2. **Search LinkedIn** profiles (3 queries)
3. **Search company sites** for verification (3 queries)
4. **Aggregate signals** from all sources
5. **Compute confidence score** (0-100)
6. **Flag for review** if score < 80

**Output**: `verified-test.csv` with these new columns:
- `verification_status`: auto-verified / needs-review / low-confidence
- `confidence_score`: 0-100
- `verified_title`: Current title from most reliable source
- `verified_org`: Current organization
- `data_freshness`: How recent the verification data is
- `sources_found`: Number of corroborating sources
- `review_notes`: Human-readable verification summary

---

## After Test Succeeds

Once your test verification completes successfully:

### View the Results
```bash
# Generate review dashboard
python3 generate_review_dashboard.py verified-test.csv

# Open the dashboard
# Located at: verification-audit-logs/[timestamp]/dashboard.html
```

### Verify More Contacts

With your **10,000 queries/day** limit, you can verify:

```bash
# Verify all 84 contacts at once (uses ~924 queries)
python3 safe_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-all.csv \
  --max 84
```

Or stay ultra-safe with the 9/day plan:
```bash
# Day 1: Top 9 contacts
python3 safe_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-day1.csv \
  --max 9
```

---

## Troubleshooting

### Issue: Still getting PERMISSION_DENIED after 5 minutes

**Check which project your API key belongs to:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your API key in the list
3. Note the project name at the top of the page

**Then enable Custom Search API on that specific project:**
1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. Use the project selector dropdown to switch to the correct project
3. Click ENABLE

### Issue: "API key not found"

The API key might have been deleted or regenerated. Create a new one:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **+ CREATE CREDENTIALS** → **API key**
3. Copy the new key
4. Update the `GOOGLE_API_KEY` in your commands

### Issue: "Quota exceeded"

If you've already used your queries today:
- Check usage: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/metrics
- Wait until tomorrow (quota resets at midnight PST)
- With your 10,000/day limit, this is unlikely!

---

## Summary

**Current status**: API key is valid, Custom Search API just needs to be enabled

**Fix**: Enable Custom Search API at https://console.cloud.google.com/apis/library/customsearch.googleapis.com

**Then**: Run the test verification command above

**Result**: Verified contact data ready for your InfraFabric outreach campaign!

---

You're one click away from launching! 🚀
