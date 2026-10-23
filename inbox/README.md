# inbox

Upload the latest source files here each month, **replacing the old ones with the same file names**.
Uploading triggers the "Update market data" action, which rebuilds `data/market-data.json` and `data/concentration.json`.

| File | Where it comes from | How often |
|---|---|---|
| `ie_data.xls` | Robert Shiller's data page, shillerdata.com ("U.S. Stock Markets 1871-Present and CAPE Ratio") | Monthly, usually early in the month |
| `hb1-monthly.xlsx` | RBNZ statistics, exchange rates B1, monthly data file | Monthly |
| `hm1-long.xlsx` | RBNZ statistics, prices M1, long data file | Quarterly (when a new CPI quarter is out) |
| `hb1-monthly-1973-1998.xlsx` | RBNZ B1 historical file | Never changes. Leave it here. |
| `TB3MS.csv` | US Treasury bill rate from FRED. The action downloads this itself. | Automatic |
| `Portfolios_Formed_on_ME.csv` | Kenneth French Data Library, "Portfolios Formed on Size", CSV (unzip it first). For the market concentration calculator. The action tries to download this itself each month; upload it only if the action log says the download failed. | Monthly, only if needed |
