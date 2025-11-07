#!/usr/bin/env python3
"""
Real Search Agent POC - Actual Web Search with Evidence

This demonstrates ONE agent doing REAL search with proof:
- Actually searches the web (using requests + BeautifulSoup)
- Collects evidence (URLs found, snippets, timestamps)
- Returns provenance (where info came from, when, confidence reasoning)
- Self-documents search strategy

Philosophy: "Show your work" - Every result must include proof of discovery.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import Dict, List
from urllib.parse import quote_plus
import time

class RealProfessionalNetworkerAgent:
    """
    ProfessionalNetworker - But REAL this time

    Strategy:
    1. Search LinkedIn for profile
    2. Search company website for contact pages
    3. Search common email pattern databases
    4. Collect evidence at every step
    5. Return provenance with proof
    """

    def __init__(self):
        self.name = "ProfessionalNetworker"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.evidence = []
        self.search_log = []

    def find_contact(self, contact: Dict) -> Dict:
        """Execute real search with evidence collection"""

        start_time = datetime.now()
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        organization = contact.get('organization', '')

        print(f"\n{'='*80}")
        print(f"🔍 REAL SEARCH: {first_name} {last_name} - {organization}")
        print(f"{'='*80}")

        # Step 1: Search for LinkedIn profile
        print("\n[Step 1] Searching LinkedIn...")
        linkedin_result = self._search_linkedin(first_name, last_name, organization)

        # Step 2: Search for company website
        print("\n[Step 2] Searching company website...")
        company_result = self._search_company_website(organization)

        # Step 3: Search for email patterns
        print("\n[Step 3] Searching email pattern databases...")
        email_result = self._search_email_patterns(first_name, last_name, organization)

        # Calculate confidence based on evidence
        confidence = self._calculate_confidence(
            linkedin_result,
            company_result,
            email_result
        )

        # Compile evidence
        all_evidence = (
            linkedin_result.get('evidence', []) +
            company_result.get('evidence', []) +
            email_result.get('evidence', [])
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            'agent': self.name,
            'contact': contact,
            'confidence': confidence,
            'reasoning': self._generate_reasoning(linkedin_result, company_result, email_result),
            'evidence': all_evidence,
            'search_log': self.search_log,
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'proof': {
                'linkedin_searched': linkedin_result['searched'],
                'company_searched': company_result['searched'],
                'email_db_searched': email_result['searched'],
                'urls_checked': len([e for e in all_evidence if e['type'] == 'url_checked']),
                'snippets_found': len([e for e in all_evidence if e['type'] == 'snippet']),
            }
        }

        print(f"\n✅ Search complete:")
        print(f"   Confidence: {confidence}/100")
        print(f"   Evidence items: {len(all_evidence)}")
        print(f"   Duration: {duration:.2f}s")

        return result

    def _search_linkedin(self, first_name: str, last_name: str, organization: str) -> Dict:
        """Search for LinkedIn profile with evidence"""

        query = f"{first_name} {last_name} {organization} LinkedIn"
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}"

        self.search_log.append({
            'step': 'linkedin_search',
            'query': query,
            'url': search_url,
            'timestamp': datetime.now().isoformat()
        })

        evidence = []
        found_linkedin = False
        linkedin_url = None

        try:
            print(f"   Query: {query}")
            print(f"   Searching: {search_url[:80]}...")

            response = requests.get(search_url, headers=self.headers, timeout=5)

            evidence.append({
                'type': 'url_checked',
                'url': search_url,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for LinkedIn URLs in search results
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'linkedin.com/in/' in href:
                        found_linkedin = True
                        linkedin_url = href

                        # Get snippet
                        parent = link.find_parent('li') or link.find_parent('div')
                        snippet = parent.get_text()[:200] if parent else "Found LinkedIn profile link"

                        evidence.append({
                            'type': 'linkedin_profile',
                            'url': linkedin_url,
                            'snippet': snippet,
                            'timestamp': datetime.now().isoformat()
                        })

                        print(f"   ✓ Found LinkedIn: {linkedin_url[:60]}...")
                        break

                if not found_linkedin:
                    print(f"   ⚠ No LinkedIn profile found in search results")

        except Exception as e:
            evidence.append({
                'type': 'error',
                'step': 'linkedin_search',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            print(f"   ⚠ Error: {e}")

        return {
            'searched': True,
            'found': found_linkedin,
            'linkedin_url': linkedin_url,
            'evidence': evidence
        }

    def _search_company_website(self, organization: str) -> Dict:
        """Search for company website with evidence"""

        query = f"{organization} official website contact"
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}"

        self.search_log.append({
            'step': 'company_search',
            'query': query,
            'url': search_url,
            'timestamp': datetime.now().isoformat()
        })

        evidence = []
        company_domain = None

        try:
            print(f"   Query: {query}")
            print(f"   Searching: {search_url[:80]}...")

            response = requests.get(search_url, headers=self.headers, timeout=5)

            evidence.append({
                'type': 'url_checked',
                'url': search_url,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for company domain in first result
                first_result = soup.find('li', class_='b_algo')
                if first_result:
                    link = first_result.find('a', href=True)
                    if link:
                        company_domain = link['href']
                        snippet = first_result.get_text()[:200]

                        evidence.append({
                            'type': 'company_website',
                            'domain': company_domain,
                            'snippet': snippet,
                            'timestamp': datetime.now().isoformat()
                        })

                        print(f"   ✓ Found domain: {company_domain[:60]}...")

        except Exception as e:
            evidence.append({
                'type': 'error',
                'step': 'company_search',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            print(f"   ⚠ Error: {e}")

        return {
            'searched': True,
            'found': company_domain is not None,
            'domain': company_domain,
            'evidence': evidence
        }

    def _search_email_patterns(self, first_name: str, last_name: str, organization: str) -> Dict:
        """Search for email patterns with evidence"""

        query = f'"{first_name} {last_name}" email {organization}'
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}"

        self.search_log.append({
            'step': 'email_search',
            'query': query,
            'url': search_url,
            'timestamp': datetime.now().isoformat()
        })

        evidence = []
        found_email = None

        try:
            print(f"   Query: {query}")
            print(f"   Searching: {search_url[:80]}...")

            response = requests.get(search_url, headers=self.headers, timeout=5)

            evidence.append({
                'type': 'url_checked',
                'url': search_url,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            })

            if response.status_code == 200:
                # Simple email pattern detection in page text
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails_found = re.findall(email_pattern, response.text)

                # Filter for relevant emails
                for email in emails_found:
                    if first_name.lower() in email.lower() or last_name.lower() in email.lower():
                        found_email = email

                        evidence.append({
                            'type': 'email_found',
                            'email': found_email,
                            'source': 'search_results',
                            'timestamp': datetime.now().isoformat()
                        })

                        print(f"   ✓ Found email: {found_email}")
                        break

        except Exception as e:
            evidence.append({
                'type': 'error',
                'step': 'email_search',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            print(f"   ⚠ Error: {e}")

        return {
            'searched': True,
            'found': found_email is not None,
            'email': found_email,
            'evidence': evidence
        }

    def _calculate_confidence(self, linkedin_result: Dict, company_result: Dict, email_result: Dict) -> int:
        """Calculate confidence based on evidence found"""

        confidence = 40  # Base confidence

        # LinkedIn profile found: +25
        if linkedin_result.get('found'):
            confidence += 25

        # Company website found: +15
        if company_result.get('found'):
            confidence += 15

        # Email found: +20
        if email_result.get('found'):
            confidence += 20

        return min(100, confidence)

    def _generate_reasoning(self, linkedin_result: Dict, company_result: Dict, email_result: Dict) -> str:
        """Generate human-readable reasoning for confidence score"""

        reasons = []

        if linkedin_result.get('found'):
            reasons.append(f"LinkedIn profile found: {linkedin_result['linkedin_url'][:60]}...")
        else:
            reasons.append("LinkedIn profile not found in search results")

        if company_result.get('found'):
            reasons.append(f"Company website found: {company_result['domain'][:60]}...")
        else:
            reasons.append("Company website not found")

        if email_result.get('found'):
            reasons.append(f"Email address found: {email_result['email']}")
        else:
            reasons.append("Email address not found in public sources")

        return " | ".join(reasons)


def main():
    """Test real search agent on one contact"""

    print("="*80)
    print("REAL SEARCH AGENT POC - With Evidence & Proof")
    print("="*80)
    print("\nPhilosophy: 'Show your work' - Every result includes proof of discovery")
    print("="*80)

    # Test contact
    test_contact = {
        'first_name': 'Emil',
        'last_name': 'Michael',
        'organization': 'Department of Defense',
        'role_title': 'Former Uber exec',
        'company_website': 'defense.gov'
    }

    # Create agent
    agent = RealProfessionalNetworkerAgent()

    # Execute real search
    result = agent.find_contact(test_contact)

    # Save detailed results
    output_file = f"real-search-evidence-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*80}")
    print("EVIDENCE COLLECTED")
    print(f"{'='*80}")
    print(f"\n📊 Summary:")
    print(f"   Confidence: {result['confidence']}/100")
    print(f"   Evidence items: {len(result['evidence'])}")
    print(f"   URLs checked: {result['proof']['urls_checked']}")
    print(f"   Duration: {result['duration_seconds']:.2f}s")

    print(f"\n📝 Reasoning:")
    print(f"   {result['reasoning']}")

    print(f"\n🔍 Evidence Details:")
    for i, evidence in enumerate(result['evidence'], 1):
        print(f"\n   [{i}] {evidence['type'].upper()}")
        if evidence['type'] == 'url_checked':
            print(f"       URL: {evidence['url'][:70]}...")
            print(f"       Status: {evidence['status_code']}")
        elif evidence['type'] == 'linkedin_profile':
            print(f"       URL: {evidence['url'][:70]}...")
            print(f"       Snippet: {evidence['snippet'][:100]}...")
        elif evidence['type'] == 'company_website':
            print(f"       Domain: {evidence['domain'][:70]}...")
            print(f"       Snippet: {evidence['snippet'][:100]}...")
        elif evidence['type'] == 'email_found':
            print(f"       Email: {evidence['email']}")
        elif evidence['type'] == 'error':
            print(f"       Error: {evidence['error']}")
        print(f"       Timestamp: {evidence['timestamp']}")

    print(f"\n{'='*80}")
    print(f"✅ Results saved to: {output_file}")
    print(f"{'='*80}")
    print("\nThis demonstrates REAL search with provenance:")
    print("  ✓ Actually searched the web (Bing)")
    print("  ✓ Collected evidence at every step")
    print("  ✓ Recorded URLs, status codes, snippets")
    print("  ✓ Timestamped all findings")
    print("  ✓ Explained confidence reasoning")
    print("  ✓ Complete search log included")
    print("\nThe proof is in the evidence. 🪂")


if __name__ == "__main__":
    main()
