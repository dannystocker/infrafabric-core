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
try:
    import regex as _regex  # optional: enables timeout in matching
except Exception:
    _regex = None
import base64
import binascii
import math
import json
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import hashlib
import subprocess
from datetime import datetime, UTC
import json as _jsonmod

# ============================================================================
# CONSTANTS (avoid magic numbers)
# ============================================================================

DEFAULT_ERROR_THRESHOLD = 0.75
DEFAULT_WARN_THRESHOLD = 0.50
AUDIT_ERROR_THRESHOLD = 0.70
AUDIT_WARN_THRESHOLD = 0.40
RESEARCH_ERROR_THRESHOLD = 0.60
RESEARCH_WARN_THRESHOLD = 0.40
FORENSICS_ERROR_THRESHOLD = 0.65
FORENSICS_WARN_THRESHOLD = 0.45
DEFAULT_MAX_FILE_BYTES = 5_000_000

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

def detect_metadata_sibling_relationship(token: str, text: str, position: int) -> Optional[Tuple]:
    """
    兄弟 (Older-Younger Brother): metadata-data sibling relationship.

    Detect clusters of related config keys within a window around the token.
    If two or more semantically-related keys are present (e.g., user/password,
    key/secret, endpoint/token), treat as a sibling relationship.
    """
    start = max(0, position - 300)
    end = min(len(text), position + 400)
    window = text[start:end]

    keyval_re = re.compile(r'(?i)([A-Za-z0-9_\.\-]+)\s*[:=]\s*["\']?([^\s"\'\n]+)')
    keys = [m.group(1).lower() for m in keyval_re.finditer(window)]
    if not keys:
        return None

    sensitive = {'password', 'pass', 'secret', 'token', 'key'}
    metadata = {'user', 'username', 'account', 'endpoint', 'url', 'host', 'client', 'app', 'region'}

    has_sensitive = any(any(s in k for s in sensitive) for k in keys)
    related = [k for k in keys if any(t in k for t in sensitive | metadata)]

    if has_sensitive and len(set(related)) >= 2:
        k1 = next(k for k in related if any(s in k for s in sensitive))
        k2 = next(k for k in related if k != k1)
        return ('metadata-sibling', k1, k2)

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

    metadata_sibling = detect_metadata_sibling_relationship(token, file_content, token_position)
    if metadata_sibling:
        relationships.append(metadata_sibling)

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
        'metadata-sibling': 0.60,   # Sibling keys/metadata cluster (兄弟)
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

        # Secrets (generic) - only with quotes or assignment
        (r'(?i)(?:secret|api_secret)\s*[:=]\s*["\']([^"\']{8,})["\']', 'SECRET_REDACTED'),

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
        (r'_auth\s*=\s*([A-Za-z0-9+/=]{8,})', 'NPM_AUTH_REDACTED'),

        # PuTTY private keys (multiline header)
        (r'PuTTY-User-Key-File-[\d]+:.*?Private-Lines:\s*\d+', 'PUTTY_KEY_REDACTED'),

        # WordPress authentication salts (8 keys)
        (r"define\(\s*'(AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY|AUTH_SALT|SECURE_AUTH_SALT|LOGGED_IN_SALT|NONCE_SALT)'\s*,\s*'([^']+)'\s*\)", 'WORDPRESS_SALT_REDACTED'),

        # WordPress DB password
        (r"define\(\s*'DB_PASSWORD'\s*,\s*'([^']+)'\s*\)", 'WORDPRESS_DB_PASSWORD_REDACTED'),

        # PostgreSQL .pgpass (colon-delimited) - hostname:port:db:user:pass (port is 1-5 digits or *)
        (r'^([a-zA-Z0-9.-]+|localhost|\*):(\d{1,5}|\*):([a-zA-Z0-9_-]+|\*):([a-zA-Z0-9_-]+):(.+)$', 'PGPASS_PASSWORD_REDACTED'),

        # esmtprc password (with or without =)
        (r'(?i)password\s*[=\s]\s*"([^"]+)"', 'ESMTPRC_PASSWORD_REDACTED'),
        (r'(?i)(?:username|identity)\s+["\']([^"\']+)["\']', 'ESMTPRC_USERNAME_REDACTED'),

        # Rails master.key (32 hex chars)
        (r'^[0-9a-f]{32}$', 'RAILS_MASTER_KEY_REDACTED'),

        # Salesforce Org ID
        (r'00D[A-Za-z0-9]{15}', 'SALESFORCE_ORG_ID_REDACTED'),

        # V3 MISSING PATTERNS (to reach 96/96)

        # Apache MD5 password hash (.htpasswd)
        (r'\$apr1\$[./0-9A-Za-z]{8}\$[./0-9A-Za-z]{22}', 'APACHE_MD5_REDACTED'),

        # .netrc format (machine ... login ... password ...)
        (r'machine\s+\S+\s+login\s+\S+\s+password\s+(\S+)', 'NETRC_PASSWORD_REDACTED'),

        # FileZilla XML passwords (Base64 encoded) and users
        (r'<Pass[^>]*>([A-Za-z0-9+/=]{8,})</Pass>', 'FILEZILLA_PASSWORD_REDACTED'),
        (r'<User>([^<]+)</User>', 'FILEZILLA_USER_REDACTED'),

        # Git credentials (protocol://user:pass@host) - username can contain @, password until final @
        (r'https?://([^:]+):([^@\s]+@[^@\s]+)@', 'GIT_CREDENTIALS_REDACTED'),

        # Cloud provider credentials files (.s3cfg, .credentials)
        # Note: \b before access_key/secret_key prevents matching inside longer key names
        (r'(?i)(?:aws_access_key_id|\baccess_key)\s*[=:]\s*([A-Z0-9]{20})', 'AWS_ACCESS_KEY_REDACTED'),
        (r'(?i)(?:aws_secret_access_key|\bsecret_key)\s*[=:]\s*([A-Za-z0-9/+=]{32,64})', 'AWS_SECRET_REDACTED'),

        # Salesforce session tokens
        (r'00D[A-Z0-9]{15}![A-Z0-9._]{32,}', 'SALESFORCE_SESSION_REDACTED'),

        # OAuth tokens in YAML/config files
        (r'(?i)oauth_token\s*:\s*["\']?([a-f0-9]{40})["\']?', 'OAUTH_TOKEN_REDACTED'),

        # IRC/config passwords (short form)
        (r'(?i)(?:IRC_PASS|irc_password)\s*=\s*([^\s]+)', 'IRC_PASSWORD_REDACTED'),

        # Config file password assignment (generic, allows short passwords)
        (r'(?i)_PASS(?:WORD)?\s*=\s*([^\s]{4,})', 'CONFIG_PASSWORD_REDACTED'),

        # Firefox encrypted credentials (logins.json)
        (r'"encrypted(?:Username|Password)"\s*:\s*"(M[DF][oI]EEPgA[A-Za-z0-9+/=]{40,})"', 'FIREFOX_ENCRYPTED_CREDENTIAL_REDACTED'),

        # Rails secret_key_base (secrets.yml) - 128 hex char keys
        (r'(?i)secret_key_base:\s*([a-f0-9]{128})', 'RAILS_SECRET_KEY_BASE_REDACTED'),

        # Django SECRET_KEY (settings.py)
        (r"(?i)SECRET_KEY\s*=\s*['\"]([^'\"]{30,})['\"]", 'DJANGO_SECRET_KEY_REDACTED'),

        # Salesforce credentials in JS/Python code (conn.login pattern)
        (r"(?:conn\.login|sf_login|salesforce.*login)\s*\(\s*['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]", 'SALESFORCE_CREDENTIALS_REDACTED'),

        # JSON credentials (robomongo, config files, Docker) - with optional whitespace
        (r'"(?:auth|userPassword|sshUserPassword|sshPassphrase|password|pass|pwd|secret)"\s*:\s*"([^"]{4,})"', 'JSON_PASSWORD_REDACTED'),

        # PHP variable assignments ($var = 'value';)
        (r'\$(?:dbpasswd|password|pass|pwd|secret)\s*=\s*["\']([^"\']+)["\']', 'PHP_PASSWORD_REDACTED'),

        # FTP/SFTP config files (.ftpconfig, sftp-config.json) - includes passphrase, user, and username
        (r'(?i)"(?:password|pass|passphrase)"\s*:\s*"([^"]+)"', 'FTP_PASSWORD_REDACTED'),
        (r'"(?:user|username)"\s*:\s*"([^"]+)"', 'FTP_USER_REDACTED'),
    ]

    def __init__(self):
        """Initialize v3 redactor with Confucian + Aristotelian features."""
        flags = (re.DOTALL | re.MULTILINE)
        if _regex:
            self.patterns_compiled = [(_regex.compile(p, flags), r) for p, r in self.PATTERNS]
        else:
            self.patterns_compiled = [(re.compile(p, flags), r) for p, r in self.PATTERNS]

    def scan_with_patterns(self, text: str) -> List[Tuple[str, str, int]]:
        """Scan text with all compiled patterns.

        Returns: List of (replacement, match_text, start_position) tuples
        """
        matches = []
        for pattern, replacement in self.patterns_compiled:
            try:
                if _regex and hasattr(pattern, 'finditer'):
                    for match in pattern.finditer(text, timeout=0.02):
                        matches.append((replacement, match.group(0), match.start()))
                else:
                    for match in pattern.finditer(text):
                        matches.append((replacement, match.group(0), match.start()))
            except Exception:
                # Timeout or matching error – skip this pattern for this text
                continue
        return matches

    def predecode_and_rescan(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Enhanced scanning with:
        1. Original text scan (with accurate positions)
        2. High-entropy token detection + Base64/hex decode + rescan (position = -1)
        3. JSON/XML value extraction + rescan (position = -1)

        Returns: List of (replacement, match_text, position) tuples
        Position is -1 for decoded/extracted content where original position is unknown.

        Note: Deduplication moved to scan_file() for location-aware dedup.
        This allows same secret at different locations to be counted separately.
        """
        results = []

        # Scan original text (has accurate positions)
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
                            # Decoded content has unknown position
                            for repl, match_text, pos in self.scan_with_patterns(decoded_text):
                                results.append((repl, match_text, -1))
                    except:
                        pass

            # Try hex decode
            decoded_hex = try_decode_hex(token)
            if decoded_hex:
                try:
                    decoded_text = decoded_hex.decode('utf-8', errors='ignore')
                    if decoded_text:
                        # Decoded content has unknown position
                        for repl, match_text, pos in self.scan_with_patterns(decoded_text):
                            results.append((repl, match_text, -1))
                except:
                    pass

        # Try JSON extraction
        if '{' in text:
            for value in extract_values_from_json(text):
                # Extracted values have unknown position
                for repl, match_text, pos in self.scan_with_patterns(value):
                    results.append((repl, match_text, -1))

        # Try XML extraction
        if '<' in text:
            for value in extract_values_from_xml(text):
                # Extracted values have unknown position
                for repl, match_text, pos in self.scan_with_patterns(value):
                    results.append((repl, match_text, -1))

        return results

    def redact(self, text: str) -> str:
        """Redact secrets from text using v3 enhanced detection."""
        matches = self.predecode_and_rescan(text)

        redacted = text
        for replacement, match_text, position in matches:
            redacted = redacted.replace(match_text, replacement)

        return redacted

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a file and return all detected secrets with metadata.

        Uses location-aware deduplication:
        - Same secret at SAME position (multiple patterns) → keep only first
        - Same secret at DIFFERENT positions → keep all occurrences
        """
        # Binary sniff – skip likely binary files
        try:
            with open(file_path, 'rb') as fb:
                chunk = fb.read(512)
                non_text = sum(1 for b in chunk if b < 32 and b not in (9, 10, 13))
                if len(chunk) and (non_text / len(chunk)) > 0.30:
                    return []
        except Exception:
            return []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return []

        matches = self.predecode_and_rescan(content)

        secrets = []
        for replacement, match_text, position in matches:
            # Calculate line number from position
            if position >= 0:
                # Accurate position from regex match
                line_num = content[:position].count('\n') + 1
            else:
                # Position unknown (decoded content) - use find() as fallback
                line_num = content[:content.find(match_text)].count('\n') + 1 if match_text in content else -1

            # Relationship analysis
            rels = []
            rel_score = 0.0
            try:
                pos_for_rel = position if position >= 0 else (content.find(match_text) if match_text in content else -1)
                if pos_for_rel >= 0:
                    rels = find_secret_relationships(match_text, content, pos_for_rel)
                    rel_score = confucian_relationship_score(rels)
            except Exception:
                pass

            # Classification: component vs usable (based on pattern label)
            def _is_component(pattern_label: str) -> bool:
                components = {
                    'AWS_KEY_REDACTED',      # Access Key ID (needs secret key)
                    'FTP_USER_REDACTED',
                    'FILEZILLA_USER_REDACTED',
                    'SALESFORCE_ORG_ID_REDACTED',
                }
                return pattern_label in components

            classification = 'component' if _is_component(replacement) else 'usable'

            secrets.append({
                'file': str(file_path),
                'pattern': replacement,
                'match': match_text[:50] + '...' if len(match_text) > 50 else match_text,
                'line': line_num,
                'position': position,
                'relationship_score': round(rel_score, 3),
                'relationships': [r[0] for r in rels] if rels else [],
                'classification': classification,
            })

        # Location-aware deduplication: deduplicate by (match_text, position)
        # This keeps same secret at different positions but removes duplicate patterns at same position
        seen = set()
        deduplicated = []
        for secret in secrets:
            key = (secret['match'], secret['position'])
            if key not in seen:
                seen.add(key)
                deduplicated.append(secret)

        return deduplicated


# ============================================================================
# EXAMPLE USAGE & TESTS
# ============================================================================

def _sha256_file(path: Path) -> str:
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ''


def _git_commit_for(path: Path) -> str:
    try:
        # Use git from the directory if possible
        proc = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return ''


if __name__ == "__main__":
    # Minimal CLI: --scan <path> [--json out.json] [--out summary.txt] [--demo]
    import argparse, json, sys
    from pathlib import Path as _Path

    _parser = argparse.ArgumentParser(description="IF.yologuard v3 - Secret detector")
    _parser.add_argument('--scan', help='File or directory to scan')
    _parser.add_argument('--json', dest='json_out', help='Write detections to JSON file')
    _parser.add_argument('--out', dest='text_out', help='Write a text summary to file')
    _parser.add_argument('--sarif', dest='sarif_out', help='Write detections to SARIF v2.1.0 file')
    _parser.add_argument('--manifest', dest='manifest_out', help='Write TTT manifest JSON to file')
    _parser.add_argument('--forensics', action='store_true', help='Enable Immuno‑Epistemic Forensics (IEF) assays and graph output')
    _parser.add_argument('--graph-out', dest='graph_out', help='Write Indra graph JSON to file (implies --forensics)')
    _parser.add_argument('--memory-state', dest='memory_state', default='code/yologuard/state/memory.json', help='Path to adaptive memory state file')
    _parser.add_argument('--reset-memory', action='store_true', help='Reset adaptive memory state before run')
    _parser.add_argument('--pq-report', dest='pq_report', help='Write Quantum Readiness (QES) report JSON to file')
    _parser.add_argument('--sbom', dest='sbom_path', help='Path to CycloneDX SBOM or lockfile directory (optional)')
    # (added below to avoid duplication)
    _parser.add_argument('--error-threshold', type=float, default=DEFAULT_ERROR_THRESHOLD, help=f'Relationship score threshold for ERROR (default: {DEFAULT_ERROR_THRESHOLD})')
    _parser.add_argument('--warn-threshold', type=float, default=DEFAULT_WARN_THRESHOLD, help=f'Relationship score threshold for WARNING (default: {DEFAULT_WARN_THRESHOLD})')
    _parser.add_argument('--mode', choices=['usable','component','both'], default='both', help='Filter by detection type (default: both)')
    _parser.add_argument('--stats', action='store_true', help='Print compact stats (files, detections, usable/components)')
    _parser.add_argument('--max-file-bytes', type=int, default=DEFAULT_MAX_FILE_BYTES, help=f'Skip files larger than this size (default: {DEFAULT_MAX_FILE_BYTES} bytes)')
    _parser.add_argument('--profile', choices=['ci','ops','audit','research','forensics'], help='Preset profile for thresholds/mode (ci, ops, audit, research, forensics)')
    _parser.add_argument('--simple-output', action='store_true', help='Print beginner-friendly per-detection lines')
    _parser.add_argument('--format', dest='out_format', choices=['default','json-simple'], default='default', help='Choose JSON output format when using --json (default or json-simple)')
    _parser.add_argument('--demo', action='store_true', help='Run built-in relationship demo')
    _args, _unknown = _parser.parse_known_args()

    if _args.scan and not _args.demo:
        _base = _Path(_args.scan)
        if not _base.exists():
            print(f"ERROR: path not found: {_base}")
            sys.exit(1)

        # Apply profile presets (can be overridden by explicit flags)
        if _args.profile:
            if _args.profile == 'ci':
                # Low-noise PR gating: usable-only, conservative thresholds, 5MB cap
                _args.mode = 'usable'
                if _args.error_threshold == DEFAULT_ERROR_THRESHOLD:
                    _args.error_threshold = DEFAULT_ERROR_THRESHOLD
                if _args.warn_threshold == DEFAULT_WARN_THRESHOLD:
                    _args.warn_threshold = DEFAULT_WARN_THRESHOLD
                if _args.max_file_bytes == DEFAULT_MAX_FILE_BYTES:
                    _args.max_file_bytes = DEFAULT_MAX_FILE_BYTES
            elif _args.profile == 'ops':
                # Security operations: include components, balanced thresholds
                _args.mode = 'both' if _args.mode == 'both' else _args.mode
                if _args.error_threshold == DEFAULT_ERROR_THRESHOLD:
                    _args.error_threshold = DEFAULT_ERROR_THRESHOLD
                if _args.warn_threshold == DEFAULT_WARN_THRESHOLD:
                    _args.warn_threshold = DEFAULT_WARN_THRESHOLD
                _args.max_file_bytes = max(_args.max_file_bytes, 10_000_000)
            elif _args.profile == 'audit':
                # Broad audit: include components, lower warn bar, larger files
                _args.mode = 'both'
                if _args.error_threshold == DEFAULT_ERROR_THRESHOLD:
                    _args.error_threshold = AUDIT_ERROR_THRESHOLD
                if _args.warn_threshold == DEFAULT_WARN_THRESHOLD:
                    _args.warn_threshold = AUDIT_WARN_THRESHOLD
                _args.max_file_bytes = max(_args.max_file_bytes, 20_000_000)
            elif _args.profile == 'research':
                # Maximum sensitivity for research sweeps
                _args.mode = 'both'
                if _args.error_threshold == DEFAULT_ERROR_THRESHOLD:
                    _args.error_threshold = RESEARCH_ERROR_THRESHOLD
                if _args.warn_threshold == DEFAULT_WARN_THRESHOLD:
                    _args.warn_threshold = RESEARCH_WARN_THRESHOLD
                _args.max_file_bytes = max(_args.max_file_bytes, 100_000_000)
            elif _args.profile == 'forensics':
                # Forensics profile: enable assays/graph, broad mode, lower thresholds
                _args.forensics = True
                _args.mode = 'both'
                if _args.error_threshold == DEFAULT_ERROR_THRESHOLD:
                    _args.error_threshold = FORENSICS_ERROR_THRESHOLD
                if _args.warn_threshold == DEFAULT_WARN_THRESHOLD:
                    _args.warn_threshold = FORENSICS_WARN_THRESHOLD
                _args.max_file_bytes = max(_args.max_file_bytes, 50_000_000)

        detector = SecretRedactorV3()
        # Simple binary filter + exclude internal meta dirs
        _binary_ext = {
            '.db', '.sqlite', '.sqlite3', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.pyc', '.pyo'
        }
        _exclude_dirs = {'.git', '.leaky-meta'}

        if _base.is_dir():
            _files = [
                p for p in _base.rglob('*')
                if p.is_file() and not any(ed in p.parts for ed in _exclude_dirs) and p.suffix.lower() not in _binary_ext
            ]
        else:
            _files = [_base]

        _results = []
        _count = 0
        _skipped_large = 0
        _file_sha_cache = {}
        # Use timezone-aware UTC to avoid deprecation and standardize to Z suffix
        _now_iso = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
        # Try to capture a repo commit for provenance (best-effort)
        _repo_commit = _git_commit_for(_base if _base.is_dir() else _base.parent)

        # Indra graph structures (nodes/edges)
        graph_nodes = []
        graph_edges = []

        # Simple adaptive memory
        _mem_path = Path(_args.memory_state)
        if _args.reset_memory and _mem_path.exists():
            try:
                _mem_path.unlink()
            except Exception:
                pass
        try:
            _mem_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        try:
            _memory = json.loads(_mem_path.read_text()) if _mem_path.exists() else {}
        except Exception:
            _memory = {}

        # PQ readiness accumulators
        pq_repo = {
            'classicalUse': {
                'rsa': 0, 'ecdsa': 0, 'ecdh': 0, 'x25519': 0, 'aes128': 0, 'sha1md5': 0, 'tls12': 0
            },
            'pqUse': {
                'kyber': 0, 'dilithium': 0, 'falcon': 0, 'liboqs': 0
            },
            'sbomFindings': [],
            'exposureScores': [],
        }

        def _analyze_pq_text(txt: str) -> dict:
            txt_l = txt.lower()
            found = {
                'algorithms': [],
                'keySize': None,
                'protocols': [],
            }
            # Classical
            if 'rsa' in txt_l:
                found['algorithms'].append('RSA')
            if 'ecdsa' in txt_l:
                found['algorithms'].append('ECDSA')
            if 'ecdh' in txt_l or 'x25519' in txt_l:
                if 'ecdh' in txt_l: found['algorithms'].append('ECDH')
                if 'x25519' in txt_l: found['algorithms'].append('X25519')
            if 'aes-128' in txt_l or 'aes128' in txt_l:
                found['algorithms'].append('AES-128')
            if 'sha1' in txt_l or 'md5' in txt_l:
                found['algorithms'].append('SHA1/MD5')
            if 'tls1.2' in txt_l or 'tls 1.2' in txt_l:
                found['protocols'].append('TLS1.2')
            # PQ
            for pq in ('kyber','dilithium','falcon','liboqs','oqs'):
                if pq in txt_l:
                    found['algorithms'].append(pq.upper())
            # Key sizes
            m = re.search(r'\b(2048|1024|4096)\b', txt)
            if m:
                found['keySize'] = int(m.group(1))
            return found

        def _compute_qes(cls: str, rels: list, pqf: dict, file_path: str) -> dict:
            score = 0
            drivers = []
            algs = [a.upper() for a in pqf.get('algorithms', [])]
            if any(a in algs for a in ('RSA','ECDSA','ECDH','X25519')):
                score += 30; drivers.append('classical_public_key')
            if 'AES-128' in algs:
                score += 10; drivers.append('aes128')
            if 'SHA1/MD5' in algs:
                score += 15; drivers.append('sha1_md5')
            if cls == 'usable':
                score += 10; drivers.append('usable_secret')
            if any(r in ('key-endpoint','user-password','token-session') for r in rels or []):
                score += 10; drivers.append('relation_context')
            if re.search(r'backup|archive|export|dump', file_path, re.IGNORECASE):
                score += 10; drivers.append('long_lived_data_hint')
            # PQ presence dampens risk
            if any(a in algs for a in ('KYBER','DILITHIUM','FALCON','LIBOQS','OQS')):
                score = max(0, score - 15); drivers.append('pq_present')
            return {'score': min(100, score), 'drivers': drivers}

        # SBOM/lockfile scan (best-effort)
        sbom_meta = {}
        if _args.sbom_path:
            sp = Path(_args.sbom_path)
            try:
                if sp.is_file() and sp.suffix.lower() in ('.json', '.cdx'):
                    data = _jsonmod.loads(sp.read_text())
                    comps = data.get('components') or []
                    for c in comps:
                        name = (c.get('name') or '').lower()
                        ver = c.get('version') or ''
                        if any(k in name for k in ('openssl','bouncycastle','crypto','liboqs','oqs')):
                            pq_repo['sbomFindings'].append({'name': name, 'version': ver})
                            if 'oqs' in name:
                                pq_repo['pqUse']['liboqs'] += 1
                elif sp.is_dir():
                    # look for package manifests
                    for lf in sp.rglob('*'):
                        if lf.name in ('package.json','poetry.lock','Pipfile.lock','pom.xml','build.gradle','go.mod','go.sum','Cargo.toml','Cargo.lock'):
                            txt = lf.read_text(encoding='utf-8', errors='ignore').lower()
                            if any(k in txt for k in ('liboqs','oqs','openquantum','pqclean')):
                                pq_repo['sbomFindings'].append({'name': lf.name, 'hint': 'pq_libs_present'})
                                pq_repo['pqUse']['liboqs'] += 1
            except Exception:
                pass
        for _fp in _files:
            try:
                # Skip large files
                try:
                    if _fp.stat().st_size > _args.max_file_bytes:
                        _skipped_large += 1
                        continue
                except Exception:
                    pass
                _dets = detector.scan_file(_fp)
            except Exception:
                _dets = []
            if _dets:
                for _d in _dets:
                    cls = _d.get('classification', 'usable')
                    if _args.mode == 'usable' and cls != 'usable':
                        continue
                    if _args.mode == 'component' and cls != 'component':
                        continue

                    rel_score = float(_d.get('relationship_score') or 0.0)
                    always_error = {
                        'PRIVATE_KEY_REDACTED', 'OPENSSH_PRIVATE_REDACTED', 'PASSWORD_REDACTED',
                        'JSON_PASSWORD_REDACTED', 'PHP_PASSWORD_REDACTED', 'AWS_SECRET_REDACTED',
                        'JWT_REDACTED', 'GITHUB_PAT_REDACTED', 'NPM_TOKEN_REDACTED',
                    }
                    pat = _d.get('pattern','')
                    if pat in always_error:
                        sev = 'error'
                    elif rel_score >= _args.error_threshold and cls == 'usable':
                        sev = 'error'
                    elif rel_score >= _args.warn_threshold:
                        sev = 'warning'
                    else:
                        sev = 'note'

                    # Danger signals (heuristic)
                    danger = []
                    try:
                        txt = _fp.read_text(encoding='utf-8', errors='ignore')
                        if re.search(r'[A-Za-z0-9+/]{120,}={0,2}', txt):
                            danger.append('encoded_blob_in_text')
                        if re.search(r'(?i)canary|honey(token)?', txt):
                            danger.append('honeypot_marker')
                    except Exception:
                        pass

                    # Structure checks (JWT/PEM) – no exfiltration
                    structure = {}
                    try:
                        if 'JWT' in pat or re.search(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.', _d.get('match','')):
                            parts = _d.get('match','').split('.')
                            if len(parts) >= 2:
                                import base64, json as _json
                                def b64d(s):
                                    s = s + '='*((4-len(s)%4)%4)
                                    return base64.urlsafe_b64decode(s.encode('utf-8'))
                                try:
                                    h = _json.loads(b64d(parts[0]).decode('utf-8','ignore'))
                                    p = _json.loads(b64d(parts[1]).decode('utf-8','ignore'))
                                    structure['jwt_struct_valid'] = True
                                except Exception:
                                    structure['jwt_struct_valid'] = False
                        if 'PRIVATE_KEY' in pat or 'OPENSSH' in pat or 'PEM' in _d.get('match',''):
                            if re.search(r'-----BEGIN[^-]+-----[\s\S]+-----END[^-]+-----', _d.get('match','')):
                                structure['pem_block'] = True
                    except Exception:
                        pass

                    # Two‑source rule – simple: pattern+relations or pattern+danger
                    sources = []
                    if pat:
                        sources.append('pattern')
                    if _d.get('relationships'):
                        sources.append('relations')
                    if danger:
                        sources.append('danger')
                    two_source = len(set(sources)) >= 2

                    # Traceability (TTT): per-file hash and rationale
                    _fpath = _fp if _base.is_dir() else _fp
                    if _fpath not in _file_sha_cache:
                        _file_sha_cache[_fpath] = _sha256_file(_fpath)
                    rationale = [
                        f"pattern:{pat}",
                        f"classification:{cls}",
                        f"relations:{','.join(_d.get('relationships', []))}",
                        f"relation_score:{rel_score}",
                        f"always_error:{pat in always_error}",
                        f"thresholds:error={_args.error_threshold},warn={_args.warn_threshold}",
                        f"two_source:{two_source}",
                    ]

                    _results.append({
                        'file': str(_fp.relative_to(_base)) if _base.is_dir() else str(_fp),
                        'line': _d.get('line', -1),
                        'pattern': pat,
                        'match': _d.get('match', ''),
                        'severity': sev.upper(),
                        'relationshipScore': round(rel_score,3),
                        'relations': _d.get('relationships', []),
                        'classification': cls,
                        'dangerSignals': danger,
                        'structureChecks': structure,
                        'pqRisk': None,  # populated below
                        'apcPacket': {
                            'provenance': {
                                'repoCommit': _repo_commit,
                                'fileSha256': _file_sha_cache[_fpath],
                                'scanTimestamp': _now_iso,
                            },
                            'relations': _d.get('relationships', []),
                            'dangerSignals': danger,
                        },
                        'provenance': {
                            'repoCommit': _repo_commit,
                            'fileSha256': _file_sha_cache[_fpath],
                            'scanTimestamp': _now_iso,
                        },
                        'rationale': rationale,
                    })
                    _count += 1

                    # PQ analysis on file text (best-effort)
                    try:
                        txt = _fp.read_text(encoding='utf-8', errors='ignore')
                        pqf = _analyze_pq_text(txt)
                        if pqf.get('algorithms'):
                            # accumulate repo counters
                            for a in pqf['algorithms']:
                                al = a.lower()
                                if al in ('rsa','ecdsa','ecdh','x25519'):
                                    pq_repo['classicalUse'][al] += 1
                                if al in ('aes-128','sha1/md5','tls1.2'):
                                    # map to counters
                                    if al == 'aes-128': pq_repo['classicalUse']['aes128'] += 1
                                    if al == 'sha1/md5': pq_repo['classicalUse']['sha1md5'] += 1
                                    if al == 'tls1.2': pq_repo['classicalUse']['tls12'] += 1
                                if al in ('kyber','dilithium','falcon','liboqs','oqs'):
                                    key = 'liboqs' if al in ('liboqs','oqs') else al
                                    pq_repo['pqUse'][key] += 1
                            qes = _compute_qes(cls, _d.get('relationships', []), pqf, str(_fp))
                            _results[-1]['pqRisk'] = { **pqf, 'qes': qes }
                            pq_repo['exposureScores'].append(qes['score'])
                    except Exception:
                        pass

                    # Indra graph nodes/edges
                    if _args.forensics or _args.graph_out:
                        det_id = f"{_fp}:{_d.get('line',-1)}:{pat}"
                        graph_nodes.append({'id': det_id, 'type': 'antigen', 'file': str(_fp), 'pattern': pat, 'severity': sev.upper()})
                        graph_nodes.append({'id': str(_fp), 'type': 'file'})
                        graph_edges.append({'source': str(_fp), 'target': det_id, 'type': 'contains'})
                        for r in _d.get('relationships', []):
                            graph_edges.append({'source': det_id, 'target': r, 'type': 'relation'})
                        for dg in danger:
                            graph_edges.append({'source': det_id, 'target': dg, 'type': 'danger'})

        print("="*80)
        print("IF.yologuard v3.0 - SCAN SUMMARY")
        print("="*80)
        print(f"Files scanned: {len(_files)}")
        print(f"Detections:   {_count}")
        if _results:
            _usable = sum(1 for r in _results if r.get('classification') == 'usable')
            _components = sum(1 for r in _results if r.get('classification') == 'component')
            print(f"  • Usable credentials:   {_usable}")
            print(f"  • Credential components: {_components}")
        if _skipped_large:
            print(f"  • Skipped large files:  {_skipped_large} (> {_args.max_file_bytes} bytes)")

        if _args.stats:
            _usable = sum(1 for r in _results if r.get('classification') == 'usable')
            _components = sum(1 for r in _results if r.get('classification') == 'component')
            print(f"stats: files={len(_files)} detections={_count} usable={_usable} components={_components}")

        # Simple output lines for beginners
        if _args.simple_output and _results:
            for _r in _results:
                _f = _r.get('file','?')
                _ln = _r.get('line', -1)
                _sev = _r.get('severity','NOTE')
                _pat = _r.get('pattern','')
                print(f"simple: {_f}:{_ln} [{_sev}] {_pat}")

        # Optional outputs
        if _args.text_out:
            try:
                with open(_args.text_out, 'w') as _f:
                    for _r in _results:
                        _f.write(f"{_r['file']}:{_r['line']} [{_r['severity']}] {_r['classification']} {_r['pattern']} {_r['match']}\n")
                print(f"Wrote summary: {_args.text_out}")
            except Exception as _e:
                print(f"WARN: failed writing summary: {_e}")

        if _args.json_out:
            try:
                with open(_args.json_out, 'w') as _jf:
                    if _args.out_format == 'json-simple':
                        _simple = []
                        for _r in _results:
                            _simple.append({
                                'file': _r.get('file'),
                                'line': _r.get('line'),
                                'pattern': _r.get('pattern'),
                                'severity': _r.get('severity'),
                            })
                        json.dump(_simple, _jf, indent=2)
                    else:
                        json.dump(_results, _jf, indent=2)
                print(f"Wrote JSON:    {_args.json_out}")
            except Exception as _e:
                print(f"WARN: failed writing JSON: {_e}")

        # SARIF output
        if _args.sarif_out:
            try:
                def _to_sarif(detections):
                    tool = {
                        "driver": {
                            "name": "IF.yologuard",
                            "version": "3.0",
                            "informationUri": "https://github.com/dannystocker/infrafabric",
                            "rules": [
                                {
                                    "id": "IF.YOLOGUARD.SECRET",
                                    "name": "Secret Detected",
                                    "shortDescription": {"text": "Potential secret or credential detected"},
                                    "fullDescription": {"text": "IF.yologuard detected a potential secret/credential"},
                                    "defaultConfiguration": {"level": "error"},
                                    "properties": {"tags": ["security", "secret", "credential"]}
                                }
                            ]
                        }
                    }
                    results = []
                    for d in detections:
                        file_uri = str(d.get('file', '')).replace('\\', '/')
                        line = int(d.get('line') or 1)
                        msg = f"{d.get('pattern','')}: {d.get('match','')}"
                        lvl = (d.get('severity') or 'ERROR').lower()
                        if lvl not in ('error','warning','note'):
                            lvl = 'error'
                        results.append({
                            "ruleId": "IF.YOLOGUARD.SECRET",
                            "level": lvl,
                            "message": {"text": msg},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": file_uri},
                                        "region": {"startLine": line if line > 0 else 1}
                                    }
                                }
                            ],
                            "properties": {
                                "pattern": d.get('pattern',''),
                                "relationshipScore": d.get('relationshipScore', 0.0),
                                "relations": d.get('relations', []),
                                "classification": d.get('classification',''),
                                "provenance": d.get('provenance', {}),
                                "rationale": d.get('rationale', []),
                                "pqRisk": d.get('pqRisk', {}),
                            }
                        })
                    return {
                        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
                        "version": "2.1.0",
                        "runs": [
                            {
                                "tool": tool,
                                "results": results
                            }
                        ]
                    }
                with open(_args.sarif_out, 'w') as _sf:
                    json.dump(_to_sarif(_results), _sf, indent=2)
                print(f"Wrote SARIF:   {_args.sarif_out}")
            except Exception as _e:
                print(f"WARN: failed writing SARIF: {_e}")

        # Write Indra graph
        if (_args.forensics or _args.graph_out) and (_args.graph_out):
            try:
                with open(_args.graph_out, 'w') as gf:
                    json.dump({'nodes': graph_nodes, 'edges': graph_edges}, gf, indent=2)
                print(f"Wrote graph:   {_args.graph_out}")
            except Exception as _e:
                print(f"WARN: failed writing graph: {_e}")

        # Manifest (TTT) output
        if _args.manifest_out:
            try:
                # Best-effort import of manifest tool
                try:
                    import sys as _sys
                    _root = Path(__file__).resolve().parents[4]
                    _sys.path.insert(0, str(_root))
                    from infrafabric.manifests import create_manifest
                except Exception:
                    create_manifest = None
                summary = {
                    'files_scanned': len(_files),
                    'detections': _count,
                    'usable': sum(1 for r in _results if r.get('classification') == 'usable'),
                    'components': sum(1 for r in _results if r.get('classification') == 'component'),
                    'skipped_large': _skipped_large,
                    'quantum': {
                        'classicalUse': pq_repo['classicalUse'],
                        'pqUse': pq_repo['pqUse'],
                        'avgExposureScore': (sum(pq_repo['exposureScores'])/len(pq_repo['exposureScores'])) if pq_repo['exposureScores'] else 0.0,
                    }
                }
                cfg = {
                    'mode': _args.mode,
                    'profile': _args.profile,
                    'error_threshold': _args.error_threshold,
                    'warn_threshold': _args.warn_threshold,
                    'max_file_bytes': _args.max_file_bytes,
                }
                if create_manifest:
                    m = create_manifest(config=cfg, inputs={'scan': str(_base)}, results=summary)
                    m.add_philosophical_insight('TTT: Traceability-Trust-Transparency manifest recorded')
                    m.save(_args.manifest_out)
                else:
                    with open(_args.manifest_out, 'w') as _mf:
                        json.dump({'config': cfg, 'inputs': {'scan': str(_base)}, 'results': summary}, _mf, indent=2)
                print(f"Wrote manifest: {_args.manifest_out}")
            except Exception as _e:
                print(f"WARN: failed writing manifest: {_e}")

        # PQ report output
        if _args.pq_report:
            try:
                with open(_args.pq_report,'w') as pqf:
                    _jsonmod.dump({
                        'classicalUse': pq_repo['classicalUse'],
                        'pqUse': pq_repo['pqUse'],
                        'sbomFindings': pq_repo['sbomFindings'],
                        'exposureScores': pq_repo['exposureScores'],
                        'avgExposureScore': (sum(pq_repo['exposureScores'])/len(pq_repo['exposureScores'])) if pq_repo['exposureScores'] else 0.0,
                    }, pqf, indent=2)
                print(f"Wrote PQ report: {_args.pq_report}")
            except Exception as _e:
                print(f"WARN: failed writing PQ report: {_e}")

        sys.exit(0)

    # Default: fall back to built-in demo
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
   - Implemented: sibling config keys (e.g., user/password, key/secret, endpoint/token)

KEY INSIGHT:
A token's meaning emerges from its relationships, not from pattern matching alone.
Isolated tokens are noise; tokens in relationship are secrets.
    """)
