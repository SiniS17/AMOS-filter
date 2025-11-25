from pathlib import Path
import sys


def get_base_dir() -> Path:
    """
    Return the base directory of the app.

    - When running as a PyInstaller EXE (onedir or onefile):
        base_dir = folder containing the executable.
    - When running from source:
        base_dir = project root (parent of `doc_validator`).
    """
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        return Path(sys.executable).resolve().parent

    # Running from source: .../project_root/doc_validator/config.py
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()

# --- LINK FILE ---

# Primary location: bin/link.txt (inside dist folder when frozen)
bin_link = BASE_DIR / "bin" / "link.txt"
root_link = BASE_DIR / "link.txt"  # fallback for dev mode

if bin_link.is_file():
    LINK_FILE = str(bin_link)
else:
    LINK_FILE = str(root_link)

# --- DATA / LOG FOLDERS ---

DATA_FOLDER = str((BASE_DIR / "DATA").resolve())
LOG_FOLDER = "log"  # subfolder name under each WP folder or DATA/log if you use it

# other constants (REF_KEYWORDS, INVALID_CHARACTERS, etc.) stay the same


""" 
Configuration file for the documentation validator.
Contains all constants and configuration settings.

UPDATED: Added HEADER_SKIP_KEYWORDS for wo_text_action.header filtering
"""

# Reason dictionary for validation results (SIMPLIFIED - 3 states only)
REASONS_DICT = {
    "valid": "Valid documentation with reference and revision",
    "ref": "Missing reference documentation (includes incomplete references)",
    "rev": "Missing revision date"
}

# Keywords for reference documentation (AMM, SRM, etc.)
# These are the PRIMARY references that count as valid
REF_KEYWORDS = [
    "AMM", "SRM", "CMM", "EMM", "SOPM", "SWPM",
    "IPD", "FIM", "TSM", "IPC", "SB", "AD",
    "NTO", "MEL", "NEF", "MME", "LMM", "NTM", "DWG", "AIPC", "AMMS",
    "DDG", "VSB", "BSI", "FIM", "FTD", "TIPF", "MNT", "EEL VNA", "EO EOD"  # NEW: Additional document types
]

# Keywords for linking words (IAW, REF, PER)
IAW_KEYWORDS = ["IAW", "REF", "PER", "I.A.W"]

# Phrases that should skip validation (valid by default)
# IMPORTANT: Only include phrases that are PURELY procedural and NEVER contain references
# Removed: "MAKE SURE", "ENSURE THAT", "CHECK THAT" (too broad, can appear with incomplete refs)
SKIP_PHRASES = [
    "GET ACCESS", "GAIN ACCESS", "GAINED ACCESS", "ACCESS GAINED",
    "SPARE ORDERED", "ORDERED SPARE",
    "OBEY ALL", "FOLLOW ALL", "COMPLY WITH", "MEASURE AND RECORD", "SET TO INACTIVE", "SEE FIGURE",
    "REFER TO FIGURE"
]

# NEW: Keywords in wo_text_action.header that should mark row as Valid automatically
# These are procedural/setup tasks that don't require documentation references
HEADER_SKIP_KEYWORDS = [
    "CLOSE UP", "CLOSEUP",
    "JOB SET UP", "JOB SETUP", "JOBSETUP",
    "OPEN ACCESS", "OPENACCESS",
    "CLOSE ACCESS", "CLOSEACCESS",
    "GENERAL", "JOB SET-UP", "JOB CLOSE-UP"
]

# Invalid characters for folder names
INVALID_CHARACTERS = r'[\\/:*?"<>|]'

# Folder paths
DATA_FOLDER = 'DATA'
LOG_FOLDER = 'log'

# File paths
LINK_FILE = 'bin/link.txt'
