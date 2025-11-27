# doc_validator/validation/engine.py

from .helpers import (
    fix_common_typos,
    has_revision,
    has_primary_reference,
    has_dmc_or_doc_id,
    has_ndt_report,
    has_sb_full_number,
    has_data_module_task,
    contains_skip_phrase,
    contains_header_skip_keyword,
    has_referenced_pattern,
    has_iaw_keyword,
    is_seq_auto_valid,
)
from .patterns import DOC_ID_PATTERN


def _des_has_any_reference(des_text):
    """
    Return True if DES field contains any kind of reference.

    Used to decide whether we should enforce "Missing reference" on the row:

      - If DES is empty / None / not a string -> False
      - If DES has any of:
            * primary reference (AMM/SRM/CMM/MEL/...)
            * DMC/B787/doc-ID style reference
            * NDT REPORT
            * SB full number
            * DATA MODULE TASK
            * "REFERENCED AMM/SRM/..." pattern
        -> True
    """
    if des_text is None:
        return False

    if not isinstance(des_text, str):
        des_text = str(des_text)

    cleaned = fix_common_typos(des_text)

    if has_primary_reference(cleaned):
        return True
    if has_dmc_or_doc_id(cleaned):
        return True
    if has_ndt_report(cleaned):
        return True
    if has_sb_full_number(cleaned):
        return True
    if has_data_module_task(cleaned):
        return True
    if has_referenced_pattern(cleaned):
        return True

    return False


def check_ref_keywords(text, seq_value=None, header_text=None, des_text=None):

    """
    Validation function - returns 4 states now:
    - "Valid"
    - "Missing reference"  -> No reference documents (AMM/SRM/etc.) when they are expected
    - "Missing revision"
    - "N/A"                 -> For None/blank/N/A inputs

    CHANGES:
    1) "Missing reference type" has been REMOVED completely.
    2) "Missing reference" is only enforced if the header itself has a reference.
       If wo_text_action.header has NO reference at all, rows that would be
       "Missing reference" are treated as "Valid".

    LOGIC FLOW:
    0. SEQ auto-valid -> "Valid"
    1. HEADER skip keywords (CLOSE UP, JOB SET UP, etc.) -> "Valid"
    2. Preserve N/A / blank
    3. Skip phrases -> "Valid"
    4. Fix common typos
    5. Special patterns:
       - REFERENCED AMM/SRM/etc. -> "Valid"
       - NDT REPORT + ID -> "Valid"
       - DATA MODULE TASK + SB full number -> "Valid"
       - SB full number + IAW/REF/PER -> "Valid"
    6. Check for primary reference
       - If NO primary reference:
           * If header_has_any_reference(header_text) -> "Missing reference"
           * Else -> "Valid"
       - If HAS primary reference:
           * If no revision -> "Missing revision"
           * Else -> "Valid" (with doc-ID+IAW special-case kept)
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
    upper = stripped.upper()
    if upper in ["N/A", "NA", "NONE", ""]:
        # Preserve original casing except normalize None -> "N/A" already handled
        return stripped

    # ========== STEP 3: Skip phrases ==========
    if contains_skip_phrase(stripped):
        return "Valid"

    # ========== STEP 4: Fix typos ==========
    cleaned = fix_common_typos(stripped)

    # ========== STEP 5: Special patterns ==========

    # 5A: "REFERENCED AMM/SRM/etc."
    if has_referenced_pattern(cleaned):
        return "Valid"

    # 5B: NDT REPORT with doc ID
    if has_ndt_report(cleaned):
        return "Valid"

    # 5C: DATA MODULE TASK + SB reference
    if has_data_module_task(cleaned) and has_sb_full_number(cleaned):
        return "Valid"

    # 5D: SB with full number + linking word (IAW/REF/PER)
    iaw = has_iaw_keyword(cleaned)
    if has_sb_full_number(cleaned) and iaw:
        return "Valid"

    # ========== STEP 6: Check for PRIMARY reference ==========
    primary = has_primary_reference(cleaned)

    # Decide if we should enforce "Missing reference" based on DES context
    enforce_reference = _des_has_any_reference(des_text)

    if not primary:
        # No AMM/SRM/etc. in this row.
        if enforce_reference:
            # DES has some reference => this row is expected to carry one too
            return "Missing reference"
        else:
            # DES has no reference at all => allow row without reference
            return "Valid"

    # At this point we DO have a primary reference in the text row.

    # ========== STEP 7: Has primary reference, check revision ==========
    if has_revision(cleaned):
        return "Valid"

    # Optional special case: doc ID + linking word (IAW/REF/PER)
    doc_id = DOC_ID_PATTERN.search(cleaned)
    if doc_id and iaw:
        return "Valid"

    # ========== STEP 8: Has reference but missing revision ==========
    return "Missing revision"

