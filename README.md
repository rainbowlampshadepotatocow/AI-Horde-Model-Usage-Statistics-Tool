# AI-Horde-Popular-Tag-Automation-Tool

This repository contains a small script for updating the model whitelist used
by the AI Horde. By default all input and output files are placed in a folder
named `user-files` inside the project directory. Copy your `models.csv` file
into this directory before running the script. After execution, the updated
CSV and the downloaded usage data will also be saved there.

The script also creates `usage_data.xlsx` after fetching usage information.
This workbook contains separate sheets named **Day**, **Month**, and **Total**,
mirroring the structure of `text_models_tidy.xlsx` from the Examples folder.
Each sheet is formatted as an Excel table for easier filtering and sorting.

## Requirements:
- Microsoft Excel
- Python
- run `pip install -r requirements.txt`
    - Will install:
        - requests  (for getting usage stats)
        - pandas    (for performing magic on the data)
        - openpyxl  (for writing to Excel)