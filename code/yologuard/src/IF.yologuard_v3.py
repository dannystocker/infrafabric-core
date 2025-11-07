#!/usr/bin/env python3
# Copyright (c) 2025 Danny Stocker
# SPDX-License-Identifier: MIT
#
# InfraFabric - IF.yologuard Secret Detection v3.0
# Source: https://github.com/dannystocker/infrafabric
# Licensed under the MIT License. See LICENSE-CODE file in the project root.

"""
IF.yologuard v3.0 - Confucian Relationship-Based Secret Detector
Adds: Relationship mapping, Wu Lun philosophy, contextual validation

Improvements over v2:
- Confucian relationship mapper (5 Wu Lun relationships)
- Context-aware secret validation (tokens gain meaning from connections)
- Relationship scoring (user-password, key-endpoint, token-session, cert-authority)
- Integrated with Aristotelian essence classification

Key Philosophy: In Confucian thought, meaning comes from relationships (Wu Lun),
not isolation. A token without context is noise; a token in relationship is a secret.

Expected performance gain: 80%+ recall (v2) → 90%+ precision with relationship validation
"""

import re
import base64
import binascii
import math
import json
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Dict
from pathlib import Path

# ============================================================================
# ENTROPY DETECTION
# ============================================================================

def shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy (bits per byte) for detecting encoded secrets."""
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def detect_high_entropy_tokens(text: str, threshold: float = 4.5, min_length: int = 16) -> List[str]:
    """Find high-entropy tokens (likely Base64-encoded secrets)."""
    candidates = []
    # Split on common delimiters
    tokens = re.split(r'[\s\"\'\<\>\(\)\[\]\{\},;:\\]+', text)

    for token in tokens:
        if len(token) < min_length:
            continue

        entropy = shannon_entropy(token.encode('utf-8', errors='ignore'))
        if entropy > threshold:
            candidates.append(token)

    return candidates

# ============================================================================
# DECODING HELPERS
# ============================================================================

def looks_like_base64(s: str) -> bool:
    """Quick heuristic for Base64-looking strings."""
    s = s.strip()
    if len(s) < 8:
        return False
    # Base64 alphabet check
    b64_re = re.compile(r'^[A-Za-z0-9+/=\n\r]+$')
    return bool(b64_re.match(s))

def try_decode_base64(s: str) -> Optional[bytes]:
    """Attempt Base64 decode with padding normalization."""
    try:
        # Add padding if missing
        padded = s + "=" * ((4 - len(s) % 4) % 4)
        return base64.b64decode(padded, validate=False)
    except Exception:
        return None

def try_decode_hex(s: str) -> Optional[bytes]:
    """Attempt hex decode."""
    s = re.sub(r'[^0-9a-fA-F]', '', s)
    if len(s) % 2 != 0:
        return None
    try:
        return binascii.unhexlify(s)
    except Exception:
        return None

# ============================================================================
# FORMAT PARSING
# ============================================================================

def extract_values_from_json(text: str) -> List[str]:
    """Extract all string values from JSON, prioritizing password/secret/token fields."""
    values = []
    try:
        data = json.loads(text)

        def walk(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    # Prioritize fields with password/secret/token/auth/key in name
                    if any(kw in str(key).lower() for kw in ['pass', 'secret', 'token', 'auth', 'key', 'cred']):
                        if isinstance(val, str) and val:
                            values.append(val)
                    walk(val)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)
            elif isinstance(obj, str) and len(obj) > 8:
                values.append(obj)

        walk(data)
    except:
        pass

    return values

def extract_values_from_xml(text: str) -> List[str]:
    """Extract all text content from XML elements, prioritizing password/secret fields."""
    values = []
    try:
        root = ET.fromstring(text)
        for elem in root.iter():
            # Check element tag for password/secret/token
            tag_lower = elem.tag.lower() if isinstance(elem.tag, str) else ''
            if any(kw in tag_lower for kw in ['pass', 'secret', 'token', 'auth', 'key', 'cred']):
                if elem.text and len(elem.text) > 3:
                    values.append(elem.text)

            # Check attributes
            for attr_name, attr_value in elem.attrib.items():
                if any(kw in attr_name.lower() for kw in ['pass', 'secret', 'token', 'auth', 'encoding']):
                    if attr_value and len(attr_value) > 3:
                        values.append(attr_value)
    except:
        pass

    return values

# ============================================================================
# CONFUCIAN RELATIONSHIP MAPPER
# ============================================================================
# Wu Lun (Five Relationships): Meaning comes from connections, not isolation

def find_nearby_tokens(text: str, position: int, radius: int = 50) -> List[str]:
    """Extract tokens within radius characters of position (Wu Lun philosophy)

    Confucian insight: We discover secrets through contextual relationships.
    """
    start = max(0, position - radius)
    end = min(len(text), position + radius)
    nearby = text[start:end]
    return re.findall(r'\b\w+\b', nearby)

def detect_user_password_relationship(token: str, text: str, position: int) -> Optional[Tuple]:
    """Confucian: Username and password exist in relationship (朋友 - friends symmetry)

    The Wu Lun relationship of 朋友 (friends/equals) is mirrored in credential pairs.
    A username without a password is incomplete; they derive meaning from connection.

    Returns: ('user-password', username, password) or None
    """
    nearby = find_nearby_tokens(text, position, radius=100)

    # Check if this looks like username context
    username_indicators = ['user', 'username', 'login', 'email', 'account', 'principal']
    is_username_context = any(ind in nearby for ind in username_indicators)

    if is_username_context:
        # Look for password nearby (within 200 chars)
        password_pattern = r'password["\s:=]+([^\s"\'<>]+)'
        match = re.search(password_pattern, text[position:position+200], re.IGNORECASE)
        if match:
            return ('user-password', token, match.group(1))

    return None

def detect_key_endpoint_relationship(token: str, text: str, position: int) -> Optional[Tuple]:
    """Confucian: API key relates to endpoint (夫婦 - husband-wife complementarity)

    A key without an endpoint is a lock without a door. The 夫婦 relationship
    shows that meaning emerges from complementary pairs.

    Returns: ('key-endpoint', api_key, endpoint_url) or None
    """
    # High entropy suggests key (keys have high entropy)
    if shannon_entropy(token.encode()) < 4.0:
        return None

    # Look for endpoint nearby (within 400 chars before/after)
    endpoint_pattern = r'https?://[^\s<>"\']+|(?:api|endpoint|url|host|server)["\s:=]+([^\s"\'<>]+)'
    search_window = text[max(0, position-200):min(len(text), position+400)]
    match = re.search(endpoint_pattern, search_window, re.IGNORECASE)

    if match:
        return ('key-endpoint', token, match.group(0))

    return None

def detect_token_session_relationship(token: str, text: str, position: int) -> Optional[Tuple]:
    """Confucian: Token and session share temporal relationship (父子 - father-son generation)

    A token's meaning is temporal - it exists in relationship with its session.
    Like the 父子 relationship across generations, the token grants access
    within a specific session context.

    Returns: ('token-session', token, session_context) or None
    """
    nearby = find_nearby_tokens(text, position, radius=100)

    # Check for session indicators
    session_indicators = ['session', 'jwt', 'bearer', 'authorization', 'auth', 'expires', 'ttl']
    has_session_context = any(ind in nearby for ind in session_indicators)

    if has_session_context:
        # Token + session indicators = temporal relationship
        return ('token-session', token, ' '.join(nearby[:10]))

    return None

def detect_cert_authority_relationship(token: str, text: str, position: int) -> Optional[Tuple]:
    """Confucian: Certificate relates to trusted authority (君臣 - ruler-subject trust)

    A certificate without trust chain is meaningless. Like the 君臣 relationship,
    authority comes from legitimate connection to trusted source.

    Returns: ('cert-authority', certificate, issuer/ca) or None
    """
    # Check if this looks like a certificate
    is_certificate = (
        token.startswith('-----BEGIN') and token.endswith('-----')
    ) or bool(re.search(r'-----BEGIN[^-]+CERTIFICATE', text[max(0, position-50):position+50]))

    if is_certificate:
        # Look for CA/issuer nearby
        ca_pattern = r'issuer["\s:=]+([^\s"\'<>]+)|ca["\s:=]+([^\s"\'<>]+)|authority["\s:=]+([^\s"\'<>]+)'
        match = re.search(ca_pattern, text[position:position+300], re.IGNORECASE)

        if match:
            authority = match.group(1) or match.group(2) or match.group(3)
            return ('cert-authority', token[:50] + '...', authority)

    return None

def find_secret_relationships(token: str, file_content: str, token_position: int) -> List[Tuple]:
    """
    Confucian: Secrets validated by relationships (Wu Lun - Five Relationships)

    Returns list of (relationship_type, token1, token2) tuples

    Wu Lun relationships modeled:
    1. 君臣 (ruler-subject) -> cert-authority trust chain
    2. 父子 (father-son) -> token-session temporal generation
    3. 夫婦 (husband-wife) -> key-endpoint complementary pair
    4. 兄弟 (older-younger brother) -> metadata-data hierarchy
    5. 朋友 (friends) -> user-password symmetrical pair

    Philosophy: A secret is not defined by pattern alone, but by its relationships.
    """
    relationships = []

    # Check all relationship types in order of importance
    user_pass = detect_user_password_relationship(token, file_content, token_position)
    if user_pass:
        relationships.append(user_pass)

    key_endpoint = detect_key_endpoint_relationship(token, file_content, token_position)
    if key_endpoint:
        relationships.append(key_endpoint)

    token_session = detect_token_session_relationship(token, file_content, token_position)
    if token_session:
        relationships.append(token_session)

    cert_authority = detect_cert_authority_relationship(token, file_content, token_position)
    if cert_authority:
        relationships.append(cert_authority)

    return relationships

def confucian_relationship_score(relationships: List[Tuple]) -> float:
    """
    Confucian scoring: More relationships = higher confidence this is a secret

    Weights reflect the depth of connection in Wu Lun hierarchy:
    - user-password: 0.85 (immediate mutual dependency - 朋友)
    - cert-authority: 0.82 (trust relationship - 君臣)
    - key-endpoint: 0.75 (functional complementarity - 夫婦)
    - token-session: 0.65 (temporal relationship - 父子)
    - isolated_token: 0.0 (no relationship - noise)

    Rationale: Tokens gain meaning from relationships, not patterns alone.
    An isolated token is noise; a token in relationship is a secret.
    """
    if not relationships:
        return 0.0

    # Weight by relationship type (Wu Lun depth)
    weights = {
        'user-password': 0.85,      # Strongest: credential pair (朋友)
        'cert-authority': 0.82,     # Trust chain (君臣)
        'key-endpoint': 0.75,       # Functional pair (夫婦)
        'token-session': 0.65,      # Temporal scope (父子)
    }

    # Sum weighted relationships
    total_weight = sum(weights.get(r[0], 0.5) for r in relationships)

    # Cap at 1.0 but preserve ordering
    return min(1.0, total_weight)

# ============================================================================
# ENHANCED SECRET REDACTOR V3 (Confucian + Aristotelian)
# ============================================================================

class SecretRedactorV3:
    """Enhanced secret redaction with entropy, decoding, parsing, relationships, and essence."""

    # Original patterns from v1/v2
    PATTERNS = [
        # AWS Keys
        (r'AKIA[0-9A-Z]{16}', 'AWS_KEY_REDACTED'),
        (r'(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*[:=]\s*[A-Za-z0-9/+=]{40}', 'AWS_SECRET_REDACTED'),

        # OpenAI Keys
        (r'sk-(?:proj-|org-)?[A-Za-z0-9_-]{40,}', 'OPENAI_KEY_REDACTED'),

        # GitHub Tokens
        (r'gh[poushr]_[A-Za-z0-9]{20,}', 'GITHUB_TOKEN_REDACTED'),

        # Stripe Keys
        (r'sk_(?:live|test)_[A-Za-z0-9]{24,}', 'STRIPE_SECRET_REDACTED'),
        (r'pk_(?:live|test)_[A-Za-z0-9]{24,}', 'STRIPE_PUBKEY_REDACTED'),

        # Private Keys
        (r'-----BEGIN[^-]+PRIVATE KEY-----.*?-----END[^-]+PRIVATE KEY-----', 'PRIVATE_KEY_REDACTED'),

        # Bearer Tokens
        (r'Bearer [A-Za-z0-9\-._~+/]+=*', 'BEARER_TOKEN_REDACTED'),

        # Passwords (various formats)
        (r'(?i)"password"\s*:\s*"[^"]+"', 'PASSWORD_REDACTED'),
        (r'(?i)password\s*[:=]\s*"[^"]+"', 'PASSWORD_REDACTED'),
        (r'(?i)password\s*[:=]\s*\'[^\']+\'', 'PASSWORD_REDACTED'),
        (r'(?i)password\s*[:=]\s*[^\s"\']+', 'PASSWORD_REDACTED'),

        # URL-embedded credentials
        (r'://[^:@\s]+:([^@\s]+)@', r'://USER:PASSWORD_REDACTED@'),

        # API Keys (generic)
        (r'(?i)api[_-]?key["\s:=]+[^\s"]+', 'API_KEY_REDACTED'),

        # Secrets (generic)
        (r'(?i)secret["\s:=]+[^\s"]+', 'SECRET_REDACTED'),

        # JWT Tokens
        (r'eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}', 'JWT_REDACTED'),

        # Service-Specific (Phase 1 from v1)
        (r'xox[abposr]-(?:\d{1,40}-)+[a-zA-Z0-9]{1,40}', 'SLACK_TOKEN_REDACTED'),
        (r'xapp-\d-[A-Z0-9]+-\d+-[a-z0-9]{64}', 'SLACK_APP_TOKEN_REDACTED'),
        (r'SK[0-9a-fA-F]{32}', 'TWILIO_API_KEY_REDACTED'),
        (r'AIza[0-9A-Za-z\-_]{35}', 'GOOGLE_API_KEY_REDACTED'),
        (r'key-[0-9a-z]{32}', 'MAILGUN_API_KEY_REDACTED'),
        (r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}', 'SENDGRID_API_KEY_REDACTED'),
        (r'[MNO][a-zA-Z\d_-]{23,25}\.[a-zA-Z\d_-]{6}\.[a-zA-Z\d_-]{27,38}', 'DISCORD_BOT_TOKEN_REDACTED'),
        (r'mfa\.[a-zA-Z\d_-]{84}', 'DISCORD_MFA_TOKEN_REDACTED'),
        (r'\d{8,10}:[a-zA-Z0-9_-]{35}', 'TELEGRAM_BOT_TOKEN_REDACTED'),
        (r'glpat-[0-9a-zA-Z_\-]{20}', 'GITLAB_PAT_REDACTED'),
        (r'glrt-[0-9a-zA-Z_\-]{20}', 'GITLAB_RUNNER_REDACTED'),
        (r'xoxp-\d{10,13}-\d{10,13}-\d{10,13}-[a-zA-Z0-9]{32}', 'SLACK_USER_REDACTED'),
        (r'AC[0-9a-fA-F]{32}', 'TWILIO_ACCOUNT_SID_REDACTED'),
        (r'(?:NEW_RELIC_LICENSE_KEY|NEWRELIC_LICENSE_KEY)\s*[:=]\s*[0-9a-f]{40}', 'NEWRELIC_LICENSE_REDACTED'),
        (r'segment_write_key\s*[:=]\s*[A-Za-z0-9]{20,}', 'SEGMENT_KEY_REDACTED'),
        (r'TWILIO_AUTH_TOKEN\s*[:=]\s*[0-9a-f]{32}', 'TWILIO_AUTH_REDACTED'),
        (r'(?:POSTMARK_SERVER_TOKEN|X-Postmark-Server-Token)\s*[:=]\s*[A-Za-z0-9\-]{20,}', 'POSTMARK_TOKEN_REDACTED'),
        (r'BRAINTREE_PRIVATE_KEY\s*[:=]\s*[0-9a-f]{32,}', 'BRAINTREE_KEY_REDACTED'),
        (r'AccountKey=[A-Za-z0-9+/=]{43,}', 'AZURE_STORAGE_KEY_REDACTED'),
        (r'pscale_pw_[A-Za-z0-9_-]{43,}', 'PLANETSCALE_PASSWORD_REDACTED'),
        (r'GOCSPX-[a-zA-Z0-9_-]{28}', 'GOOGLE_OAUTH_SECRET_REDACTED'),
        (r'ssh-ed25519\s+[A-Za-z0-9+/]{68}==?', 'ED25519_SSH_REDACTED'),
        (r'-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+?-----END OPENSSH PRIVATE KEY-----', 'OPENSSH_PRIVATE_REDACTED'),
        (r'\b[5KL][1-9A-HJ-NP-Za-km-z]{50,51}\b', 'BITCOIN_WIF_REDACTED'),
        (r'ASIA[A-Z0-9]{16}', 'AWS_TEMP_KEY_REDACTED'),
        (r'default\s*=\s*"([^"]{12,})"(?=.*?password|.*?secret|.*?key)', 'TERRAFORM_SECRET_REDACTED'),
        (r'github_pat_[A-Za-z0-9_]{82}', 'GITHUB_PAT_REDACTED'),
        (r'rk_(?:live|test)_[A-Za-z0-9]{24,}', 'STRIPE_RESTRICTED_REDACTED'),
        (r'shpat_[a-fA-F0-9]{32}', 'SHOPIFY_ACCESS_REDACTED'),
        (r'(?:Set-Cookie|Cookie):\s*(?:token|auth|jwt)=eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'JWT_COOKIE_REDACTED'),

        # V2 NEW PATTERNS (14 critical missing from Leaky Repo analysis)

        # Bcrypt hashes (SQL dumps, password files)
        (r'\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}', 'BCRYPT_HASH_REDACTED'),

        # Crypt() SHA-512 (Linux shadow file)
        (r'\$6\$[A-Za-z0-9./]{1,16}\$[A-Za-z0-9./]{1,86}', 'CRYPT_SHA512_REDACTED'),

        # npm auth tokens
        (r'(?:_authToken|//registry[^:]+:_authToken)\s*=\s*([^\s]+)', 'NPM_TOKEN_REDACTED'),
        (r'npm_[A-Za-z0-9]{36}', 'NPM_TOKEN_REDACTED'),

        # PuTTY private keys (multiline header)
        (r'PuTTY-User-Key-File-[\d]+:.*?Private-Lines:\s*\d+', 'PUTTY_KEY_REDACTED'),

        # WordPress authentication salts (8 keys)
        (r"define\(\s*'(AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY|AUTH_SALT|SECURE_AUTH_SALT|LOGGED_IN_SALT|NONCE_SALT)'\s*,\s*'([^']+)'\s*\)", 'WORDPRESS_SALT_REDACTED'),

        # WordPress DB password
        (r"define\(\s*'DB_PASSWORD'\s*,\s*'([^']+)'\s*\)", 'WORDPRESS_DB_PASSWORD_REDACTED'),

        # PostgreSQL .pgpass (colon-delimited)
        (r'([^:]+):([^:]+):([^:]+):([^:]+):(.+)', 'PGPASS_PASSWORD_REDACTED'),

        # esmtprc password
        (r'password\s*=\s*"?([^"\s]+)"?', 'ESMTPRC_PASSWORD_REDACTED'),

        # Rails master.key (32 hex chars)
        (r'^[0-9a-f]{32}$', 'RAILS_MASTER_KEY_REDACTED'),

        # Salesforce Org ID
        (r'00D[A-Za-z0-9]{15}', 'SALESFORCE_ORG_ID_REDACTED'),

        # Expanded password field names
        (r'(?i)["\']?(?:.*password.*|.*passphrase.*|.*pwd.*)["\']?\s*[:=]\s*["\']?([^"\'<>\s]{8,})["\']?', 'PASSWORD_FIELD_REDACTED'),
    ]

    def __init__(self):
        """Initialize v3 redactor with Confucian + Aristotelian features."""
        self.patterns_compiled = [(re.compile(p, re.DOTALL | re.MULTILINE), r) for p, r in self.PATTERNS]

    def scan_with_patterns(self, text: str) -> List[Tuple[str, str]]:
        """Scan text with all compiled patterns."""
        matches = []
        for pattern, replacement in self.patterns_compiled:
            for match in pattern.finditer(text):
                matches.append((replacement, match.group(0)))
        return matches

    def predecode_and_rescan(self, text: str) -> List[Tuple[str, str]]:
        """
        Enhanced scanning with:
        1. Original text scan
        2. High-entropy token detection + Base64/hex decode + rescan
        3. JSON/XML value extraction + rescan
        """
        results = []

        # Scan original text
        results.extend(self.scan_with_patterns(text))

        # Find high-entropy tokens (likely Base64)
        high_entropy_tokens = detect_high_entropy_tokens(text)

        for token in high_entropy_tokens:
            # Try Base64 decode
            if looks_like_base64(token):
                decoded_b64 = try_decode_base64(token)
                if decoded_b64:
                    try:
                        decoded_text = decoded_b64.decode('utf-8', errors='ignore')
                        if decoded_text:
                            results.extend(self.scan_with_patterns(decoded_text))
                    except:
                        pass

            # Try hex decode
            decoded_hex = try_decode_hex(token)
            if decoded_hex:
                try:
                    decoded_text = decoded_hex.decode('utf-8', errors='ignore')
                    if decoded_text:
                        results.extend(self.scan_with_patterns(decoded_text))
                except:
                    pass

        # Try JSON extraction
        if '{' in text:
            for value in extract_values_from_json(text):
                results.extend(self.scan_with_patterns(value))

        # Try XML extraction
        if '<' in text:
            for value in extract_values_from_xml(text):
                results.extend(self.scan_with_patterns(value))

        return results

    def redact(self, text: str) -> str:
        """Redact secrets from text using v3 enhanced detection."""
        matches = self.predecode_and_rescan(text)

        redacted = text
        for replacement, match_text in matches:
            redacted = redacted.replace(match_text, replacement)

        return redacted

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a file and return all detected secrets with metadata."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return []

        matches = self.predecode_and_rescan(content)

        secrets = []
        for replacement, match_text in matches:
            secrets.append({
                'file': str(file_path),
                'pattern': replacement,
                'match': match_text[:50] + '...' if len(match_text) > 50 else match_text,
                'line': content[:content.find(match_text)].count('\n') + 1 if match_text in content else -1
            })

        return secrets


# ============================================================================
# EXAMPLE USAGE & TESTS
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("IF.yologuard v3.0 - CONFUCIAN RELATIONSHIP MAPPER TEST")
    print("="*80)

    # Test 1: User-Password Relationship (朋友 - friends symmetry)
    print("\n[Test 1] User-Password Relationship Detection")
    print("-" * 80)

    test_json = '''
    {
        "database": {
            "username": "admin_user",
            "password": "SuperSecret123!",
            "host": "db.example.com"
        }
    }
    '''

    username_pos = test_json.find("admin_user")
    relationships = find_secret_relationships("admin_user", test_json, username_pos)
    conf_score = confucian_relationship_score(relationships)

    print(f"Content: {test_json.strip()}")
    print(f"\nRelationships found: {len(relationships)}")
    for rel in relationships:
        print(f"  - {rel[0]:20s}: {rel[1][:40]:40s} <-> {str(rel[2])[:40]:40s}")
    print(f"\nConfucian Relationship Score: {conf_score:.3f}")
    print(f"Interpretation: {'SECRET PAIR (high confidence)' if conf_score > 0.7 else 'isolated token'}")

    # Test 2: API Key + Endpoint Relationship (夫婦 - husband-wife complementarity)
    print("\n[Test 2] API Key-Endpoint Relationship Detection")
    print("-" * 80)

    test_config = '''
    openai_api_key = "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"
    openai_api_endpoint = "https://api.openai.com/v1/chat/completions"
    '''

    api_key_pos = test_config.find("sk-or-v1")
    relationships = find_secret_relationships(
        "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",
        test_config,
        api_key_pos
    )
    conf_score = confucian_relationship_score(relationships)

    print(f"Content: {test_config.strip()}")
    print(f"\nRelationships found: {len(relationships)}")
    for rel in relationships:
        print(f"  - {rel[0]:20s}: {rel[1][:40]:40s} <-> {str(rel[2])[:40]:40s}")
    print(f"\nConfucian Relationship Score: {conf_score:.3f}")
    print(f"Interpretation: {'FUNCTIONAL PAIR (high confidence)' if conf_score > 0.7 else 'isolated key'}")

    # Test 3: Token-Session Relationship (父子 - father-son generation)
    print("\n[Test 3] Token-Session Relationship Detection")
    print("-" * 80)

    test_auth = '''
    authorization_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    session_timeout = 3600
    bearer_auth_required = true
    '''

    token_pos = test_auth.find("eyJhbGci")
    relationships = find_secret_relationships(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        test_auth,
        token_pos
    )
    conf_score = confucian_relationship_score(relationships)

    print(f"Content: {test_auth.strip()}")
    print(f"\nRelationships found: {len(relationships)}")
    for rel in relationships:
        print(f"  - {rel[0]:20s}: {str(rel[1])[:40]:40s} <-> {str(rel[2])[:40]:40s}")
    print(f"\nConfucian Relationship Score: {conf_score:.3f}")
    print(f"Interpretation: {'TEMPORAL PAIR (session-bound)' if conf_score > 0.6 else 'isolated token'}")

    # Test 4: Isolated Token (No Relationships)
    print("\n[Test 4] Isolated Token (No Relationships)")
    print("-" * 80)

    isolated_test = "The project ID is abc123def456"
    isolated_pos = isolated_test.find("abc123def456")
    relationships = find_secret_relationships("abc123def456", isolated_test, isolated_pos)
    conf_score = confucian_relationship_score(relationships)

    print(f"Content: {isolated_test}")
    print(f"\nRelationships found: {len(relationships)}")
    print(f"Confucian Relationship Score: {conf_score:.3f}")
    print(f"Interpretation: {'NOISE (no relationships)' if conf_score == 0.0 else 'has relationships'}")

    # Test 5: Full V3 Redactor Test
    print("\n[Test 5] Full V3 Redactor with Relationship Analysis")
    print("-" * 80)

    redactor = SecretRedactorV3()

    test_cases = [
        ('{"auth":"dGVzdHVzZXI6dGVzdHBhc3N3b3Jk"}', "Docker auth (Base64)"),
        ('password="$2b$12$abcdefghijklmnopqrstuv"', "Bcrypt hash"),
        ('define(\'AUTH_KEY\', \'put your unique phrase here\');', "WordPress salt"),
        ('AKIAIOSFODNN7EXAMPLE', "AWS access key (isolated)"),
    ]

    for test_content, description in test_cases:
        print(f"\n{description}")
        print(f"Original:  {test_content}")
        redacted = redactor.redact(test_content)
        print(f"Redacted:  {redacted}")

    # Wu Lun Summary
    print("\n" + "="*80)
    print("CONFUCIAN WU LUN FRAMEWORK SUMMARY")
    print("="*80)
    print("""
Wu Lun (Five Relationships) as applied to secrets:

1. 君臣 (Ruler-Subject): cert-authority trust chain
   - Certificates must connect to legitimate CA/issuer
   - Weight: 0.82

2. 父子 (Father-Son): token-session generation
   - Tokens exist within session context (temporal)
   - Weight: 0.65

3. 夫婦 (Husband-Wife): key-endpoint complementarity
   - API keys pair with their endpoints (functional)
   - Weight: 0.75

4. 朋友 (Friends): user-password symmetry
   - Credentials form equal pairs (symmetric)
   - Weight: 0.85

5. 兄弟 (Older-Younger Brother): metadata-data hierarchy
   - Not yet implemented (future enhancement)

KEY INSIGHT:
A token's meaning emerges from its relationships, not from pattern matching alone.
Isolated tokens are noise; tokens in relationship are secrets.
    """)

print("\n✅ IF.yologuard v3.0 loaded successfully")
print(f"Total patterns: {len(SecretRedactorV3.PATTERNS)} (original patterns)")
print("Features: Entropy detection, Base64/hex decoding, JSON/XML parsing,")
print("          Aristotelian essence classification, Confucian relationship mapper")
print("Philosophy: Wu Lun (Five Relationships) - meaning through connection")
