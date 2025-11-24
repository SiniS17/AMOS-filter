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
LINK_FILE = 'link.txt'