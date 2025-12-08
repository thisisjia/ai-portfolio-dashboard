"""Validation utilities for security and data integrity.

BEGINNER'S NOTE: Validation means checking if data is correct and safe
before we use it. It's like checking if a key fits before trying to
open a door - prevents problems before they happen!
"""

import re
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta


def validate_token(token: str, token_database: Dict[str, Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """Check if an access token is valid and return company info.
    
    BEGINNER'S EXPLANATION:
    This function is like a bouncer at a club:
    1. Someone shows their ID (token)
    2. Bouncer checks if it's on the list (token_database)
    3. If yes, lets them in and notes who they are
    4. If no, turns them away
    
    Args:
        token: The access token provided by the user
        token_database: Dictionary of valid tokens and their info
        
    Returns:
        Tuple of (is_valid, company_name)
        
    Example:
        >>> tokens = {"GOOGLE2024": {"company": "Google", "expires": "2024-12-31"}}
        >>> validate_token("GOOGLE2024", tokens)
        (True, "Google")
    """
    # First, check if token exists at all
    if not token or not isinstance(token, str):
        return (False, None)
    
    # Remove any whitespace (users might copy-paste with spaces)
    token = token.strip().upper()
    
    # Check if token exists in our database
    if token not in token_database:
        return (False, None)
    
    # Get token info
    token_info = token_database[token]
    
    # Check if token has expired
    if "expires" in token_info:
        # Convert string date to datetime for comparison
        expiry_date = datetime.strptime(token_info["expires"], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return (False, None)
    
    # Token is valid! Return company name
    company = token_info.get("company", "Unknown")
    return (True, company)


def validate_input(user_input: str, input_type: str = "general") -> Tuple[bool, Optional[str]]:
    """Validate and sanitize user input to prevent security issues.
    
    BEGINNER'S EXPLANATION:
    When users type things into your website, they might:
    1. Make honest mistakes (typos)
    2. Try to break your site (hackers)
    3. Paste weird characters by accident
    
    This function cleans up their input and makes sure it's safe.
    
    Args:
        user_input: What the user typed
        input_type: What kind of input we expect (email, message, etc.)
        
    Returns:
        Tuple of (is_valid, cleaned_input)
    """
    if not user_input:
        return (False, None)
    
    # Remove leading/trailing whitespace
    cleaned = user_input.strip()
    
    # Check length limits (prevent someone from pasting a whole book)
    if len(cleaned) > 10000:
        return (False, None)
    
    if input_type == "email":
        # Simple email validation
        # Explanation: Must have @ symbol and a dot after it
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, cleaned):
            return (True, cleaned.lower())  # Emails are case-insensitive
        return (False, None)
    
    elif input_type == "token":
        # Tokens should only have letters and numbers
        if re.match(r'^[A-Z0-9]+$', cleaned.upper()):
            return (True, cleaned.upper())
        return (False, None)
    
    elif input_type == "message":
        # For chat messages, remove any HTML/script tags for safety
        # This prevents someone from trying to inject malicious code
        cleaned = re.sub(r'<[^>]+>', '', cleaned)  # Remove HTML tags
        cleaned = cleaned.replace('\x00', '')  # Remove null bytes
        return (True, cleaned)
    
    else:  # general input
        # Basic sanitization
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)  # Remove control characters
        return (True, cleaned)


def generate_token(company_name: str, expiry_days: int = 30) -> Dict[str, Any]:
    """Generate a new access token for a company.
    
    BEGINNER'S EXPLANATION:
    This is like creating a new key for someone:
    1. Make it unique (so no two companies have the same key)
    2. Make it hard to guess (so people can't break in)
    3. Set an expiration date (like a hotel key card)
    
    Args:
        company_name: Name of the company
        expiry_days: How many days until token expires
        
    Returns:
        Dictionary with token info
        
    Example:
        >>> generate_token("Google", 30)
        {
            "token": "GOOGLE_A7B9X2",
            "company": "Google",
            "created": "2024-01-15",
            "expires": "2024-02-14"
        }
    """
    # Create base token from company name
    base = company_name.upper().replace(" ", "_")
    
    # Add random suffix for uniqueness
    # secrets.token_hex(3) creates 6 random characters
    random_suffix = secrets.token_hex(3).upper()
    
    # Combine to create final token
    token = f"{base}_{random_suffix}"
    
    # Calculate dates
    created = datetime.now()
    expires = created + timedelta(days=expiry_days)
    
    return {
        "token": token,
        "company": company_name,
        "created": created.strftime("%Y-%m-%d"),
        "expires": expires.strftime("%Y-%m-%d"),
        "active": True
    }


def hash_token(token: str) -> str:
    """Create a secure hash of a token for storage.
    
    BEGINNER'S EXPLANATION:
    Never store passwords or tokens as plain text! 
    Hashing is like putting it through a blender:
    - "GOOGLE2024" → "a7b9c3d4e5f6..."
    - You can't reverse it to get the original
    - Same input always gives same output
    
    This way, even if someone steals your database,
    they can't see the actual tokens!
    
    Args:
        token: The token to hash
        
    Returns:
        Secure hash of the token
    """
    # Add a "salt" - makes it even harder to crack
    salt = "resume_dashboard_2024"
    
    # Create the hash
    token_with_salt = f"{salt}{token}"
    return hashlib.sha256(token_with_salt.encode()).hexdigest()


# Example usage to help understand:
if __name__ == "__main__":
    # This code only runs if you execute this file directly
    # It's here to help you understand how these functions work
    
    print("=== Token Validation Example ===")
    
    # Create a fake database of tokens
    token_db = {
        "GOOGLE2024": {"company": "Google", "expires": "2024-12-31"},
        "META2024": {"company": "Meta", "expires": "2024-12-31"},
    }
    
    # Test valid token
    valid, company = validate_token("GOOGLE2024", token_db)
    print(f"Token 'GOOGLE2024': Valid={valid}, Company={company}")
    
    # Test invalid token
    valid, company = validate_token("FAKE123", token_db)
    print(f"Token 'FAKE123': Valid={valid}, Company={company}")
    
    print("\n=== Input Validation Example ===")
    
    # Test email validation
    valid, cleaned = validate_input("user@example.com", "email")
    print(f"Email validation: Valid={valid}, Cleaned='{cleaned}'")
    
    # Test message with HTML (security risk!)
    valid, cleaned = validate_input("Hello <script>alert('hack')</script>", "message")
    print(f"Message validation: Valid={valid}, Cleaned='{cleaned}'")
    
    print("\n=== Token Generation Example ===")
    
    # Generate a new token
    new_token = generate_token("Apple Inc")
    print(f"Generated token: {new_token}")
    
    # Hash it for storage
    hashed = hash_token(new_token["token"])
    print(f"Hashed for storage: {hashed[:20]}...")  # Show first 20 chars