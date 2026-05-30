#!/usr/bin/env python3
"""
maps_analyze.py — Parse Apify Maps results, score RC-relevance, group by state.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "yt_rc_output_multicity", "maps_results.json")
OUT = os.path.join(HERE, "yt_rc_output_multicity", "maps_vendors.json")

# city -> state
CITY_STATE = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra",
    "Delhi": "Delhi NCR",
    "Ahmedabad": "Gujarat", "Surat": "Gujarat",
    "Bengaluru": "Karnataka",
    "Jaipur": "Rajasthan",
    "Hyderabad": "Telangana",
    "Kolkata": "West Bengal",
    "Chennai": "Tamil Nadu",
}

# Strong RC indicators
RC_STRONG = ["rc ", "r.c.", "remote control", "remote-control", "remote car", "rc car",
             "rcdh", "rcdc", "hobby grade", "drift", "racing car", "1:10", "1:18", "1:24"]
# Medium RC indicators
RC_MEDIUM = ["hobby", "hobbies", "die cast", "diecast", "scale model", "model car",
             "model store", "aero", "drone", "tygatec"]
# Weak / generic toy
TOY_GENERIC = ["toy", "toys", "kids", "gift", "playset", "ride on", "rideon", "battery toy"]


def score_relevance(place):
    """Returns ('STRONG_RC' / 'MEDIUM_RC' / 'GENERIC_TOY' / 'UNCLEAR', signals_list)"""
    blob_parts = [place["name"], place["category"]]
    blob_parts.extend(place["categories"] or [])
    addi = place.get("additional_info", {})
    if isinstance(addi, dict):
        for k, v in addi.items():
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        blob_parts.extend(str(x) for x in item.values())
    blob = " ".join(blob_parts).lower()

    strong = [k for k in RC_STRONG if k in blob]
    medium = [k for k in RC_MEDIUM if k in blob]
    toy = [k for k in TOY_GENERIC if k in blob]

    if strong:
        return "STRONG_RC", strong + medium
    if medium and not toy:
        return "MEDIUM_RC", medium
    if medium and toy:
        return "MEDIUM_RC", medium + toy[:2]
    if toy:
        return "GENERIC_TOY", toy
    return "UNCLEAR", []


def main():
    data = json.load(open(IN))

    all_places = []
    for k, places in data.items():
        city = k.split("::")[0]
        for p in places:
            p["search_city"] = city
            p["state"] = CITY_STATE.get(city, "Unknown")
            rel, sig = score_relevance(p)
            p["rc_relevance"] = rel
            p["rc_signals"] = sig
            all_places.append(p)

    # dedup by (name + address) globally
    seen = set()
    uniq = []
    for p in all_places:
        key = (p["name"].lower().strip(), p["address"].lower().strip()[:80])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)

    # Save
    with open(OUT, "w") as f:
        json.dump(uniq, f, indent=2, ensure_ascii=False)
    print(f"[output] {OUT}")
    print(f"[stats] {len(uniq)} unique places\n")

    # By state
    by_state = {}
    for p in uniq:
        by_state.setdefault(p["state"], []).append(p)

    print("=== State-level vendor count (all toy/RC shops) ===")
    state_ranked = sorted(by_state.items(), key=lambda x: -len(x[1]))
    for state, ps in state_ranked:
        strong = sum(1 for p in ps if p["rc_relevance"] == "STRONG_RC")
        medium = sum(1 for p in ps if p["rc_relevance"] == "MEDIUM_RC")
        generic = sum(1 for p in ps if p["rc_relevance"] == "GENERIC_TOY")
        unclear = sum(1 for p in ps if p["rc_relevance"] == "UNCLEAR")
        with_phone = sum(1 for p in ps if p["phone"] or p["phones"])
        with_web = sum(1 for p in ps if p["website"])
        print(f"  {state:15s}: {len(ps):3d} total  | STRONG_RC={strong:2d}  MEDIUM_RC={medium:2d}  GENERIC_TOY={generic:2d}  UNCLEAR={unclear:2d}  | 📞{with_phone:3d}  🌐{with_web:2d}")

    print("\n=== STRONG_RC vendors (most relevant to BCH drift SKU) ===")
    strong_all = sorted([p for p in uniq if p["rc_relevance"] == "STRONG_RC"],
                        key=lambda x: (-(x["rating"] or 0), -(x["reviews_count"] or 0)))
    print(f"Found {len(strong_all)} STRONG_RC vendors")
    for p in strong_all:
        phone = p["phone"] or (p["phones"][0] if p["phones"] else "—")
        print(f"  [{p['state'][:10]:10s}] {p['name'][:42]:42s} | ⭐{p['rating'] or '?'} ({p['reviews_count'] or 0}) | 📞{phone:15s} | 🌐{p['website'][:30] if p['website'] else '—'}")

    print("\n=== MEDIUM_RC vendors (worth a call) ===")
    medium_all = sorted([p for p in uniq if p["rc_relevance"] == "MEDIUM_RC"],
                       key=lambda x: (-(x["rating"] or 0), -(x["reviews_count"] or 0)))
    print(f"Found {len(medium_all)} MEDIUM_RC vendors (showing top 25)")
    for p in medium_all[:25]:
        phone = p["phone"] or (p["phones"][0] if p["phones"] else "—")
        print(f"  [{p['state'][:10]:10s}] {p['name'][:42]:42s} | ⭐{p['rating'] or '?'} ({p['reviews_count'] or 0}) | 📞{phone:15s} | signals: {','.join(p['rc_signals'][:3])}")


if __name__ == "__main__":
    main()
