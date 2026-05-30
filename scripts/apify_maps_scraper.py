#!/usr/bin/env python3
"""
apify_maps_scraper.py — Use Apify Google Maps scraper to find verified RC/toy wholesalers
in target Indian cities. Replaces IndiaMART (which is broken for this query) and Justdial
(blacklisted per user feedback). Google Maps gives real phone + address + rating + hours.

Output: yt_rc_output_multicity/maps_results.json + maps_results.md
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = json.load(open(os.path.join(HERE, "keys.json")))
OUT_DIR = os.path.join(HERE, "yt_rc_output_multicity")
os.makedirs(OUT_DIR, exist_ok=True)

# Apify actor for Google Maps
ACTOR_ID = "compass~crawler-google-places"

# Target cities + queries
TARGETS = [
    ("Mumbai",     ["rc car wholesale Mumbai",     "remote control car wholesaler Mumbai",  "toy importer Mumbai Bhiwandi"]),
    ("Delhi",      ["rc car wholesale Delhi Sadar Bazar", "remote control car wholesaler Delhi"]),
    ("Ahmedabad",  ["rc car wholesale Ahmedabad",  "toy importer Ahmedabad", "toy manufacturer Ahmedabad"]),
    ("Bengaluru",  ["rc car wholesale Bengaluru",  "hobby rc store Bangalore"]),
    ("Pune",       ["rc car wholesale Pune",       "toy wholesaler Pune"]),
    ("Surat",      ["rc car wholesale Surat",      "toy importer Surat"]),
    ("Jaipur",     ["rc car wholesale Jaipur",     "toy wholesaler Jaipur"]),
    ("Hyderabad",  ["rc car wholesale Hyderabad",  "hobby rc store Hyderabad"]),
    ("Kolkata",    ["rc car wholesale Kolkata",    "toy wholesaler Kolkata Burrabazar"]),
    ("Chennai",    ["rc car wholesale Chennai",    "toy wholesaler Chennai"]),
]


class KeyPool:
    def __init__(self, name, keys):
        self.name = name
        # skip the first 2 (partially-used from prior sessions per keys.json comment)
        # use indices 2-10 (the 9 fresh ones with ~$5/mo each)
        self.keys = [k for k in keys if k and not k.startswith("PASTE_")]
        self.i = 0
    def current(self): return self.keys[self.i]
    def rotate(self):
        if self.i + 1 >= len(self.keys):
            return False
        self.i += 1
        print(f"  [{self.name}] rotating to key #{self.i+1}/{len(self.keys)}")
        return True


def http(method, url, headers=None, data=None, timeout=300):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()


def is_quota_error(status, body_str):
    if status == 429: return True
    b = (body_str or "").lower()
    return any(k in b for k in ["resource_exhausted", "quota", "rate limit", "max data limit", "monthly usage"])


def run_actor(pool, search_string, max_places=20):
    """Run Apify Google Maps scraper for a single search string. Return list of place records."""
    body = {
        "searchStringsArray": [search_string],
        "maxCrawledPlacesPerSearch": max_places,
        "language": "en",
        "countryCode": "in",
        "scrapeContacts": True,
        "scrapeReviewsCount": 0,  # skip reviews — save credits
        "scrapeImageAuthors": False,
    }
    while True:
        token = pool.current()
        status, raw = http(
            "POST",
            f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?waitForFinish=240&token={token}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(body).encode(),
        )
        body_txt = raw.decode("utf-8", "ignore")
        if is_quota_error(status, body_txt):
            if pool.rotate(): continue
            print(f"  [apify] all keys exhausted")
            return []
        if status not in (200, 201):
            print(f"  [apify] run failed ({status}): {body_txt[:200]}")
            return []
        try:
            ds = json.loads(raw)["data"].get("defaultDatasetId")
        except Exception:
            return []
        if not ds:
            return []
        s2, raw2 = http("GET", f"https://api.apify.com/v2/datasets/{ds}/items?format=json&token={token}")
        body2 = raw2.decode("utf-8", "ignore")
        if is_quota_error(s2, body2):
            if pool.rotate(): continue
            return []
        try:
            items = json.loads(raw2)
        except Exception:
            return []
        return items if isinstance(items, list) else []


def normalize_place(p):
    """Extract relevant fields from a Google Maps place record."""
    return {
        "name": p.get("title", "") or p.get("name", ""),
        "address": p.get("address", ""),
        "city": p.get("city", ""),
        "state": p.get("state", ""),
        "postal_code": p.get("postalCode", "") or p.get("postal_code", ""),
        "category": p.get("categoryName", "") or "",
        "categories": p.get("categories", []) or [],
        "phone": p.get("phone", "") or p.get("phoneUnformatted", "") or "",
        "phones": p.get("phones", []) or [],
        "website": p.get("website", "") or "",
        "google_maps_url": p.get("url", "") or "",
        "place_id": p.get("placeId", "") or "",
        "rating": p.get("totalScore", None),
        "reviews_count": p.get("reviewsCount", 0),
        "permanently_closed": p.get("permanentlyClosed", False),
        "temporary_closed": p.get("temporarilyClosed", False),
        "claimed": p.get("claimedByOwner", False),
        "additional_info": p.get("additionalInfo", {}) or {},
    }


def main():
    pool = KeyPool("apify", KEYS["apify"])
    print(f"[apify] {len(pool.keys)} keys in pool, starting at key #{pool.i+1}")

    all_results = {}  # (city, query) -> [places]
    for city, queries in TARGETS:
        for q in queries:
            print(f"\n[search] {q}")
            items = run_actor(pool, q, max_places=20)
            places = [normalize_place(p) for p in items]
            # filter obvious junk
            places = [p for p in places if p["name"] and not p["permanently_closed"]]
            print(f"  → {len(places)} places")
            for p in places[:3]:
                phone = p["phone"] or (p["phones"][0] if p["phones"] else "—")
                print(f"     · {p['name'][:40]:40s} | {p['city'] or '?':12s} | ⭐{p['rating'] or '?'} | 📞 {phone}")
            all_results[f"{city}::{q}"] = places
            time.sleep(2)

    out_json = os.path.join(OUT_DIR, "maps_results.json")
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {out_json}")

    # Quick summary
    print("\n=== SUMMARY ===")
    by_city = {}
    for k, places in all_results.items():
        city = k.split("::")[0]
        by_city.setdefault(city, []).extend(places)
    # dedup by name within city
    for city, places in by_city.items():
        seen = set()
        uniq = []
        for p in places:
            key = (p["name"].lower(), p["address"].lower())
            if key in seen: continue
            seen.add(key)
            uniq.append(p)
        by_city[city] = uniq
        print(f"  {city:12s}: {len(uniq)} unique places  (top rated: " + ", ".join(
            f"{p['name'][:25]}({p['rating'] or '?'}⭐)" for p in sorted(uniq, key=lambda x: -(x['rating'] or 0))[:3]
        ) + ")")


if __name__ == "__main__":
    main()
