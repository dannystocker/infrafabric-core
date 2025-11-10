# ANNEX A: Technical Specification - IF.yologuard v3

**Purpose:** Complete technical details enabling independent implementation and verification

---

## 1. Complete Pattern Library (58 Patterns)

### 1.1 Password Hashes (12 patterns)

```python
# Bcrypt (2a, 2b, 2y variants)
pattern_bcrypt = r'\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}'
# Example: $2a$12$R9h/cIPz0gi.URNN...
# Strength: Very high (Bcrypt-specific format)

# MD5 Hash (128-bit)
pattern_md5 = r'\b[a-fA-F0-9]{32}\b'
# Example: 5d41402abc4b2a76b9719d911017c592
# Strength: Medium (many false positives, used with context)

# SHA1 Hash (160-bit)
pattern_sha1 = r'\b[a-fA-F0-9]{40}\b'
# Example: 356a192b7913b04c54574d18c28d46e6395428ab
# Strength: Medium (many false positives, requires context)

# SHA256 Hash (256-bit)
pattern_sha256 = r'\b[a-fA-F0-9]{64}\b'
# Example: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
# Strength: High (longer, fewer false positives)

# WordPress Salts (8 random strings)
pattern_wordpress_salt = r"define\s*\(\s*'([A-Z_]+_SALT)'\s*,\s*'[^']{32,}'\s*\)"
# Strength: Very high (WordPress-specific syntax)

# AWS RDS Master Password patterns
pattern_aws_rds_password = r'MasterUserPassword\s*[=:]\s*["\']([^"\']{12,})["\']'
# Strength: High (AWS-specific context)

# Docker auth token
pattern_docker_auth = r'auth["\']?\s*[=:]\s*["\']([A-Za-z0-9+/]{32,})["\']'

# Firebase API Key in config
pattern_firebase_key = r'apiKey\s*["\']?\s*[=:]\s*["\']([A-Za-z0-9_-]{32,})["\']'

# Generic password in key-value config
pattern_generic_password = r'password\s*["\']?\s*[=:]\s*["\']([^\s"\']{8,})["\']'
# Requires relationship validation to avoid false positives

# Certificate password
pattern_cert_password = r'CERT_PASS\s*[=:]\s*["\']([^"\']{8,})["\']'

# API secret patterns
pattern_api_secret_generic = r'(secret|api_secret|secret_key)\s*["\']?\s*[=:]\s*["\']([A-Za-z0-9_-]{20,})["\']'
```

### 1.2 API Keys (14 patterns)

```python
# AWS Access Key (AKIA prefix, 20 chars)
pattern_aws_access_key = r'AKIA[0-9A-Z]{16}'
# Strength: Very high (AWS-specific prefix)

# AWS Secret Access Key
pattern_aws_secret_key = r'aws_secret_access_key\s*=\s*["\']?([A-Za-z0-9/+=]{40})["\']?'
# Strength: High (AWS documentation standard)

# GitHub Personal Access Token
pattern_github_pat = r'ghp_[A-Za-z0-9_]{36}'
# Strength: Very high (GitHub-specific format)

# GitHub OAuth token
pattern_github_oauth = r'gho_[A-Za-z0-9_]{36}'
# Strength: Very high

# SendGrid API Key
pattern_sendgrid_key = r'SG\.[A-Za-z0-9_-]{60,}'
# Strength: Very high (SendGrid prefix)

# Slack Bot Token
pattern_slack_bot = r'xoxb-[0-9]+-[0-9]+-[A-Za-z0-9_-]{32}'
# Strength: Very high (Slack-specific format)

# Slack User Token
pattern_slack_user = r'xoxp-[0-9]+-[0-9]+-[0-9]+-[A-Za-z0-9_]+'
# Strength: Very high

# Slack Webhook URL
pattern_slack_webhook = r'https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9_-]{20,}'
# Strength: Very high

# Mailgun API Key
pattern_mailgun_key = r'key-[a-z0-9]{32}'
# Strength: Very high

# Stripe Secret Key
pattern_stripe_secret = r'sk_live_[A-Za-z0-9]{20,}'
# Strength: Very high

# Stripe Publishable Key
pattern_stripe_pub = r'pk_live_[A-Za-z0-9]{20,}'
# Strength: High (less sensitive than secret)

# Google API Key
pattern_google_api_key = r'AIza[0-9A-Za-z\-_]{35}'
# Strength: Very high

# Heroku API Key
pattern_heroku_api = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
# Strength: Medium (UUID format, requires context)

# Generic Bearer token
pattern_bearer_token = r'bearer\s+[A-Za-z0-9_-]{32,}'
# Strength: Medium (requires relationship validation)
```

### 1.3 Authentication Tokens (8 patterns)

```python
# JWT Token (eyJ... format with 3 parts)
pattern_jwt = r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.([A-Za-z0-9_-]+)?'
# Strength: High (JWT-specific format)

# OAuth2 access token
pattern_oauth2_access = r'oauth_token["\']?\s*[=:]\s*["\']([A-Za-z0-9_-]{32,})["\']'

# Session token (generic)
pattern_session_token = r'session[_id]*["\']?\s*[=:]\s*["\']([A-Za-z0-9]{32,})["\']'

# Authorization header
pattern_auth_header = r'Authorization\s*:\s*(Bearer|Basic|Digest)\s+([A-Za-z0-9_.+=\-/]+)'

# API token in header
pattern_api_token_header = r'X-API-Key\s*:\s*([A-Za-z0-9_-]{32,})'

# Firebase ID Token
pattern_firebase_id_token = r'firebase[_-]id[_-]token["\']?\s*:\s*["\']([A-Za-z0-9._-]+)["\']'

# CSRF Token
pattern_csrf_token = r'csrf[_-]?token["\']?\s*[=:]\s*["\']([A-Za-z0-9]{32,})["\']'

# Refresh Token
pattern_refresh_token = r'refresh[_-]?token["\']?\s*[=:]\s*["\']([A-Za-z0-9_-]{20,})["\']'
```

### 1.4 Certificates & Keys (7 patterns)

```python
# RSA Private Key (PEM format, 1024-2048 bit typical)
pattern_rsa_private_key = r'-----BEGIN RSA PRIVATE KEY-----[\s\S]+-----END RSA PRIVATE KEY-----'
# Strength: Very high (explicit PEM markers)

# EC Private Key (Elliptic Curve)
pattern_ec_private_key = r'-----BEGIN EC PRIVATE KEY-----[\s\S]+-----END EC PRIVATE KEY-----'
# Strength: Very high

# DSA Private Key
pattern_dsa_private_key = r'-----BEGIN DSA PRIVATE KEY-----[\s\S]+-----END DSA PRIVATE KEY-----'
# Strength: Very high

# OpenSSH Private Key
pattern_openssh_private = r'-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+-----END OPENSSH PRIVATE KEY-----'
# Strength: Very high

# PGP Private Key Block
pattern_pgp_private = r'-----BEGIN PGP PRIVATE KEY BLOCK-----[\s\S]+-----END PGP PRIVATE KEY BLOCK-----'
# Strength: Very high

# AWS PEM Certificate
pattern_aws_pem_cert = r'-----BEGIN CERTIFICATE-----[\s\S]+-----END CERTIFICATE-----'
# Strength: High (requires context to distinguish public certificates)

# PKCS#12 Certificate (Binary, Base64 encoded)
pattern_pkcs12_cert = r'-----BEGIN PKCS12-----[\s\S]+-----END PKCS12-----'
# Strength: Very high
```

### 1.5 Database Credentials (10 patterns)

```python
# MySQL connection string
pattern_mysql_conn = r'mysql://([a-zA-Z0-9_]+):[^@]+@[^\s/]+/[^\s]*'
# Strength: High (includes password in URL)

# PostgreSQL connection string
pattern_postgres_conn = r'postgres(?:ql)?://([a-zA-Z0-9_]+):[^@]+@[^\s/]+/[^\s]*'
# Strength: High

# MongoDB URI
pattern_mongodb_uri = r'mongodb://([a-zA-Z0-9_]+):[^@]+@[^\s/]+/[^\s]*'
# Strength: High

# Oracle connection string
pattern_oracle_conn = r'(Data Source|SERVER)\s*=\s*[^\s;]+.*?(User ID|UID|Uid)\s*=\s*[^\s;]+.*?(Password|PWD|Pwd)\s*=\s*[^\s;]+'
# Strength: High (connection string format)

# SQL Server connection string
pattern_sqlserver_conn = r'Server\s*=\s*[^\s;]+.*?(User ID|UID)\s*=\s*[^\s;]+.*?(Password|PWD)\s*=\s*[^\s;]+'
# Strength: High

# Redis connection with password
pattern_redis_conn = r'redis://:[^\@]+\@[^\s/]+(?::[\d]+)?'
# Strength: High

# pgpass file entry (PostgreSQL)
pattern_pgpass = r'^[^\s:]+:[^:]+:[^:]+:[^\s:]+:[^\s]+'
# Strength: Very high (pgpass format)

# Database password in ENV variable
pattern_db_password_env = r'DB_PASSWORD\s*=\s*["\']?([^"\'\s]+)["\']?'
# Strength: Medium (requires context)

# JDBC connection string
pattern_jdbc_conn = r'jdbc:[a-z]+://[a-zA-Z0-9_]+:[^@]+@[^\s/]+:[^/\s]+/[^\s]*'
# Strength: High

# Generic database configuration
pattern_db_config_generic = r'database[_-]?(password|passwd|pwd)\s*[=:]\s*["\']?([^\s"\']+)["\']?'
# Strength: Medium (requires relationship validation)
```

### 1.6 SSH & Cloud Keys (7 patterns)

```python
# SSH Public Key (OpenSSH format, ssh-rsa prefix)
pattern_ssh_public_key = r'ssh-(?:rsa|dss|ecdsa|ed25519)\s+[A-Za-z0-9/+]+(?:==)?(?:\s+.+)?'
# Strength: Medium (public key, not secret, but useful context)

# SSH Config Identity (private key reference)
pattern_ssh_identity_file = r'IdentityFile\s+~?/?\.ssh/([^\s/]+)'
# Strength: Low (references key, not the key itself)

# Azure Storage Connection String
pattern_azure_storage = r'DefaultEndpointsProtocol=https?;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]+;'
# Strength: Very high (Azure-specific format)

# Azure Key Vault Secret
pattern_azure_keyvault = r'https://[a-z0-9-]+\.vault\.azure\.net/secrets/[^/\s]+'
# Strength: High (URL format)

# GCP Service Account Key (JSON embedded)
pattern_gcp_service_key = r'"private_key":\s*"-----BEGIN PRIVATE KEY-----[^"]+-----END PRIVATE KEY-----\\n"'
# Strength: Very high

# AWS Credentials in config/profile
pattern_aws_credentials = r'aws_access_key_id\s*=\s*AKIA[0-9A-Z]{16}'
# Strength: Very high

# Google OAuth Client Secret
pattern_google_oauth_secret = r'"client_secret":\s*"([A-Za-z0-9_-]{24})"'
# Strength: Very high (OAuth-specific format)
```

## 2. Entropy Detection Algorithm

### 2.1 Shannon Entropy Calculation

```python
def shannon_entropy(data: bytes) -> float:
    """
    Calculate Shannon entropy in bits per byte.

    H(X) = -Σ p(x) * log₂(p(x))

    where:
    - p(x) = frequency of byte value x
    - H(X) = information entropy (0-8 bits/byte range)

    Interpretation:
    - 0.0: All bytes identical (entropy = 0)
    - 4.7: English text (entropy ≈ 4.7)
    - 6.5: Base64-encoded data (entropy ≈ 6.5)
    - 8.0: Random/cryptographic data (entropy = 8.0)

    Threshold: H > 4.5 indicates non-text (likely secret or noise)
    """
    if not data:
        return 0.0

    # Count frequency of each byte
    frequency = {}
    for byte in data:
        frequency[byte] = frequency.get(byte, 0) + 1

    # Calculate entropy
    entropy = 0.0
    length = len(data)
    for count in frequency.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy

# Pseudocode for entropy detection:
for token in high_entropy_candidates:
    entropy = shannon_entropy(token.encode())
    if entropy > ENTROPY_THRESHOLD (4.5):
        flag_as_candidate(token, "high_entropy", entropy)
```

### 2.2 Entropy Threshold Calibration

| Data Type | Typical Entropy | Detection |
|-----------|-----------------|-----------|
| English text | 4.5-4.8 bits/byte | Not flagged |
| JSON/XML | 3.8-4.5 bits/byte | Not flagged |
| Code/source | 4.2-4.9 bits/byte | Not flagged |
| Base64-encoded | 6.0-6.5 bits/byte | **Flagged** |
| Hex-encoded data | 6.5-7.5 bits/byte | **Flagged** |
| Cryptographic keys | 7.5-8.0 bits/byte | **Flagged** |
| Random bytes | 8.0 bits/byte | **Flagged** |
| Bitcoin addresses | 7.2 bits/byte | **Flagged (FP)** |

**False Positive Mitigation:** High-entropy tokens filtered through relationship validation.

## 3. Decoding Pipeline

### 3.1 Base64 Decoding

```python
def try_decode_base64(token: str) -> Optional[bytes]:
    """
    Attempt Base64 decode with automatic padding.

    Base64 padding rules:
    - Length % 4 == 0: No padding needed
    - Length % 4 == 2: Add "=="
    - Length % 4 == 3: Add "="
    - Length % 4 == 1: Invalid (ignore)
    """
    try:
        # Normalize whitespace
        token = token.strip()

        # Add padding if needed
        padding_needed = (4 - len(token) % 4) % 4
        padded_token = token + "=" * padding_needed

        # Attempt decode
        decoded = base64.b64decode(padded_token, validate=False)

        # Sanity check: decoded should have bytes
        if decoded:
            return decoded
    except Exception:
        pass

    return None

# Example:
# Input:  "aGVsbG8gd29ybGQ"
# Padded: "aGVsbG8gd29ybGQ="
# Output: b"hello world"
```

### 3.2 Hexadecimal Decoding

```python
def try_decode_hex(token: str) -> Optional[bytes]:
    """
    Attempt hexadecimal decode.

    Hex strings consist of [0-9a-fA-F] only.
    Length must be even (2 hex digits = 1 byte).
    """
    try:
        # Remove whitespace and non-hex characters
        hex_only = re.sub(r'[^0-9a-fA-F]', '', token)

        # Must be even length
        if len(hex_only) % 2 != 0:
            return None

        # Decode
        decoded = binascii.unhexlify(hex_only)

        if decoded:
            return decoded
    except Exception:
        pass

    return None

# Example:
# Input:  "48656c6c6f"
# Output: b"Hello"
```

### 3.3 JSON/XML Parsing

```python
def extract_values_from_json(text: str) -> List[str]:
    """
    Extract all string values from JSON, prioritizing secret-related fields.

    Priority order:
    1. Fields with password/secret/token/auth/key/credential in name
    2. Long strings (>8 chars)
    3. Base64-looking strings (>20 chars)
    """
    values = []
    secret_keywords = ['pass', 'secret', 'token', 'auth', 'key', 'cred']

    try:
        data = json.loads(text)

        def walk(obj):
            if isinstance(obj, dict):
                # High-priority: secret-named fields
                for key, val in obj.items():
                    key_lower = str(key).lower()
                    if any(kw in key_lower for kw in secret_keywords):
                        if isinstance(val, str) and len(val) > 8:
                            values.append(val)

                # Medium-priority: all string values
                for val in obj.values():
                    walk(val)

            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

            elif isinstance(obj, str):
                if len(obj) > 16:
                    values.append(obj)

        walk(data)
    except:
        pass

    return values

# Example JSON:
# {
#   "username": "admin",
#   "password": "super_secret_123456",
#   "api_key": "AIza_xyz123..."
# }
#
# Extracted (high priority):
# ["super_secret_123456", "AIza_xyz123..."]
```

## 4. Relationship Validation (Wu Lun Framework)

### 4.1 Relationship Detection Algorithm

```python
class WuLunValidator:
    """
    Confucian relationship-based validation.

    The Wu Lun (Five Relationships) framework maps naturally to
    credential relationship patterns.
    """

    # Relationship weights (normalized 0-1)
    WEIGHTS = {
        'cert_authority': 0.82,    # 君臣: Ruler-Subject
        'key_endpoint': 0.75,       # 父子: Father-Son
        'token_session': 0.65,      # 夫婦: Husband-Wife
        'user_password': 0.85,      # 朋友: Friends
        'sequence': 0.60            # 長幼: Elder-Younger
    }

    def validate_candidate(self, candidate: str, context: str, position: int) -> float:
        """
        Calculate relationship-based confidence score.

        Returns confidence: 0.0-1.0
        """
        score = 0.0

        # Check each Wu Lun relationship
        if self.detect_user_password(candidate, context, position):
            score += self.WEIGHTS['user_password']

        if self.detect_key_endpoint(candidate, context, position):
            score += self.WEIGHTS['key_endpoint']

        if self.detect_token_session(candidate, context, position):
            score += self.WEIGHTS['token_session']

        if self.detect_cert_authority(candidate, context, position):
            score += self.WEIGHTS['cert_authority']

        if self.detect_sequence(candidate, context, position):
            score += self.WEIGHTS['sequence']

        # Normalize (multiple relationships sum)
        return min(score, 1.0)

    def detect_user_password(self, token: str, context: str, pos: int) -> bool:
        """
        Confucian 朋友 (Friends): Symmetric credential pair.
        Username and password exist in relationship.
        """
        # Check for username context
        nearby_window = context[max(0, pos-200):min(len(context), pos+200)]
        has_user_keyword = any(
            kw in nearby_window.lower()
            for kw in ['user', 'username', 'login', 'email', 'account']
        )

        if not has_user_keyword:
            return False

        # Look for password within 200 chars of candidate
        password_pattern = r'password\s*["\']?\s*[=:]\s*["\']?([^\s"\'<>]{8,})'
        search_window = context[pos:min(len(context), pos+200)]

        return bool(re.search(password_pattern, search_window, re.IGNORECASE))

    def detect_key_endpoint(self, token: str, context: str, pos: int) -> bool:
        """
        Confucian 夫婦 (Husband-Wife): Complementary pair.
        API key relates to endpoint (key + endpoint = meaningful pair).
        """
        # Keys have high entropy
        entropy = shannon_entropy(token.encode())
        if entropy < 4.0:
            return False

        # Look for endpoint nearby
        endpoint_pattern = r'https?://[^\s<>"\']+|(?:api|endpoint|url|host|server)\s*[=:]\s*https?://[^\s<>"\']+'
        search_window = context[max(0, pos-200):min(len(context), pos+400)]

        return bool(re.search(endpoint_pattern, search_window, re.IGNORECASE))

    def detect_token_session(self, token: str, context: str, pos: int) -> bool:
        """
        Confucian 夫婦 (Token-Session): Complementary pair.
        Session token relates to user session/ID.
        """
        entropy = shannon_entropy(token.encode())
        if entropy < 3.5:
            return False

        # Look for session/user context
        session_pattern = r'(?:session|user|client|request)[_-]?(?:id|token)?\s*[=:]\s*'
        search_window = context[max(0, pos-150):min(len(context), pos+150)]

        return bool(re.search(session_pattern, search_window, re.IGNORECASE))

    def detect_cert_authority(self, token: str, context: str, pos: int) -> bool:
        """
        Confucian 君臣 (Ruler-Subject): Hierarchical relationship.
        Certificate and authority key appear together.
        """
        # Check if token looks like certificate
        if not any(marker in token for marker in ['BEGIN', 'CERTIFICATE', 'RSA', 'EC']):
            return False

        # Look for matching private key or authority cert
        key_pattern = r'PRIVATE KEY'
        search_window = context[max(0, pos-500):min(len(context), pos+500)]

        return bool(re.search(key_pattern, search_window))

    def detect_sequence(self, token: str, context: str, pos: int) -> bool:
        """
        Confucian 長幼 (Elder-Younger): Sequence relationship.
        Multiple credentials in ordered sequence (configuration file pattern).
        """
        # Check if this looks like a config file
        if not any(
            marker in context[:pos]
            for marker in ['password', 'key', 'token', 'secret', 'credential']
        ):
            return False

        # Count nearby credentials
        cred_pattern = r'(?:password|key|token|secret|credential)\s*[=:]\s*'
        search_window = context[max(0, pos-500):min(len(context), pos+500)]
        matches = len(re.findall(cred_pattern, search_window, re.IGNORECASE))

        return matches > 1  # Multiple credentials indicate configuration
```

### 4.2 Confidence Score Calculation

```python
def calculate_final_score(
    pattern_weight: float,
    entropy_value: float,
    relationship_confidence: float
) -> Tuple[float, str]:
    """
    Combined scoring from all detection stages.

    Inputs:
    - pattern_weight: 0.0-1.0 (pattern-specific confidence)
    - entropy_value: 0.0-8.0 (Shannon entropy bits/byte)
    - relationship_confidence: 0.0-1.0 (Wu Lun relationship validation)

    Returns:
    - final_score: 0.0-1.0 (combined confidence)
    - confidence_level: "HIGH" | "MEDIUM" | "LOW"
    """

    # Entropy bonus (normalized to 0-0.3)
    entropy_bonus = min(entropy_value - 4.5, 3.5) / 10.0

    # Relationship multiplier (weights high relationship validation)
    if relationship_confidence > 0.5:
        relationship_multiplier = 1.0 + relationship_confidence
    else:
        relationship_multiplier = 1.0

    # Combined score
    base_score = pattern_weight + entropy_bonus
    final_score = base_score * relationship_multiplier

    # Normalize to 0-1
    final_score = min(final_score, 1.0)

    # Classify confidence
    if final_score >= 0.85:
        confidence_level = "HIGH"
    elif final_score >= 0.60:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    return final_score, confidence_level

# Examples:
# Pattern-matched API key (0.95) + high entropy (7.2) + found endpoint (0.75 rel)
#   → 0.95 + 0.27 = 1.22 * 1.75 = 2.14 → capped 1.0 = "HIGH"

# High-entropy string (no pattern) + no context relationships
#   → 0.0 + 0.35 = 0.35 * 1.0 = 0.35 → "LOW" (filtered as false positive)
```

## 5. Binary File Protection

### 5.1 Magic Byte Detection

```python
def is_binary_file(filepath: str) -> bool:
    """
    Detect binary files by magic bytes (file signatures).

    Prevents:
    - Crashes on binary data
    - False positives from random binary content
    - Hangs on malformed files
    """
    binary_signatures = {
        b'\xFF\xD8\xFF': 'JPEG',
        b'\x89PNG': 'PNG',
        b'GIF8': 'GIF',
        b'BM': 'BMP',
        b'\x1A\x45\xDF\xA3': 'WEBM',
        b'\x00\x00\x00\x20\x66\x74\x79\x70': 'MP4',
        b'\x7FELF': 'ELF executable',
        b'PK\x03\x04': 'ZIP/JAR',
        b'\x1f\x8b\x08': 'GZIP',
        b'BZh': 'BZIP2',
        b'\x50\x4B\x03\x04': 'ZIP',
        b'\xCA\xFE\xBA\xBE': 'Java class',
        b'\xCE\xFA\xED\xFE': 'Mach-O (macOS)',
        b'\xCE\xFA\xED\xFD': 'Mach-O 32-bit',
        b'\xCE\xFA\xEF\xFE': 'Mach-O 64-bit',
        b'MZ': 'Windows PE executable',
    }

    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)

        for signature, filetype in binary_signatures.items():
            if header.startswith(signature):
                return True
    except:
        pass

    return False

# Usage in scanner:
for filepath in files_to_scan:
    if is_binary_file(filepath):
        continue  # Skip binary files

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Process content through pipeline
    scan_file(content)
```

## 6. Pseudocode: Complete Scanning Pipeline

```python
def scan_repository(repo_path: str) -> List[Detection]:
    """Complete IF.yologuard v3 scanning pipeline."""

    detections = []

    # Walk repository
    for root, dirs, files in os.walk(repo_path):
        # Skip common non-code directories
        skip_dirs = ['.git', '.hg', '__pycache__', 'node_modules', '.env.local']
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            filepath = os.path.join(root, filename)

            # Skip binary files
            if is_binary_file(filepath):
                continue

            try:
                # Read file
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue

            # Stage 1: Pattern matching
            for pattern_name, pattern_regex in PATTERN_LIBRARY.items():
                for match in re.finditer(pattern_regex, content):
                    candidate = match.group(0)
                    position = match.start()

                    # Get pattern weight
                    pattern_weight = PATTERN_WEIGHTS[pattern_name]

                    # Stage 2: Entropy analysis
                    entropy = shannon_entropy(candidate.encode())

                    # Stage 3: Format decoding (try Base64, hex)
                    decoded = try_decode_base64(candidate)
                    if not decoded:
                        decoded = try_decode_hex(candidate)

                    # Stage 4: Relationship validation
                    context = content[max(0, position-500):min(len(content), position+500)]
                    rel_confidence = wu_lun_validator.validate_candidate(
                        candidate, content, position
                    )

                    # Calculate final score
                    final_score, confidence = calculate_final_score(
                        pattern_weight, entropy, rel_confidence
                    )

                    # Report if HIGH confidence
                    if confidence == "HIGH":
                        detection = Detection(
                            file=filepath,
                            line=content[:position].count('\n') + 1,
                            pattern=pattern_name,
                            secret=candidate[:50] + '...',  # Truncated for safety
                            confidence=final_score,
                            entropy=entropy,
                            relationship_score=rel_confidence
                        )
                        detections.append(detection)

            # Stage 2 only: Entropy-based (novel format detection)
            for token in detect_high_entropy_tokens(content):
                if token not in [d.secret for d in detections]:
                    entropy = shannon_entropy(token.encode())
                    rel_confidence = wu_lun_validator.validate_candidate(
                        token, content, content.find(token)
                    )

                    final_score, confidence = calculate_final_score(
                        0.5, entropy, rel_confidence  # Lower base score (no pattern)
                    )

                    if confidence in ["HIGH", "MEDIUM"]:
                        detection = Detection(
                            file=filepath,
                            line=content[:content.find(token)].count('\n') + 1,
                            pattern="entropy_only",
                            secret=token[:50] + '...',
                            confidence=final_score,
                            entropy=entropy,
                            relationship_score=rel_confidence
                        )
                        detections.append(detection)

    return detections
```

## 7. Output Format

### 7.1 JSON Output Schema

```json
{
  "metadata": {
    "scanner": "IF.yologuard v3",
    "scan_time": "2025-11-07T12:34:56Z",
    "repository": "/path/to/repo",
    "files_scanned": 49,
    "scan_duration_seconds": 0.412
  },
  "statistics": {
    "total_detections": 95,
    "high_confidence": 88,
    "medium_confidence": 7,
    "low_confidence": 0
  },
  "detections": [
    {
      "id": 1,
      "file": "db/dump.sql",
      "line": 42,
      "pattern": "bcrypt_hash",
      "secret_preview": "$2a$12$R9h/cIPz0gi.URNN...",
      "confidence": 0.98,
      "entropy_bits": 5.23,
      "relationship_score": 0.75,
      "wu_lun_relationships": ["sequence"],
      "notes": "Database password hash in SQL dump file"
    },
    {
      "id": 2,
      "file": "web/var/www/public_html/wp-config.php",
      "line": 15,
      "pattern": "wordpress_salt",
      "secret_preview": "define('AUTH_KEY', 'vmlzaWJs...",
      "confidence": 0.99,
      "entropy_bits": 6.84,
      "relationship_score": 0.85,
      "wu_lun_relationships": ["user_password", "sequence"],
      "notes": "WordPress authentication salt"
    }
  ]
}
```

---

**Document:** ANNEX_A_TECHNICAL_SPEC.md
**Purpose:** Complete technical specification for independent implementation
**Status:** Reference material for Annex D verification

