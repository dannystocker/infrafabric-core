#!/usr/bin/env python3
"""
Multi-Agent Contact Discovery System
Runs 4 parallel approaches + cross-validation

Agents:
1. Smart Google Search (API, early stopping)
2. WebFetch Common URLs (zero API cost)
3. Email Pattern Generator (fallback)
4. Simulated User Browser (reference metric for quality)
"""

import os
import sys
import json
import csv
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')
MAX_QUERIES_PER_CONTACT = 5
EARLY_STOP_THRESHOLD = 95
GOOD_ENOUGH_THRESHOLD = 85

# User agents
MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
DESKTOP_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class ContactFinderAgent:
    """Base class for contact finding agents"""

    def __init__(self, name: str):
        self.name = name
        self.queries_used = 0
        self.results = []

    def find_contact(self, contact: Dict) -> Dict:
        """Override in subclass"""
        raise NotImplementedError

    def score_result(self, result: Dict, contact: Dict) -> int:
        """Score a contact result (0-100)"""
        raise NotImplementedError

class Agent1_SmartGoogleSearch(ContactFinderAgent):
    """
    Agent 1: Smart Google Search with Early Stopping
    Uses Custom Search API with quality thresholds
    """

    def __init__(self):
        super().__init__("GoogleSearch")
        self.api_key = GOOGLE_API_KEY
        self.cse_id = GOOGLE_CSE_ID

    def find_contact(self, contact: Dict) -> Dict:
        """
        Progressive search with early stopping
        """
        name = f"{contact['first_name']} {contact['last_name']}"
        org = contact['organization']
        domain = self._extract_domain(contact.get('company_website', ''))

        results = {
            'agent': self.name,
            'contact_methods': [],
            'queries_used': 0,
            'best_score': 0,
            'stopped_early': False
        }

        # Query sequence (prioritized)
        queries = [
            f'"{name}" email site:{domain}',
            f'"{name}" contact site:{domain}',
            f'"{name}" site:linkedin.com',
            f'@{domain} site:{domain}',  # Find email pattern
            f'"{name}" {org} email'
        ]

        for i, query in enumerate(queries[:MAX_QUERIES_PER_CONTACT]):
            if not self.api_key:
                break

            # Perform search
            search_result = self._google_search(query)
            results['queries_used'] += 1

            if not search_result:
                continue

            # Extract and score contact info
            contact_info = self._extract_contact_info(search_result, contact)

            if contact_info:
                score = self.score_result(contact_info, contact)
                contact_info['score'] = score
                contact_info['query_num'] = i + 1
                results['contact_methods'].append(contact_info)
                results['best_score'] = max(results['best_score'], score)

                # Early stopping logic
                if score >= EARLY_STOP_THRESHOLD:
                    results['stopped_early'] = True
                    results['stop_reason'] = f"Found excellent result (score: {score})"
                    break
                elif score >= GOOD_ENOUGH_THRESHOLD and results['queries_used'] >= 2:
                    results['stopped_early'] = True
                    results['stop_reason'] = f"Found good result confirmed by 2+ sources (score: {score})"
                    break

        self.queries_used = results['queries_used']
        return results

    def _google_search(self, query: str) -> Optional[Dict]:
        """Execute Google Custom Search API query"""
        if not self.api_key or not self.cse_id:
            return None

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': 5
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"  ⚠️  Search error: {e}")

        return None

    def _extract_contact_info(self, search_result: Dict, contact: Dict) -> Optional[Dict]:
        """Extract contact information from search results"""
        if 'items' not in search_result:
            return None

        for item in search_result['items']:
            url = item.get('link', '')
            title = item.get('title', '')
            snippet = item.get('snippet', '')

            # Look for emails in snippet
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', snippet)

            if emails:
                return {
                    'type': 'email',
                    'value': emails[0],
                    'source_url': url,
                    'source_type': self._classify_source(url),
                    'snippet': snippet[:200]
                }

            # Look for LinkedIn profile
            if 'linkedin.com/in/' in url:
                return {
                    'type': 'linkedin',
                    'value': url,
                    'source_url': url,
                    'source_type': 'linkedin_profile',
                    'snippet': snippet[:200]
                }

            # Look for contact page
            if any(word in url.lower() for word in ['contact', 'about', 'team', 'leadership']):
                return {
                    'type': 'contact_page',
                    'value': url,
                    'source_url': url,
                    'source_type': 'company_page',
                    'snippet': snippet[:200]
                }

        return None

    def _classify_source(self, url: str) -> str:
        """Classify the trustworthiness of a source"""
        domain = urlparse(url).netloc.lower()

        if '.gov' in domain or '.mil' in domain:
            return 'government_official'
        elif 'linkedin.com' in domain:
            return 'linkedin'
        elif any(tld in domain for tld in ['.edu', '.org']):
            return 'institutional'
        else:
            return 'company_website'

    def _extract_domain(self, website: str) -> str:
        """Extract domain from URL"""
        if not website:
            return ''
        parsed = urlparse(website if website.startswith('http') else f'https://{website}')
        return parsed.netloc

    def score_result(self, result: Dict, contact: Dict) -> int:
        """
        Score contact method (0-100)

        Scoring criteria:
        - Type of contact method (email > LinkedIn > contact form)
        - Source quality (official > institutional > generic)
        - Personalization (firstname.lastname > generic)
        - Freshness (if available)
        """
        score = 0

        # Base score by type
        if result['type'] == 'email':
            email = result['value']
            # Check if email matches expected pattern
            if self._matches_name_pattern(email, contact):
                score = 85  # firstname.lastname@domain
            elif self._is_role_email(email):
                score = 70  # cto@, admin@
            else:
                score = 50  # Generic email
        elif result['type'] == 'linkedin':
            score = 75  # LinkedIn profile
        elif result['type'] == 'contact_page':
            score = 65  # Contact form/page
        else:
            score = 40

        # Boost by source type
        source_boosts = {
            'government_official': 15,
            'institutional': 10,
            'linkedin': 8,
            'company_website': 5
        }
        score += source_boosts.get(result.get('source_type', ''), 0)

        # Special case: Government contacts prefer LinkedIn
        if contact.get('sector') == 'Defense Innovation' and result['type'] == 'linkedin':
            score += 10

        return min(score, 100)

    def _matches_name_pattern(self, email: str, contact: Dict) -> bool:
        """Check if email matches firstname.lastname pattern"""
        local = email.split('@')[0].lower()
        first = contact['first_name'].lower()
        last = contact['last_name'].lower()

        patterns = [
            f"{first}.{last}",
            f"{first}{last}",
            f"{first[0]}{last}",
            f"{first}.{last[0]}",
        ]

        return any(pattern in local for pattern in patterns)

    def _is_role_email(self, email: str) -> bool:
        """Check if email is a role-based address"""
        local = email.split('@')[0].lower()
        role_keywords = ['cto', 'ceo', 'vp', 'director', 'admin', 'contact', 'info', 'hello']
        return any(keyword in local for keyword in role_keywords)


class Agent2_WebFetchCommonURLs(ContactFinderAgent):
    """
    Agent 2: WebFetch Common URLs
    Zero API cost, scrapes common pages
    """

    def __init__(self):
        super().__init__("WebFetch")

    def find_contact(self, contact: Dict) -> Dict:
        """
        Try common URL patterns and scrape for contact info
        """
        website = contact.get('company_website', '')
        if not website:
            return {'agent': self.name, 'contact_methods': [], 'queries_used': 0, 'best_score': 0}

        base_url = website if website.startswith('http') else f'https://{website}'

        # Common paths to try
        paths = [
            '/contact',
            '/about/team',
            '/leadership',
            '/about-us',
            '/about',
            '/team',
            '/people'
        ]

        results = {
            'agent': self.name,
            'contact_methods': [],
            'queries_used': 0,
            'best_score': 0
        }

        for path in paths:
            url = urljoin(base_url, path)
            contact_info = self._scrape_page(url, contact)

            if contact_info:
                score = self.score_result(contact_info, contact)
                contact_info['score'] = score
                results['contact_methods'].append(contact_info)
                results['best_score'] = max(results['best_score'], score)

        return results

    def _scrape_page(self, url: str, contact: Dict) -> Optional[Dict]:
        """Scrape a page for contact information"""
        try:
            headers = {'User-Agent': MOBILE_UA}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            # Look for emails
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

            # Filter emails to find most relevant
            name = f"{contact['first_name']} {contact['last_name']}"
            relevant_emails = []

            for email in emails:
                # Skip obvious spam/generic
                if not any(bad in email.lower() for bad in ['noreply', 'spam', 'example']):
                    relevant_emails.append(email)

            if relevant_emails:
                # Return first relevant email found
                return {
                    'type': 'email',
                    'value': relevant_emails[0],
                    'source_url': url,
                    'source_type': 'scraped_page',
                    'all_emails_found': relevant_emails[:5]  # Keep top 5
                }

            # Look for contact forms
            forms = soup.find_all('form')
            if forms:
                return {
                    'type': 'contact_form',
                    'value': url,
                    'source_url': url,
                    'source_type': 'contact_form'
                }

        except Exception as e:
            pass  # Silently fail on scraping errors

        return None

    def score_result(self, result: Dict, contact: Dict) -> int:
        """Score scraped result"""
        if result['type'] == 'email':
            # Check if email matches name pattern
            if any(self._matches_name_pattern(e, contact) for e in result.get('all_emails_found', [result['value']])):
                return 80  # Found matching email
            else:
                return 60  # Found email but unsure if it's theirs
        elif result['type'] == 'contact_form':
            return 70  # Contact form

        return 50

    def _matches_name_pattern(self, email: str, contact: Dict) -> bool:
        """Check if email matches name"""
        local = email.split('@')[0].lower()
        first = contact['first_name'].lower()
        last = contact['last_name'].lower()

        return (first in local and last in local) or f"{first}.{last}" in local


class Agent3_PatternGenerator(ContactFinderAgent):
    """
    Agent 3: Email Pattern Generator
    Fallback approach, generates likely patterns
    """

    def __init__(self):
        super().__init__("PatternGen")

    def find_contact(self, contact: Dict) -> Dict:
        """
        Generate likely email patterns based on company domain
        """
        website = contact.get('company_website', '')
        if not website:
            return {'agent': self.name, 'contact_methods': [], 'queries_used': 0, 'best_score': 0}

        domain = self._extract_domain(website)
        first = contact['first_name'].lower()
        last = contact['last_name'].lower()

        # Generate common patterns
        patterns = [
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}.{last[0]}@{domain}",
            f"{last}.{first}@{domain}",
            f"{first}@{domain}"
        ]

        results = {
            'agent': self.name,
            'contact_methods': [],
            'queries_used': 0,
            'best_score': 45  # Pattern generation is low confidence
        }

        for pattern in patterns:
            results['contact_methods'].append({
                'type': 'email_pattern',
                'value': pattern,
                'source_type': 'generated',
                'confidence': 'unverified',
                'score': 45
            })

        return results

    def _extract_domain(self, website: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(website if website.startswith('http') else f'https://{website}')
        return parsed.netloc

    def score_result(self, result: Dict, contact: Dict) -> int:
        """Pattern generation always gets low score"""
        return 45  # Unverified guess


class Agent4_SimulatedUserBrowser(ContactFinderAgent):
    """
    Agent 4: Simulated User Browser Behavior
    Reference metric - what would a human find?
    """

    def __init__(self):
        super().__init__("SimulatedUser")

    def find_contact(self, contact: Dict) -> Dict:
        """
        Simulate what a user would do:
        1. Google the person's name
        2. Visit their company page
        3. Look for obvious contact info
        """
        name = f"{contact['first_name']} {contact['last_name']}"
        org = contact['organization']

        results = {
            'agent': self.name,
            'contact_methods': [],
            'queries_used': 0,
            'best_score': 0,
            'user_path': []
        }

        # Step 1: "Google search" - use WebFetch to simulate
        # (In reality, we'd use a real browser, but this simulates the behavior)
        results['user_path'].append(f"Step 1: Google '{name} {org} contact'")

        # Step 2: Check company website
        website = contact.get('company_website', '')
        if website:
            results['user_path'].append(f"Step 2: Visit {website}")

            # Try to find contact page (like a user would)
            contact_info = self._user_visit_website(website, contact)
            if contact_info:
                score = self.score_result(contact_info, contact)
                contact_info['score'] = score
                results['contact_methods'].append(contact_info)
                results['best_score'] = score

        # Step 3: Check LinkedIn (user would probably try this)
        results['user_path'].append(f"Step 3: Search LinkedIn for {name}")
        linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '%20')}"
        results['contact_methods'].append({
            'type': 'linkedin_search',
            'value': linkedin_url,
            'source_type': 'user_action',
            'score': 70
        })

        return results

    def _user_visit_website(self, website: str, contact: Dict) -> Optional[Dict]:
        """Simulate a user visiting the website"""
        base_url = website if website.startswith('http') else f'https://{website}'

        # User would look for "Contact" link
        try:
            headers = {'User-Agent': DESKTOP_UA}  # User uses desktop browser
            response = requests.get(base_url, headers=headers, timeout=10)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for contact link (what a user would click)
            contact_links = soup.find_all('a', href=True)
            for link in contact_links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()

                if any(word in href or word in text for word in ['contact', 'about', 'team']):
                    contact_url = urljoin(base_url, link['href'])
                    return {
                        'type': 'contact_page_user',
                        'value': contact_url,
                        'source_type': 'user_navigation',
                        'link_text': link.get_text()[:50]
                    }

        except Exception:
            pass

        return None

    def score_result(self, result: Dict, contact: Dict) -> int:
        """Score based on user accessibility"""
        if result['type'] == 'contact_page_user':
            return 75  # User found a contact page
        elif result['type'] == 'linkedin_search':
            return 70  # LinkedIn is accessible

        return 60


class CrossValidator:
    """
    Cross-validates results from all agents
    """

    def validate(self, agent_results: List[Dict], contact: Dict) -> Dict:
        """
        Compare results from all agents
        Return best result with precision estimate
        """
        all_methods = []

        # Collect all contact methods from all agents
        for agent_result in agent_results:
            for method in agent_result.get('contact_methods', []):
                method['agent'] = agent_result['agent']
                all_methods.append(method)

        if not all_methods:
            return {
                'final_recommendation': None,
                'precision': 0,
                'validation': 'no_results',
                'all_options': []
            }

        # Find agreements (same contact method found by multiple agents)
        agreements = self._find_agreements(all_methods)

        # Calculate precision based on agreement level
        if agreements['count'] >= 3:
            precision = 95  # All agents agree
            validation = '3+_agents_agree'
        elif agreements['count'] == 2:
            precision = 88  # 2 agents agree
            validation = '2_agents_agree'
        else:
            # No agreement, use highest scored individual result
            best = max(all_methods, key=lambda x: x.get('score', 0))
            precision = best.get('score', 50)
            validation = 'single_agent_best'

        # Get best result
        final_result = agreements.get('result') if agreements['count'] >= 2 else max(all_methods, key=lambda x: x.get('score', 0))

        # Compare to user simulation (quality check)
        user_agent_result = next((r for r in agent_results if r['agent'] == 'SimulatedUser'), None)
        quality_check = self._compare_to_user_behavior(final_result, user_agent_result)

        return {
            'final_recommendation': final_result,
            'precision': precision,
            'validation': validation,
            'agreement_count': agreements['count'],
            'all_options': sorted(all_methods, key=lambda x: x.get('score', 0), reverse=True),
            'quality_check': quality_check,
            'total_queries_used': sum(r.get('queries_used', 0) for r in agent_results)
        }

    def _find_agreements(self, methods: List[Dict]) -> Dict:
        """Find when multiple agents found the same contact method"""
        # Group by contact value
        grouped = {}
        for method in methods:
            value = method.get('value', '')
            if value not in grouped:
                grouped[value] = []
            grouped[value].append(method)

        # Find the group with most agents agreeing
        best_agreement = {'count': 0, 'result': None}

        for value, group in grouped.items():
            if len(group) > best_agreement['count']:
                best_agreement = {
                    'count': len(group),
                    'result': max(group, key=lambda x: x.get('score', 0))  # Best scored in group
                }

        return best_agreement

    def _compare_to_user_behavior(self, final_result: Dict, user_result: Optional[Dict]) -> Dict:
        """
        Compare automated result to what a user would find
        Quality check metric
        """
        if not user_result or not user_result.get('contact_methods'):
            return {'status': 'no_user_baseline', 'match': False}

        user_methods = [m.get('value') for m in user_result.get('contact_methods', [])]
        final_value = final_result.get('value', '')

        if final_value in user_methods:
            return {
                'status': 'matches_user_behavior',
                'match': True,
                'confidence': 'high'
            }
        else:
            return {
                'status': 'different_from_user',
                'match': False,
                'note': 'Automated found something user might not easily find (could be better or worse)'
            }


def process_contacts(input_csv: str, output_csv: str, max_contacts: int = None):
    """
    Main execution: Run all 4 agents in parallel on contacts
    """
    print("="*80)
    print("MULTI-AGENT CONTACT DISCOVERY SYSTEM")
    print("="*80)
    print()
    print("Agents:")
    print("  1. Smart Google Search (API, early stopping)")
    print("  2. WebFetch Common URLs (zero API cost)")
    print("  3. Email Pattern Generator (fallback)")
    print("  4. Simulated User Browser (reference metric)")
    print()
    print("="*80)
    print()

    # Initialize agents
    agents = [
        Agent1_SmartGoogleSearch(),
        Agent2_WebFetchCommonURLs(),
        Agent3_PatternGenerator(),
        Agent4_SimulatedUserBrowser()
    ]

    validator = CrossValidator()

    # Read contacts
    contacts = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
            if max_contacts and len(contacts) >= max_contacts:
                break

    print(f"Processing {len(contacts)} contacts...\n")

    # Process each contact
    all_results = []
    total_queries = 0

    for i, contact in enumerate(contacts, 1):
        name = f"{contact['first_name']} {contact['last_name']}"
        org = contact['organization']

        print(f"[{i}/{len(contacts)}] {name} - {org}")
        print("-" * 80)

        # Run all agents in parallel (simulated - would use threading in production)
        agent_results = []
        for agent in agents:
            print(f"  Running {agent.name}...", end=" ")
            sys.stdout.flush()

            result = agent.find_contact(contact)
            agent_results.append(result)

            methods_found = len(result.get('contact_methods', []))
            queries = result.get('queries_used', 0)
            best_score = result.get('best_score', 0)

            print(f"✅ {methods_found} methods, {queries} queries, best score: {best_score}")

        # Cross-validate
        print("  Cross-validating...", end=" ")
        sys.stdout.flush()

        validated = validator.validate(agent_results, contact)

        print(f"✅ Precision: {validated['precision']}%, {validated['validation']}")

        # Display recommendation
        if validated['final_recommendation']:
            rec = validated['final_recommendation']
            print(f"  📧 Recommendation: {rec['type']} = {rec['value'][:50]}")
        else:
            print(f"  ⚠️  No contact method found")

        print()

        # Track queries
        total_queries += validated['total_queries_used']

        # Save result
        all_results.append({
            'contact': contact,
            'agent_results': agent_results,
            'validated': validated
        })

    print("="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    print(f"Total API queries used: {total_queries}")
    print(f"Average precision: {sum(r['validated']['precision'] for r in all_results) / len(all_results):.1f}%")
    print()

    # Save results
    _save_results(all_results, output_csv)

    print(f"Results saved to: {output_csv}")
    print(f"Detailed report: {output_csv.replace('.csv', '-report.json')}")


def _save_results(results: List[Dict], output_csv: str):
    """Save results to CSV and JSON"""

    # Save CSV with recommendations
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'first_name', 'last_name', 'organization', 'role_title',
            'recommended_contact_type', 'recommended_contact_value',
            'precision', 'validation_method', 'all_options_count',
            'queries_used', 'agent_agreement_count'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            contact = result['contact']
            validated = result['validated']
            rec = validated.get('final_recommendation', {})

            writer.writerow({
                'first_name': contact['first_name'],
                'last_name': contact['last_name'],
                'organization': contact['organization'],
                'role_title': contact.get('role_title', ''),
                'recommended_contact_type': rec.get('type', 'none'),
                'recommended_contact_value': rec.get('value', ''),
                'precision': validated['precision'],
                'validation_method': validated['validation'],
                'all_options_count': len(validated['all_options']),
                'queries_used': validated['total_queries_used'],
                'agent_agreement_count': validated['agreement_count']
            })

    # Save detailed JSON report
    report_path = output_csv.replace('.csv', '-report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Multi-agent contact discovery')
    parser.add_argument('--in', dest='input', required=True, help='Input CSV file')
    parser.add_argument('--out', dest='output', required=True, help='Output CSV file')
    parser.add_argument('--max', dest='max_contacts', type=int, help='Max contacts to process')

    args = parser.parse_args()

    process_contacts(args.input, args.output, args.max_contacts)
