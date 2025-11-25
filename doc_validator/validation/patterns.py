# doc_validator/validation/patterns.py

import re
from doc_validator.config import REF_KEYWORDS

# Document ID pattern
DOC_ID_PATTERN = re.compile(r'\b[A-Z0-9]{1,4}[0-9A-Z\-]{0,}\d+\b', re.IGNORECASE)

# DMC pattern - specifically for Data Module Code detection
DMC_PATTERN = re.compile(r'\bDMC-?[A-Z0-9\-]+\b', re.IGNORECASE)

# B787 document pattern (without AMM/SRM prefix)
B787_DOC_PATTERN = re.compile(r'\bB787-[A-Z0-9\-]+\b', re.IGNORECASE)

# Data Module Task text pattern (without number)
DATA_MODULE_TASK_TEXT = re.compile(r'\bDATA\s+MODULE\s+TASK\b', re.IGNORECASE)

# Document type words pattern
DOC_TYPE_WORDS = re.compile(
    r'\b(?:SB|NDT\s+REPORT|NDT|SERVICE\s+BULLETIN)\b',
    re.IGNORECASE,
)

# Standard revision patterns
REV_PATTERN = re.compile(r'\bREV\s*[:\.]?\s*\d+\b', re.IGNORECASE)
ISSUE_PATTERN = re.compile(r'\bISSUE\s*[:\.]?\s*\d+\b', re.IGNORECASE)
ISSUED_SD_PATTERN = re.compile(r'\bISSUED\s+SD\.?\s*\d+\b', re.IGNORECASE)
TAR_PATTERN = re.compile(r'\bTAR\s*\d+\b', re.IGNORECASE)

# Date-based revision patterns
EXP_DATE_PATTERN = re.compile(
    r'\b(?:EXP|DEADLINE|DUE\s+DATE|REV\s+DATE)\s*[:\.]?\s*\d{1,2}[-/]?[A-Z]{3}[-/]?\d{2,4}\b',
    re.IGNORECASE,
)
DEADLINE_DATE_PATTERN = re.compile(
    r'\b(?:EXP|DEADLINE|DUE\s+DATE|REV\s+DATE)\s*[:\.]?\s*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b',
    re.IGNORECASE,
)

# Pattern for "REFERENCED AMM/SRM/etc."
REFERENCED_PATTERN = re.compile(
    r'\bREFERENCED\s+(?:' + '|'.join(re.escape(k) for k in REF_KEYWORDS) + r')\b',
    re.IGNORECASE,
)

# Special document patterns (no explicit REV required)
NDT_REPORT_PATTERN = re.compile(r'\bNDT\s+REPORT\s+[A-Z0-9\-]+\b', re.IGNORECASE)
SB_FULL_PATTERN = re.compile(r'\bSB\s+[A-Z0-9]{1,5}-[A-Z0-9\-]+\b', re.IGNORECASE)
DATA_MODULE_TASK_PATTERN = re.compile(r'\bDATA\s+MODULE\s+TASK\s+\d+\b', re.IGNORECASE)
