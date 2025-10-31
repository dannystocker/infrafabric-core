# Test With 1 Contact - Debug Process

Perfect approach! Testing with 1 contact lets you verify the entire process works before scheduling your full 10-day verification plan.

---

## Quick Test (3 Steps)

### Step 1: Enable Custom Search API (if not done yet)

Go to: **https://console.cloud.google.com/apis/library/customsearch.googleapis.com**

Click: **ENABLE**

Wait 2 minutes.

### Step 2: Test API

```bash
cd /home/setup/infrafabric
bash test-api.sh
```

Look for: `✅ SUCCESS! API is working correctly`

### Step 3: Verify 1 Contact

```bash
cd /home/setup/infrafabric/marketing/page-zero

# Set credentials
export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"

# Run single contact test
python3 test_single_contact.py
```

---

## What Will Happen

### Expected Output:
```
================================================================================
SINGLE CONTACT VERIFICATION TEST
================================================================================

This will verify exactly 1 contact to test the process.
Expected API usage: ~11 queries

✅ API Key: AIzaSyBxcqXfSRavUnN7...
✅ CSE ID: 011079723395396642122:0xx-5mjdafi

Input: outreach-targets-hyper-personalized.csv
Output: verified-single-test.csv

Ready to verify 1 contact? (y/N): y

================================================================================
Starting verification...
================================================================================

Processing: Emil Michael (Pentagon CTO)
  - Searching Google for: "Emil Michael" "Pentagon CTO"
  - Searching LinkedIn: "Emil Michael" site:linkedin.com
  - Searching company site: "Emil Michael" site:defense.gov
  - Found 7 signals across 4 sources
  - Confidence score: 92/100
  - Status: auto-verified ✅

================================================================================
✅ VERIFICATION COMPLETE
================================================================================

Results saved to: verified-single-test.csv

Next steps:
1. Check the output CSV for verification results
2. Review the audit log in: verification-audit-logs/
3. If everything looks good, run with --max 9 for full daily batch
```

### API Usage:
- **~11 queries** for 1 contact
- **89 queries remaining** today (out of 100 free)
- **Cost: $0.00**

---

## What to Check After Test

### 1. Output CSV (`verified-single-test.csv`)

Should contain new columns:
- `verification_status`: auto-verified / needs-review / low-confidence
- `confidence_score`: 0-100
- `verified_title`: Current title from most reliable sources
- `verified_org`: Current organization
- `data_freshness`: How recent (2024-2025 preferred)
- `sources_found`: Number of corroborating sources
- `review_notes`: Human-readable summary

### 2. Audit Logs (`verification-audit-logs/`)

Check the timestamp folder for:
- **raw-signals.json**: All signals found for the contact
- **verification-log.txt**: Detailed process log
- **api-usage.json**: Query count and timestamps

### 3. Console Output

Look for:
- ✅ API calls successful (no errors)
- ✅ Multiple sources found (LinkedIn, news, company site)
- ✅ Confidence score calculated
- ✅ Verification status assigned

---

## Possible Outcomes

### ✅ Success (Most Likely)
```
Confidence score: 85/100
Status: auto-verified ✅
Sources found: 5
```

**Next step**: Run with `--max 9` for your daily batch

### ⚠️ Needs Review
```
Confidence score: 65/100
Status: needs-review
Sources found: 3
```

**Next step**: Check the review notes, verify manually if needed, then proceed with batch

### ❌ Low Confidence
```
Confidence score: 35/100
Status: low-confidence
Sources found: 1
```

**Next step**: This contact may have outdated info in the original CSV. Manual research needed.

---

## Troubleshooting

### Issue: "PERMISSION_DENIED"

**Cause**: Custom Search API not enabled yet

**Fix**:
1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. Click ENABLE
3. Wait 2 minutes
4. Try again

**See**: API-PERMISSION-FIX.md

### Issue: "API key not valid"

**Cause**: Environment variable not set correctly

**Fix**:
```bash
export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"
```

### Issue: "No results found"

**Cause**: Contact name or title may have changed

**Expected**: The system will flag this for manual review

**Action**: Check the review notes and update the CSV manually if needed

### Issue: "Rate limit exceeded"

**Cause**: Hit the 100 queries/day limit

**Fix**: Wait until tomorrow (midnight PST) for quota reset

**Note**: With 1 contact test using ~11 queries, this is unlikely

---

## After Successful Test

### If Confidence Score ≥ 80:
```bash
# Proceed with daily batch verification
python3 safe_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-day1.csv \
  --max 9
```

### If You Want to Review the Dashboard:
```bash
# Generate HTML dashboard
python3 generate_review_dashboard.py verified-single-test.csv

# Open in browser (location printed in output)
```

### Schedule Daily Verification (10-Day Plan):
```bash
# Day 1
python3 safe_verify_contacts.py --in outreach-targets-hyper-personalized.csv --out verified-day1.csv --max 9

# Day 2 (tomorrow)
python3 safe_verify_contacts.py --in outreach-targets-hyper-personalized.csv --out verified-day2.csv --max 9

# ... etc for 10 days
```

---

## Alternative: Test With Top 5 Contacts

If you want a slightly larger test sample:

```bash
python3 safe_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-5contacts-test.csv \
  --max 5
```

- Uses ~55 queries (safe, 45 remaining today)
- Tests more variety of contacts
- Still $0.00 cost

---

## Cost Summary

### 1 Contact Test:
- **Queries**: ~11
- **Cost**: $0.00
- **Remaining today**: 89

### 5 Contact Test:
- **Queries**: ~55
- **Cost**: $0.00
- **Remaining today**: 45

### 9 Contact Daily Batch:
- **Queries**: ~99
- **Cost**: $0.00
- **Remaining today**: 1

**All options are free!**

---

## Quick Reference Commands

```bash
# Test API
bash /home/setup/infrafabric/test-api.sh

# Set credentials
export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"

# Verify 1 contact (debug)
cd /home/setup/infrafabric/marketing/page-zero
python3 test_single_contact.py

# View results
cat verified-single-test.csv | column -t -s,

# Generate dashboard
python3 generate_review_dashboard.py verified-single-test.csv
```

---

## What's Next

After your 1-contact test succeeds:

1. ✅ **Verify API works**: No PERMISSION_DENIED errors
2. ✅ **Verify results quality**: Confidence score makes sense
3. ✅ **Verify audit logs**: Process is transparent and traceable
4. ✅ **Verify output format**: CSV has all expected columns

Then proceed to:
- **Option A**: Full daily batch (9 contacts/day for 10 days)
- **Option B**: Enable billing and verify all 84 at once ($4.12)

**Recommended**: Option A (free, 10-day plan)

---

**Ready to test? Run the commands above!** 🚀
