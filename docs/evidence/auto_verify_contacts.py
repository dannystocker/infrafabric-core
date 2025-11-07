#!/usr/bin/env python3
"""
InfraFabric Contact Verification System
Uses only FREE APIs: Google Custom Search, Google News RSS, GitHub, public HTML parsing
Requires: Google Cloud Education free tier (100 searches/day free)
"""

import csv
import time
import requests
import json
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import re
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION - Set your Google Cloud API credentials
# ============================================================================

# Get from: https://console.cloud.google.com/apis/credentials
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'YOUR_GOOGLE_API_KEY_HERE')

# Get from: https://programmablesearchengine.google.com/
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', 'YOUR_GOOGLE_CSE_ID_HERE')

USER_AGENT = 'Mozilla/5.0 (compatible; InfraFabricVerifier/1.0; +research@infrafabric.ai)'
RATE_LIMIT_SECONDS = 1.2  # Respect API rate limits
MAX_RETRIES = 3
TIMEOUT = 15

# ============================================================================
# SOURCE WEIGHTS (reliability scoring)
# ============================================================================

SOURCE_WEIGHTS = {
    'company_site_official': 1.0,      # company.com/team, /about, /leadership
    'gov_site': 1.0,                   # .gov, .mil domains
    'crunchbase_free': 0.9,            # Crunchbase public pages
    'conference_speaker': 0.9,          # Conference speaker listings
    'news_reputable': 0.8,             # Financial Times, Bloomberg, TechCrunch, etc.
    'linkedin_public': 0.7,            # LinkedIn public profiles (via search)
    'company_press': 0.7,              # Press releases
    'github_profile': 0.6,             # GitHub profile pages
    'university_page': 0.6,            # .edu domains
    'social_verified': 0.5,            # Twitter/X verified accounts
    'aggregator': 0.5,                 # ZoomInfo, etc. (free tiers)
    'social_unverified': 0.3,          # Regular social media posts
}

REPUTABLE_NEWS_DOMAINS = [
    'nytimes.com', 'wsj.com', 'ft.com', 'bloomberg.com', 'reuters.com',
    'techcrunch.com', 'wired.com', 'theverge.com', 'arstechnica.com',
    'forbes.com', 'fortune.com', 'economist.com', 'cnbc.com'
]

CONFERENCE_DOMAINS = [
    'supercomputing.org', 'isc-hpc.com', 'nvidia.com/gtc',
    'aws.amazon.com/events', 'cloud.google.com/events',
    'microsoft.com/events', 'qce.quantum.ieee.org',
    'aps.org', 'acm.org', 'ieee.org'
]

# ============================================================================
# TITLE NORMALIZATION & MATCHING
# ============================================================================

TITLE_SYNONYMS = {
    'cto': ['chief technology officer', 'chief technical officer', 'vp technology', 'vp engineering'],
    'ceo': ['chief executive officer', 'president & ceo', 'founder & ceo'],
    'cfo': ['chief financial officer', 'vp finance'],
    'ciso': ['chief information security officer', 'vp security'],
    'cdo': ['chief data officer', 'chief digital officer'],
    'vp': ['vice president', 'senior vice president', 'svp', 'evp', 'executive vice president'],
    'director': ['dir', 'head of', 'lead'],
    'manager': ['mgr', 'program manager', 'product manager'],
}

def normalize_title(title):
    """Normalize job titles for better matching"""
    if not title:
        return ""

    title_lower = title.lower().strip()

    # Remove common punctuation
    title_lower = re.sub(r'[,\.\(\)]', ' ', title_lower)

    # Remove extra whitespace
    title_lower = re.sub(r'\s+', ' ', title_lower).strip()

    return title_lower

def expand_title_variants(title):
    """Generate title variants for better matching"""
    variants = [title]
    title_norm = normalize_title(title)
    variants.append(title_norm)

    # Add synonym expansions
    for abbrev, expansions in TITLE_SYNONYMS.items():
        if abbrev in title_norm:
            for expansion in expansions:
                variants.append(title_norm.replace(abbrev, expansion))
        for expansion in expansions:
            if expansion in title_norm:
                variants.append(title_norm.replace(expansion, abbrev))

    return list(set(variants))

def title_similarity(title_a, title_b):
    """Calculate similarity between two titles (0-1 score)"""
    if not title_a or not title_b:
        return 0.0

    # Normalize both
    norm_a = normalize_title(title_a)
    norm_b = normalize_title(title_b)

    # Exact match
    if norm_a == norm_b:
        return 1.0

    # Token overlap (Jaccard)
    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())

    if not tokens_a or not tokens_b:
        return 0.0

    jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

    # Sequence similarity
    seq_sim = SequenceMatcher(None, norm_a, norm_b).ratio()

    # Weighted combination
    return 0.6 * jaccard + 0.4 * seq_sim

# ============================================================================
# ORGANIZATION NORMALIZATION
# ============================================================================

def normalize_org_name(org):
    """Normalize organization names for matching"""
    if not org:
        return ""

    org_lower = org.lower().strip()

    # Remove common suffixes
    suffixes = [' inc', ' inc.', ' corp', ' corp.', ' corporation',
                ' ltd', ' ltd.', ' llc', ' llc.', ' gmbh', ' ag',
                ' technologies', ' systems', ' solutions']

    for suffix in suffixes:
        if org_lower.endswith(suffix):
            org_lower = org_lower[:-len(suffix)].strip()

    # Remove punctuation
    org_lower = re.sub(r'[,\.\(\)]', ' ', org_lower)
    org_lower = re.sub(r'\s+', ' ', org_lower).strip()

    return org_lower

def org_similarity(org_a, org_b):
    """Calculate similarity between organization names"""
    if not org_a or not org_b:
        return 0.0

    norm_a = normalize_org_name(org_a)
    norm_b = normalize_org_name(org_b)

    if norm_a == norm_b:
        return 1.0

    # Check if one is substring of other
    if norm_a in norm_b or norm_b in norm_a:
        return 0.9

    # Token overlap
    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())

    if not tokens_a or not tokens_b:
        return 0.0

    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

# ============================================================================
# SOURCE CLASSIFICATION
# ============================================================================

def classify_source(url, snippet="", title=""):
    """Classify URL source type and assign weight"""
    domain = urlparse(url).netloc.lower()

    # Government sites
    if domain.endswith('.gov') or domain.endswith('.mil'):
        return 'gov_site', SOURCE_WEIGHTS['gov_site']

    # University sites
    if domain.endswith('.edu'):
        return 'university_page', SOURCE_WEIGHTS['university_page']

    # LinkedIn
    if 'linkedin.com' in domain:
        return 'linkedin_public', SOURCE_WEIGHTS['linkedin_public']

    # Crunchbase
    if 'crunchbase.com' in domain:
        return 'crunchbase_free', SOURCE_WEIGHTS['crunchbase_free']

    # GitHub
    if 'github.com' in domain:
        return 'github_profile', SOURCE_WEIGHTS['github_profile']

    # Reputable news
    for news_domain in REPUTABLE_NEWS_DOMAINS:
        if news_domain in domain:
            return 'news_reputable', SOURCE_WEIGHTS['news_reputable']

    # Conference sites
    for conf_domain in CONFERENCE_DOMAINS:
        if conf_domain in domain:
            return 'conference_speaker', SOURCE_WEIGHTS['conference_speaker']

    # Company press releases
    if any(kw in url.lower() for kw in ['press', 'news', 'media', 'blog']):
        return 'company_press', SOURCE_WEIGHTS['company_press']

    # Company official pages
    if any(kw in url.lower() for kw in ['team', 'about', 'leadership', 'management', 'executive']):
        return 'company_site_official', SOURCE_WEIGHTS['company_site_official']

    # Default: treat as aggregator
    return 'aggregator', SOURCE_WEIGHTS['aggregator']

# ============================================================================
# FRESHNESS SCORING
# ============================================================================

def extract_date_from_snippet(snippet):
    """Try to extract publication date from snippet text"""
    if not snippet:
        return None

    # Common date patterns
    date_patterns = [
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{2}-\d{2}',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, snippet)
        if match:
            date_str = match.group()
            # Try to parse (simplified - would need proper parsing)
            return date_str

    return None

def freshness_multiplier(date_str=None):
    """Calculate freshness multiplier based on date"""
    if not date_str:
        return 0.7  # Default for unknown dates

    try:
        # Try to parse date (simplified)
        # In production, use dateutil.parser
        now = datetime.now()

        # Assume format approximations
        if '2025' in str(date_str) or '2024' in str(date_str):
            return 1.0  # Very fresh
        elif '2023' in str(date_str):
            return 0.8
        elif '2022' in str(date_str):
            return 0.6
        else:
            return 0.4
    except:
        return 0.7

# ============================================================================
# FREE API INTEGRATIONS
# ============================================================================

def google_custom_search(query, num=5):
    """
    Google Custom Search API (FREE tier: 100 queries/day)
    Setup: https://developers.google.com/custom-search/v1/overview
    """
    if GOOGLE_API_KEY == 'YOUR_GOOGLE_API_KEY_HERE':
        print("⚠️  WARNING: Google API key not configured. Returning empty results.")
        return []

    url = (
        "https://www.googleapis.com/customsearch/v1?"
        f"key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={quote_plus(query)}&num={num}"
    )

    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        items = data.get('items', [])
        results = []

        for item in items:
            results.append({
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'link': item.get('link', ''),
                'displayLink': item.get('displayLink', ''),
            })

        time.sleep(RATE_LIMIT_SECONDS)
        return results

    except requests.exceptions.RequestException as e:
        print(f"❌ Google search error: {e}")
        return []

def google_news_search(query):
    """
    Google News RSS (FREE, no API key needed)
    """
    rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"

    try:
        resp = requests.get(rss_url, headers={'User-Agent': USER_AGENT}, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, 'xml')
        items = soup.find_all('item')

        results = []
        for item in items[:5]:  # Top 5 news items
            title = item.find('title').text if item.find('title') else ''
            link = item.find('link').text if item.find('link') else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') else ''

            results.append({
                'title': title,
                'link': link,
                'date': pub_date,
                'source': 'google_news'
            })

        time.sleep(RATE_LIMIT_SECONDS)
        return results

    except Exception as e:
        print(f"⚠️  Google News search error: {e}")
        return []

def fetch_page_content(url):
    """Fetch and parse HTML page content"""
    try:
        headers = {'User-Agent': USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, 'html.parser')

        # Extract text content
        text = soup.get_text(separator=' ', strip=True)

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else ''

        return {
            'text': text[:2000],  # First 2000 chars
            'description': description,
            'title': soup.title.string if soup.title else ''
        }

    except Exception as e:
        print(f"⚠️  Page fetch error for {url}: {e}")
        return None

def github_user_check(first_name, last_name):
    """
    Check GitHub for user profile (FREE, no auth needed for public data)
    """
    # Common username patterns
    username_patterns = [
        f"{first_name}{last_name}".lower(),
        f"{first_name}.{last_name}".lower(),
        f"{first_name}-{last_name}".lower(),
        f"{first_name[0]}{last_name}".lower(),
    ]

    for username in username_patterns:
        try:
            url = f"https://api.github.com/users/{username}"
            headers = {'User-Agent': USER_AGENT}
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                return {
                    'username': data.get('login'),
                    'name': data.get('name'),
                    'bio': data.get('bio'),
                    'company': data.get('company'),
                    'url': data.get('html_url'),
                    'public_repos': data.get('public_repos', 0)
                }

            time.sleep(0.5)  # Rate limit

        except:
            continue

    return None

# ============================================================================
# VERIFICATION ENGINE
# ============================================================================

def gather_signals(contact):
    """Gather verification signals from multiple free sources"""
    first = contact.get('first_name', '')
    last = contact.get('last_name', '')
    org = contact.get('organization', '')
    role = contact.get('role_title', '')
    company_website = contact.get('company_website', '')

    signals = []

    # Query 1: Full name + org + role
    query1 = f'"{first} {last}" "{org}" "{role}"'
    print(f"  🔍 Searching: {query1}")
    results1 = google_custom_search(query1, num=5)

    for r in results1:
        source_type, weight = classify_source(r['link'], r['snippet'], r['title'])
        title_sim = title_similarity(role, r['title'] + ' ' + r['snippet'])
        org_sim = org_similarity(org, r['displayLink'] + ' ' + r['snippet'])

        signals.append({
            'source': 'google_search',
            'url': r['link'],
            'title': r['title'],
            'snippet': r['snippet'],
            'source_type': source_type,
            'source_weight': weight,
            'title_similarity': title_sim,
            'org_similarity': org_sim,
            'freshness': freshness_multiplier(r['snippet'])
        })

    # Query 2: LinkedIn specific
    query2 = f'site:linkedin.com/in "{first} {last}" "{org}"'
    print(f"  🔍 Searching: {query2}")
    results2 = google_custom_search(query2, num=3)

    for r in results2:
        source_type, weight = classify_source(r['link'], r['snippet'], r['title'])
        signals.append({
            'source': 'linkedin_search',
            'url': r['link'],
            'title': r['title'],
            'snippet': r['snippet'],
            'source_type': source_type,
            'source_weight': weight,
            'title_similarity': title_similarity(role, r['snippet']),
            'org_similarity': org_similarity(org, r['snippet']),
            'freshness': 0.9  # LinkedIn is generally current
        })

    # Query 3: Company website specific
    if company_website:
        domain = urlparse(company_website).netloc
        query3 = f'site:{domain} "{first} {last}"'
        print(f"  🔍 Searching: {query3}")
        results3 = google_custom_search(query3, num=3)

        for r in results3:
            signals.append({
                'source': 'company_site',
                'url': r['link'],
                'title': r['title'],
                'snippet': r['snippet'],
                'source_type': 'company_site_official',
                'source_weight': SOURCE_WEIGHTS['company_site_official'],
                'title_similarity': title_similarity(role, r['snippet']),
                'org_similarity': 1.0,  # Definitely correct org
                'freshness': 0.9
            })

    # Query 4: News mentions
    query4 = f'"{first} {last}" "{org}"'
    print(f"  📰 News search: {query4}")
    news_results = google_news_search(query4)

    for r in news_results:
        signals.append({
            'source': 'google_news',
            'url': r['link'],
            'title': r['title'],
            'snippet': r['title'],  # News RSS doesn't have snippets
            'source_type': 'news_reputable' if any(nd in r['link'] for nd in REPUTABLE_NEWS_DOMAINS) else 'aggregator',
            'source_weight': SOURCE_WEIGHTS['news_reputable'] if any(nd in r['link'] for nd in REPUTABLE_NEWS_DOMAINS) else 0.5,
            'title_similarity': title_similarity(role, r['title']),
            'org_similarity': org_similarity(org, r['title']),
            'freshness': freshness_multiplier(r.get('date'))
        })

    # Query 5: GitHub (if tech role)
    if any(kw in role.lower() for kw in ['engineer', 'developer', 'cto', 'technical', 'technology', 'research']):
        print(f"  🐙 GitHub check: {first} {last}")
        gh_data = github_user_check(first, last)
        if gh_data:
            org_match = org_similarity(org, gh_data.get('company', ''))
            if org_match > 0.5:  # Only include if org matches
                signals.append({
                    'source': 'github',
                    'url': gh_data['url'],
                    'title': gh_data.get('name', ''),
                    'snippet': gh_data.get('bio', ''),
                    'source_type': 'github_profile',
                    'source_weight': SOURCE_WEIGHTS['github_profile'],
                    'title_similarity': 0.5,  # GitHub doesn't have titles
                    'org_similarity': org_match,
                    'freshness': 0.8
                })

    return signals

def compute_confidence_score(contact, signals):
    """
    Compute confidence score (0-100) based on aggregated signals

    Formula: 70 * corroboration_factor + 30 * max_signal_score
    """
    if not signals:
        return 0

    # Calculate individual signal scores
    signal_scores = []
    high_weight_sources = 0

    for sig in signals:
        # Signal score = weight * freshness * (0.6*title_sim + 0.4*org_sim)
        match_score = 0.6 * sig['title_similarity'] + 0.4 * sig['org_similarity']
        sig_score = sig['source_weight'] * sig['freshness'] * match_score
        signal_scores.append(sig_score)

        # Count high-weight independent sources
        if sig['source_weight'] >= 0.8:
            high_weight_sources += 1

    if not signal_scores:
        return 0

    # Corroboration factor (how many independent high-quality sources)
    corroboration_factor = min(1.0, high_weight_sources / 3.0)

    # Max signal score
    max_signal_score = max(signal_scores)

    # Final confidence (0-100)
    confidence = min(100, int(70 * corroboration_factor + 30 * max_signal_score * 100))

    return confidence

def determine_verification_status(confidence_score):
    """Map confidence score to verification status"""
    if confidence_score >= 80:
        return 'verified', 'auto'
    elif confidence_score >= 50:
        return 'partial', 'quick_review'
    else:
        return 'unverified', 'manual_review'

# ============================================================================
# MAIN VERIFICATION WORKFLOW
# ============================================================================

def verify_contact(contact, audit_log_dir):
    """Verify a single contact and return enriched data"""
    print(f"\n{'='*80}")
    print(f"Verifying: {contact['first_name']} {contact['last_name']} - {contact['organization']}")
    print(f"{'='*80}")

    # Gather signals
    signals = gather_signals(contact)

    # Compute confidence
    confidence = compute_confidence_score(contact, signals)

    # Determine status
    status, review_type = determine_verification_status(confidence)

    # Get primary source (highest weighted signal)
    primary_source = ''
    if signals:
        sorted_signals = sorted(signals, key=lambda s: s['source_weight'], reverse=True)
        primary_source = sorted_signals[0]['url']

    print(f"\n✅ Confidence Score: {confidence}/100")
    print(f"   Status: {status} ({review_type})")
    print(f"   Primary Source: {primary_source}")
    print(f"   Signals Found: {len(signals)}")

    # Create audit log
    contact_id = hashlib.md5(f"{contact['first_name']}{contact['last_name']}{contact['organization']}".encode()).hexdigest()[:12]

    audit_data = {
        'contact_id': contact_id,
        'contact': {
            'first_name': contact['first_name'],
            'last_name': contact['last_name'],
            'organization': contact['organization'],
            'role_title': contact['role_title']
        },
        'verification': {
            'confidence_score': confidence,
            'status': status,
            'review_type': review_type,
            'verified_at': datetime.now().isoformat(),
            'verifier_version': '1.0-free'
        },
        'signals': signals[:10],  # Store top 10 signals
        'primary_source': primary_source
    }

    # Save audit log
    audit_file = Path(audit_log_dir) / f"audit_{contact_id}.json"
    with open(audit_file, 'w') as f:
        json.dump(audit_data, f, indent=2)

    return {
        'confidence_score': confidence,
        'verified_status': status,
        'verified_by': review_type,
        'verified_source_url': primary_source,
        'signals_count': len(signals),
        'last_verified': datetime.now().isoformat()
    }

def process_csv(input_csv, output_csv, audit_log_dir, max_contacts=None):
    """Process CSV and verify contacts"""
    # Create audit log directory
    Path(audit_log_dir).mkdir(parents=True, exist_ok=True)

    # Read input
    contacts = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)

    print(f"\n{'='*80}")
    print(f"InfraFabric Contact Verification System")
    print(f"{'='*80}")
    print(f"Total contacts to verify: {len(contacts)}")
    if max_contacts:
        print(f"Limiting to first {max_contacts} contacts (testing mode)")
        contacts = contacts[:max_contacts]
    print(f"Audit logs will be saved to: {audit_log_dir}")
    print(f"{'='*80}\n")

    # Process contacts
    verified_contacts = []
    for i, contact in enumerate(contacts, 1):
        print(f"\n[{i}/{len(contacts)}]", end=" ")

        try:
            verification_result = verify_contact(contact, audit_log_dir)

            # Merge verification data with contact
            enriched_contact = dict(contact)
            enriched_contact.update(verification_result)
            verified_contacts.append(enriched_contact)

        except Exception as e:
            print(f"❌ Error verifying contact: {e}")
            # Add with error status
            enriched_contact = dict(contact)
            enriched_contact.update({
                'confidence_score': 0,
                'verified_status': 'error',
                'verified_by': 'manual_review',
                'verified_source_url': '',
                'signals_count': 0,
                'last_verified': datetime.now().isoformat(),
                'error': str(e)
            })
            verified_contacts.append(enriched_contact)

        # Rate limit between contacts
        time.sleep(RATE_LIMIT_SECONDS * 2)

    # Write output CSV
    if verified_contacts:
        fieldnames = list(verified_contacts[0].keys())
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(verified_contacts)

    # Generate summary
    auto_verified = sum(1 for c in verified_contacts if c['verified_by'] == 'auto')
    quick_review = sum(1 for c in verified_contacts if c['verified_by'] == 'quick_review')
    manual_review = sum(1 for c in verified_contacts if c['verified_by'] == 'manual_review')

    print(f"\n{'='*80}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total processed: {len(verified_contacts)}")
    print(f"✅ Auto-verified (score >= 80): {auto_verified} ({auto_verified/len(verified_contacts)*100:.1f}%)")
    print(f"⚠️  Quick review needed (50-79): {quick_review} ({quick_review/len(verified_contacts)*100:.1f}%)")
    print(f"❌ Manual review needed (<50): {manual_review} ({manual_review/len(verified_contacts)*100:.1f}%)")
    print(f"\nOutput saved to: {output_csv}")
    print(f"Audit logs saved to: {audit_log_dir}/")
    print(f"{'='*80}\n")

# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='InfraFabric Contact Verification System (Free APIs only)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify top 5 contacts (testing)
  python3 auto_verify_contacts.py --in outreach-targets-FINAL-RANKED.csv --out verified.csv --max 5

  # Verify all contacts
  python3 auto_verify_contacts.py --in outreach-targets-FINAL-RANKED.csv --out verified.csv

  # Custom audit log directory
  python3 auto_verify_contacts.py --in contacts.csv --out verified.csv --audit-dir ./verification-logs

Environment variables:
  GOOGLE_API_KEY - Your Google Cloud API key
  GOOGLE_CSE_ID  - Your Google Custom Search Engine ID
        """
    )

    parser.add_argument('--in', dest='input', required=True,
                        help='Input CSV file with contacts')
    parser.add_argument('--out', dest='output', required=True,
                        help='Output CSV file with verification results')
    parser.add_argument('--audit-dir', dest='audit_dir',
                        default='./verification-audit-logs',
                        help='Directory for audit logs (default: ./verification-audit-logs)')
    parser.add_argument('--max', dest='max_contacts', type=int,
                        help='Maximum contacts to process (for testing)')

    args = parser.parse_args()

    # Check API keys
    if GOOGLE_API_KEY == 'YOUR_GOOGLE_API_KEY_HERE':
        print("\n⚠️  WARNING: Google API credentials not configured!")
        print("Set environment variables or edit the script:")
        print("  export GOOGLE_API_KEY='your-key'")
        print("  export GOOGLE_CSE_ID='your-cse-id'")
        print("\nSetup instructions:")
        print("  1. Enable Custom Search API: https://console.cloud.google.com/apis/library/customsearch.googleapis.com")
        print("  2. Create API key: https://console.cloud.google.com/apis/credentials")
        print("  3. Create Custom Search Engine: https://programmablesearchengine.google.com/")
        print("\nContinuing with limited functionality...\n")

    # Run verification
    process_csv(args.input, args.output, args.audit_dir, args.max_contacts)
