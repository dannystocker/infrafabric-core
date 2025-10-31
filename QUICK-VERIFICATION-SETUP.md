# Quick Verification Setup - You're Almost Ready!

## ✅ What You Have

Based on your `cloud-cse-config.pdf`:

- **Custom Search Engine ID**: `011079723395396642122:0xx-5mjdafi`
- **Search Engine Name**: LGBTQ~
- **Daily Quota Ceiling**: 10,000 queries/day (if billing enabled)
- **Free Tier Limit**: **100 queries/day** (without billing)
- **Search entire web**: ✅ Enabled
- **Region**: Canada

**Important**: The 10,000/day shown in your CSE config is your quota **ceiling** if you enable billing. The actual free tier for the JSON API is **100 queries/day**.

---

## 🔑 What You Still Need

Just **ONE thing**: Your Google API Key

### Get Your API Key (2 minutes)

1. Go to: https://console.cloud.google.com/apis/credentials
2. Make sure you're in the right project
3. Click **+ CREATE CREDENTIALS** → **API key**
4. Copy the key (starts with `AIza...`)
5. (Optional but recommended) Click on the key name to restrict it:
   - **API restrictions**: Select "Restrict key"
   - Check **only** "Custom Search API"
   - Save

---

## 🚀 Quick Start (3 Commands)

Once you have your API key:

```bash
cd /home/setup/infrafabric

# Set your API key (replace with your actual key)
export GOOGLE_API_KEY="AIzaSy..."

# CSE ID is already configured
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"

# Test verification on 5 contacts
cd marketing/page-zero
python3 auto_verify_contacts.py \
  --in outreach-targets-hyper-personalized.csv \
  --out verified-test.csv \
  --max 5
```

---

## 📊 Your Daily Capacity (Free Tier)

With **100 queries/day** (free tier):

- **~9 contacts per day** (11 queries each)
- **All 84 contacts in 10 days**
- **Total cost: $0.00**

**With billing enabled** (10,000 queries/day ceiling):
- ~900 contacts per day
- All 84 contacts in < 1 hour
- Cost: ~$4.12 for all 84 contacts

**Recommendation**: Use the free tier (9 contacts/day) for zero cost!

---

## 🔧 Permanent Configuration

To avoid setting environment variables each time:

```bash
# Edit the .env file
nano /home/setup/infrafabric/.env

# Add your API key to the line:
GOOGLE_API_KEY=AIzaSy...  # Replace with your actual key

# Then load it automatically:
cd /home/setup/infrafabric
export $(grep -v '^#' .env | xargs)

# Or add to ~/.bashrc for persistence:
echo 'export GOOGLE_API_KEY="AIzaSy..."' >> ~/.bashrc
echo 'export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🎯 CSE Configuration Review

Your current CSE settings are good for InfraFabric:

### ✅ Optimal Settings
- **Search entire web**: Enabled (perfect!)
- **Image search**: Enabled (helps find recent photos/headshots)
- **SafeSearch**: Enabled (professional results)
- **Region**: Canada (fine, results are still global)

### 💡 Optional Improvements

If you want to optimize for InfraFabric specifically, you could:

1. **Add relevant sites to prioritize** (optional):
   - linkedin.com
   - crunchbase.com
   - techcrunch.com
   - bloomberg.com
   - reuters.com

   This would give these sites higher ranking in results.

2. **Disable ads** (already done in your config ✅)

3. **Add excluded sites** (optional):
   - Spam/scraper sites
   - Job boards (if not relevant)

But honestly, **your current setup is perfect as-is** for verification!

---

## 🧪 Test Your Setup

```bash
# Set your API key
export GOOGLE_API_KEY="AIzaSy..."

# Test with curl
curl "https://www.googleapis.com/customsearch/v1?key=$GOOGLE_API_KEY&cx=011079723395396642122:0xx-5mjdafi&q=Emil+Michael+Pentagon+CTO"

# Should return JSON with search results
```

If you get results, you're ready to go!

---

## 📝 Next Steps

### Today (5 minutes)
1. ✅ CSE ID configured (already done!)
2. Get API key from console
3. Test with curl command above
4. Run verification on 5 contacts

### This Week
1. Verify all 84 contacts (< 1 hour with your quota)
2. Review verification dashboard
3. Process quick-review queue
4. Launch email campaign

---

## 🆘 Troubleshooting

### Issue: "API key not valid"

**Check:**
- API key is correct (starts with `AIza`)
- Custom Search API is enabled in your project
- API key restrictions allow Custom Search API

**Fix:**
```bash
# Enable the API
gcloud services enable customsearch.googleapis.com

# Or via console:
# https://console.cloud.google.com/apis/library/customsearch.googleapis.com
```

### Issue: "Daily limit exceeded"

**This happens after 100 queries on the free tier.**

**Check usage:**
```bash
# View usage in console:
# https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
```

**Solution**: Wait until tomorrow (quota resets at midnight PST), or enable billing if you need more than 100/day.

---

## 🎁 Bonus: Your CSE Code

You provided this code snippet:
```html
<script async src="https://cse.google.com/cse.js?cx=011079723395396642122:0xx-5mjdafi"></script>
<div class="gcse-search"></div>
```

This is for **embedding search on a webpage**. For the Python verification script, we use the **JSON API** instead (which is what `auto_verify_contacts.py` uses).

Both use the same CSE ID, so you're all set!

---

## 📊 Expected Results

With your setup, you should see:

### Verification Performance
- **Auto-verified (≥80)**: 60-70% of contacts
- **Quick review (50-79)**: 20-30% of contacts
- **Manual review (<50)**: 5-10% of contacts

### Time to Complete (Free Tier)
- **5 contacts**: ~2 minutes
- **9 contacts**: ~4 minutes (daily free limit)
- **84 contacts**: 10 days × 4 minutes = 40 minutes total

### Time to Complete (With Billing)
- **84 contacts**: ~30 minutes (all at once, costs $4.12)

---

## ✨ Summary

**You have:**
✅ Custom Search Engine configured
✅ CSE ID: `011079723395396642122:0xx-5mjdafi`
✅ Free tier: 100 queries/day (9 contacts/day)
✅ Quota ceiling: 10,000/day (if billing enabled)
✅ Verification script ready
✅ .env file with CSE ID pre-configured

**You need:**
❓ Google API Key (2 minutes to get)

**Then you can:**
🚀 Verify 9 contacts/day for free (10-day plan)
💰 Or verify all 84 at once for $4.12 (with billing enabled)
🎯 Launch InfraFabric outreach campaign

---

**Get your API key now**: https://console.cloud.google.com/apis/credentials

Then run:
```bash
export GOOGLE_API_KEY="your-key-here"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"
cd /home/setup/infrafabric/marketing/page-zero
python3 auto_verify_contacts.py --in outreach-targets-hyper-personalized.csv --out verified-test.csv --max 5
```

You're minutes away from launching! 🎉
