"""
Real-World Data Test Suite
Tests based on actual maintenance log entries from customer data.

Run with: python test_real_world_data.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators import check_ref_keywords


class TestResults:
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
            self.failures.append(f"✗ {test_name}: expected '{expected}', got '{actual}'")
            print(f"✗ {test_name}: expected '{expected}', got '{actual}'")

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


def test_valid_with_amm_and_dmc():
    """Test valid entries with AMM/SRM + DMC + REV"""
    print("\n=== Testing Valid: AMM/SRM + DMC + REV ===")

    results.assert_equal(
        check_ref_keywords("REFER TO AMM TASK DMC-B787-A-52-09-01-00A-280A-A REV:158 SATIS"),
        "Valid",
        "AMM TASK + DMC + REV"
    )

    results.assert_equal(
        check_ref_keywords("IAW AMM DMC-B787-A-21-52-38-00A-520A-A REV 158"),
        "Valid",
        "IAW AMM + DMC + REV"
    )

    results.assert_equal(
        check_ref_keywords("REF SRM DMC-B787-A-27-81-04-01A-520A-A REV 158"),
        "Valid",
        "REF SRM + DMC + REV"
    )

    results.assert_equal(
        check_ref_keywords("IAW AMM TASK B787-A-G71-11-01-00A-720A-A REV 158"),
        "Valid",
        "AMM TASK + B787 format + REV"
    )


def test_date_based_revisions():
    """Test date-based revision formats"""
    print("\n=== Testing Valid: Date-Based Revisions ===")

    results.assert_equal(
        check_ref_keywords("ADD C330 RAISED BRACKET ASSY IAW NEF-VNA-00, EXP 03JAN25"),
        "Valid",
        "NEF + EXP date format 1"
    )

    results.assert_equal(
        check_ref_keywords("IAW NEF-VNA-00, EXP: 28/06/2026"),
        "Valid",
        "NEF + EXP date format 2"
    )

    results.assert_equal(
        check_ref_keywords("REF MEL 33-44-01-02A, DEADLINE: 01/11/2025"),
        "Valid",
        "MEL + DEADLINE date"
    )

    results.assert_equal(
        check_ref_keywords("IAW DDG 38-30-01A REV 158"),
        "Valid",
        "DDG + REV number"
    )

    results.assert_equal(
        check_ref_keywords("REF MME 3.32.7.5 REV 02, DEADLINE: 01/11/2025"),
        "Valid",
        "MME + REV + DEADLINE"
    )


def test_dmc_only_missing_reference():
    """Test DMC-only entries (should be Missing reference/reference type)"""
    print("\n=== Testing Missing Reference/Reference Type: DMC Only ===")

    results.assert_equal(
        check_ref_keywords("IAW DMC-B787-A-21-52-38-00A-520A-A REV 158"),
        "Missing reference/reference type",
        "DMC only with REV (no AMM/SRM)"
    )

    results.assert_equal(
        check_ref_keywords("REF DMC-B787-A-27-81-04-01A-520A-A REV 158"),
        "Missing reference/reference type",
        "REF DMC only with REV"
    )

    results.assert_equal(
        check_ref_keywords("PER DMCB787-A-53-01-01-00B-520A-A"),
        "Missing reference/reference type",
        "DMC only without REV"
    )


def test_work_step_no_reference():
    """Test work step entries without references"""
    print("\n=== Testing Missing Reference/Reference Type: Work Steps ===")

    results.assert_equal(
        check_ref_keywords("PERFORMED WORK STEP `FWD LARGE CARGO DOOR ACTUATORS...`"),
        "Missing reference/reference type",
        "Work step without reference"
    )

    results.assert_equal(
        check_ref_keywords("C/O WORK STEP 1 SATIS"),
        "Missing reference/reference type",
        "Work step completion"
    )

    results.assert_equal(
        check_ref_keywords("DONE SATIS"),
        "Missing reference/reference type",
        "Simple completion"
    )

    results.assert_equal(
        check_ref_keywords("PERFORMED C/O SATIS"),
        "Missing reference/reference type",
        "Performed check-out"
    )

    results.assert_equal(
        check_ref_keywords("RE-INSPECTED SATIS"),
        "Missing reference/reference type",
        "Re-inspection"
    )

    results.assert_equal(
        check_ref_keywords("INSPECTED SATIS"),
        "Missing reference/reference type",
        "Inspection"
    )


def test_work_step_with_reference():
    """Test work step entries that contain references"""
    print("\n=== Testing Valid: Work Steps WITH References ===")

    results.assert_equal(
        check_ref_keywords("PERFORMED WORK STEP IAW AMM 52-11-01 REV 156 SATIS"),
        "Valid",
        "Work step with AMM reference"
    )

    results.assert_equal(
        check_ref_keywords("C/O WORK STEP 1 REF SRM 54-21-03 ISSUE 002 SATIS"),
        "Valid",
        "Work step with SRM reference"
    )


def test_ndt_reports():
    """Test NDT report entries"""
    print("\n=== Testing Valid: NDT Reports ===")

    results.assert_equal(
        check_ref_keywords(
            "REF NDT REPORT NDT02-251067, LEFT SIDE SOB FITTING AT STA STA1449,1473,1497,1521,1545,1569,1593 WITH TI-6AL-4V MATERIAL, SATIS, NO ACTION REQUIRE"),
        "Valid",
        "Full NDT report entry"
    )

    results.assert_equal(
        check_ref_keywords("REF NDT REPORT NDT02-251105"),
        "Valid",
        "Short NDT report"
    )


def test_sb_full_number():
    """Test Service Bulletin with full numbers"""
    print("\n=== Testing Valid: SB Full Numbers ===")

    results.assert_equal(
        check_ref_keywords("IAW SB B787-A-21-00-0128-02A-933B-D"),
        "Valid",
        "SB with full number"
    )

    results.assert_equal(
        check_ref_keywords("REF SB B787-A-21-00-0128-02A-933B-D, DONE, SATIS"),
        "Valid",
        "SB full number with completion"
    )


def test_data_module_task():
    """Test DATA MODULE TASK entries"""
    print("\n=== Testing Valid & Missing Revision: DATA MODULE TASK ===")

    results.assert_equal(
        check_ref_keywords("IN ACCORDANCE WITH DATA MODULE TASK 2, SB B787-A-21-00-0128-02A-933B-D. DONE, SATIS"),
        "Valid",
        "DATA MODULE TASK with SB full number"
    )

    results.assert_equal(
        check_ref_keywords(
            "REMOVE THE BELLCRANK AND THE OUTBOARD FITTING FROM THE RAM AIR OUTLET DUCT ASSEMBLY IN ACCORDANCE WITH DATA MODULE TASK 2, SB B787-A-21-00-0128-02A-933B-D"),
        "Valid",
        "Long entry with DATA MODULE TASK + SB"
    )


def test_referenced_pattern():
    """Test REFERENCED AMM/SRM pattern"""
    print("\n=== Testing Valid: REFERENCED Pattern ===")

    results.assert_equal(
        check_ref_keywords(
            "THE OUTBOARD FITTING FROM THE RAM AIR OUTLET DUCT ASSEMBLY IN ACCORDANCE WITH C/O MAKE SURE THAT YOU OBEY ALL THE WARNINGS AND CAUTIONS IN THE REFERENCED AMM TASKS. SAITS"),
        "Valid",
        "REFERENCED AMM TASKS"
    )

    results.assert_equal(
        check_ref_keywords("FOLLOW THE REFERENCED SRM PROCEDURES"),
        "Valid",
        "Short REFERENCED SRM"
    )


def test_missing_revision():
    """Test entries with reference but missing revision"""
    print("\n=== Testing Missing Revision ===")

    results.assert_equal(
        check_ref_keywords("IAW AMM 52-11-01"),
        "Missing revision",
        "AMM without revision"
    )

    results.assert_equal(
        check_ref_keywords("REF SRM 54-21-03"),
        "Missing revision",
        "SRM without revision"
    )

    results.assert_equal(
        check_ref_keywords("PER CMM 32-42-11"),
        "Missing revision",
        "CMM without revision"
    )


def test_na_and_blank():
    """Test N/A and blank entries"""
    print("\n=== Testing N/A and Blanks ===")

    results.assert_equal(
        check_ref_keywords("N/A"),
        "N/A",
        "N/A preserved"
    )

    results.assert_equal(
        check_ref_keywords(""),
        "",
        "Blank preserved"
    )

    results.assert_equal(
        check_ref_keywords(None),
        "N/A",
        "None returns N/A"
    )


def test_edge_cases():
    """Test edge cases from real data"""
    print("\n=== Testing Edge Cases ===")

    results.assert_equal(
        check_ref_keywords("REFER TO 787 AMM 29-11-00 REV 159"),
        "Valid",
        "787 AMM format"
    )

    results.assert_equal(
        check_ref_keywords("IAW GENX-1B BOEING 787 AMM, TASK B787-A-G72-22-04-00A-720A-A. REV 158"),
        "Valid",
        "GENX AMM format"
    )

    results.assert_equal(
        check_ref_keywords("REF EMM 72-54-00, SUBTASK 72-54-00-040-160 REV 41"),
        "Valid",
        "EMM with subtask"
    )

    results.assert_equal(
        check_ref_keywords("IAW SRM B787-A-51-11-02-02A-280A-A REV 14"),
        "Valid",
        "SRM with full reference"
    )


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("REAL-WORLD DATA TEST SUITE")
    print("Based on Customer Maintenance Logs")
    print("=" * 60)

    test_valid_with_amm_and_dmc()
    test_date_based_revisions()
    test_dmc_only_missing_reference()
    test_work_step_no_reference()
    test_work_step_with_reference()
    test_ndt_reports()
    test_sb_full_number()
    test_data_module_task()
    test_referenced_pattern()
    test_missing_revision()
    test_na_and_blank()
    test_edge_cases()

    # Print summary
    success = results.print_summary()

    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nVALIDATION RULES SUMMARY:")
        print("  ✅ Valid = AMM/SRM/etc. + DMC + REV/ISSUE/EXP/DEADLINE")
        print("  ✅ Valid = REFERENCED AMM/SRM/etc.")
        print("  ✅ Valid = NDT REPORT + doc ID")
        print("  ✅ Valid = SB with full number")
        print("  ✅ Valid = DATA MODULE TASK + SB")
        print("  ❌ Missing reference/reference type = DMC only (no AMM/SRM)")
        print("  ❌ Missing reference/reference type = No reference at all")
        print("  ❌ Missing revision = Has AMM/SRM but no REV/ISSUE")
        print("  • N/A = Blank or N/A entries")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)