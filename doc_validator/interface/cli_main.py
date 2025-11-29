# doc_validator/interface/cli_main.py
"""
Command-line interface for the Documentation Validator.

Replaces the old top-level `main.py` script. This module:
- Reads credentials (API key + folder ID)
- Calls the high-level processing pipeline
- Prints a concise summary for CLI users
"""

from __future__ import annotations

import sys
from typing import List

from doc_validator.config import LINK_FILE
from doc_validator.core.pipeline import process_from_credentials_file


def _cli_logger(message: str) -> None:
    """Logger function passed to the pipeline (currently just prints)."""
    print(message)


def main(argv: List[str] | None = None) -> int:
    """
    Main CLI entry point.

    Usage:
        python -m doc_validator.interface.cli_main
        python run_cli.py
        python -m doc_validator.interface.cli_main path/to/credentials.txt
        python -m doc_validator.interface.cli_main path/to/credentials.txt --no-asc
        python -m doc_validator.interface.cli_main --no-asc

    If a path is provided as the first argument (excluding --no-asc),
    it will be used as the credentials file (instead of the default LINK_FILE).

    The optional flag:
        --no-asc   disables Action Step Control (ASC) sheet generation.
    """
    if argv is None:
        argv = sys.argv[1:]

    print("=" * 60)
    print("Documentation Validator - BATCH MODE")
    print("=" * 60 + "\n")

    # Defaults
    enable_asc = True
    credentials_path = LINK_FILE

    # Very simple argument parsing:
    #   []                         -> default LINK_FILE, ASC enabled
    #   [creds]                    -> creds, ASC enabled
    #   [--no-asc]                 -> default LINK_FILE, ASC disabled
    #   [creds, --no-asc]          -> creds, ASC disabled
    if argv:
        # Check for --no-asc as the last argument
        if argv[-1] == "--no-asc":
            enable_asc = False
            argv = argv[:-1]

        if argv:
            # First remaining arg is the credentials path
            credentials_path = argv[0]
            print(f"Using credentials file from CLI argument: {credentials_path}")
        else:
            # No credentials path left after stripping --no-asc
            print(f"Using default credentials file from config: {credentials_path}")
    else:
        print(f"Using default credentials file from config: {credentials_path}")

    try:
        # Run the high-level pipeline
        results = process_from_credentials_file(
            credentials_path=credentials_path,
            logger=_cli_logger,
            enable_action_step_control=enable_asc,
        )

    except Exception as e:  # pragma: no cover - runtime error path
        print("\n" + "=" * 60)
        print("❌ ERROR DURING PROCESSING")
        print("=" * 60)
        print(str(e))
        return 1

    # No files processed (pipeline already printed details)
    if not results:
        print("\n" + "=" * 60)
        print("NO FILES WERE PROCESSED")
        print("=" * 60)
        return 0

    # Build summary similar to old main.py
    processed_files = [r for r in results if r.get("output_file")]
    failed_files = [r for r in results if not r.get("output_file")]

    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Total files: {len(results)}")
    print(f"   ✅ Successful: {len(processed_files)}")
    print(f"   ❌ Failed: {len(failed_files)}")

    if processed_files:
        print(f"\n✅ Successfully processed files:")
        for i, r in enumerate(processed_files, 1):
            print(f"   {i}. {r['source_name']}")
            print(f"      → {r['output_file']}")

    if failed_files:
        print(f"\n❌ Failed files:")
        for i, r in enumerate(failed_files, 1):
            print(f"   {i}. {r['source_name']}")

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
