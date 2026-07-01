"""Local configuration for Google Sheets output.

Keep real credential values outside git. Set these environment variables before
running `sentiment_dashboard.py`:

- `GOOGLE_APPLICATION_CREDENTIALS`: path to a Google service-account JSON file.
- `GOOGLE_SHEET_ID`: destination spreadsheet ID.
"""

import os

GC_SHEET_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
