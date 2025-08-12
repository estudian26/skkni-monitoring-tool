import os, time, requests, pandas as pd, gspread, sys, logging
from gspread.utils import rowcol_to_a1
from IPython.display import display

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("skkni")

# ---------- Configuration ----------
INPUT_GID  = int(os.getenv("INPUT_GID", "372282629"))
OUTPUT_GID = int(os.getenv("OUTPUT_GID", "372282629"))
SHEET_KEY  = os.getenv("SHEET_KEY", "1EJqpHxeZz1CDt9qbZOXEW6Bm8MGVU1KQjiTeQiGh3GU")

CREDS_FILE = os.getenv("CREDS_FILE", "creds.json")  # written by CI from secret
SERP_KEY   = os.getenv("SERPAPI_API_KEY")
if not SERP_KEY:
    raise RuntimeError("Missing SERPAPI_API_KEY environment secret")

# ---------- Google Sheets Auth ----------
log.info("Authorizing to Google Sheets…")
gc = gspread.service_account(filename=CREDS_FILE)
ss = gc.open_by_key(SHEET_KEY)
ws_in  = ss.get_worksheet_by_id(INPUT_GID)
ws_out = ss.get_worksheet_by_id(OUTPUT_GID)

# ---------- Load data ----------
log.info("Loading data from INPUT GID=%s …", INPUT_GID)
df_raw = pd.DataFrame(ws_in.get_all_records())

# Extract unique pairs
df_pairs = (
    df_raw[["Nomor SKKNI", "Tahun SKKNI"]]
      .dropna(how="all")
      .rename(columns={"Nomor SKKNI": "Nomor", "Tahun SKKNI": "Tahun"})
      .astype({"Nomor": "Int64", "Tahun": "Int64"})
      .drop_duplicates(subset=["Nomor", "Tahun"])
      .reset_index(drop=True)
)
log.info("%d unique SKKNI to check", len(df_pairs))

# ---------- SerpAPI helper ----------
def check_status_snippet(nomor: int, tahun: int) -> str:
    query = f'"Nomor {nomor} Tahun {tahun}" "SKKNI" site:skkni.kemnaker.go.id'
    r = requests.get(
        "https://serpapi.com/search.json",
        params={"q": query, "api_key": SERP_KEY, "hl": "id", "num": 10},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    blob = " ".join(
        (res.get("title", "") + " " + res.get("snippet", ""))
        for res in data.get("organic_results", [])
    ).upper()
    if "DICABUT" in blob:
        return "Dicabut"
    if "BERLAKU" in blob:
        return "Berlaku"
    return "Tidak ditemukan"

# ---------- Build status DataFrame ----------
status_rows = []
for _, row in df_pairs.iterrows():
    nomor = int(row.Nomor)
    tahun = int(row.Tahun)
    try:
        status = check_status_snippet(nomor, tahun)
    except Exception as e:
        log.error("SerpAPI error for %s/%s: %s", nomor, tahun, e)
        status = "Error"
    status_rows.append({"Nomor": nomor, "Tahun": tahun, "Status": status})
    time.sleep(1.2)  # Respect free-tier SerpAPI rate limits

df_status = pd.DataFrame(status_rows)
log.info("Status sample:\n%s", df_status.head().to_string(index=False))

# ---------- Map back ----------
status_map = {(int(r.Nomor), int(r.Tahun)): r.Status for _, r in df_status.iterrows()}
def map_status(r):
    key = (int(r["Nomor SKKNI"]), int(r["Tahun SKKNI"])) if pd.notna(r["Nomor SKKNI"]) and pd.notna(r["Tahun SKKNI"]) else None
    return status_map.get(key, "Tidak ditemukan")

df_raw["Status"] = df_raw.apply(map_status, axis=1)

# ---------- Write back ----------
tahun_idx = df_raw.columns.get_loc("Tahun SKKNI") + 1  # 1-based
status_idx = tahun_idx + 1  # after Tahun SKKNI

current_cols = len(ws_out.row_values(1))
if status_idx > current_cols:
    ws_out.add_cols(status_idx - current_cols)

# Header
ws_out.update_cell(1, status_idx, "Status")

# Values
from gspread.utils import rowcol_to_a1
start = rowcol_to_a1(2, status_idx)
end   = rowcol_to_a1(len(df_raw) + 1, status_idx)
ws_out.update(f"{start}:{end}", [[v] for v in df_raw["Status"].tolist()])

log.info("Done. Wrote Status column to GID=%s (column #%s).", OUTPUT_GID, status_idx)