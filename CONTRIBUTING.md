# Contributing to win-disk-doctor

Small, focused contributions are welcome.

## Development setup
```bash
git clone https://github.com/SQasimHamdani/win-disk-doctor.git
cd win-disk-doctor
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Adding a location
Add a `Location` to `src/win_disk_doctor/locations.py`. Be conservative with the label:
- `safe`: only data that is rebuilt or downloaded again, never anything a person made.
- `check first`: may hold something someone wants, or removal depends on timing.
- `leave alone`: removing it by hand can break Windows or programs.

## Rules
- Tests must use made-up folders (`tests/fakes.py`), never real system locations.
- The tool is read-only. Open an issue before proposing anything that changes files.
- No personal paths, user names or file names in issues, tests or screenshots.

Be respectful: see the [Code of Conduct](CODE_OF_CONDUCT.md).
