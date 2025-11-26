from pathlib import Path

# ------------------------------------------------------------
# Base directory (project root during development, and
# dist/AMOSFilter/ when built with PyInstaller onedir)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------
# Credentials file
# ------------------------------------------------------------
# You already placed link.txt inside a bin/ folder at project root.
# With PyInstaller onedir + --add-data "bin;bin", the same folder
# will appear beside AMOSFilter.exe.
#
# Final structure after building:
#   dist/AMOSFilter/
#       AMOSFilter.exe
#       bin/
#           link.txt
#
# So this path works both in development and in the built app.
# ------------------------------------------------------------
LINK_FILE = str(BASE_DIR / "bin" / "link.txt")

# ------------------------------------------------------------
# Data folder
# ------------------------------------------------------------
# The program will create a DATA/ folder next to the .exe
# or next to your project root in dev mode.
# ------------------------------------------------------------
DATA_FOLDER = str(BASE_DIR / "DATA")

# Subfolder name for logs inside each WP folder
LOG_FOLDER = "log"

# ------------------------------------------------------------
# Other constants (just examples)
# ------------------------------------------------------------
INVALID_CHARACTERS = r'[\\/*?:"<>|]'  # for cleaning folder names
