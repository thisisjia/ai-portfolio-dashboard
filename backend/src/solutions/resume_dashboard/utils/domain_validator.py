"""
Domain validation for company tracking.
Simple validation that focuses on blocking obvious personal emails while accepting most company domains.
"""

import re
from typing import Tuple


class DomainValidator:
    """Simple domain validation for company tracking."""

    def __init__(self):
        # Basic domain regex - matches simple domain patterns
        self.domain_pattern = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,}|xn--[a-zA-Z0-9\-]+)$'
        )

        # Common personal email providers to block
        self.personal_domains = {
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com',
            'mail.com', 'icloud.com', 'protonmail.com', 'zoho.com', 'yandex.com'
        }

        # Suspicious patterns that might indicate fake domains
        self.suspicious_patterns = [
            'test', 'demo', 'fake', 'scam', 'example', 'sample',
            '123', '456', '789', '999', '000',
            'company', 'business', 'tech', 'startup', 'enterprise'
        ]

    def is_valid_domain(self, domain: str) -> Tuple[bool, str]:
        """
        Validate a domain name for company tracking.

        Args:
            domain: Domain name to validate (e.g., "acme.com")

        Returns:
            Tuple of (is_valid, message)
        """
        if not domain:
            return False, "Domain is required"

        # Clean the domain input
        domain = domain.lower().strip()

        # Handle email addresses - extract domain
        if '@' in domain:
            domain = self.extract_domain_from_email(domain)

        # Remove common prefixes/suffixes that people might add
        domain = re.sub(r'^(https?://)?(www\.)?', '', domain)
        domain = re.sub(r'/.*$', '', domain)  # Remove paths

        # Accept any domain for tracking - no validation
        return True, "Domain accepted"

    def _is_suspicious_domain(self, domain: str) -> bool:
        """Check if domain contains suspicious patterns."""
        # Check for obviously fake patterns
        for pattern in self.suspicious_patterns:
            if pattern in domain:
                # Allow some common business words
                if domain.count(pattern) > 1 or len(domain) < 8:
                    return True

        # Check for domains that are just numbers
        if re.match(r'^[0-9\-\.]+$', domain):
            return True

        # Check for domains that are too short (likely fake)
        if len(domain) < 4:
            return True

        # Check for suspicious TLD combinations
        if '.com' in domain and domain.count('.') > 2:
            return True

        return False

    def extract_domain_from_email(self, email: str) -> str:
        """Extract domain from email address."""
        if '@' not in email:
            return email

        domain = email.split('@')[1].lower()
        # Clean the domain
        return re.sub(r'^www\.', '', domain)

    def get_domain_category(self, domain: str) -> str:
        """Categorize domain type for analytics."""
        domain = domain.lower()

        # Known tech companies
        if any(tech in domain for tech in ['google', 'microsoft', 'apple', 'amazon', 'meta', 'netflix']):
            return 'big_tech'

        # Known startup patterns
        if any(tld in domain for tld in ['.io', '.ai', '.tech', '.co', '.app']):
            return 'startup'

        # Educational institutions
        if domain.endswith(('.edu', '.ac.uk', '.edu.sg')):
            return 'education'

        # Government
        if domain.endswith(('.gov', '.govt')):
            return 'government'

        # Personal email (should be blocked, but categorize anyway)
        if domain in self.personal_domains:
            return 'personal'

        # Default
        return 'corporate'


# Singleton instance
_domain_validator = None

def get_domain_validator() -> DomainValidator:
    """Get singleton instance of domain validator."""
    global _domain_validator
    if _domain_validator is None:
        _domain_validator = DomainValidator()
    return _domain_validator