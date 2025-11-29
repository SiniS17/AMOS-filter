# AMOSFilter Developer Guide

## Architecture
```
doc_validator/
├── core/          # IO + processing pipeline
├── validation/    # Rules, patterns, regex
├── interface/     # GUI + CLI
├── tools/         # Scripts
└── tests/         # Unit tests
```

## Key Components
### `main_window.py`
Controls layout and orchestrates user interactions.

### Panels
- `InputSourcePanel`
- `DateFilterPanel`

### Workers
Background processing handled via QThread wrappers.

## Adding New Rules
Modify `validation/patterns.py` and `validation/engine.py`.

## Building Executable
```
pyinstaller AMOSFilter.spec
```

