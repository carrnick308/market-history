# Market history calculators

The market timing, Shiller P/E, lump sum or drip-feed, and market concentration calculators for yourmoneyblueprint.co.nz.
The pages are served by GitHub Pages and shown on the Squarespace site in a Code Block.

## Before you start (do these first)

1. **Keep the file names exactly as they are.** The Squarespace code points at `market-timing.html` and `shiller-pe.html`, and the pages load `data/market-data.json`. Renaming any of them breaks the live calculators.
2. **Turn on write access for Actions** (otherwise the monthly data update can't save its results): Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.
3. **Turn on GitHub Pages**: Settings → Pages → Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)** → Save. After a minute the pages are live at
   - https://carrnick308.github.io/market-history/market-timing.html
   - https://carrnick308.github.io/market-history/shiller-pe.html

## Adding the calculators to Squarespace

1. Create the page (e.g. `/market-timing-calculator`) with your H1, intro copy and SEO settings as usual.
2. Add a **Code Block** where the calculator should appear and paste in the whole of `embed/squarespace-market-timing.html`.
3. Do the same on `/shiller-pe-calculator` with `embed/squarespace-shiller-pe.html`, on `/lump-sum-or-drip-feed-calculator` with `embed/squarespace-lump-sum.html`, and on `/market-concentration-calculator` with `embed/squarespace-market-concentration.html`.
4. Add the pages to the `/calculators` hub (the hub is the only place they get listed). The calculators link to each other using these page addresses, so keep them exactly as written.

The Code Block sizes itself to the calculator, so there's no inner scroll bar. As people change the settings, the page address updates (e.g. `/market-timing-calculator?from=2000-01&to=2009-12&mode=lump...`), so a link copied from the address bar or the "Copy link to these settings" button opens the calculator with the same settings.

If the calculator only appears after refreshing the page, your template's Ajax loading is stopping the Code Block's script from running. Turn it off under Design → Site Styles (look for "Enable Ajax Loading").

## Monthly update

Each month, upload the newest source files to the `inbox/` folder, **replacing the old files with the same names**:

| File | Where to get it | How often |
|---|---|---|
| `ie_data.xls` | shillerdata.com, "U.S. Stock Markets 1871-Present and CAPE Ratio" | Monthly. Shiller usually updates early in the month |
| `hb1-monthly.xlsx` | RBNZ statistics, exchange rates (B1), monthly data file | Monthly |
| `hm1-long.xlsx` | RBNZ statistics, prices (M1), long data file | Quarterly, when a new CPI quarter is released |
| `Portfolios_Formed_on_ME.csv` | Kenneth French Data Library, "Portfolios Formed on Size", CSV (unzip it). For the market concentration calculator | Only if the action says it couldn't download it. It tries to fetch the latest file itself each month |

Don't delete `hb1-monthly-1973-1998.xlsx`. It holds the exchange rates back to 1985 and never changes.

Uploading to `inbox/` starts the **Update market data** action (Actions tab). It downloads the latest US Treasury bill rate from FRED itself, rebuilds `data/market-data.json`, and commits it. The live calculators pick it up within a few minutes. The action also runs by itself on the 20th of each month, and you can run it by hand from the Actions tab ("Run workflow").

If the action fails, nothing is published and the calculators keep the previous month's data. The concentration data is a separate step: if only that fails (shown as a warning on the run), the other calculators still update and the concentration calculator keeps last month's figures. The error message in the action's log says which file is the problem (for example, a Shiller file with fewer months than last time usually means the wrong file was uploaded).

## What's in here

| Path | What it is |
|---|---|
| `market-timing.html`, `shiller-pe.html`, `lump-sum.html`, `market-concentration.html` | The four calculator pages |
| `assets/core.js` | Shared data loading, maths, charts and embedding code |
| `assets/timing.js`, `assets/pe.js`, `assets/lump.js`, `assets/conc.js` | Each calculator's own code (scrambled; the readable copies are kept privately) |
| `assets/style.css` | Styling for all the pages |
| `data/market-data.json` | The monthly market data the pages load (also used by the apps) |
| `data/concentration.json` | Monthly concentration data for the market concentration calculator |
| `scripts/build_data.py` | Builds `market-data.json` from the files in `inbox/` |
| `scripts/build_concentration.py` | Builds `concentration.json` from the French Data Library |
| `.github/workflows/update-data.yml` | The monthly update action |
| `embed/` | The Squarespace Code Block snippets |

## Data sources

- Robert J. Shiller, U.S. Stock Markets 1871-Present and CAPE Ratio (shillerdata.com)
- US 3-month Treasury bill rate, FRED series TB3MS (Federal Reserve Bank of St. Louis)
- Reserve Bank of New Zealand, B1 exchange rates and M1 prices
- Eugene F. Fama and Kenneth R. French, Portfolios Formed on Size (Kenneth R. French Data Library, built from CRSP)
