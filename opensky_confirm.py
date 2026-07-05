#!/usr/bin/env python3
"""
OpenSky confirmation step for jet identification — PROTOTYPE.

Context: FAA registry + home-metro geography yields a CANDIDATE pool of business
jets per firm (see opensky_candidates_4firms.csv), but cannot attribute a tail to
a specific firm — e.g. NVDA and AVGO share the identical KSJC candidate pool, which
also contains unrelated VC/billionaire jets. This script performs the attribution
the registry cannot: it asks OpenSky which candidate aircraft are actually *based*
at the firm's home airport (high departure+arrival frequency) and whether their
destination pattern matches the firm's footprint.

Validation already done on cohort data (flights_business.csv): a firm's jets put a
median 32% of all movements through one home airport (71% of firms >=25%). So
"based at home airport" is a strong, quantified discriminator.

BLOCKER: OpenSky moved to OAuth2 client-credentials in 2025; anonymous historical
access returns HTTP 403. The M2 node held credentials but is unreachable. Supply
OPENSKY_CLIENT_ID / OPENSKY_CLIENT_SECRET (or a legacy user/pass) to run.

Usage:
    OPENSKY_CLIENT_ID=... OPENSKY_CLIENT_SECRET=... python3 opensky_confirm.py
"""
import os, time, json, csv, urllib.request, urllib.parse, urllib.error
from collections import defaultdict

# ---- firm -> home airport(s) (derived from cohort home-base validation + flight dept facts) ----
HOME = {
    'MSFT': ['KBFI'],                 # Boeing Field, Seattle
    'NVDA': ['KSJC'],                 # Norman Y. Mineta San Jose
    'AVGO': ['KSJC'],                 # San Jose
    'BMY':  ['KTTN', 'KMMU', 'KTEB'], # Trenton-Mercer / Morristown / Teterboro
}
# project backtest window
WIN_BEGIN = 1514764800   # 2018-01-01 UTC
WIN_END   = 1767225600   # 2026-01-01 UTC
CHUNK     = 7 * 24 * 3600  # OpenSky /flights/* caps each call at <=7 days

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
API = "https://opensky-network.org/api"


def get_token():
    cid, sec = os.environ.get('OPENSKY_CLIENT_ID'), os.environ.get('OPENSKY_CLIENT_SECRET')
    if not (cid and sec):
        raise SystemExit("Set OPENSKY_CLIENT_ID / OPENSKY_CLIENT_SECRET (OAuth2 client credentials).")
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials', 'client_id': cid, 'client_secret': sec}).encode()
    r = urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data), timeout=30)
    return json.load(r)['access_token']


def fetch(endpoint, airport, begin, end, token):
    """endpoint in {'arrival','departure'}; returns list of flight dicts (icao24, est*Airport, callsign)."""
    q = urllib.parse.urlencode({'airport': airport, 'begin': begin, 'end': end})
    req = urllib.request.Request(f"{API}/flights/{endpoint}?{q}",
                                 headers={'Authorization': f'Bearer {token}'})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        if e.code == 404:   # OpenSky returns 404 for "no flights in window"
            return []
        raise


def load_candidates(path='opensky_candidates_4firms.csv'):
    cand = defaultdict(dict)   # ticker -> {hex: (N, owner, model)}
    with open(path) as f:
        for row in csv.DictReader(f):
            cand[row['ticker']][row['hex'].lower()] = (row['N'], row['NAME'], row['MODEL'])
    return cand


def main():
    token = get_token()
    cand = load_candidates()
    # movement counts per (airport, icao24)
    counts = defaultdict(lambda: defaultdict(int))   # airport -> icao24 -> n movements
    airports = sorted({a for aps in HOME.values() for a in aps})
    for ap in airports:
        b = WIN_BEGIN
        while b < WIN_END:
            e = min(b + CHUNK, WIN_END)
            for ep in ('departure', 'arrival'):
                for fl in fetch(ep, ap, b, e, token):
                    ic = (fl.get('icao24') or '').lower()
                    if ic:
                        counts[ap][ic] += 1
                time.sleep(1)        # be polite to the API
            b = e
        print(f"[{ap}] distinct aircraft seen: {len(counts[ap])}")

    # attribute: for each firm, rank its candidate hexes by movements at its home airport(s)
    out = []
    for tk, homes in HOME.items():
        agg = defaultdict(int)
        for ap in homes:
            for ic, n in counts[ap].items():
                agg[ic] += n
        for hx, (N, owner, model) in cand.get(tk, {}).items():
            mv = agg.get(hx, 0)
            out.append((tk, '/'.join(homes), N, hx, owner, model, mv))
    out.sort(key=lambda r: (r[0], -r[6]))
    with open('opensky_confirmed.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ticker', 'home', 'N', 'hex', 'owner', 'model', 'home_movements'])
        w.writerows(out)
    print("wrote opensky_confirmed.csv — high home_movements => the firm's based jet; "
          "0 => candidate is based elsewhere (not this firm).")
    # NEXT: for top tails, pull /flights/aircraft?icao24=hex over the window and test whether
    # destinations cluster on the firm's known sites / M&A target HQs (deals.csv target_hq).


if __name__ == '__main__':
    main()
