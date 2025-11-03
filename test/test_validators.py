"""
Unit tests for validation functions.
Run with: python -m pytest tests/test_validators.py
Or simply: python tests/test_validators.py
"""

import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators import (
    has_keyword_match,
    has_skip_phrase,
    has_reference_keyword,
    has_iaw_keyword,
    has_valid_revision,
    check_ref_keywords
)


def test_has_keyword_match():
    """Test keyword matching with word boundaries."""
    # Should match
    assert has_keyword_match("IAW AMM 123", ["AMM"]) == True
    assert has_keyword_match("REFER TO AMM", ["AMM", "SRM"]) == True

    # Should NOT match (AMM is inside HAMMER)
    assert has_keyword_match("HAMMER", ["AMM"]) == False

    # Case insensitive
    assert has_keyword_match("amm 123", ["AMM"]) == True

    print("✓ test_has_keyword_match passed")


def test_has_skip_phrase():
    """Test skip phrase detection."""
    assert has_skip_phrase("GET ACCESS TO PANEL") == True
    assert has_skip_phrase("SPARE ORDERED") == True
    assert has_skip_phrase("NORMAL TEXT") == False

    print("✓ test_has_skip_phrase passed")


def test_has_reference_keyword():
    """Test reference keyword detection."""
    assert has_reference_keyword("REFER TO AMM 123") == True
    assert has_reference_keyword("IAW SRM 456") == True
    assert has_reference_keyword("NO REFERENCE") == False
    assert has_reference_keyword("HAMMER") == False  # AMM is in HAMMER but not standalone

    print("✓ test_has_reference_keyword passed")


def test_has_iaw_keyword():
    """Test IAW keyword detection."""
    assert has_iaw_keyword("IAW document") == True
    assert has_iaw_keyword("REFER TO AMM") == True
    assert has_iaw_keyword("PER manual") == True
    assert has_iaw_keyword("I.A.W document") == True
    assert has_iaw_keyword("NO LINKING WORD") == False

    print("✓ test_has_iaw_keyword passed")


def test_has_valid_revision():
    """Test revision detection and suspicious format detection."""
    # Valid formats
    assert has_valid_revision("REV 158") == (True, False)
    assert has_valid_revision("REV158") == (True, False)
    assert has_valid_revision("REV:158") == (True, False)
    assert has_valid_revision("REV.158") == (True, False)
    assert has_valid_revision("REV: 158") == (True, False)
    assert has_valid_revision("REV. 158") == (True, False)

    # Suspicious formats (multiple spaces)
    assert has_valid_revision("REV  158") == (True, True)
    assert has_valid_revision("REV   158") == (True, True)
    assert has_valid_revision("REV    158") == (True, True)

    # No revision
    assert has_valid_revision("NO REVISION") == (False, False)

    print("✓ test_has_valid_revision passed")


def test_check_ref_keywords_valid():
    """Test complete validation for valid cases."""
    # Perfect documentation
    assert check_ref_keywords("REFER TO AMM REV 158") == "Valid documentation"
    assert check_ref_keywords("IAW SRM REV:158") == "Valid documentation"

    # Reference without IAW (still valid)
    assert check_ref_keywords("787 AMM REV 158") == "Valid documentation"

    # Skip phrases
    assert check_ref_keywords("GET ACCESS TO PANEL") == "Valid documentation"

    print("✓ test_check_ref_keywords_valid passed")


def test_check_ref_keywords_errors():
    """Test complete validation for error cases."""
    # Missing both reference and IAW
    assert "Missing reference documentation" in check_ref_keywords("SOME TEXT")
    assert "Missing revision date" in check_ref_keywords("SOME TEXT")

    # Missing reference type (has IAW but no AMM/SRM/etc)
    assert "Missing reference type" in check_ref_keywords("IAW document REV 158")

    # Suspicious revision format
    assert "Suspicious revision format" in check_ref_keywords("REFER TO AMM REV  158")

    # Missing revision
    assert "Missing revision date" in check_ref_keywords("REFER TO AMM without revision")

    print("✓ test_check_ref_keywords_errors passed")


def test_real_world_examples():
    """Test with real-world examples from the spreadsheet."""
    # Row 724 - Should be valid
    text1 = "4.REMOVE AND KEEP FLOOR PANELS AT STA 1233 AND 1257. REFER TO 787 AMM DMCB787-A-53-01-01-00B-520A-A REV 158"
    assert check_ref_keywords(text1) == "Valid documentation"

    # Row with REV:158 format
    text2 = "5. DO AMM TASK DMC-B787-A-52-09-07-00A-280A-A FORWARD ELECTRICAL EQUIPMENT ACCESS DOOR SEAL – INSPECTION. REV:158 SATIS"
    assert check_ref_keywords(text2) == "Valid documentation"

    # Row with suspicious spacing
    text3 = "REFER TO AMM REV  158"
    assert "Suspicious revision format" in check_ref_keywords(text3)

    print("✓ test_real_world_examples passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running validation tests...")
    print("=" * 60 + "\n")

    try:
        test_has_keyword_match()
        test_has_skip_phrase()
        test_has_reference_keyword()
        test_has_iaw_keyword()
        test_has_valid_revision()
        test_check_ref_keywords_valid()
        test_check_ref_keywords_errors()
        test_real_world_examples()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)