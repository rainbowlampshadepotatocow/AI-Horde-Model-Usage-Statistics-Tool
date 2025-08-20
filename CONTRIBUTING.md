# Contributing

Thank you for taking the time to contribute to this project!

## Development setup

1. Create and activate a Python virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Install the required packages:
   ```powershell
   pip install -r requirements.txt
   ```

## Testing changes

This repository does not yet contain automated tests. After making code changes,
run the script to ensure it still works:

```powershell
python AI_Horde_Popular_Tag_Automation_Tool.py
```

The output files in `user-files` should be regenerated without errors.

## Coding style

- Keep functions small and add docstrings explaining their purpose.
- Submit pull requests against the main branch with a clear description of your changes.

