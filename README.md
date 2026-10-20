# Market history calculators

The market timing calculator and Shiller P/E calculator for yourmoneyblueprint.co.nz.
The pages are served by GitHub Pages and shown on the Squarespace site in a Code Block.

## The code in this repo is scrambled

The calculator scripts in `assets/` (`core.js`, `timing.js`, `pe.js`) are deliberately scrambled, because this repository is public. The readable source is kept off GitHub, in `C:\Projects\market-history-source`. **Don't edit the scrambled files directly.** For any change, start from the readable source, then scramble it again before replacing the files here. `style.css`, the HTML pages, the data script and the data file are left readable.

## Before you start (do these first)

1. **Keep the file names exactly as they are.** The Squarespace code points at `market-timing.html` and `shiller-pe.html`, and the pages load `data/market-data.json`. Renaming any of them breaks the live calculators.
2. **Turn on write access for Actions** (otherwise the monthly data update can't save its results): Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.
3. **Turn on GitHub Pages**: Settings → Pages → Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)** → Save. After a minute the pages are live at
   - https://carrnick308.github.io/market-history/market-timing.html
   - https://carrnick308.github.io/market-history/shiller-pe.html

## Adding the calculators to Squarespace

1. Create the page (e.g. `/market-timing-calculator`) with your H1, intro copy and SEO settings as usual.
2. Add a **Code Block** where the calculator should appear and paste in the whole of `embed/squarespace-market-timing.html`.
3. Do the same on `/shiller-pe-calculator` with `embed/squarespace-shiller-pe.html`.
4. Add both pages to the `/calculators` hub (the hub is the only place they get listed).

The Code Block sizes itself to the calculator, so there's no inner scroll bar. As people change the settings, the page address updates (e.g. `/market-timing-calculator?from=2000-01&to=2009-12&mode=lump...`), so a link copied from the address bar or the "Copy link to these settings" button opens the calculator with the same settings.

If the calculator only appears after refreshing the page, your template's Ajax loading is stopping the Code Block's script from running. Turn it off under Design → Site Styles (look for "Enable Ajax Loading").

## Monthly update

Each month, upload the newest source files to the `inbox/` folder, **replacing the old files with the same names**:

| File | Where to get it | How often |
|---|---|---|
| `ie_data.xls` | shillerdata.com, "U.S. Stock Markets 1871-Present and CAPE Ratio" | Monthly. Shiller usually updates early in the month |
| `hb1-monthly.xlsx` | RBNZ statistics, exchange rates (B1), monthly data file | Monthly |
| `hm1-long.xlsx` | RBNZ statistics, prices (M1), long data file | Quarterly, when a new CPI quarter is released |

Don't delete `hb1-monthly-1973-1998.xlsx`. It holds the exchange rates back to 1985 and never changes.

Uploading to `inbox/` starts the **Update market data** action (Actions tab). It downloads the latest US Treasury bill rate from FRED itself, rebuilds `data/market-data.json`, and commits it. The live calculators pick it up within a few minutes. The action also runs by itself on the 20th of each month, and you can run it by hand from the Actions tab ("Run workflow").

If the action fails, nothing is published and the calculators keep the previous month's data. The error message in the action's log says which file is the problem (for example, a Shiller file with fewer months than last time usually means the wrong file was uploaded).

## What's in here

| Path | What it is |
|---|---|
| `market-timing.html`, `shiller-pe.html` | The two calculator pages |
| `assets/core.js` | Shared data loading, maths, charts and embedding code (scrambled) |
| `assets/timing.js`, `assets/pe.js` | Each calculator's own code (scrambled) |
| `assets/style.css` | Styling for both pages |
| `data/market-data.json` | The monthly data both pages load (also usable by the apps) |
| `scripts/build_data.py` | Builds the data file from the files in `inbox/` |
| `.github/workflows/update-data.yml` | The monthly update action |
| `embed/` | The Squarespace Code Block snippets |

## Data sources

- Robert J. Shiller, U.S. Stock Markets 1871-Present and CAPE Ratio (shillerdata.com)
- US 3-month Treasury bill rate, FRED series TB3MS (Federal Reserve Bank of St. Louis)
- Reserve Bank of New Zealand, B1 exchange rates and M1 prices
