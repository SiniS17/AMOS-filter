# doc_validator/validation/engine.py

from .helpers import (
    is_seq_auto_valid,
    contains_header_skip_keyword,
    fix_common_typos,
    contains_skip_phrase,
    has_referenced_pattern,
    has_ndt_report,
    has_sb_full_number,
    has_data_module_task,
    has_iaw_keyword,
    has_primary_reference,
    has_dmc_or_doc_id,
    has_revision,
)
from .patterns import DOC_ID_PATTERN


def check_ref_keywords(text, seq_value=None, header_text=None):
    """
    SPLIT validation function - returns 5 states:
    - "Valid"
    - "Missing reference" - No reference documents (AMM/SRM/etc.) at all
    - "Missing reference type" - Has DMC/doc ID but no AMM/SRM/etc.
    - "Missing revision"
    - "N/A"

    NEW: If seq_value matches auto-valid patterns (1.xx, 2.xx, 3.xx, 10.xx),
         returns "Valid" immediately without further validation.

    NEW: If header_text contains skip keywords (CLOSE UP, JOB SET UP, etc.),
         returns "Valid" immediately without further validation.

    LOGIC FLOW:
    0. Check SEQ - if auto-valid pattern, return "Valid"
    1. Check HEADER - if contains skip keywords, return "Valid"
    2. Preserve N/A/blank
    3. Skip phrases → Valid
    4. Special patterns (REFERENCED, NDT, SB, DATA MODULE TASK)
    5. Check for primary reference (AMM/SRM/etc.)
       - If NO primary AND NO DMC/doc ID → "Missing reference"
       - If NO primary BUT HAS DMC/doc ID → "Missing reference type"
       - If HAS primary → check revision
    """

    # ========== STEP 0: Check SEQ for auto-valid patterns ==========
    if seq_value is not None and is_seq_auto_valid(seq_value):
        return "Valid"

    # ========== STEP 1: Check HEADER for skip keywords ==========
    if header_text is not None and contains_header_skip_keyword(header_text):
        return "Valid"

    # ========== STEP 2: Preserve N/A / blank / None ==========
    if text is None:
        return "N/A"
    if isinstance(text, float):
        return "N/A"

    stripped = str(text).strip()
    if stripped.upper() in ["N/A", "NA", "NONE", ""]:
        return stripped

    # ========== STEP 3: Skip phrases ==========
    if contains_skip_phrase(stripped):
        return "Valid"

    # ========== STEP 4: Fix typos ==========
    cleaned = fix_common_typos(stripped)

    # ========== STEP 5: Check for "REFERENCED" pattern ==========
    if has_referenced_pattern(cleaned):
        return "Valid"

    # ========== STEP 6: Special document patterns ==========

    # 6A: NDT REPORT with doc ID
    if has_ndt_report(cleaned):
        return "Valid"

    # 6B: DATA MODULE TASK + SB reference
    if has_data_module_task(cleaned) and has_sb_full_number(cleaned):
        return "Valid"

    # 6C: SB with full number + linking word
    iaw = has_iaw_keyword(cleaned)
    if has_sb_full_number(cleaned) and iaw:
        return "Valid"

    # ========== STEP 7: Check for PRIMARY reference ==========
    primary = has_primary_reference(cleaned)
    has_dmc = has_dmc_or_doc_id(cleaned)

    # Split into two statuses
    if not primary:
        # Has DMC/doc ID but no AMM/SRM/etc. → "Missing reference type"
        if has_dmc:
            return "Missing reference type"
        # No reference documents at all → "Missing reference"
        return "Missing reference"

    # ========== STEP 8: Has primary reference, check revision ==========
    if has_revision(cleaned):
        return "Valid"

    # ========== STEP 9: Special case - doc ID + linking word ==========
    doc_id = DOC_ID_PATTERN.search(cleaned)
    if doc_id and iaw:
        return "Valid"

    # ========== STEP 10: Has reference but missing revision ==========
    return "Missing revision"
