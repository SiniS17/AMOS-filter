"""
Validation functions for documentation checker.
Contains all logic for checking references, revisions, and keywords.
"""

import re
from config import REASONS_DICT, REF_KEYWORDS, IAW_KEYWORDS, SKIP_PHRASES


def has_keyword_match(text, keywords, word_boundary=True):
    """
    Check if any keyword exists in text as a standalone word.

    Args:
        text: String to search in
        keywords: List of keywords to search for
        word_boundary: If True, enforce word boundaries (AMM matches, but not in HAMMER)

    Returns:
        bool: True if any keyword is found
    """
    if not isinstance(text, str):
        return False

    if word_boundary:
        # Use word boundaries to avoid matching within words
        pattern = r'\b(?:' + '|'.join(re.escape(k) for k in keywords) + r')\b'
    else:
        pattern = '|'.join(re.escape(k) for k in keywords)

    return bool(re.search(pattern, text, re.IGNORECASE))


def has_skip_phrase(text):
    """Check if text contains phrases that should skip validation."""
    if not isinstance(text, str):
        return False

    return any(phrase in text.upper() for phrase in SKIP_PHRASES)


def has_reference_keyword(text):
    """
    Check if text contains a reference documentation keyword (AMM, SRM, etc.).
    """
    if not isinstance(text, str):
        return False

    return has_keyword_match(text, REF_KEYWORDS, word_boundary=True)


def has_iaw_keyword(text):
    """
    Check if text contains a linking keyword (IAW, REF, PER).
    """
    if not isinstance(text, str):
        return False

    return has_keyword_match(text, IAW_KEYWORDS, word_boundary=True)


def has_valid_revision(text):
    """
    Check if text contains a valid revision reference.
    Valid patterns:
    - REV followed by a number with standard separators: REV158, REV 158, REV:158, REV.158
    - REV DATE followed by number and date (e.g., REV DATE: 15 (01-Jan-2024))

    Returns:
        tuple: (has_revision: bool, is_suspicious: bool)
    """
    if not isinstance(text, str):
        return False, False

    # Pattern 1: REV followed by number with valid separators (space, colon, dot, or nothing)
    # Valid: REV158, REV 158, REV:158, REV.158, REV: 158, REV. 158
    valid_rev_pattern = r'\bREV\s*[:\.]?\s*(\d+)\b'

    # Pattern 2: REV with multiple spaces (suspicious)
    # Suspicious: REV  158 (2+ spaces), REV   158 (3+ spaces)
    suspicious_rev_pattern = r'\bREV\s{2,}(\d+)\b'

    # Pattern 3: REV DATE with number and date
    rev_date_pattern = r'\bREV\s*DATE\s*[:\-\.\s]*\d+\s*\([^)]+\)'

    # Check for valid revision
    valid_rev_match = re.search(valid_rev_pattern, text, re.IGNORECASE)
    suspicious_rev_match = re.search(suspicious_rev_pattern, text, re.IGNORECASE)
    rev_date_match = re.search(rev_date_pattern, text, re.IGNORECASE)

    has_revision = bool(valid_rev_match or rev_date_match)
    is_suspicious = bool(suspicious_rev_match)

    return has_revision, is_suspicious


def check_ref_keywords(text):
    """
    Layered validation of text for documentation requirements.

    New logic:
    - If BOTH IAW and reference keywords are missing → "Missing reference documentation"
    - If ONLY reference keyword is missing (but IAW present) → "Missing reference type"
    - If reference keyword present (regardless of IAW) → Valid for reference check
    - Separately check for revision date
    - Flag suspicious revision formats (multiple spaces)

    Returns:
        str: Reason code indicating validation status
    """
    if not isinstance(text, str):
        return 'Error'

    # Layer 1: Check for skip phrases (override all validation)
    if has_skip_phrase(text):
        return REASONS_DICT["valid"]

    # Layer 2: Check reference documentation
    has_ref = has_reference_keyword(text)
    has_iaw = has_iaw_keyword(text)

    # Layer 3: Check for revision information
    has_rev, is_suspicious_rev = has_valid_revision(text)

    # Build reason based on what's missing
    reasons = []

    # Reference logic:
    if not has_ref and not has_iaw:
        # Both missing → Missing reference documentation
        reasons.append(REASONS_DICT["ref"])
    elif not has_ref and has_iaw:
        # Only reference keyword missing → Missing the reference type
        reasons.append(REASONS_DICT["ref_type"])
    # If has_ref (regardless of has_iaw) → Valid, no error added

    # Revision logic:
    if is_suspicious_rev:
        # Has revision but format is suspicious
        reasons.append(REASONS_DICT["suspicious_rev"])
    elif not has_rev:
        # No revision found at all
        reasons.append(REASONS_DICT["rev"])

    # If nothing is missing, it's valid
    if not reasons:
        return REASONS_DICT["valid"]

    return ', '.join(reasons)