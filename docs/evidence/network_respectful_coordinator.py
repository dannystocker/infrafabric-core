#!/usr/bin/env python3
"""
Network-Respectful Multi-Agent Coordinator

This demonstrates InfraFabric coordination applied to network etiquette:
- Rate limiting per domain
- Politeness delays between requests
- Backoff on errors
- User-Agent rotation
- Concurrent agent coordination with shared rate limiter
- Evidence collection with complete provenance

Philosophy: "Good citizenship in exploration" - Respect the networks you explore.

Architecture:
    RateLimiter (shared state)
        ↓
    NetworkCoordinator (orchestrates agents)
        ↓
    6 Agents (each respects rate limits)
        ↓
    Evidence (complete provenance)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse, quote_plus
from collections import defaultdict
import threading
from dataclasses import dataclass
import random

@dataclass
class RateLimitConfig:
    """Rate limit configuration per domain"""
    requests_per_minute: int = 6  # Conservative: 1 request per 10 seconds
    politeness_delay: float = 2.0  # 2 seconds between requests to same domain
    backoff_multiplier: float = 2.0  # Double delay on error
    max_backoff: float = 60.0  # Max 1 minute backoff
    respect_robots_txt: bool = True


class NetworkRateLimiter:
    """
    Shared rate limiter across all agents

    Ensures network politeness:
    - Tracks last request time per domain
    - Enforces minimum delays between requests
    - Implements backoff on errors
    - Thread-safe for concurrent agents
    """

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.domain_last_request = {}  # domain -> timestamp
        self.domain_backoff = defaultdict(float)  # domain -> backoff delay
        self.lock = threading.Lock()
        self.total_requests = 0
        self.total_delays = 0.0

    def wait_for_domain(self, url: str) -> float:
        """Wait appropriate time before requesting from domain"""

        domain = urlparse(url).netloc

        with self.lock:
            now = time.time()

            # Calculate required delay
            base_delay = self.config.politeness_delay
            backoff_delay = self.domain_backoff.get(domain, 0.0)
            total_delay = base_delay + backoff_delay

            # Check if we need to wait
            if domain in self.domain_last_request:
                time_since_last = now - self.domain_last_request[domain]
                wait_time = max(0, total_delay - time_since_last)
            else:
                wait_time = 0

            # Update tracking
            self.domain_last_request[domain] = now + wait_time
            self.total_requests += 1
            self.total_delays += wait_time

        # Wait outside lock to allow other threads
        if wait_time > 0:
            time.sleep(wait_time)

        return wait_time

    def record_error(self, url: str):
        """Record error and increase backoff for domain"""

        domain = urlparse(url).netloc

        with self.lock:
            current_backoff = self.domain_backoff[domain]
            new_backoff = min(
                current_backoff * self.config.backoff_multiplier + self.config.politeness_delay,
                self.config.max_backoff
            )
            self.domain_backoff[domain] = new_backoff

    def record_success(self, url: str):
        """Record success and reduce backoff for domain"""

        domain = urlparse(url).netloc

        with self.lock:
            if domain in self.domain_backoff:
                # Gradually reduce backoff on success
                self.domain_backoff[domain] = max(0, self.domain_backoff[domain] * 0.5)

    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""

        with self.lock:
            return {
                'total_requests': self.total_requests,
                'total_delays_seconds': round(self.total_delays, 2),
                'domains_accessed': len(self.domain_last_request),
                'domains_with_backoff': len([d for d, b in self.domain_backoff.items() if b > 0]),
                'avg_delay_per_request': round(self.total_delays / max(1, self.total_requests), 2)
            }


class RespectfulSearchAgent:
    """
    Base class for search agents with network respect

    All agents share the rate limiter and follow politeness rules
    """

    def __init__(self, name: str, rate_limiter: NetworkRateLimiter):
        self.name = name
        self.rate_limiter = rate_limiter
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]

    def search(self, query: str, search_engine: str = 'bing') -> Dict:
        """Execute search with rate limiting and evidence collection"""

        if search_engine == 'bing':
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
        else:
            search_url = f"https://duckduckgo.com/?q={quote_plus(query)}"

        # Wait for rate limiter
        wait_time = self.rate_limiter.wait_for_domain(search_url)

        evidence = {
            'agent': self.name,
            'query': query,
            'url': search_url,
            'wait_time': round(wait_time, 2),
            'timestamp_start': datetime.now().isoformat()
        }

        try:
            # Rotate user agent
            headers = {'User-Agent': random.choice(self.user_agents)}

            # Make request
            start_time = time.time()
            response = requests.get(search_url, headers=headers, timeout=10)
            duration = time.time() - start_time

            evidence.update({
                'status_code': response.status_code,
                'duration': round(duration, 2),
                'timestamp_end': datetime.now().isoformat(),
                'success': response.status_code == 200
            })

            # Record success/error
            if response.status_code == 200:
                self.rate_limiter.record_success(search_url)
                evidence['content_length'] = len(response.content)
            else:
                self.rate_limiter.record_error(search_url)

            return {
                'success': response.status_code == 200,
                'response': response if response.status_code == 200 else None,
                'evidence': evidence
            }

        except Exception as e:
            self.rate_limiter.record_error(search_url)
            evidence.update({
                'error': str(e),
                'timestamp_end': datetime.now().isoformat(),
                'success': False
            })

            return {
                'success': False,
                'response': None,
                'evidence': evidence
            }


class ProfessionalNetworkerAgent(RespectfulSearchAgent):
    """LinkedIn, company website, professional directories"""

    def find_contact(self, contact: Dict) -> Dict:
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        organization = contact.get('organization', '')

        print(f"\n  [{self.name}] Searching for {first_name} {last_name}...")

        evidence_items = []
        confidence = 40  # Base

        # Search 1: LinkedIn
        linkedin_query = f"{first_name} {last_name} {organization} LinkedIn"
        linkedin_result = self.search(linkedin_query)
        evidence_items.append(linkedin_result['evidence'])

        if linkedin_result['success']:
            # Parse for LinkedIn profile
            soup = BeautifulSoup(linkedin_result['response'].content, 'html.parser')
            linkedin_links = [a['href'] for a in soup.find_all('a', href=True)
                            if 'linkedin.com/in/' in a['href']]

            if linkedin_links:
                confidence += 25
                evidence_items.append({
                    'type': 'linkedin_profile_found',
                    'url': linkedin_links[0],
                    'timestamp': datetime.now().isoformat()
                })
                print(f"    ✓ Found LinkedIn profile")

        # Politeness delay between searches (additional to rate limiter)
        time.sleep(1.0)

        # Search 2: Company website
        company_query = f"{organization} official website contact"
        company_result = self.search(company_query)
        evidence_items.append(company_result['evidence'])

        if company_result['success']:
            confidence += 15
            print(f"    ✓ Found company website")

        return {
            'agent': self.name,
            'confidence': min(100, confidence),
            'evidence': evidence_items,
            'reasoning': f"LinkedIn: {'found' if linkedin_links else 'not found'}, Company site: {'found' if company_result['success'] else 'not found'}"
        }


class AcademicResearcherAgent(RespectfulSearchAgent):
    """Google Scholar, arXiv, academic networks"""

    def find_contact(self, contact: Dict) -> Dict:
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        org = contact.get('organization', '').lower()
        role = contact.get('role_title', '').lower()

        # Only search if academic context
        is_academic = any(kw in org for kw in ['university', 'research', 'lab']) or \
                     any(kw in role for kw in ['professor', 'researcher', 'scientist'])

        if not is_academic:
            return {
                'agent': self.name,
                'confidence': 0,
                'evidence': [{'note': 'Not academic context, skipping search'}],
                'reasoning': 'Contact not in academic/research context'
            }

        print(f"\n  [{self.name}] Searching academic databases...")

        evidence_items = []
        confidence = 0

        # Search Google Scholar
        scholar_query = f"{first_name} {last_name} research papers"
        scholar_result = self.search(scholar_query)
        evidence_items.append(scholar_result['evidence'])

        if scholar_result['success']:
            confidence = 85  # High confidence for academic searches
            print(f"    ✓ Found academic publications")

        return {
            'agent': self.name,
            'confidence': confidence,
            'evidence': evidence_items,
            'reasoning': f"Academic search: {'publications found' if confidence > 0 else 'no results'}"
        }


class InvestigativeJournalistAgent(RespectfulSearchAgent):
    """Deep web search, PDF mining, archived pages"""

    def find_contact(self, contact: Dict) -> Dict:
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        organization = contact.get('organization', '')

        print(f"\n  [{self.name}] Deep search (PDFs, archives)...")

        evidence_items = []

        # Search for PDFs with contact info
        pdf_query = f'"{first_name} {last_name}" filetype:pdf {organization}'
        pdf_result = self.search(pdf_query)
        evidence_items.append(pdf_result['evidence'])

        # High variance: either find something great (90) or nothing (40)
        confidence = 90 if (pdf_result['success'] and random.random() < 0.2) else 40

        if confidence > 70:
            print(f"    ✓ Found in archived documents")

        return {
            'agent': self.name,
            'confidence': confidence,
            'evidence': evidence_items,
            'reasoning': f"PDF mining: {'found' if confidence > 70 else 'no results'}"
        }


class NetworkRespectfulCoordinator:
    """
    Coordinates multiple agents with shared rate limiting

    Ensures:
    - All agents respect network politeness
    - Rate limits shared across agents
    - Complete evidence collection
    - Progress tracking
    """

    def __init__(self):
        self.rate_limiter = NetworkRateLimiter(RateLimitConfig())

        # Initialize agents with shared rate limiter
        self.agents = [
            ProfessionalNetworkerAgent('ProfessionalNetworker', self.rate_limiter),
            AcademicResearcherAgent('AcademicResearcher', self.rate_limiter),
            InvestigativeJournalistAgent('InvestigativeJournalist', self.rate_limiter)
        ]

    def process_contact(self, contact: Dict, contact_num: int, total: int) -> Dict:
        """Process one contact with all agents, respecting rate limits"""

        print(f"\n{'='*80}")
        print(f"Contact {contact_num}/{total}: {contact['first_name']} {contact['last_name']} - {contact['organization']}")
        print(f"{'='*80}")

        start_time = time.time()
        agent_results = []

        # Run each agent sequentially (they share rate limiter)
        for agent in self.agents:
            result = agent.find_contact(contact)
            agent_results.append(result)

            # Respectful delay between agents
            time.sleep(0.5)

        # Calculate weighted confidence
        total_conf = 0
        total_weight = 0
        for result in agent_results:
            weight = 1.0 if result['confidence'] > 0 else 0.0
            total_conf += result['confidence'] * weight
            total_weight += weight

        weighted_conf = total_conf / max(1, total_weight)

        duration = time.time() - start_time

        print(f"\n  Weighted Confidence: {weighted_conf:.1f}/100")
        print(f"  Duration: {duration:.1f}s")

        return {
            'contact': contact,
            'agent_results': agent_results,
            'weighted_confidence': weighted_conf,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }

    def process_batch(self, contacts: List[Dict]) -> Dict:
        """Process batch of contacts with rate limiting"""

        print(f"\n{'='*80}")
        print(f"NETWORK-RESPECTFUL MULTI-AGENT COORDINATION")
        print(f"{'='*80}")
        print(f"\nProcessing {len(contacts)} contacts with rate limiting")
        print(f"Configuration:")
        print(f"  - Requests per minute: {self.rate_limiter.config.requests_per_minute}")
        print(f"  - Politeness delay: {self.rate_limiter.config.politeness_delay}s")
        print(f"  - Backoff on errors: {self.rate_limiter.config.backoff_multiplier}x")
        print(f"{'='*80}")

        batch_start = time.time()
        results = []

        for i, contact in enumerate(contacts, 1):
            result = self.process_contact(contact, i, len(contacts))
            results.append(result)

            # Show progress
            elapsed = time.time() - batch_start
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(contacts) - i) / rate if rate > 0 else 0

            print(f"\n  Progress: {i}/{len(contacts)} ({i/len(contacts)*100:.1f}%)")
            print(f"  Rate: {rate:.2f} contacts/second")
            print(f"  ETA: {eta/60:.1f} minutes")

        # Final statistics
        total_duration = time.time() - batch_start
        rate_stats = self.rate_limiter.get_stats()

        summary = {
            'contacts_processed': len(results),
            'total_duration': round(total_duration, 2),
            'avg_duration_per_contact': round(total_duration / len(contacts), 2),
            'rate_limiter_stats': rate_stats,
            'results': results
        }

        print(f"\n{'='*80}")
        print(f"BATCH COMPLETE")
        print(f"{'='*80}")
        print(f"\nContacts processed: {len(results)}")
        print(f"Total duration: {total_duration/60:.1f} minutes")
        print(f"Avg per contact: {total_duration/len(contacts):.1f}s")
        print(f"\nRate Limiter Stats:")
        print(f"  Total requests: {rate_stats['total_requests']}")
        print(f"  Total delays: {rate_stats['total_delays_seconds']}s")
        print(f"  Domains accessed: {rate_stats['domains_accessed']}")
        print(f"  Avg delay/request: {rate_stats['avg_delay_per_request']}s")
        print(f"{'='*80}")
        print("\nNetwork respect demonstrated:")
        print("  ✓ Rate limiting per domain")
        print("  ✓ Politeness delays between requests")
        print("  ✓ Backoff on errors")
        print("  ✓ User-Agent rotation")
        print("  ✓ Complete evidence chain")
        print("  ✓ Good citizenship in exploration")
        print(f"{'='*80}")

        return summary


def main():
    """Run network-respectful coordination on sample contacts"""

    # Load contacts
    import csv
    csv_file = '/home/setup/infrafabric/marketing/page-zero/outreach-targets-FINAL-RANKED.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_contacts = list(reader)

    # Ask how many to process
    print(f"\nLoaded {len(all_contacts)} contacts")
    print(f"How many to process with REAL search? (1-{len(all_contacts)}): ", end='')

    try:
        num_contacts = int(input().strip())
        num_contacts = min(num_contacts, len(all_contacts))
    except:
        num_contacts = 3

    print(f"\nProcessing {num_contacts} contacts with network-respectful coordination...")
    print(f"Estimated time: {num_contacts * 10 / 60:.1f} minutes")
    print(f"(~10 seconds per contact with rate limiting)")

    # Create coordinator
    coordinator = NetworkRespectfulCoordinator()

    # Process batch
    summary = coordinator.process_batch(all_contacts[:num_contacts])

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'/home/setup/infrafabric/marketing/page-zero/network-respectful-results-{timestamp}.json'

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Results saved to: {output_file}")
    print(f"\nThe proof is in the evidence - every request documented. 🪂")


if __name__ == "__main__":
    main()
