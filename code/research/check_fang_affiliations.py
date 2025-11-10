#!/usr/bin/env python3
"""
Quick script to check if any top endorser candidates have FANG affiliations.
Requires fetching actual arXiv paper pages (not just RSS).
"""

import json
import time
import requests
from bs4 import BeautifulSoup

FANG_KEYWORDS = [
    "Google", "DeepMind", "Google Research", "Google Brain",
    "Meta", "Facebook", "Meta AI",
    "Amazon", "AWS", "Amazon Web Services",
    "Netflix",
    "Microsoft", "MSR", "Microsoft Research",  # Often grouped with FANG
    "OpenAI", "Anthropic",  # Major AI labs
    "Epic Games", "Epic", "Unreal Engine"  # Gaming/real-time systems
]

def fetch_paper_affiliations(arxiv_url: str) -> list:
    """Fetch author affiliations from arXiv paper page"""
    try:
        response = requests.get(arxiv_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # arXiv author affiliations are in <div class="authors">
        authors_div = soup.find('div', class_='authors')
        if not authors_div:
            return []
        
        affiliations = []
        # Look for text containing affiliation keywords
        text = authors_div.get_text()
        for keyword in FANG_KEYWORDS:
            if keyword.lower() in text.lower():
                affiliations.append(keyword)
        
        return list(set(affiliations))
    except Exception as e:
        print(f"Error fetching {arxiv_url}: {e}")
        return []

def check_endorsers_fang(json_path: str, top_n: int = 10):
    """Check top N endorsers for FANG affiliations"""
    with open(json_path, 'r') as f:
        endorsers = json.load(f)
    
    print(f"Checking top {top_n} endorsers for FANG/major AI lab affiliations...\n")
    
    fang_found = []
    for i, endorser in enumerate(endorsers[:top_n], 1):
        print(f"[{i}/{top_n}] Checking: {endorser['name']}")
        
        for url in endorser['urls'][:1]:  # Check first paper only (rate limiting)
            affiliations = fetch_paper_affiliations(url)
            if affiliations:
                print(f"   ✅ FOUND: {', '.join(affiliations)}")
                fang_found.append({
                    "name": endorser['name'],
                    "affiliations": affiliations,
                    "paper": url,
                    "relevance": endorser['relevance_score']
                })
            else:
                print(f"   ❌ No FANG affiliation detected")
        
        time.sleep(2)  # Rate limiting
    
    print(f"\n{'='*70}")
    print(f"Summary: Found {len(fang_found)} FANG/major lab researchers")
    print(f"{'='*70}\n")
    
    for candidate in fang_found:
        print(f"• {candidate['name']}")
        print(f"  Affiliations: {', '.join(candidate['affiliations'])}")
        print(f"  Paper: {candidate['paper']}")
        print(f"  IF Relevance: {candidate['relevance']:.1f}")
        print()

if __name__ == "__main__":
    import sys
    import glob
    
    # Find most recent endorser JSON
    json_files = sorted(glob.glob("arxiv_endorsers.*.json"), reverse=True)
    if not json_files:
        print("Error: No arxiv_endorsers.*.json found. Run find_arxiv_endorsers.py first.")
        sys.exit(1)
    
    latest = json_files[0]
    print(f"Using: {latest}\n")
    check_endorsers_fang(latest, top_n=10)
