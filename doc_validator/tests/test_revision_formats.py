# doc_validator/tests/test_revision_formats.py
"""
Test cases for the enhanced revision detection with 12-character window.

Run with:
    python -m doc_validator.tests.test_revision_formats
"""

from doc_validator.validation.helpers import has_revision


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def assert_true(self, condition, test_name):
        if condition:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            msg = f"✗ {test_name}: expected True, got False"
            self.failures.append(msg)
            print(msg)

    def assert_false(self, condition, test_name):
        if not condition:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            msg = f"✗ {test_name}: expected False, got True"
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


def test_standard_rev_formats():
    """Test standard REV number formats (existing functionality)"""
    print("\n=== Testing Standard REV Formats ===")

    results.assert_true(
        has_revision("IAW AMM 52-11-01 REV 156"),
        "Standard REV with space"
    )

    results.assert_true(
        has_revision("IAW AMM 52-11-01 REV: 156"),
        "REV with colon"
    )

    results.assert_true(
        has_revision("IAW AMM 52-11-01 REV.156"),
        "REV with period"
    )

    results.assert_true(
        has_revision("IAW AMM 52-11-01 REV-156"),
        "REV with dash"
    )

    results.assert_true(
        has_revision("REF SRM 54-21-03 ISSUE 002"),
        "ISSUE format"
    )

    results.assert_true(
        has_revision("PER CMM ISSUED SD 45"),
        "ISSUED SD format"
    )


def test_new_date_formats():
    """Test NEW date formats: AUG 01/2025 and 01AUG 25"""
    print("\n=== Testing NEW Date Formats (12-char window) ===")

    # Format 1: REV AUG 01/2025
    results.assert_true(
        has_revision("IAW AMM 52-11-01 REV AUG 01/2025"),
        "REV AUG 01/2025 format"
    )

    results.assert_true(
        has_revision("REF SRM REV AUG 01/2025 DONE"),
        "REV AUG 01/2025 in middle"
    )

    # Format 2: REV 01AUG 25
    results.assert_true(
        has_revision("IAW AMM 52-11-01 REV 01AUG 25"),
        "REV 01AUG 25 format"
    )

    results.assert_true(
        has_revision("REF SRM REV 01AUG 25 SATIS"),
        "REV 01AUG 25 in middle"
    )

    # All months
    results.assert_true(
        has_revision("REV JAN 15/2025"),
        "JAN month"
    )

    results.assert_true(
        has_revision("REV FEB 20/2025"),
        "FEB month"
    )

    results.assert_true(
        has_revision("REV MAR 10/2025"),
        "MAR month"
    )

    results.assert_true(
        has_revision("REV APR 05/2025"),
        "APR month"
    )

    results.assert_true(
        has_revision("REV MAY 12/2025"),
        "MAY month"
    )

    results.assert_true(
        has_revision("REV JUN 08/2025"),
        "JUN month"
    )

    results.assert_true(
        has_revision("REV JUL 25/2025"),
        "JUL month"
    )

    results.assert_true(
        has_revision("REV SEP 30/2025"),
        "SEP month"
    )

    results.assert_true(
        has_revision("REV OCT 18/2025"),
        "OCT month"
    )

    results.assert_true(
        has_revision("REV NOV 22/2025"),
        "NOV month"
    )

    results.assert_true(
        has_revision("REV DEC 31/2025"),
        "DEC month"
    )


def test_mixed_formats():
    """Test mixed and variations of date formats"""
    print("\n=== Testing Mixed/Variation Formats ===")

    # Various separators
    results.assert_true(
        has_revision("REV: AUG 01/2025"),
        "REV: with colon + date"
    )

    results.assert_true(
        has_revision("REV. AUG 01/2025"),
        "REV. with period + date"
    )

    results.assert_true(
        has_revision("REV - AUG 01/2025"),
        "REV - with dash + date"
    )

    # Compact format
    results.assert_true(
        has_revision("REV01AUG25"),
        "Compact no space REV01AUG25"
    )

    results.assert_true(
        has_revision("REVAUG 01/2025"),
        "No space after REV"
    )

    # Different year formats
    results.assert_true(
        has_revision("REV AUG 01/25"),
        "Two-digit year"
    )

    results.assert_true(
        has_revision("REV 15AUG2025"),
        "No spaces in date"
    )


def test_existing_date_patterns():
    """Test existing EXP and DEADLINE patterns still work"""
    print("\n=== Testing Existing Date Patterns ===")

    results.assert_true(
        has_revision("EXP 03JAN25"),
        "EXP date format"
    )

    results.assert_true(
        has_revision("DEADLINE: 01/11/2025"),
        "DEADLINE date format"
    )

    results.assert_true(
        has_revision("EXP: 28/06/2026"),
        "EXP with slash date"
    )

    results.assert_true(
        has_revision("DUE DATE 15/03/2025"),
        "DUE DATE format"
    )


def test_edge_cases():
    """Test edge cases and potential false positives"""
    print("\n=== Testing Edge Cases ===")

    # Should PASS (valid revisions)
    results.assert_true(
        has_revision("REV R00"),
        "Alphanumeric revision code with digit"
    )

    results.assert_true(
        has_revision("REV 2024-01"),
        "Year-month format"
    )

    # Should FAIL (not valid revisions - no standalone number or date)
    results.assert_false(
        has_revision("REV A-D"),
        "Letter-dash-letter (no digit, not a date)"
    )

    results.assert_false(
        has_revision("REVIEW THE DOCUMENT"),
        "REVIEW word (not REV)"
    )

    results.assert_false(
        has_revision("REVERSE THE PROCESS"),
        "REVERSE word (not REV)"
    )

    results.assert_false(
        has_revision("REVENUE REPORT"),
        "REVENUE word (not REV)"
    )

    # Edge case: REV with no following content
    results.assert_false(
        has_revision("CHECK REV"),
        "REV at end with no number"
    )

    results.assert_false(
        has_revision("REV     "),
        "REV with only spaces"
    )


def test_real_world_examples():
    """Test real-world examples from maintenance logs"""
    print("\n=== Testing Real-World Examples ===")

    results.assert_true(
        has_revision(
            "REFER TO AMM TASK DMC-B787-A-52-09-01-00A-280A-A REV AUG 01/2025 SATIS"
        ),
        "Real example: REV AUG 01/2025"
    )

    results.assert_true(
        has_revision(
            "IAW AMM DMC-B787-A-21-52-38-00A-520A-A REV 01AUG 25"
        ),
        "Real example: REV 01AUG 25"
    )

    results.assert_true(
        has_revision(
            "REF SRM DMC-B787-A-27-81-04-01A-520A-A REV 158"
        ),
        "Real example: Standard REV 158"
    )

    results.assert_true(
        has_revision(
            "IAW NEF-VNA-00, EXP 03JAN25"
        ),
        "Real example: EXP date"
    )

    results.assert_true(
        has_revision(
            "REF MEL 33-44-01-02A, DEADLINE: 01/11/2025"
        ),
        "Real example: DEADLINE date"
    )


def test_12_char_window_boundary():
    """Test the 12-character window boundary conditions"""
    print("\n=== Testing 12-Character Window Boundary ===")

    # Exactly at boundary (should pass)
    results.assert_true(
        has_revision("REV 123456789012"),  # 12 digits
        "12 digits after REV"
    )

    # Month at start of window (should pass)
    results.assert_true(
        has_revision("REV AUG012025"),  # AUG01/2025 = 10 chars
        "Month date compact within 12 chars"
    )

    # Standard revision well within window
    results.assert_true(
        has_revision("REV 158"),  # 3 digits
        "Short revision number"
    )


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("REVISION FORMAT TEST SUITE")
    print("Testing Enhanced 12-Character Window Detection")
    print("=" * 60)

    test_standard_rev_formats()
    test_new_date_formats()
    test_mixed_formats()
    test_existing_date_patterns()
    test_edge_cases()
    test_real_world_examples()
    test_12_char_window_boundary()

    # Print summary
    success = results.print_summary()

    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nSUPPORTED REVISION FORMATS:")
        print("  ✅ REV 156")
        print("  ✅ REV: 156")
        print("  ✅ REV.156")
        print("  ✅ ISSUE 002")
        print("  ✅ EXP 03JAN25")
        print("  ✅ DEADLINE: 01/11/2025")
        print("  ✅ REV AUG 01/2025  (NEW)")
        print("  ✅ REV 01AUG 25     (NEW)")
        print("\n12-CHARACTER WINDOW LOGIC:")
        print("  • Looks 12 chars after 'REV' keyword")
        print("  • Accepts any content with digits")
        print("  • Recognizes month names (JAN-DEC)")
        print("  • Flexible spacing and punctuation")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    raise SystemExit(exit_code)