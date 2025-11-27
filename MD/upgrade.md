# AMOSFilter GUI/UX Upgrade Plan

This document consolidates all recommended improvements for the AMOSFilter PyQt6 GUI. It is intended as a development roadmap for staged enhancements, covering workflow, UX, appearance, performance, and additional features.

---

# 1. Functional Workflow Improvements

## 1.1 Add Progress Window / Progress Bar
- Display a modal progress dialog when processing files.
- Show per-file progress and overall progress.
- Display estimated remaining time.
- Add an optional **Cancel** button.
- Prevent the GUI from appearing frozen.

## 1.2 Implement Multi-threading
- Move the validation pipeline into a `QThread` or `QThreadPool` worker.
- Allow UI updates during processing.
- Improve responsiveness and prevent app from becoming unresponsive.

## 1.3 Add File Success/Failure Indicators
- After processing, each file row should show a status icon:
  - ✓ Success
  - ⚠ Issues found
  - ✖ Failed (bad Excel, missing sheet, etc.)
- Color-code rows for clarity.

## 1.4 Add "Open Output Folder" Button
- Provide a button that opens Windows Explorer to the output directory.
- Useful immediately after processing.

## 1.5 Add Refresh Button
- Manually refresh the Google Drive file list.
- Eliminates the need to restart the application.

---

# 2. UI & Layout Enhancements

## 2.1 Collapsible Console Output
- Convert the console output area into a collapsible panel.
- Optionally move it into a tab system:
  - **[Files] [Console]**
- Reduces clutter and increases visible space for the file list.

## 2.2 Add File Details Columns
Enhance the file table with more metadata:
- Google Drive modified time
- File size
- WP number (parsed)
- Row count or sheet count (optional by pre-read)

## 2.3 Search Bar for Filtering Files
- Add a search bar above the table.
- Filter rows by filename or extracted WP number.
- Instant filtering as user types.

## 2.4 Toggle-Style Checkboxes
- Replace classic checkboxes with modern toggle switches via stylesheets.
- Alternatively, make entire rows selectable.

## 2.5 Modernize Theme & Visual Style
- Apply a dark theme or custom stylesheet.
- Use rounded corners, subtle shadows, and spacing.
- Add icons for:
  - Run
  - Select All / Deselect All
  - Refresh
  - Open Folder
  - Settings

---

# 3. Quality-of-Life Features

## 3.1 Settings Panel
Add a dedicated settings window for:
- Changing Google Drive Folder ID
- Updating API key
- Toggling debug mode (write debug CSVs)
- Toggling logbook generation
- Changing output directory (optional)

## 3.2 Consistent File Path Handling
- Ensure all outputs and logs remain under the directory containing the executable.
- Use improved `config.py` logic for frozen vs source mode.

## 3.3 Improve Messages and Dialogs
- More readable success/error dialogs.
- Better multi-line formatting.
- Provide clear user instructions.

---

# 4. Architecture & Code Improvements

## 4.1 Separate GUI and Worker Logic
- Move long-running tasks into worker classes.
- Keep interface code clean and maintainable.

## 4.2 Centralized Styling
- Maintain a single `.qss` (stylesheet) file for visual design.

## 4.3 Logging Improvements
- Use Python's logging module to write console output to log files.
- Add timestamps for debugging.

---

# 5. Potential Future Enhancements

## 5.1 Drive File Browser
- Allow opening nested Google Drive folders.
- Preview file metadata before processing.

## 5.2 Drag-and-Drop Local Excel Files
- Enable local-only mode by dragging Excel files directly into the GUI.

## 5.3 Built-In Excel Viewer (Optional)
- Quick preview of the first few rows.
- Helps verify correct WP selection.

---

# 6. Priority Recommendations
To maximize impact quickly:

1. **Threaded processing + progress bar**
2. **Collapsible console**
3. **Refresh button**
4. **Open output folder button**
5. **Search bar**

These five items significantly improve usability without redesigning the entire UI.

---

# Ready for Implementation
This document is now the master upgrade plan for the AMOSFilter GUI. You can decide which features to begin with, and we will implement them step-by-step.

