# doc_validator/tests/test_validators.py
"""
Unit tests for FULL validator (5 states):

- "Valid"
- "Missing reference"
- "Missing reference type"
- "Missing revision"
- "N/A"

Run with:
    python -m doc_validator.tests.test_validators
"""

from doc_validator.validation.engine import check_ref_keywords
from doc_validator.validation.helpers import (
    fix_common_typos,
    has_revision,
    has_primary_reference,
)


class TestResults:
    """Simple test result tracker"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            msg = f"✗ {test_name}: expected '{expected}', got '{actual}'"
            self.failures.append(msg)
            print(msg)

    def print_summary(self):
        print("\n" + "=" * 60)
        print(f"PASSED: {self.passed}")
        print(f"FAILED: {self.failed}")
        if self.failures:
            print("\nFailures:")
            for f in self.failures:
                print(f"  {f}")
        print("=" * 60)
        return self.failed == 0


results = TestResults()


def test_preserve_na_and_blanks():
    """Test that N/A, blank, and None values are preserved"""
    print("\n=== Testing N/A and Blank Preservation ===")

    results.assert_equal(check_ref_keywords("N/A"), "N/A", "N/A preserved")
    results.assert_equal(check_ref_keywords("n/a"), "n/a", "lowercase n/a preserved")
    results.assert_equal(check_ref_keywords("NA"), "NA", "NA preserved")
    results.assert_equal(check_ref_keywords(""), "", "Empty string preserved")
    results.assert_equal(check_ref_keywords(None), "N/A", "None returns N/A")


def test_skip_phrases():
    """Test that skip phrases are marked as Valid"""
    print("\n=== Testing Skip Phrases ===")

    results.assert_equal(
        check_ref_keywords("GET ACCESS TO PANEL"),
        "Valid",
        "GET ACCESS phrase",
    )
    results.assert_equal(
        check_ref_keywords("GAIN ACCESS"),
        "Valid",
        "GAIN ACCESS phrase",
    )
    results.assert_equal(
        check_ref_keywords("SPARE ORDERED"),
        "Valid",
        "SPARE ORDERED phrase",
    )


def test_valid_documentation():
    """Test cases that should be marked as Valid"""
    print("\n=== Testing Valid Documentation ===")

    # Standard formats with revisions
    results.assert_equal(
        check_ref_keywords("IAW AMM 52-11-01 REV 156"),
        "Valid",
        "Standard AMM with REV",
    )

    results.assert_equal(
        check_ref_keywords("REF SRM 54-21-03 ISSUE 002"),
        "Valid",
        "SRM with ISSUE",
    )

    # Auto-corrected typos
    results.assert_equal(
        check_ref_keywords("REFAMM52-11-01REV156"),
        "Valid",
        "Multiple typos auto-corrected",
    )

    # "REFERENCED" pattern (reference is in header/wpno field)
    results.assert_equal(
        check_ref_keywords("IN ACCORDANCE WITH REFERENCED AMM TASKS"),
        "Valid",
        "REFERENCED AMM pattern",
    )

    # NDT REPORT pattern (no REV required)
    results.assert_equal(
        check_ref_keywords(
            "REF NDT REPORT NDT02-251067, LEFT SIDE SOB FITTING AT STA STA1449"
        ),
        "Valid",
        "NDT REPORT with doc ID",
    )

    results.assert_equal(
        check_ref_keywords(
            "REF NDT REPORT NDT02-251067, LEFT SIDE SOB FITTING AT STA "
            "STA1449,1473,1497,1521,1545,1569,1593 WITH TI-6AL-4V MATERIAL, "
            "SATIS, NO ACTION REQUIRE"
        ),
        "Valid",
        "Full NDT REPORT example",
    )

    # Service Bulletin with full number (no explicit REV required)
    results.assert_equal(
        check_ref_keywords("IAW SB B787-A-21-00-0128-02A-933B-D"),
        "Valid",
        "SB with full part number",
    )

    results.assert_equal(
        check_ref_keywords("REF SB B787-A-21-00-0128-02A-933B-D, DONE, SATIS"),
        "Valid",
        "SB full number with completion text",
    )

    # DATA MODULE TASK + SB pattern
    results.assert_equal(
        check_ref_keywords(
            "IN ACCORDANCE WITH DATA MODULE TASK 2, "
            "SB B787-A-21-00-0128-02A-933B-D. DONE, SATIS"
        ),
        "Valid",
        "DATA MODULE TASK with SB",
    )

    results.assert_equal(
        check_ref_keywords("PER DATA MODULE TASK 5, SB B737-52-1234-A"),
        "Valid",
        "DATA MODULE TASK short version",
    )


def test_missing_reference():
    """
    Test cases missing proper reference type or any reference.

    NOTE:
    - "Missing reference" = no AMM/SRM/etc. and no DMC/doc ID.
    - "Missing reference type" = has DMC/doc ID but missing AMM/SRM/etc.
    """
    print("\n=== Testing Missing Reference vs Missing Reference Type ===")

    # No reference at all
    results.assert_equal(
        check_ref_keywords("INSPECTED PANEL"),
        "Missing reference",
        "No reference at all",
    )

    results.assert_equal(
        check_ref_keywords("REMOVED AND REPLACED PART"),
        "Missing reference",
        "Action without reference",
    )

    # DMC-only → Missing reference type (has doc ID but no AMM/SRM/etc.)
    results.assert_equal(
        check_ref_keywords("DMCB787-A-53-01-01-00B-520A-A"),
        "Missing reference type",
        "DMC without AMM/SRM prefix",
    )

    results.assert_equal(
        check_ref_keywords("REF DMCB787-A-53-01-01-00B-520A-A"),
        "Missing reference type",
        "DMC with REF but no document type",
    )

    # Has doc-like number but no reference type → Missing reference
    results.assert_equal(
        check_ref_keywords("IAW 52-11-01"),
        "Missing reference",
        "Doc ID-like number without type",
    )

    # Has REV but no document type
    results.assert_equal(
        check_ref_keywords("CHECK OK REV 123"),
        "Missing reference",
        "Has REV but no document type",
    )


def test_missing_revision():
    """Test cases with reference but missing revision"""
    print("\n=== Testing Missing Revision ===")

    results.assert_equal(
        check_ref_keywords("IAW AMM 52-11-01"),
        "Missing revision",
        "AMM without revision",
    )

    results.assert_equal(
        check_ref_keywords("REF SRM 54-21-03"),
        "Missing revision",
        "SRM without revision",
    )

    results.assert_equal(
        check_ref_keywords("PER CMM 32-42-11"),
        "Missing revision",
        "CMM without revision",
    )

    # With DMC but still missing revision
    results.assert_equal(
        check_ref_keywords("IAW AMM DMCB787-A-53-01-01-00B-520A-A"),
        "Missing revision",
        "AMM with DMC but no revision",
    )


def test_edge_cases():
    """Test unusual but valid edge cases"""
    print("\n=== Testing Edge Cases ===")

    # Various REV formats
    results.assert_equal(
        check_ref_keywords("IAW AMM 52-11-01 REV: 156"),
        "Valid",
        "REV with colon",
    )

    results.assert_equal(
        check_ref_keywords("IAW AMM 52-11-01 REV. 156"),
        "Valid",
        "REV with period",
    )

    # Lowercase
    results.assert_equal(
        check_ref_keywords("iaw amm 52-11-01 rev 156"),
        "Valid",
        "Lowercase reference",
    )

    # Multiple spaces
    results.assert_equal(
        check_ref_keywords("IAW   AMM   52-11-01   REV   156"),
        "Valid",
        "Multiple spaces normalized",
    )


def test_real_world_scenarios():
    """Test actual examples from maintenance logs"""
    print("\n=== Testing Real-World Scenarios ===")

    # Good entries
    results.assert_equal(
        check_ref_keywords("ACCOMPLISHED IAW AMM 52-11-01 REV 156"),
        "Valid",
        "Typical maintenance entry",
    )

    results.assert_equal(
        check_ref_keywords("PERFORMED INSPECTION PER SRM 54-21-03 ISSUE 002"),
        "Valid",
        "Inspection with ISSUE",
    )

    # Real example from your data
    results.assert_equal(
        check_ref_keywords(
            "THE OUTBOARD FITTING FROM THE RAM AIR OUTLET DUCT ASSEMBLY "
            "IN ACCORDANCE WITH C/O MAKE SURE THAT YOU OBEY ALL THE "
            "WARNINGS AND CAUTIONS IN THE REFERENCED AMM TASKS. SAITS"
        ),
        "Valid",
        "Real example: REFERENCED AMM TASKS pattern",
    )

    results.assert_equal(
        check_ref_keywords("FOLLOW REFERENCED SRM INSTRUCTIONS"),
        "Valid",
        "Short REFERENCED pattern",
    )

    # Common errors
    results.assert_equal(
        check_ref_keywords("REMOVED AND REPLACED COMPONENT"),
        "Missing reference",
        "Forgot to add reference",
    )

    results.assert_equal(
        check_ref_keywords("IAW AMM 52-11-01"),
        "Missing revision",
        "Forgot revision number",
    )

    # DMC-only should be Missing reference type
    results.assert_equal(
        check_ref_keywords("REF DMCB787-A-53-01-01-00B-520A-A REV 45"),
        "Missing reference type",
        "DMC without AMM prefix (now 'Missing reference type')",
    )

    # Typos auto-corrected
    results.assert_equal(
        check_ref_keywords("REFAMM52-11-01REV156"),
        "Valid",
        "Multiple typos auto-corrected",
    )


def test_comparison_old_vs_new():
    """Show how DMC-only cases are classified in the new 5-state logic"""
    print("\n=== DMC-only Classification (New Logic) ===")

    # These are now clearly "Missing reference type"
    test_cases = [
        "DMCB787-A-53-01-01-00B-520A-A",
        "REF DMCB787 ONLY",
        "CHECK DMC-AMM-23-41 ONLY",
    ]

    print("   DMC-only cases should be 'Missing reference type':")
    for case in test_cases:
        result = check_ref_keywords(case)
        results.assert_equal(result, "Missing reference type", f"   {case[:40]}...")


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("FULL VALIDATOR TEST SUITE (5 States)")
    print("=" * 60)

    test_preserve_na_and_blanks()
    test_skip_phrases()
    test_valid_documentation()
    test_missing_reference()
    test_missing_revision()
    test_edge_cases()
    test_real_world_scenarios()
    test_comparison_old_vs_new()

    # Print summary
    success = results.print_summary()

    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nLOGIC OVERVIEW:")
        print("  ✅ Valid = Has AMM/SRM/etc. OR special patterns (NDT, SB, DATA MODULE TASK)")
        print("  ❌ Missing reference = No AMM/SRM/etc. and no doc ID (DMC/B787/etc.)")
        print("  ❌ Missing reference type = Has DMC/doc ID but no AMM/SRM/etc.")
        print("  ❌ Missing revision = Has AMM/SRM/etc. but no REV/ISSUE/DATE")
        print("  • N/A = Blank or N/A entries")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = run_all_tests()
    sys.exit(exit_code)
