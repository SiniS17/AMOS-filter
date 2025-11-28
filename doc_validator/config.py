from pathlib import Path
import sys

# ------------------------------------------------------------
# Determine base directory:
# - In development: project root
# - In onedir PyInstaller build: folder containing AMOSFilter.exe
# ------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # EXE mode
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Source mode
    BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------
# Credentials file (always under bin/)
# ------------------------------------------------------------
LINK_FILE = str(BASE_DIR / "bin" / "link.txt")

# ------------------------------------------------------------
# Data folder (always created next to exe)
# ------------------------------------------------------------
DATA_FOLDER = str(BASE_DIR / "DATA")
Path(DATA_FOLDER).mkdir(exist_ok=True)

# ------------------------------------------------------------
# Input folder (for local Excel files)
# ------------------------------------------------------------
INPUT_FOLDER = str(BASE_DIR / "INPUT")
Path(INPUT_FOLDER).mkdir(exist_ok=True)

# Subfolder for log inside each WP folder
LOG_FOLDER = "log"

# ------------------------------------------------------------
# Other constants
# ------------------------------------------------------------
INVALID_CHARACTERS = r'[\\/*?:"<>|]'