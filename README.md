# 🧩 SKKNI Monitoring Tool (GitHub Actions version)

This project helps **Lembaga Sertifikasi Profesi (LSP)** automatically monitor the **SKKNI (Standar Kompetensi Kerja Nasional Indonesia)** they use.  

It reads a Google Sheet, checks each SKKNI’s status from Kemnaker via SerpAPI, updates the “Status” column, highlights any **“Dicabut”** entries, and can send weekly email notifications.  

Everything runs automatically through **GitHub Actions** — no manual execution needed once set up.

---

## ⚙️ Setup (beginner friendly)

1. **Create the repository** on GitHub and upload these files.

2. **Add GitHub Secrets**  
   Go to **Settings → Secrets and variables → Actions → New repository secret** and add:
   - `SERPAPI_API_KEY` — your SerpAPI key  
   - `GSHEETS_JSON` — paste the full contents of your Google Service Account JSON  
   - *(optional)* `SMTP_USER`, `SMTP_PASS`, `RECIPIENTS` if you want email alerts

3. **Share the Google Sheet**  
   Share it with the `client_email` found inside your Service Account JSON file (with **Editor** access).

4. **Workflow trigger**  
   - Default: runs daily at **07:05 WIB (00:05 UTC)**  
   - Manual: open **Actions → SKKNI Validator → Run workflow**

---

## 📂 Files

| File | Description |
|------|--------------|
| `main.py` | Main Python script that performs validation, highlighting, and email alerts |
| `requirements.txt` | Python dependencies |
| `.github/workflows/daily.yml` | GitHub Actions workflow (scheduler and environment setup) |

---

## 🔧 Adjustments

- **Change Sheet IDs:**  
  Edit `INPUT_GID`, `OUTPUT_GID`, or `SHEET_KEY` in the workflow `env:` section or set them as repository variables.

- **Change schedule time:**  
  Update the cron expression in `.github/workflows/daily.yml`.  
  GitHub Actions uses **UTC**, so `07:05 WIB` = `00:05 UTC`.

  ```yaml
  on:
    schedule:
      - cron: "5 0 * * *"   # runs at 07:05 WIB (00:05 UTC)
    workflow_dispatch: {}   # allows manual trigger
