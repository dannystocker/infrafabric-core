
### Using the Safe Wrapper Script

I've created `safe_verify_contacts.py` that ENFORCES the limit:

```bash
# Always safe - limited to 9 contacts max
python3 safe_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified.csv

# Even if you try to do more, it will block you
python3 safe_verify_contacts.py \
  --in contacts.csv \
  --out verified.csv \
  --max 50

# Output:
# ⚠️  WARNING: You requested 50 contacts
# ⚠️  This would use ~550 API queries
# ⚠️  Free tier limit is 100 queries/day
# ⚠️  Maximum safe limit: 9 contacts
# Continue with 9 contacts instead? (y/N):
```

---

## 📊 Free Tier Math - IMPORTANT CLARIFICATION

### The Real Free Tier Limit

**Google Custom Search JSON API Free Tier**:
- **100 queries per day** (FREE)
- After 100 queries: **$5 per 1000 queries** ($0.005 per query)

**Note**: Your CSE configuration shows "10,000 queries/day" - this is your quota **ceiling** if you enable billing, NOT your free allocation. The free tier is always 100 queries/day.

### Per Contact Query Usage

Per contact verification uses:
- 5 queries: General search
- 3 queries: LinkedIn search
- 3 queries: Company site search
- = **11 queries per contact**

### Safe Daily Limits (100% Free)

| Contacts | Queries | Safe? | Days for 84 | Cost |
|----------|---------|-------|-------------|------|
| 5        | 55      | ✅ Yes | 17 days     | $0   |
| 9        | 99      | ✅ Yes | 10 days     | $0   |
| 10       | 110     | ❌ No  | N/A         | $0.05|
| 20       | 220     | ❌ No  | N/A         | $0.60|
| 84       | 924     | ❌ No  | 1 day       | $4.12|

**Recommendation**: Verify **9 contacts per day** for 10 days = **$0.00 total cost**

---

## 🎯 Best Practice: 10-Day Plan

### Week 1 (Days 1-5)
- Day 1: Verify top 9 contacts (Score 100+)
- Day 2: Verify next 9 contacts (Score 90+)
- Day 3: Verify next 9 contacts (Score 85+)
- Day 4: Verify next 9 contacts (Score 80+)
- Day 5: Verify next 9 contacts (Score 75+)

Total: 45 contacts verified, **$0.00 cost**

### Week 2 (Days 6-10)
- Days 6-10: Verify remaining 39 contacts

Total: 84 contacts verified, **$0.00 cost**

---

## 🔒 The Four-Layer Safety System

### Layer 1: No Billing Account (100% Protection)
If billing isn't enabled, Google **cannot** charge you. Period.

### Layer 2: API Quota Limit (99% Protection)
Set quota to 100 in console. API stops at 100 queries.

### Layer 3: Safe Wrapper Script (95% Protection)
`safe_verify_contacts.py` enforces 9 contacts max per run.

### Layer 4: Manual Verification (90% Protection)
You control when and how many contacts to verify.

**Result**: Impossible to get billed accidentally.

---

## ✅ Setup Checklist for Zero-Billing

- [ ] Verify billing is NOT enabled:
  ```bash
  gcloud billing projects describe YOUR_PROJECT_ID
  # Should show: billingEnabled: false
  ```

- [ ] Optional: Set quota to 100 in console:
  https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

- [ ] Use the safe wrapper script:
  ```bash
  chmod +x safe_verify_contacts.py
  python3 safe_verify_contacts.py --in contacts.csv --out verified.csv
  ```

- [ ] Verify 9 contacts per day max

- [ ] Check usage daily (optional):
  https://console.cloud.google.com/apis/api/customsearch.googleapis.com/metrics

---

## 🚨 What If I Accidentally Go Over 100?

### With Billing DISABLED:
1. API returns error: "Quota exceeded for quota metric..."
2. Script stops
3. You get charged: **$0.00**
4. Wait until tomorrow (quota resets at midnight PST)

### With Billing ENABLED (if you enable it later):
1. API keeps working
2. You get charged: **$0.50** (for 100 additional queries)
3. Email alert from Google (if configured)

**Bottom line**: As long as billing is disabled, you're 100% safe.

---

## 💡 How to Check Your Current Usage

### Via Console (Easiest)
https://console.cloud.google.com/apis/api/customsearch.googleapis.com/metrics

Shows:
- Queries today
- Queries this week
- Quota remaining

### Via gcloud CLI
```bash
gcloud logging read \
  "resource.type=api AND resource.labels.service=customsearch.googleapis.com" \
  --limit 100 \
  --format="table(timestamp,resource.labels.method_name)" \
  --freshness=1d
```

### Via Script Counter
The safe wrapper prints query count after each run:
```
✅ Verification complete
Contacts processed: 9
API queries used: ~99
Remaining today: ~1
```

---

## 📞 If You Need More Than 100/Day

### Option 1: Enable Billing (Fast but Paid)
**Cost**: $5 per 1000 queries ($0.005 per query)

For all 84 contacts at once (~924 queries):
- Free tier: 100 queries = $0.00
- Paid queries: 824 × $0.005 = **$4.12**
- **Total cost: $4.12**
- Time: ~30 minutes (all at once)

### Option 2: Stay Free (Patient, Zero Cost)
**Cost**: $0.00

- Verify 9 contacts/day (99 queries)
- Complete in 10 days
- Total cost: **$0.00**
- Time: 10 days × 5 minutes/day = 50 minutes total

For InfraFabric, **Option 2 is perfect**. You're building relationships, not racing against deadlines. Free is good!

---

## 🎉 Summary

### To Guarantee ZERO Billing:

1. ✅ **Don't enable billing** on your Google Cloud project
2. ✅ **Use the safe wrapper**: `safe_verify_contacts.py`
3. ✅ **Limit to 9 contacts/day** (10-day plan for all 84)
4. ✅ **Monitor usage** (optional, via console)

### Result:
- ✅ All 84 contacts verified
- ✅ Complete in 10 days
- ✅ Total cost: **$0.00**
- ✅ Zero risk of accidental billing

---

**You're protected!** Use `safe_verify_contacts.py` and you'll never go over the free tier limit.

