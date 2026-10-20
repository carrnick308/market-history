"""Build data/market-data.json for the market timing and Shiller P/E calculators.

Reads the source files in inbox/:
  ie_data.xls                 Robert Shiller's monthly US market data (manual upload)
  hb1-monthly*.xlsx           RBNZ B1 exchange rates (the 1973-1998 file never changes; the current file is a manual upload)
  hm1*.xlsx                   RBNZ M1 prices, quarterly CPI (manual upload)
  TB3MS.csv                   US 3-month Treasury bill rate. Downloaded from FRED automatically when possible;
                              the copy in inbox/ is used if the download fails.

Every series is lined up month by month with Shiller's data (January 1871 onwards). Where a series
ends before Shiller's latest month, its last value is carried forward and the real last month is
recorded under "sources" so the pages can say so.

The script stops with an error, and publishes nothing, if anything looks wrong.
"""
import glob, json, math, os, sys, urllib.request, datetime
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX = os.path.join(ROOT, 'inbox')
OUT = os.path.join(ROOT, 'data', 'market-data.json')
FRED_URL = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS'
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def fail(msg):
    print('ERROR: ' + msg)
    sys.exit(1)


def one(pattern, label):
    files = sorted(glob.glob(os.path.join(INBOX, pattern)))
    if not files:
        fail('No %s file found in inbox/ (looking for %s)' % (label, pattern))
    return files[-1]


# ---------- Shiller ----------
shiller_path = one('ie_data*.xls*', 'Shiller')
raw = pd.read_excel(shiller_path, sheet_name='Data', header=None, skiprows=8)
# columns: 0 date (1871.01), 4 CPI, 9 real total return price, 12 CAPE
raw = raw[pd.to_numeric(raw[0], errors='coerce').notna()].reset_index(drop=True)
dates = [float(v) for v in raw[0]]
y0 = int(dates[0]); m0 = round((dates[0] - y0) * 100)
if (y0, m0) != (1871, 1):
    fail('Shiller data should start in January 1871, found %s' % dates[0])
N = len(raw)
for k, d in enumerate(dates):  # check months are continuous
    y, m = divmod(m0 - 1 + k, 12)
    if (int(d), round((d - int(d)) * 100)) != (y0 + y, m + 1):
        fail('Shiller months are not continuous at row %d (%s)' % (k, d))
tr = pd.to_numeric(raw[9], errors='coerce')
cpi = pd.to_numeric(raw[4], errors='coerce')
cape = pd.to_numeric(raw[12], errors='coerce')
if tr.isna().any() or cpi.isna().any():
    fail('Shiller total return or CPI has gaps')
last_y, last_m = divmod(m0 - 1 + N - 1, 12)
last_y += y0; last_m += 1


def idx(y, m):
    return (y - y0) * 12 + (m - m0)


def label(i):
    y, m = divmod(m0 - 1 + i, 12)
    return '%s %d' % (MON[m], y0 + y)


def carry(series):
    """Fill months after the series ends with its last value; return the real last month."""
    last = None; real_last = None
    for i in range(N):
        if series[i] is None and last is not None:
            series[i] = last
        elif series[i] is not None:
            last = series[i]; real_last = i
    return real_last


# ---------- US Treasury bills ----------
tb_csv = os.path.join(INBOX, 'TB3MS.csv')
try:
    with urllib.request.urlopen(FRED_URL, timeout=30) as r:
        body = r.read().decode('utf-8')
    if 'TB3MS' not in body.splitlines()[0]:
        raise ValueError('unexpected FRED response')
    with open(tb_csv, 'w') as f:
        f.write(body)
    print('Downloaded TB3MS from FRED')
except Exception as e:  # FRED unreachable: use the copy in inbox/
    print('FRED download failed (%s); using inbox/TB3MS.csv' % e)
    if not os.path.exists(tb_csv):
        fail('No TB3MS.csv in inbox/ and FRED could not be reached')
tbdf = pd.read_csv(tb_csv)
tb = [None] * N
for _, row in tbdf.iterrows():
    dt = pd.to_datetime(row.iloc[0]); v = pd.to_numeric(row.iloc[1], errors='coerce')
    i = idx(dt.year, dt.month)
    if 0 <= i < N and not pd.isna(v):
        tb[i] = round(float(v), 2)
tb_last = carry(tb)

# ---------- RBNZ B1 exchange rates (NZD/USD, US dollars per NZ dollar) ----------
fx = [None] * N
hb1_files = sorted(glob.glob(os.path.join(INBOX, 'hb1*.xlsx')))
if not hb1_files:
    fail('No RBNZ B1 file (hb1*.xlsx) in inbox/')
for f in hb1_files:
    x = pd.read_excel(f, sheet_name='Data', header=None)
    col = None
    for c in range(x.shape[1]):
        if str(x.iloc[3, c]).strip() == 'NZD/USD':
            col = c
    if col is None:
        fail('Could not find the NZD/USD column in %s' % os.path.basename(f))
    for _, r in x.iloc[5:].iterrows():
        v = pd.to_numeric(r[col], errors='coerce')
        if pd.isna(v):
            continue
        dt = pd.to_datetime(r[0]); i = idx(dt.year, dt.month)
        if 0 <= i < N:
            fx[i] = round(float(v), 5)
fx_last = carry(fx)
if fx[idx(1985, 3)] is None:
    fail('Exchange rates do not reach back to March 1985. Is hb1-monthly-1973-1998.xlsx still in inbox/?')

# ---------- RBNZ M1 CPI (quarterly, spread evenly across each quarter) ----------
m1 = pd.read_excel(one('hm1*.xlsx', 'RBNZ M1 prices'), sheet_name='Data', header=None)
col = None
for c in range(m1.shape[1]):
    if str(m1.iloc[4, c]).strip() == 'CPI.Q.C.ia':
        col = c
if col is None:
    fail('Could not find the CPI index column (CPI.Q.C.ia) in the M1 file')
q = {}
for _, r in m1.iloc[5:].iterrows():
    v = pd.to_numeric(r[col], errors='coerce')
    if pd.isna(v):
        continue
    dt = pd.to_datetime(r[0]); i = idx(dt.year, dt.month)
    if 0 <= i < N:
        q[i] = float(v)
ks = sorted(q)
nzcpi = [None] * N
for a, b in zip(ks, ks[1:]):
    for i in range(a, b + 1):
        nzcpi[i] = round(math.exp(math.log(q[a]) + (math.log(q[b]) - math.log(q[a])) * (i - a) / (b - a)), 3)
nz_last = ks[-1]
for i in range(nz_last + 1, N):
    nzcpi[i] = q[nz_last]
nz_from = idx(1985, 2)  # only needed from the 1985 float
nzcpi = [None if i < nz_from else v for i, v in enumerate(nzcpi)]

# ---------- sanity checks against the previous build ----------
if os.path.exists(OUT):
    prev = json.load(open(OUT))
    if len(prev['tr']) > N:
        fail('New Shiller file has fewer months (%d) than the published data (%d). Wrong file?' % (N, len(prev['tr'])))
for name, s, start in [('T-bill', tb, idx(1934, 1)), ('exchange rate', fx, idx(1985, 3)), ('NZ CPI', nzcpi, idx(1985, 3))]:
    if any(v is None for v in s[start:]):
        fail('%s series has gaps after %s' % (name, label(start)))
for name, last in [('T-bill', tb_last), ('exchange rate', fx_last), ('NZ CPI', nz_last)]:
    if N - 1 - last > 6:
        print('WARNING: %s data ends %s, more than 6 months before the Shiller data. Upload a newer file.' % (name, label(last)))

out = {
    'start': [y0, m0],
    # asOf lets the app's useRemoteData hook keep whichever copy is newest (bundled vs downloaded)
    'asOf': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
    'built': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
    'sources': {
        'shiller': label(N - 1),
        'tbill': label(tb_last),
        'fx': label(fx_last),
        'nzcpi': label(nz_last),
    },
    'tr': [round(float(v), 4) for v in tr],
    'cpi': [round(float(v), 4) for v in cpi],
    'cape': [None if pd.isna(v) else round(float(v), 2) for v in cape],
    'tb': tb, 'fx': fx, 'nzcpi': nzcpi,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as f:
    json.dump(out, f, separators=(',', ':'))
print('Wrote %s: %d months, %s to %s' % (os.path.relpath(OUT, ROOT), N, label(0), label(N - 1)))
print('Sources:', out['sources'])
