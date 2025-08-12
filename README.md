# SKKNI Validator (GitHub Actions version)

This repo runs a daily job (07:05 WIB) to read a Google Sheet, look up SKKNI status via SerpAPI, and write a "Status" column back.

## Setup (beginner friendly)

1) **Create the repository** on GitHub and upload these files.

2) **Create Secrets** in *Settings → Secrets and variables → Actions → New repository secret*:
   - `SERPAPI_API_KEY`: your SerpAPI key.
   - `GSHEETS_JSON`: paste the full contents of your Google service account JSON (multi-line OK).

3) **Share the Google Sheet** with the `client_email` found inside your JSON (Editor access).

4) The workflow runs every day at 07:05 WIB (00:05 UTC). You can also run it manually: *Actions → daily-skkni → Run workflow*.

## Files
- `main.py` — the script.
- `requirements.txt` — Python dependencies.
- `.github/workflows/daily.yml` — scheduler.

## Adjustments
- If your Sheet key or tab IDs differ, change them in the workflow `env:` or set as repo variables.
- If you want a different time, update the cron in `.github/workflows/daily.yml`. Remember: **GitHub uses UTC**.

## Troubleshooting
- **403/permission**: The Sheet must be shared with the service account email in `creds.json`.
- **SerpAPI errors/rate limit**: consider a higher tier or increase the delay between requests.
- **JSON not found**: ensure `GSHEETS_JSON` secret exists and is valid JSON.