#!/bin/bash
# Quick API Test Script
# Tests if your Google Custom Search API is properly enabled

echo "=========================================="
echo "Testing Google Custom Search API"
echo "=========================================="
echo ""

# Load environment variables
export GOOGLE_API_KEY="AIzaSyBxcqXfSRavUnN7KKF-ywWb_sXbDGHb3AY"
export GOOGLE_CSE_ID="011079723395396642122:0xx-5mjdafi"

echo "API Key: ${GOOGLE_API_KEY:0:20}..."
echo "CSE ID: $GOOGLE_CSE_ID"
echo ""
echo "Sending test query..."
echo ""

# Test the API
RESPONSE=$(curl -s "https://www.googleapis.com/customsearch/v1?key=$GOOGLE_API_KEY&cx=$GOOGLE_CSE_ID&q=test&num=1")

# Check for errors
if echo "$RESPONSE" | grep -q "PERMISSION_DENIED"; then
    echo "❌ PERMISSION_DENIED Error"
    echo ""
    echo "The API key is valid, but Custom Search API is not enabled."
    echo ""
    echo "Fix this by:"
    echo "1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com"
    echo "2. Click the blue ENABLE button"
    echo "3. Wait 2 minutes, then run this test again"
    echo ""
    echo "See API-PERMISSION-FIX.md for detailed instructions"
    exit 1
elif echo "$RESPONSE" | grep -q "error"; then
    echo "❌ API Error"
    echo ""
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
elif echo "$RESPONSE" | grep -q "customsearch#search"; then
    echo "✅ SUCCESS! API is working correctly"
    echo ""
    echo "Response preview:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
    echo ""
    echo "=========================================="
    echo "✅ You're ready to run verification!"
    echo "=========================================="
    echo ""
    echo "Next step:"
    echo "cd /home/setup/infrafabric/marketing/page-zero"
    echo "python3 safe_verify_contacts.py --in outreach-targets-hyper-personalized.csv --out verified-test.csv --max 5"
    exit 0
else
    echo "⚠️  Unexpected response"
    echo ""
    echo "$RESPONSE"
    exit 1
fi
