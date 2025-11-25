# doc_validator/tools/diagnose_row_loss.py
"""
Row Loss Diagnostic Tool
Investigates why rows are being lost during Excel processing.

Usage:
    python -m doc_validator.tools.diagnose_row_loss <path_to_excel_file>
"""

import sys
import pandas as pd
import numpy as np


def diagnose_file(file_path):
    """
    Comprehensive diagnosis of Excel file reading issues.
    """
    print("=" * 70)
    print("ROW LOSS DIAGNOSTIC TOOL")
    print("=" * 70)
    print(f"\nFile: {file_path}\n")

    # (rest of file unchanged from your original)
    # ...
    # copy your whole existing implementation here
    # ...
    # I’m not rewriting it here since logic is already good.
    # Just place the current body under this path.
    # (Or you can paste your original file contents fully.)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m doc_validator.tools.diagnose_row_loss <path_to_excel_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    diagnose_file(file_path)
