from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Any, Optional

import sys

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from doc_validator.core.drive_io import (
    authenticate_drive_api,
    download_file_from_drive,
)
from doc_validator.core.excel_pipeline import process_excel


# ---------------------------------------------------------------------
# Helper dataclass for Drive files
# ---------------------------------------------------------------------


@dataclass
class DriveFileInfo:
    file_id: str
    name: str
    mime_type: str


# ---------------------------------------------------------------------
# Stream redirection to show console output in the GUI
# ---------------------------------------------------------------------


class LogEmitter(QObject):
    message = pyqtSignal(str)


class EmittingStream:
    """
    A file-like stream that sends written text to a Qt signal.
    Used to capture print() output from existing code and mirror it
    into the GUI log window, while still printing to real stdout.
    """

    def __init__(self, emitter: LogEmitter, original_stream):
        self.emitter = emitter
        self.original_stream = original_stream

    def write(self, text: str):
        if not text:
            return
        # Emit to GUI
        self.emitter.message.emit(text)
        # Also forward to the original stream so IDE / console still see it
        if self.original_stream is not None:
            self.original_stream.write(text)

    def flush(self):
        if self.original_stream is not None:
            self.original_stream.flush()


# ---------------------------------------------------------------------
# Worker thread to process selected files
# ---------------------------------------------------------------------


class ProcessingWorker(QThread):
    """
    Background worker that:
      * Authenticates with Google Drive
      * Downloads each selected file
      * Runs the Excel processing pipeline (process_excel)
      * Emits log lines and progress updates back to the GUI
    """

    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)  # percentage (0-100), status text
    finished_with_results = pyqtSignal(list)

    def __init__(
        self,
        api_key: str,
        folder_id: str,
        selected_files: List[DriveFileInfo],
        filter_start_date: Optional[date] = None,
        filter_end_date: Optional[date] = None,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.api_key = api_key
        self.folder_id = folder_id
        self.selected_files = selected_files
        self.filter_start_date = filter_start_date
        self.filter_end_date = filter_end_date

        self._cancelled = False
        self._line_count = 0
        self._estimated_lines_per_file = 50

    # ------------------------------------------------------------------
    # Public control API
    # ------------------------------------------------------------------

    def cancel(self) -> None:
        """Request cancellation of processing."""
        self._cancelled = True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit_log_and_count(self, message: str) -> None:
        """
        Emit log message and update progress estimate based on line count.

        This keeps the progress bar moving smoothly even though the
        underlying pipeline just prints text.
        """
        if not message:
            return

        self.log_message.emit(message)

        # Count lines in this message
        lines = message.count("\n")
        if message and not message.endswith("\n"):
            lines += 1
        self._line_count += lines

        # Estimate progress percentage
        total_files = len(self.selected_files)
        if total_files > 0:
            estimated_total_lines = total_files * self._estimated_lines_per_file
            progress = min(99, int((self._line_count / estimated_total_lines) * 100))
        else:
            progress = 0

        # Extract first line as a short status text
        status = message.split("\n")[0].strip()[:60] or "Processing..."
        self.progress_updated.emit(progress, status)

    # ------------------------------------------------------------------
    # QThread.run
    # ------------------------------------------------------------------

    def run(self) -> None:  # type: ignore[override]
        """
        Run in the background thread:
          * authenticate
          * download each selected file
          * process it with process_excel
          * stream console output back to the GUI
        """
        results: List[Dict[str, Any]] = []

        # Redirect stdout so all prints from process_excel() also show up
        # in the GUI's log window.
        original_stdout = sys.stdout
        emitter = LogEmitter()
        stream = EmittingStream(emitter, original_stdout)
        emitter.message.connect(self._emit_log_and_count)
        sys.stdout = stream

        try:
            self._emit_log_and_count("Authenticating with Google Drive API...\n")
            self.progress_updated.emit(5, "Authenticating...")

            drive_service = authenticate_drive_api(self.api_key)
            self._emit_log_and_count("✓ Authentication successful.\n\n")
            self.progress_updated.emit(10, "Authentication successful")

            total = len(self.selected_files)
            self._emit_log_and_count(
                f"Processing {total} selected file(s) from Drive folder...\n"
            )

            for idx, file_info in enumerate(self.selected_files, start=1):
                if self._cancelled:
                    self._emit_log_and_count("\n⚠️ Processing cancelled by user.\n")
                    break

                # Update high-level progress per file
                if total > 0:
                    pct = int(10 + (idx - 1) / total * 85)
                else:
                    pct = 10
                self.progress_updated.emit(pct, f"[{idx}/{total}] {file_info.name}")

                # Nice separator in the log
                self._emit_log_and_count(
                    "\n" + "=" * 60 + "\n"
                    + f"[{idx}/{total}] {file_info.name}\n"
                    + "=" * 60 + "\n"
                )

                # Download to a temporary GUI folder (DATA/temp_gui)
                wp_placeholder = "temp_gui"
                local_path = download_file_from_drive(
                    drive_service,
                    file_info.file_id,
                    wp_placeholder,
                    file_info.name,
                )

                if not local_path:
                    self._emit_log_and_count(
                        f"✗ Failed to download file: {file_info.name}\n"
                    )
                    results.append(
                        {
                            "source_name": file_info.name,
                            "source_id": file_info.file_id,
                            "local_path": None,
                            "output_file": None,
                        }
                    )
                    continue

                self._emit_log_and_count(f"Local file path: {local_path}\n")

                # Run the Excel processing pipeline (date filtering handled inside)
                output_file = process_excel(
                    local_path,
                    filter_start_date=self.filter_start_date,
                    filter_end_date=self.filter_end_date,
                )

                if output_file:
                    self._emit_log_and_count(
                        f"✓ Processing finished for {file_info.name}\n"
                        f"  Output: {output_file}\n"
                    )
                else:
                    self._emit_log_and_count(
                        f"✗ Processing failed for {file_info.name}\n"
                    )

                results.append(
                    {
                        "source_name": file_info.name,
                        "source_id": file_info.file_id,
                        "local_path": local_path,
                        "output_file": output_file,
                    }
                )

            if not self._cancelled:
                self._emit_log_and_count("\n✓ All selected files have been processed.\n")
                self.progress_updated.emit(100, "Complete!")

        except Exception as exc:  # defensive
            import traceback

            self._emit_log_and_count(f"\n✗ ERROR: {exc!r}\n")
            self._emit_log_and_count(traceback.format_exc())
        finally:
            # Restore stdout no matter what
            sys.stdout = original_stdout
            # Emit final results back to the GUI
            self.finished_with_results.emit(results)
