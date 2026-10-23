"""Build data/concentration.json for the market concentration calculator.

Source: Kenneth R. French Data Library, "Portfolios Formed on Size" (CSV), built from CRSP.
Each month it gives every US company's size decile (NYSE breakpoints, re-sorted each June), with
value-weighted returns, the number of firms and their average size in each decile.

From it this script works out, month by month:
  share  the share of the whole US share market's value held by the biggest 10% of companies (top decile)
  top    the value-weighted return of the biggest 10% (dividends included)
  rest   the value-weighted return of the other 90%
  all    the value-weighted return of the whole market
  firms  how many companies are in the biggest 10%

The script tries to download the latest file from the Data Library. It also looks in inbox/ for an
uploaded copy (any .csv or .zip whose name contains "size" or "_ME"), and uses whichever runs to the
latest month. It stops with an
error, and publishes nothing, if anything looks wrong.
"""
import csv, glob, io, json, os, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX = os.path.join(ROOT, 'inbox')
OUT = os.path.join(ROOT, 'data', 'concentration.json')
URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Portfolios_Formed_on_ME_CSV.zip'
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def fail(msg):
    print('ERROR: ' + msg)
    sys.exit(1)


def csv_text_from_zip(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [n for n in z.namelist() if n.lower().endswith('.csv')]
        if not names:
            fail('The French zip file has no CSV inside')
        return z.read(names[0]).decode('latin-1')


def candidates():
    """Every source we could use: the latest download first, then any copies in inbox/."""
    out = []
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (market-history data update)'})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.append((csv_text_from_zip(r.read()), 'download'))
        print('Downloaded the latest size portfolios file from the French Data Library')
    except Exception as e:  # GitHub can be blocked; fall back to the uploaded copy
        print('Could not download from the French Data Library (%s); using the copy in inbox/' % e)
    for f in sorted(glob.glob(os.path.join(INBOX, '*'))):
        name = os.path.basename(f).lower()
        if name.endswith(('.csv', '.zip')) and ('size' in name or '_me' in name):
            with open(f, 'rb') as fh:
                data = fh.read()
            out.append((csv_text_from_zip(data) if name.endswith('.zip') else data.decode('latin-1'), os.path.basename(f)))
    if not out:
        fail('No size portfolios file in inbox/ (download "Portfolios Formed on Size" CSV from the French Data Library)')
    return out


def last_month(text):
    """The latest month in a file's monthly returns, or 0 if it isn't the right file."""
    best = 0
    for r in csv.reader(io.StringIO(text)):
        if r and r[0].strip().isdigit() and len(r[0].strip()) == 6:
            best = max(best, int(r[0]))
    return best


# use whichever source runs to the latest month (an old copy left in inbox/ can't win)
text, origin = max(candidates(), key=lambda c: last_month(c[0]))
rows = list(csv.reader(io.StringIO(text)))
if not rows or 'size portfolios' not in ' '.join(rows[0] + rows[1]).lower():
    fail('This does not look like the "Portfolios Formed on Size" file')


def section(title):
    hits = [k for k, r in enumerate(rows) if r and r[0].strip() == title]
    if not hits:
        fail('Section "%s" not found in the size portfolios file' % title)
    k = hits[0]
    hdr = [h.strip() for h in rows[k + 1]]
    out = {}
    for r in rows[k + 2:]:
        if not r or not r[0].strip():
            break
        out[int(r[0])] = [float(x) for x in r[1:len(hdr)]]
    return hdr, out


hdr, vw = section('Average Value Weight Returns -- Monthly')
_, nf = section('Number of Firms in Portfolios')
_, sz = section('Average Firm Size')
try:
    d0 = hdr.index('Lo 10') - 1
    d9 = hdr.index('Hi 10') - 1
except ValueError:
    fail('Decile columns (Lo 10 ... Hi 10) not found')
dec = list(range(d0, d9 + 1))
if len(dec) != 10:
    fail('Expected 10 decile columns, found %d' % len(dec))

months = sorted(vw)
if months[0] != 192607:
    fail('Data should start in July 1926, found %s' % months[0])
for a, b in zip(months, months[1:]):  # continuous months
    ya, ma = divmod(a, 100)
    if b != (ya * 100 + ma + 1 if ma < 12 else (ya + 1) * 100 + 1):
        fail('Months are not continuous after %s' % a)
if set(months) != set(nf) or set(months) != set(sz):
    fail('Returns, firm counts and firm sizes cover different months')

share, top, rest, allr, firms = [], [], [], [], []
for m in months:
    caps = [nf[m][j] * sz[m][j] for j in dec]
    rets = [vw[m][j] / 100 for j in dec]
    if min(caps) <= 0 or any(r <= -0.9999 for r in rets):
        fail('Missing or impossible values in %s' % m)
    tot = sum(caps)
    share.append(round(caps[-1] / tot, 5))
    top.append(round(rets[-1], 6))
    rest.append(round(sum(c * r for c, r in zip(caps[:9], rets[:9])) / sum(caps[:9]), 6))
    allr.append(round(sum(c * r for c, r in zip(caps, rets)) / tot, 6))
    firms.append(int(nf[m][dec[-1]]))

if not 0.3 < share[-1] < 0.95:
    fail('The latest concentration figure (%.1f%%) looks wrong' % (share[-1] * 100))

# Don't go backwards: a file with fewer months than the published one is probably the wrong file.
if os.path.exists(OUT):
    try:
        old = json.load(open(OUT))
        if len(old.get('share', [])) > len(share):
            fail('This file has fewer months (%d) than the published data (%d). Is it an old file?' % (len(share), len(old['share'])))
    except ValueError:
        pass

ly, lm = divmod(months[-1], 100)
out = {
    'start': [1926, 7],
    'share': share, 'top': top, 'rest': rest, 'all': allr, 'firms': firms,
    'sources': {'french': '%s %d' % (MON[lm - 1], ly), 'origin': origin},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as fh:
    json.dump(out, fh, separators=(',', ':'))
print('Wrote %s: %d months, July 1926 to %s %d. Biggest 10%% hold %.1f%% of the market.' % (OUT, len(months), MON[lm - 1], ly, share[-1] * 100))
