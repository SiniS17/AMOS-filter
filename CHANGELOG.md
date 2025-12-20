# Changelog

All notable changes to AMOS Documentation Validator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Web-based interface
- API endpoint for real-time validation
- Machine learning for reference detection
- Support for additional aircraft types
- Integration with more maintenance systems

---

## [1.25.0] - 2024-12-21

### Added
- **Action Step Control (ASC)** feature for chronological verification
- ASC generates additional sheet with timing validation
- Per-WO summary sheet showing violation counts
- Optional ASC toggle in GUI and CLI (`--no-asc` flag)
- Monthly logbook tracking (`DATA/log/logbook_YYYY_MM.xlsx`)
- Work order (WO) and work task (WT) cross-reference detection
- EOD (Engineering Order) pattern recognition
- SEQ 9.x special handling for closeup tasks
- Debug folder with input/output comparison for row loss diagnosis

### Changed
- **BREAKING**: Validation now returns 4 states instead of 5
  - Removed "Missing reference type" state
  - Simplified to: Valid, Missing reference, Missing revision, N/A
- Context-aware validation using DES field
- Improved date filtering with two-stage process (file range + user range)
- Enhanced GUI with modern dark theme
- Collapsible console output in GUI
- Better progress tracking with line-count estimation

### Fixed
- Row loss issues during processing
- Date filter edge cases
- False positives for DMC-only entries
- GUI responsiveness during processing
- File refresh in GUI

---

## [1.20.0] - 2024-11-15

### Added
- Google Drive integration for cloud file processing
- Batch processing for multiple Excel files
- Date filtering feature with relative date support
- Smart date input widget with calendar picker
- Input source panel (Local / Google Drive)
- File details in table (size, modified date, status)
- Search/filter functionality for file list
- Refresh button for file list

### Changed
- Redesigned GUI with left/right split layout
- Improved file selection UX with checkboxes
- Enhanced console output with color coding
- Better error messages and validation feedback

### Fixed
- Memory leaks in background processing
- GUI freezing during large file processing
- Date parsing edge cases

---

## [1.15.0] - 2024-10-01

### Added
- SEQ auto-valid feature (1.x, 2.x, 3.x, 10.x)
- Header keyword detection (CLOSE UP, JOB SET UP, etc.)
- Skip phrase detection (GET ACCESS, SPARE ORDERED, etc.)
- "REFERENCED AMM/SRM" pattern support
- NDT REPORT pattern (no explicit REV required)
- Service Bulletin full number pattern
- DATA MODULE TASK pattern

### Changed
- Improved validation logic with special patterns
- Better handling of edge cases
- More flexible revision detection

### Fixed
- False negatives for valid references
- Typo auto-correction improvements

---

## [1.10.0] - 2024-08-15

### Added
- GUI interface with PyQt6
- Real-time console output in GUI
- Progress bar with status updates
- File selection dialog
- Output folder quick access button

### Changed
- Separated GUI and CLI into different modules
- Improved code organization
- Better separation of concerns

---

## [1.05.0] - 2024-07-01

### Added
- Support for 20+ document types (AMM, SRM, CMM, etc.)
- Date-based revision formats (EXP, DEADLINE)
- Auto-correction of common typos
- Detailed validation statistics

### Changed
- Improved validation engine performance
- Better error handling
- More detailed logging

### Fixed
- Column name detection issues
- Excel file format compatibility

---

## [1.00.0] - 2024-05-15

### Added
- Initial release
- Basic validation for AMM/SRM references
- REV and ISSUE detection
- Excel file processing
- Command-line interface
- Basic error reporting

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|-------------|--------------|
| 1.25.0 | 2024-12-21 | Action Step Control, Logbook, Enhanced validation |
| 1.20.0 | 2024-11-15 | Google Drive, Batch processing, Date filtering |
| 1.15.0 | 2024-10-01 | SEQ auto-valid, Special patterns |
| 1.10.0 | 2024-08-15 | GUI interface |
| 1.05.0 | 2024-07-01 | 20+ document types, Date revisions |
| 1.00.0 | 2024-05-15 | Initial release |

---

## Migration Guides

### Migrating from 1.20 to 1.25

**Breaking Changes**:
- Validation states reduced from 5 to 4
- "Missing reference type" removed

**What You Need to Do**:
1. Update any scripts that check for "Missing reference type"
2. Replace with checks for "Missing reference"
3. Review validation rules documentation

**Example**:
```python
# Old (v1.20)
if result == "Missing reference type":
    # Handle DMC-only case

# New (v1.25)
if result == "Missing reference":
    # Now includes DMC-only cases
```

**New Features to Try**:
- Enable Action Step Control for chronological verification
- Check monthly logbook for statistics
- Use SEQ 9.x for closeup tasks

---

## Deprecation Notices

### Deprecated in 1.25
- `create_log_file()` function in `excel_io.py`
  - Replaced by `append_to_logbook()`
  - Legacy .txt logs no longer generated by default
  - Will be removed in v2.0.0

### Deprecated in 1.20
- None

---

## Known Issues

### Current (v1.25)
- Very large files (>100MB) may be slow
- Google Drive rate limits may affect batch downloads
- Some date formats may not be recognized (workaround: use YYYY-MM-DD)

### Fixed in Future Releases
- Web interface (planned for v2.0)
- Real-time API (planned for v2.0)
- Performance improvements for large files (planned for v1.26)

---

## Upgrade Instructions

### Standard Upgrade

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt
pip install -r requirements-gui.txt

# Run tests
python -m doc_validator.tests.test_validators
```

### Clean Upgrade

```bash
# Uninstall old version
pip uninstall doc_validator

# Reinstall
pip install -r requirements.txt
pip install -r requirements-gui.txt
```

---

## Contributors

### v1.25
- Added Action Step Control feature
- Implemented logbook tracking
- Improved validation logic

### v1.20
- Implemented Google Drive integration
- Added batch processing
- Created date filtering feature

### v1.15
- Designed special pattern detection
- Added SEQ auto-valid feature
- Improved validation accuracy

### All Versions
- [Your Name] - Project creator and maintainer
- [Contributors list from GitHub]

---

## Support

For questions about changes in specific versions:
- Check the [User Guide](docs/USER_GUIDE.md)
- Review [Validation Rules](docs/VALIDATION_RULES.md)
- Ask in [GitHub Discussions](https://github.com/yourusername/amos-validator/discussions)

For bug reports related to specific versions:
- Open an [Issue](https://github.com/yourusername/amos-validator/issues)
- Include version number
- Mention if regression from previous version

---

## Links

- [GitHub Releases](https://github.com/yourusername/amos-validator/releases)
- [Documentation](docs/)
- [Issue Tracker](https://github.com/yourusername/amos-validator/issues)