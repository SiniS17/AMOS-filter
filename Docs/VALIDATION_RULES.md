# Validation Rules Documentation

Complete documentation of the validation logic used by AMOS Documentation Validator.

## Table of Contents

- [Overview](#overview)
- [Validation States](#validation-states)
- [Validation Flow](#validation-flow)
- [Reference Keywords](#reference-keywords)
- [Revision Indicators](#revision-indicators)
- [Special Patterns](#special-patterns)
- [Auto-Valid Rules](#auto-valid-rules)
- [Examples](#examples)
- [Edge Cases](#edge-cases)

---

## Overview

The AMOS Documentation Validator checks maintenance documentation to ensure compliance with aviation standards. Each row in a work order is assigned one of four validation states based on the presence and completeness of documentation references.

### Design Principles

1. **Conservative validation** - When in doubt, mark as error
2. **Auto-correction** - Fix common typos automatically
3. **Context-aware** - Consider DES field and SEQ values
4. **Special cases** - Handle NDT reports, Service Bulletins, etc.

---

## Validation States

The validator uses a **4-state system**:

### 1. Valid ✅

Row contains proper reference documentation with revision information.

**Criteria**:
- Has primary reference keyword (AMM, SRM, etc.)
- Has revision indicator (REV, ISSUE, EXP, DEADLINE)
- OR matches special pattern (NDT REPORT, SB full number, etc.)

**Examples**:
```
IAW AMM 52-11-01 REV 156
REF SRM 54-21-03 ISSUE 002
PER CMM 32-42-11 REV. 45
REF NDT REPORT NDT02-251067
DATA MODULE TASK 2, SB B787-A-21-00-0128
```

### 2. Missing reference ❌

Row lacks documentation reference when one is expected.

**Criteria**:
- No primary reference keyword found
- AND (DES field has references OR SEQ is 9.x)
- Not an auto-valid case

**Examples**:
```
REMOVED PANEL
INSPECTED COMPONENT
PERFORMED WORK STEP 1
```

### 3. Missing revision ❌

Row has reference but lacks revision information.

**Criteria**:
- Has primary reference keyword
- No revision indicator found

**Examples**:
```
IAW AMM 52-11-01
REF SRM 54-21-03
PER CMM 32-42-11
```

### 4. N/A ⚪

Entry is blank, N/A, or contains "N/A" in first 5 characters.

**Criteria**:
- Value is None
- Value is empty string
- Value starts with "N/A"

**Examples**:
```
N/A
n/a
NA
(blank)
N/A - NOT REQUIRED
```

---

## Validation Flow

### Step-by-Step Process

```
┌─────────────────────────────────────┐
│ 1. Check SEQ Auto-Valid (1.x, 2.x)  │
│    → Return "Valid"                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 2. Check Header Keywords             │
│    (CLOSE UP, JOB SET UP, etc.)     │
│    → Return "Valid"                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 3. Check for N/A or Blank           │
│    → Return "N/A" or blank           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 4. Check Skip Phrases                │
│    (GET ACCESS, SPARE ORDERED, etc.) │
│    → Return "Valid"                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 5. Auto-Correct Common Typos         │
│    (REFAMM → REF AMM, etc.)          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 6. Check Special Patterns            │
│    - REFERENCED AMM/SRM              │
│    - NDT REPORT + ID                 │
│    - DATA MODULE TASK + SB           │
│    - SB Full Number                  │
│    → Return "Valid" if match         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 7. Check for Primary Reference       │
│    (AMM, SRM, CMM, etc.)             │
└─────────────────────────────────────┘
         ↓           ↓
    NO REFERENCE    HAS REFERENCE
         ↓           ↓
┌─────────────────┐ ┌──────────────────┐
│ Check DES &     │ │ Check Revision   │
│ SEQ Context     │ │ (REV, ISSUE, etc)│
│                 │ │                  │
│ If SEQ 9.x OR   │ │ Has revision?    │
│ DES has ref:    │ │  YES → "Valid"   │
│ "Missing ref"   │ │  NO → "Missing   │
│                 │ │        revision"  │
│ Else: "Valid"   │ │                  │
└─────────────────┘ └──────────────────┘
```

### Context-Aware Logic

#### DES Field Context

The validator checks the **DES** (description) field to determine if a reference is expected:

**If DES contains any reference** (AMM, DMC, NDT REPORT, etc.):
- Rows without references → `Missing reference`

**If DES is empty or has no reference**:
- Rows without references → `Valid` (reference not required)

**Example**:
```
DES: "IAW AMM 52-11-01 REV 156"

Row 1: "REMOVED PANEL" → Missing reference (DES has reference)
Row 2: "CLOSE UP" → Valid (header keyword)
```

#### SEQ 9.x Special Handling

For SEQ values starting with "9." (closeup tasks):
- **Always enforce** reference check, regardless of DES
- Common pattern: "REFER RESULT WT X" → Valid (skip phrase)

---

## Reference Keywords

### Primary Reference Types (20+ supported)

| Keyword | Full Name | Example |
|---------|-----------|---------|
| AMM | Aircraft Maintenance Manual | IAW AMM 52-11-01 REV 156 |
| SRM | Structural Repair Manual | REF SRM 54-21-03 ISSUE 002 |
| CMM | Component Maintenance Manual | PER CMM 32-42-11 REV 45 |
| EMM | Engine Maintenance Manual | IAW EMM 72-54-00 REV 41 |
| MEL | Minimum Equipment List | REF MEL 33-44-01-02A DEADLINE: 01/11/2025 |
| NEF | Non-Essential Function | IAW NEF-VNA-00 EXP 03JAN25 |
| SB | Service Bulletin | IAW SB B787-A-21-00-0128-02A |
| AD | Airworthiness Directive | PER AD 2024-01-05 |
| MME | Maintenance Manual Engine | REF MME 3.32.7.5 REV 02 |
| DDG | Dispatch Deviation Guide | IAW DDG 38-30-01A REV 158 |
| SOPM | Standard Operating Procedures Manual | - |
| SWPM | Standard Wiring Practices Manual | - |
| IPD | Illustrated Parts Data | - |
| FIM | Fault Isolation Manual | - |
| TSM | Troubleshooting Manual | - |
| IPC | Illustrated Parts Catalog | - |
| NTO | Non-Technical Order | - |
| NTM | Non-Technical Manual | - |
| DMC | Data Module Code | IAW AMM DMC-B787-A-52-09-01-00A-280A-A |
| DWG | Drawing | REF DWG 123-456 REV A |

### Linking Keywords

These words connect the reference to the document:

- `IAW` - In Accordance With
- `REF` - Reference
- `PER` - Per
- `I.A.W` - In Accordance With (alternate)

**Note**: Linking keywords are **not required** for validation but help identify references.

---

## Revision Indicators

### Standard Revision Formats

| Format | Pattern | Example |
|--------|---------|---------|
| REV | `REV \d+` | REV 156 |
| REV: | `REV: \d+` | REV: 156 |
| REV. | `REV. \d+` | REV. 156 |
| ISSUE | `ISSUE \d+` | ISSUE 002 |
| ISSUED SD | `ISSUED SD \d+` | ISSUED SD 01 |
| TAR | `TAR \d+` | TAR 123 |

### Date-Based Revisions

| Format | Pattern | Example |
|--------|---------|---------|
| EXP | `EXP 03JAN25` | EXP 03JAN25 |
| EXP: | `EXP: 28/06/2026` | EXP: 28/06/2026 |
| DEADLINE | `DEADLINE: 01/11/2025` | DEADLINE: 01/11/2025 |
| DUE DATE | `DUE DATE 15-JAN-2025` | DUE DATE 15-JAN-2025 |
| REV DATE | `REV DATE 2024-12-31` | REV DATE 2024-12-31 |

**Supported Date Formats**:
- `DD-MMM-YY` (03JAN25)
- `DD/MM/YYYY` (28/06/2026)
- `DD-MM-YYYY` (01-11-2025)
- `YYYY-MM-DD` (2024-12-31)

---

## Special Patterns

### 1. REFERENCED Pattern

Text that references documentation in header/description.

**Pattern**: `REFERENCED AMM|SRM|CMM|etc.`

**Examples**:
```
✅ MAKE SURE THAT YOU OBEY ALL THE WARNINGS IN THE REFERENCED AMM TASKS
✅ FOLLOW THE REFERENCED SRM PROCEDURES
✅ IN ACCORDANCE WITH REFERENCED CMM INSTRUCTIONS
```

**Why Valid**: Reference details are in the header or work package description.

### 2. NDT REPORT Pattern

Non-Destructive Testing reports with document IDs.

**Pattern**: `NDT REPORT [A-Z0-9\-]+`

**Examples**:
```
✅ REF NDT REPORT NDT02-251067
✅ IAW NDT REPORT NDT-2024-123456
✅ PER NDT REPORT RT-45678, LEFT SIDE SOB FITTING
```

**Why Valid**: NDT reports are self-documenting; the report ID is sufficient.

### 3. Service Bulletin Full Number

SB with complete part number (no explicit REV required).

**Pattern**: `SB [A-Z0-9]{1,5}-[A-Z0-9\-]+`

**Examples**:
```
✅ IAW SB B787-A-21-00-0128-02A-933B-D
✅ REF SB B737-52-1234-A
✅ PER SB A320-27-5678-B
```

**Why Valid**: Full SB numbers include version information in the suffix.

### 4. DATA MODULE TASK Pattern

Data module task references with SB.

**Pattern**: `DATA MODULE TASK \d+.*SB [A-Z0-9\-]+`

**Examples**:
```
✅ IN ACCORDANCE WITH DATA MODULE TASK 2, SB B787-A-21-00-0128-02A-933B-D
✅ PER DATA MODULE TASK 5, SB B737-52-1234-A
```

**Why Valid**: Combination provides complete reference.

### 5. Work Order Cross-References

References to other work orders or work tasks.

**Patterns**:
- `REFER RESULT WT \d+` - Work Task reference
- `WO: \d+` - Work Order reference
- `WO.*EOD` - Work Order with Engineering Order

**Examples**:
```
✅ REFER RESULT WT 17
✅ REFER (WO: 7'646'970) EOD-787-57-00-0002-R00
✅ SEE WO: 8123456
```

**Why Valid**: Cross-references to other documented work are acceptable.

---

## Auto-Valid Rules

### 1. SEQ Auto-Valid

Certain sequence numbers are automatically marked as Valid:

| SEQ Pattern | Description | Rationale |
|-------------|-------------|-----------|
| `1.x` | Initial setup | Procedural steps |
| `2.x` | Preparation | Procedural steps |
| `3.x` | Access | Opening panels/access |
| `10.x` | Closeup | Closing panels/access |

**Examples**:
```
SEQ 1.1  → Valid (setup)
SEQ 2.5  → Valid (preparation)
SEQ 3.12 → Valid (access)
SEQ 10.3 → Valid (closeup)
SEQ 4.1  → Normal validation applies
```

### 2. Header Skip Keywords

Tasks with these headers are automatically Valid:

- `CLOSE UP` / `CLOSEUP` / `CLOSE-UP`
- `JOB SET UP` / `JOB SETUP` / `JOB SET-UP`
- `OPEN ACCESS` / `OPENACCESS`
- `CLOSE ACCESS` / `CLOSEACCESS`
- `GENERAL`

**Examples**:
```
Header: "JOB SET UP" → Valid
Header: "CLOSE UP" → Valid
Header: "GENERAL TASKS" → Valid
```

### 3. Skip Phrases

Text containing these phrases is automatically Valid:

- `GET ACCESS` / `GAIN ACCESS` / `GAINED ACCESS` / `ACCESS GAINED`
- `SPARE ORDERED` / `ORDERED SPARE`
- `OBEY ALL` / `FOLLOW ALL` / `COMPLY WITH`
- `MEASURE AND RECORD`
- `SET TO INACTIVE`
- `SEE FIGURE` / `REFER TO FIGURE`

**Examples**:
```
✅ GET ACCESS TO PANEL 123
✅ SPARE ORDERED FOR REPLACEMENT
✅ OBEY ALL WARNINGS IN THE REFERENCED MANUAL
```

---

## Examples

### Valid Examples

```
# Standard references with revision
✅ IAW AMM 52-11-01 REV 156
✅ REF SRM 54-21-03 ISSUE 002
✅ PER CMM 32-42-11 REV. 45
✅ REFER TO 787 AMM 29-11-00 REV 159

# Date-based revisions
✅ IAW NEF-VNA-00, EXP 03JAN25
✅ REF MEL 33-44-01-02A, DEADLINE: 01/11/2025
✅ PER MME 3.32.7.5 REV 02, DEADLINE: 01/11/2025

# Special patterns
✅ REF NDT REPORT NDT02-251067, LEFT SIDE SOB FITTING
✅ IAW SB B787-A-21-00-0128-02A-933B-D
✅ DATA MODULE TASK 2, SB B787-A-21-00-0128-02A-933B-D
✅ REFERENCED AMM TASKS

# Auto-valid
✅ SEQ 1.1: INITIAL SETUP
✅ Header: "CLOSE UP" - ANY TEXT
✅ GET ACCESS TO FUEL TANK

# With DMC
✅ IAW AMM TASK DMC-B787-A-52-09-01-00A-280A-A REV 158
✅ REF SRM DMC-B787-A-27-81-04-01A-520A-A REV 158

# Typos auto-corrected
✅ REFAMM52-11-01REV156 → REF AMM 52-11-01 REV 156
```

### Missing Reference Examples

```
❌ REMOVED PANEL (when DES has reference)
❌ INSPECTED COMPONENT
❌ PERFORMED WORK STEP 1
❌ DONE SATIS
❌ RE-INSPECTED SATIS
❌ C/O WORK STEP 1 SATIS
```

### Missing Revision Examples

```
❌ IAW AMM 52-11-01 (no REV)
❌ REF SRM 54-21-03 (no ISSUE)
❌ PER CMM 32-42-11 (no REV)
❌ IAW AMM DMCB787-A-53-01-01-00B-520A-A (DMC but no REV)
```

### N/A Examples

```
⚪ N/A
⚪ n/a
⚪ NA
⚪ (blank cell)
⚪ N/A - NOT REQUIRED
```

---

## Edge Cases

### Case 1: DMC Without AMM/SRM Prefix

**Input**: `DMCB787-A-53-01-01-00B-520A-A REV 45`

**Result**: `Missing reference`

**Reason**: DMC alone doesn't specify document type (AMM, SRM, etc.)

**Fix**: Add document type prefix:
```
✅ IAW AMM DMC B787-A-53-01-01-00B-520A-A REV 45
```

### Case 2: Reference in Description Only

**Input**:
- DES: `IAW AMM 52-11-01 REV 156`
- Text: `PERFORMED WORK STEP`

**Result**: `Missing reference` (if DES has reference)

**Reason**: Each row should have its own reference, or use "REFERENCED" pattern.

**Fix**: Either:
```
✅ Text: "IAW REFERENCED AMM TASK"
✅ Text: "IAW AMM 52-11-01 REV 156"
```

### Case 3: Multiple Spaces/Typos

**Input**: `REFAMM  52-11-01REV156`

**Result**: `Valid` (after auto-correction)

**Auto-corrected to**: `REF AMM 52-11-01 REV 156`

### Case 4: SEQ 9.x with No Reference

**Input**:
- SEQ: `9.1`
- Text: `PERFORMED CLOSEUP`
- DES: (empty)

**Result**: `Missing reference`

**Reason**: SEQ 9.x always requires reference check, regardless of DES.

**Fix**:
```
✅ REFER RESULT WT 8 (cross-reference, skip phrase)
✅ IAW REFERENCED AMM CLOSEUP TASKS
```

### Case 5: Lowercase References

**Input**: `iaw amm 52-11-01 rev 156`

**Result**: `Valid`

**Reason**: Validation is case-insensitive.

### Case 6: Multiple References in One Row

**Input**: `IAW AMM 52-11-01 REV 156 AND SRM 54-21-03 ISSUE 002`

**Result**: `Valid`

**Reason**: At least one complete reference is present.

### Case 7: Partial Revision Numbers

**Input**: `IAW AMM 52-11-01 REV`

**Result**: `Missing revision`

**Reason**: "REV" keyword present but no number follows.

**Fix**: Add complete revision:
```
✅ IAW AMM 52-11-01 REV 156
```

---

## Validation Statistics

Typical results for well-maintained data:

| State | Expected % | Acceptable Range |
|-------|-----------|------------------|
| Valid | 85-95% | 80-100% |
| N/A | 0-5% | 0-10% |
| Missing reference | 2-8% | 0-15% |
| Missing revision | 2-8% | 0-15% |
| **Error Rate** | **5-10%** | **0-20%** |

### Error Rate Interpretation

- **0-5%**: Excellent data quality
- **5-10%**: Good data quality
- **10-20%**: Acceptable, review common errors
- **20%+**: Poor data quality, requires review

---

## Testing

### Running Validation Tests

```bash
# Run all tests
python -m doc_validator.tests.test_validators

# Run real-world data tests
python -m doc_validator.tests.test_real_world_data
```

### Adding New Test Cases

Edit `doc_validator/tests/test_real_world_data.py`:

```python
def test_my_new_pattern():
    """Test new validation pattern"""
    results.assert_equal(
        check_ref_keywords("YOUR TEST TEXT"),
        "Valid",  # Expected result
        "Description of test case"
    )
```

---

## Configuration

### Customizing Validation Rules

Edit `doc_validator/validation/constants.py`:

```python
# Add new reference keywords
REF_KEYWORDS = [
    "AMM", "SRM", "CMM",
    # Add your custom keywords here
    "CUSTOM_MANUAL", "MY_DOC"
]

# Add new skip phrases
SKIP_PHRASES = [
    "GET ACCESS", "SPARE ORDERED",
    # Add your custom phrases here
    "MY_SKIP_PHRASE"
]

# Add new header skip keywords
HEADER_SKIP_KEYWORDS = [
    "CLOSE UP", "JOB SET UP",
    # Add your custom headers here
    "MY_HEADER"
]
```

### Customizing Patterns

Edit `doc_validator/validation/patterns.py`:

```python
# Add custom revision pattern
MY_REV_PATTERN = re.compile(r'\bMYREV\s*\d+\b', re.IGNORECASE)

# Add to has_revision() function in helpers.py
if MY_REV_PATTERN.search(text):
    return True
```

---

## FAQs

**Q: Why is "DMC only" marked as Missing reference?**

A: DMC specifies a document code but not the document type (AMM, SRM, etc.). Add the type prefix.

**Q: Why are SEQ 1.x/2.x/3.x/10.x auto-valid?**

A: These are procedural steps (setup, preparation, access, closeup) that don't require specific documentation.

**Q: Can I disable auto-correction?**

A: Not currently, but you can modify `fix_common_typos()` in `helpers.py`.

**Q: How do I add support for new document types?**

A: Add keywords to `REF_KEYWORDS` in `constants.py` and run tests.

**Q: What if validation is too strict?**

A: Add your patterns to `SKIP_PHRASES` or modify the validation logic in `engine.py`.

---

## References

- ISO 9001 Quality Management
- FAA Regulations Part 43
- EASA Part-145 Maintenance Organization
- Boeing 787 AMM Documentation Standards

---

**For implementation details, see**:
- `doc_validator/validation/engine.py` - Main validation logic
- `doc_validator/validation/helpers.py` - Helper functions
- `doc_validator/validation/patterns.py` - Regex patterns
- `doc_validator/validation/constants.py` - Configuration