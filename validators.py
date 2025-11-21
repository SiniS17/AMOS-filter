"""
validators.py - SPLIT VERSION with SEQ filtering
Updated to automatically mark SEQ 1.xx, 2.xx, 3.xx, 10.xx as Valid

Split "Missing reference/reference type" into two separate statuses:
1. "Missing reference" - No reference documents found at all
2. "Missing reference type" - Has DMC/doc ID but no AMM/SRM/etc. prefix

Returns 5 validation states:
- "Valid"
- "Missing reference" (no AMM/SRM/etc. at all)
- "Missing reference type" (has DMC but no AMM/SRM/etc.)
- "Missing revision"
- "N/A"
"""

import re
from config import REF_KEYWORDS, IAW_KEYWORDS, SKIP_PHRASES

# Document ID pattern
DOC_ID_PATTERN = re.compile(r'\b[A-Z0-9]{1,4}[0-9A-Z\-]{0,}\d+\b', re.IGNORECASE)

# DMC pattern - specifically for Data Module Code detection
DMC_PATTERN = re.compile(r'\bDMC-?[A-Z0-9\-]+\b', re.IGNORECASE)

# B787 document pattern (without AMM/SRM prefix)
B787_DOC_PATTERN = re.compile(r'\bB787-[A-Z0-9\-]+\b', re.IGNORECASE)

# Data Module Task pattern
DATA_MODULE_TASK_TEXT = re.compile(r'\bDATA\s+MODULE\s+TASK\b', re.IGNORECASE)

# Document type words pattern
DOC_TYPE_WORDS = re.compile(
    r'\b(?:SB|NDT\s+REPORT|NDT|SERVICE\s+BULLETIN)\b',
    re.IGNORECASE
)

# Standard revision patterns
REV_PATTERN = re.compile(r'\bREV\s*[:\.]?\s*\d+\b', re.IGNORECASE)
ISSUE_PATTERN = re.compile(r'\bISSUE\s*[:\.]?\s*\d+\b', re.IGNORECASE)
ISSUED_SD_PATTERN = re.compile(r'\bISSUED\s+SD\.?\s*\d+\b', re.IGNORECASE)
TAR_PATTERN = re.compile(r'\bTAR\s*\d+\b', re.IGNORECASE)

# Date-based revision patterns
EXP_DATE_PATTERN = re.compile(
    r'\b(?:EXP|DEADLINE|DUE\s+DATE|REV\s+DATE)\s*[:\.]?\s*\d{1,2}[-/]?[A-Z]{3}[-/]?\d{2,4}\b',
    re.IGNORECASE
)
DEADLINE_DATE_PATTERN = re.compile(
    r'\b(?:EXP|DEADLINE|DUE\s+DATE|REV\s+DATE)\s*[:\.]?\s*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b',
    re.IGNORECASE
)

# Pattern for "REFERENCED AMM/SRM/etc."
REFERENCED_PATTERN = re.compile(
    r'\bREFERENCED\s+(?:' + '|'.join(re.escape(k) for k in REF_KEYWORDS) + r')\b',
    re.IGNORECASE
)

# Special document patterns (no explicit REV required)
NDT_REPORT_PATTERN = re.compile(r'\bNDT\s+REPORT\s+[A-Z0-9\-]+\b', re.IGNORECASE)
SB_FULL_PATTERN = re.compile(r'\bSB\s+[A-Z0-9]{1,5}-[A-Z0-9\-]+\b', re.IGNORECASE)
DATA_MODULE_TASK_PATTERN = re.compile(r'\bDATA\s+MODULE\s+TASK\s+\d+\b', re.IGNORECASE)


def is_seq_auto_valid(seq_value):
    """
    Check if SEQ should be automatically marked as Valid.
    Returns True for SEQ patterns: 1.xx, 2.xx, 3.xx, 10.xx

    Args:
        seq_value: The SEQ field value (can be string, float, or int)

    Returns:
        bool: True if SEQ matches auto-valid patterns
    """
    if seq_value is None:
        return False

    # Convert to string and strip whitespace
    seq_str = str(seq_value).strip()

    if not seq_str:
        return False

    # Check for patterns: 1.xx, 2.xx, 3.xx, 10.xx
    # This handles: "1.1", "1.10", "2.5", "3.12", "10.1", "10.99", etc.
    if seq_str.startswith('1.') or \
       seq_str.startswith('2.') or \
       seq_str.startswith('3.') or \
       seq_str.startswith('10.'):
        return True

    return False


def fix_common_typos(text: str) -> str:
    """Normalize common typos in maintenance documentation."""
    if not isinstance(text, str):
        return text

    t = text
    t = re.sub(r'(?i)\bREV[:\.]?\s*(\d+)\b', r'REV \1', t)
    t = re.sub(r'(?i)\brev(\d+)\b', r'rev \1', t)
    t = re.sub(r'([A-Za-z0-9\)\]])rev(\d+)\b', r'\1 rev \2', t, flags=re.IGNORECASE)
    t = re.sub(r'(?i)\bREF([A-Z])', r'REF \1', t)

    for ref in REF_KEYWORDS:
        t = re.sub(fr'(?i)\b({re.escape(ref)})(\d)', r'\1 \2', t)

    t = re.sub(r'\s{2,}', ' ', t)
    return t


def contains_skip_phrase(text: str) -> bool:
    """Check if text contains phrases that should skip validation."""
    if not isinstance(text, str):
        return False
    up = text.upper()
    return any(phrase in up for phrase in SKIP_PHRASES)


def has_referenced_pattern(text: str) -> bool:
    """Check if text uses 'REFERENCED AMM/SRM/etc.' pattern."""
    if not isinstance(text, str):
        return False
    return bool(REFERENCED_PATTERN.search(text))


def has_ndt_report(text: str) -> bool:
    """Check for NDT REPORT pattern with document ID."""
    if not isinstance(text, str):
        return False
    return bool(NDT_REPORT_PATTERN.search(text))


def has_sb_full_number(text: str) -> bool:
    """Check for Service Bulletin with full number."""
    if not isinstance(text, str):
        return False
    return bool(SB_FULL_PATTERN.search(text))


def has_data_module_task(text: str) -> bool:
    """Check for DATA MODULE TASK pattern."""
    if not isinstance(text, str):
        return False
    return bool(DATA_MODULE_TASK_PATTERN.search(text))


def has_primary_reference(text: str) -> bool:
    """Check if text contains a primary reference keyword (AMM, SRM, CMM, etc.)."""
    if not isinstance(text, str):
        return False
    pattern = re.compile(
        r'\b(?:' + '|'.join(re.escape(k) for k in REF_KEYWORDS) + r')\b',
        re.IGNORECASE
    )
    return bool(pattern.search(text))


def has_dmc_or_doc_id(text: str) -> bool:
    """
    Check if text contains DMC, B787 doc format, or DATA MODULE TASK.
    These indicate a document reference but without the type (AMM/SRM/etc.).
    """
    if not isinstance(text, str):
        return False

    # Check for DMC pattern
    if DMC_PATTERN.search(text):
        return True

    # Check for B787 document pattern
    if B787_DOC_PATTERN.search(text):
        return True

    # Check for "DATA MODULE TASK" text (without number)
    if DATA_MODULE_TASK_TEXT.search(text):
        return True

    return False


def has_iaw_keyword(text: str) -> bool:
    """Check if text contains linking words (IAW, REF, PER)."""
    if not isinstance(text, str):
        return False
    pattern = re.compile(
        r'\b(?:' + '|'.join(re.escape(k) for k in IAW_KEYWORDS) + r')\b',
        re.IGNORECASE
    )
    return bool(pattern.search(text))


def has_revision(text: str) -> bool:
    """Check if text contains any revision indicator."""
    if not isinstance(text, str):
        return False

    if REV_PATTERN.search(text):
        return True
    if ISSUE_PATTERN.search(text):
        return True
    if ISSUED_SD_PATTERN.search(text):
        return True
    if TAR_PATTERN.search(text):
        return True
    if EXP_DATE_PATTERN.search(text):
        return True
    if DEADLINE_DATE_PATTERN.search(text):
        return True

    return False


def check_ref_keywords(text, seq_value=None):
    """
    SPLIT validation function - returns 5 states:
    - "Valid"
    - "Missing reference" - No reference documents (AMM/SRM/etc.) at all
    - "Missing reference type" - Has DMC/doc ID but no AMM/SRM/etc.
    - "Missing revision"
    - "N/A"

    NEW: If seq_value matches auto-valid patterns (1.xx, 2.xx, 3.xx, 10.xx),
         returns "Valid" immediately without further validation.

    LOGIC FLOW:
    0. Check SEQ - if auto-valid pattern, return "Valid"
    1. Preserve N/A/blank
    2. Skip phrases → Valid
    3. Special patterns (REFERENCED, NDT, SB, DATA MODULE TASK)
    4. Check for primary reference (AMM/SRM/etc.)
       - If NO primary AND NO DMC/doc ID → "Missing reference"
       - If NO primary BUT HAS DMC/doc ID → "Missing reference type"
       - If HAS primary → check revision
    """

    # ========== STEP 0: Check SEQ for auto-valid patterns ==========
    if seq_value is not None and is_seq_auto_valid(seq_value):
        return "Valid"

    # ========== STEP 1: Preserve N/A / blank / None ==========
    if text is None:
        return "N/A"
    if isinstance(text, float):
        return "N/A"

    stripped = str(text).strip()
    if stripped.upper() in ["N/A", "NA", "NONE", ""]:
        return stripped

    # ========== STEP 2: Skip phrases ==========
    if contains_skip_phrase(stripped):
        return "Valid"

    # ========== STEP 3: Fix typos ==========
    cleaned = fix_common_typos(stripped)

    # ========== STEP 4: Check for "REFERENCED" pattern ==========
    if has_referenced_pattern(cleaned):
        return "Valid"

    # ========== STEP 5: Special document patterns ==========

    # 5A: NDT REPORT with doc ID
    if has_ndt_report(cleaned):
        return "Valid"

    # 5B: DATA MODULE TASK + SB reference
    if has_data_module_task(cleaned) and has_sb_full_number(cleaned):
        return "Valid"

    # 5C: SB with full number + linking word
    iaw = has_iaw_keyword(cleaned)
    if has_sb_full_number(cleaned) and iaw:
        return "Valid"

    # ========== STEP 6: Check for PRIMARY reference ==========
    primary = has_primary_reference(cleaned)
    has_dmc = has_dmc_or_doc_id(cleaned)

    # NEW LOGIC: Split into two statuses
    if not primary:
        # Check if there's a DMC or document ID
        if has_dmc:
            # Has DMC/doc ID but no AMM/SRM/etc. → "Missing reference type"
            # Examples:
            # - "REFER TO DMC-B787-A-57-41-10-00A-720A-A REV 158"
            # - "REFER TO B787-A-53-00-0093-00A-933A-D ISSUE 001 DATA MODULE TASK 2"
            return "Missing reference type"
        else:
            # No reference documents at all → "Missing reference"
            # Examples:
            # - "DONE SATIS"
            # - "C/O SATIS"
            # - "RH CHECK VALVE INSPECTION C/O SATIS"
            return "Missing reference"

    # ========== STEP 7: Has primary reference, check revision ==========
    if has_revision(cleaned):
        return "Valid"

    # ========== STEP 8: Special case - doc ID + linking word ==========
    doc_id = DOC_ID_PATTERN.search(cleaned)
    if doc_id and iaw:
        return "Valid"

    # ========== STEP 9: Has reference but missing revision ==========
    return "Missing revision"