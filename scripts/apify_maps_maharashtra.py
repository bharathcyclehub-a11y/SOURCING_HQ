#!/usr/bin/env python3
"""
apify_maps_maharashtra.py — Maharashtra-only deep dive. Mumbai (deeper queries),
Pune (which timed out yesterday), Thane, Bhiwandi. Replaces broken Pune slot.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = json.load(open(os.path.join(HERE, "keys.json")))
OUT_DIR = os.path.join(HERE, "yt_rc_output_mumbai")
os.makedirs(OUT_DIR, exist_ok=True)

ACTOR_ID = "compass~crawler-google-places"

TARGETS = [
    # Mumbai deeper
    ("Mumbai",    ["rc car shop Mumbai", "remote control car dealer Mumbai", "hobby shop Mumbai", "scale model store Mumbai", "drift rc Mumbai"]),
    # Pune (timed out yesterday — full retry)
    ("Pune",      ["rc car shop Pune", "hobby shop Pune", "toy wholesaler Pune", "rc drift car Pune"]),
    # Thane (Bharat Hobby + K.V. Toys live here)
    ("Thane",     ["rc car shop Thane", "hobby shop Thane", "toy wholesaler Thane"]),
    # Bhiwandi (Itoyy Kiing + Amazon FCs + warehousing hub)
    ("Bhiwandi",  ["toy wholesaler Bhiwandi", "rc car wholesale Bhiwandi", "toy warehouse Bhiwandi"]),
    # Mira Road (Hobby Central is here)
    ("Mira Road", ["rc car shop Mira Road", "hobby shop Mira Road"]),
    # Navi Mumbai
    ("Navi Mumbai", ["rc car shop Navi Mumbai", "hobby shop Navi Mumbai"]),
]


class KeyPool:
    def __init__(self, name, keys):
        self.name = name
        self.keys = [k for k in keys if k and not k.startswith("PASTE_")]
        self.i = 0
    def current(self): return self.keys[self.i]
    def rotate(self):
        if self.i + 1 >= len(self.keys): return False
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
    return any(k in b for k in ["resource_exhausted", "quota", "rate limit", "max data limit", "monthly usage", "memory limit"])


def run_actor(pool, search_string, max_places=15):
    body = {
        "searchStringsArray": [search_string],
        "maxCrawledPlacesPerSearch": max_places,
        "language": "en", "countryCode": "in",
        "scrapeContacts": True, "scrapeReviewsCount": 0,
        "scrapeImageAuthors": False,
    }
    attempts = 0
    while attempts < 3:
        attempts += 1
        token = pool.current()
        status, raw = http("POST",
            f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?waitForFinish=240&token={token}",
            headers={"Content-Type": "application/json"}, data=json.dumps(body).encode())
        body_txt = raw.decode("utf-8", "ignore")
        if is_quota_error(status, body_txt):
            if pool.rotate(): continue
            return []
        if status not in (200, 201):
            print(f"  [apify] run failed ({status}): {body_txt[:120]}")
            if attempts < 3:
                time.sleep(5)
                continue
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
    return []


def normalize_place(p):
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
    print(f"[apify] {len(pool.keys)} keys, starting at key #{pool.i+1}")
    all_results = {}
    for city, queries in TARGETS:
        for q in queries:
            print(f"\n[search] {q}")
            items = run_actor(pool, q, max_places=15)
            places = [normalize_place(p) for p in items]
            places = [p for p in places if p["name"] and not p["permanently_closed"]]
            print(f"  → {len(places)} places")
            for p in places[:3]:
                phone = p["phone"] or (p["phones"][0] if p["phones"] else "—")
                print(f"     · {p['name'][:42]:42s} | ⭐{p['rating'] or '?'} | 📞 {phone}")
            all_results[f"{city}::{q}"] = places
            time.sleep(2)

    out_json = os.path.join(OUT_DIR, "maps_maharashtra_results.json")
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {out_json}")

    by_city = {}
    for k, places in all_results.items():
        city = k.split("::")[0]
        by_city.setdefault(city, []).extend(places)
    for city, places in by_city.items():
        seen = set(); uniq = []
        for p in places:
            key = (p["name"].lower(), p["address"].lower()[:80])
            if key in seen: continue
            seen.add(key); uniq.append(p)
        by_city[city] = uniq
        print(f"  {city:12s}: {len(uniq)} unique")


if __name__ == "__main__":
    main()
