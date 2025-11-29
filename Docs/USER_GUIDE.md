# AMOSFilter User Guide

## Overview
AMOSFilter validates aircraft maintenance Excel work packages using a modern PyQt6 GUI and a multi-stage validation engine.

## Workflow
1. Launch GUI:
   ```
   python run_gui.py
   ```
2. Select input source.
3. (Optional) Enable date filtering.
4. Select files, then click **Run Processing**.
5. View results in the `DATA/` directory.

## Panels
### Input Source Panel
- Choose local or Google Drive source.
- Browse folder.
- Open output directory.

### Date Filter Panel
- Supports absolute and relative date formats.
- Automatically clamps to file ranges.

### File Table
- Click refresh icon in the first column to reload files.
- Use search to filter file list.

### Console
- Collapsible output with detailed processing logs.

