# doc_validator/validation/helpers.py

import re
from doc_validator.config import (
    REF_KEYWORDS,
    IAW_KEYWORDS,
    SKIP_PHRASES,
    HEADER_SKIP_KEYWORDS,
)
from .patterns import (
    DOC_ID_PATTERN,
    DMC_PATTERN,
    B787_DOC_PATTERN,
    DATA_MODULE_TASK_TEXT,
    REV_PATTERN,
    ISSUE_PATTERN,
    ISSUED_SD_PATTERN,
    TAR_PATTERN,
    EXP_DATE_PATTERN,
    DEADLINE_DATE_PATTERN,
    REFERENCED_PATTERN,
    NDT_REPORT_PATTERN,
    SB_FULL_PATTERN,
    DATA_MODULE_TASK_PATTERN,
)

# Precompiled patterns based on config keywords
REF_KEYWORD_PATTERN = re.compile(
    r'\b(?:' + '|'.join(re.escape(k) for k in REF_KEYWORDS) + r')\b',
    re.IGNORECASE,
)

IAW_KEYWORD_PATTERN = re.compile(
    r'\b(?:' + '|'.join(re.escape(k) for k in IAW_KEYWORDS) + r')\b',
    re.IGNORECASE,
)


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
    if (
        seq_str.startswith("1.")
        or seq_str.startswith("2.")
        or seq_str.startswith("3.")
        or seq_str.startswith("10.")
    ):
        return True

    return False


def contains_header_skip_keyword(header_text):
    """
    Check if wo_text_action.header contains keywords that should skip validation.
    Keywords typically include: CLOSE UP, JOB SET UP, OPEN ACCESS, CLOSE ACCESS, GENERAL.

    Args:
        header_text: The wo_text_action.header field value

    Returns:
        bool: True if header contains skip keywords
    """
    if not isinstance(header_text, str):
        return False

    # Normalize: uppercase and remove extra spaces
    normalized = " ".join(header_text.upper().split())

    # Check against all header skip keywords
    for keyword in HEADER_SKIP_KEYWORDS:
        if keyword in normalized:
            return True

    return False


def fix_common_typos(text: str) -> str:
    """Normalize common typos in maintenance documentation."""
    if not isinstance(text, str):
        return text

    t = text
    # Normalize "REV" formats
    t = re.sub(r"(?i)\bREV[:\.]?\s*(\d+)\b", r"REV \1", t)
    t = re.sub(r"(?i)\brev(\d+)\b", r"rev \1", t)
    t = re.sub(r"([A-Za-z0-9\)\]])rev(\d+)\b", r"\1 rev \2", t, flags=re.IGNORECASE)

    # Space after REF
    t = re.sub(r"(?i)\bREF([A-Z])", r"REF \1", t)

    # Ensure space after REF keywords when followed by a digit
    for ref in REF_KEYWORDS:
        t = re.sub(fr"(?i)\b({re.escape(ref)})(\d)", r"\1 \2", t)

    # Collapse multiple spaces
    t = re.sub(r"\s{2,}", " ", t)
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
    """Check for DATA MODULE TASK pattern (with number)."""
    if not isinstance(text, str):
        return False
    return bool(DATA_MODULE_TASK_PATTERN.search(text))


def has_primary_reference(text: str) -> bool:
    """
    Check if text contains a primary reference keyword (AMM, SRM, CMM, etc.).
    """
    if not isinstance(text, str):
        return False
    return bool(REF_KEYWORD_PATTERN.search(text))


def has_dmc_or_doc_id(text: str) -> bool:
    """
    Check if text contains DMC, B787 doc format, or DATA MODULE TASK (without number).
    These indicate a document reference but without the type (AMM/SRM/etc.).
    """
    if not isinstance(text, str):
        return False

    # DMC pattern
    if DMC_PATTERN.search(text):
        return True

    # B787 document pattern
    if B787_DOC_PATTERN.search(text):
        return True

    # "DATA MODULE TASK" text (without number)
    if DATA_MODULE_TASK_TEXT.search(text):
        return True

    return False


def has_iaw_keyword(text: str) -> bool:
    """Check if text contains linking words (IAW, REF, PER)."""
    if not isinstance(text, str):
        return False
    return bool(IAW_KEYWORD_PATTERN.search(text))


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
