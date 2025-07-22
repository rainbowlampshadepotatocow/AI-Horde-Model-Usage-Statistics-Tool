# Contributing

Thank you for taking the time to contribute to this project!

## Development setup

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Testing changes

This repository does not yet contain automated tests. After making code changes,
run the script to ensure it still works:

```bash
python AI_Horde_Popular_Tag_Automation_Tool.py
```

The output files in `user-files` should be regenerated without errors.

## Coding style

- Format Python code with [black](https://black.readthedocs.io/) when possible.
- Keep functions small and add docstrings explaining their purpose.
- Submit pull requests against the main branch with a clear description of your changes.

