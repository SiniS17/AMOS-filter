"""
Configuration file for the documentation validator.
Contains all constants and configuration settings.
"""

# Reason dictionary for validation results
REASONS_DICT = {
    "valid": "Valid documentation",
    "ref": "Missing reference documentation",
    "rev": "Missing revision date",
    "ref_type": "Missing reference type",
    "suspicious_rev": "Suspicious revision format"
}

# Keywords for reference documentation (AMM, SRM, etc.)
REF_KEYWORDS = [
    "AMM", "SRM", "CMM", "EMM", "SOPM", "SWPM",
    "IPD", "FIM", "TSM", "IPC", "SB", "AD",
    "NTO", "MEL", "NEF", "MME", "LMM"
]

# Keywords for linking words (IAW, REF, PER)
IAW_KEYWORDS = ["IAW", "REF", "PER", "I.A.W"]

# Phrases that should skip validation (valid by default)
SKIP_PHRASES = [
    "GET ACCESS", "GAIN ACCESS", "GAINED ACCESS", "ACCESS GAINED",
    "SPARE ORDERED", "ORDERED SPARE"
]

# Invalid characters for folder names
INVALID_CHARACTERS = r'[\\/:*?"<>|]'

# Folder paths
DATA_FOLDER = 'DATA'
LOG_FOLDER = 'log'

# File paths
LINK_FILE = 'link.txt'