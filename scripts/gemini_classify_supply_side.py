#!/usr/bin/env python3
"""
gemini_classify_supply_side.py — SUPPLY-SIDE focused classifier.

Same architecture as gemini_classify_frames.py but with a prompt tuned to identify
MANUFACTURERS / DISTRIBUTORS / WHOLESALERS / TRADERS / IMPORTERS, not retailers.

Usage:
    python3 gemini_classify_supply_side.py --in yt_rc_output_supply/vendors.json \
                                            --out yt_rc_output_supply/gemini_supply_verdicts.json
"""

import argparse
import base64
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = json.load(open(os.path.join(HERE, "keys.json")))
GEMINI_KEY = KEYS["gemini"][0]

FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

PROMPT = """You are analyzing video frames extracted from a YouTube video about the Indian RC car / toy supply chain.

CONTEXT: The user (BCH, Bangalore) is sourcing supply-side partners for a drift RC SKU at ₹800-₹2,500 retail. He explicitly wants MANUFACTURERS, DISTRIBUTORS, WHOLESALERS, TRADERS, IMPORTERS — NOT retailers. Retailers are his future competition, not his suppliers. So your job is to look at the frames and decide what side of the supply chain the vendor is on.

CRITICAL DISTINCTIONS:

**MANUFACTURER signals (high value):**
- Factory floor visible (concrete floor, industrial lighting, fluorescent tubes)
- Assembly line / workers at benches assembling units
- Plastic injection moulding machines (large yellow/grey hydraulic presses)
- Raw materials visible (plastic pellet bags, electronic components in trays, motor coils)
- Production-line packaging (heat-sealers, blister packs, boxing stations)
- Quality control stations
- "Manufactured by" / "OEM" / "Factory direct" wording on signage
- Branded boxes being filled in volume
- Multiple identical units in production stages

**DISTRIBUTOR / WHOLESALER signals (high value):**
- Warehouse with floor-to-ceiling racking
- Pallets of stacked cartons
- Forklift visible
- Cartons with multi-brand stickers, mixed inventory at scale
- "Wholesale only" / "MOQ" / "Dealer enquiry" signs
- Open boxes showing many identical units (10+ pieces of same SKU)
- Loading dock / shutter / cargo van visible
- Cash counter with large note bundles
- GST board, dealer-license board on wall
- Older male wholesaler at counter (not customer-facing staff)

**TRADER / IMPORTER signals (high value):**
- Shipping cartons with Chinese / Korean labels
- Container unloading
- Customs paperwork visible
- Multi-brand inventory not branded as "official dealer"
- Sadar Bazar / Crawford Market / Bhajipala Lane / Lohar Chawl / Bhiwandi visible signage

**RETAILER signals (LOW value — explicitly excluded from BCH's interest):**
- Single-piece glass displays
- Showroom layout with individual products on shelves
- Price tags on every piece
- Customer-facing staff in uniforms
- Children / families browsing
- "Welcome" / opening-hours boards
- Premium boutique aesthetic

**HOBBYIST / CREATOR signals (LOW value):**
- Home workshop / garage
- Single vehicle being unboxed / reviewed
- Personal tools / pegboard
- Track / driving footage

Examine the frames carefully and return ONLY this JSON (no markdown fences):

{
  "vendor_type": "MANUFACTURER | DISTRIBUTOR | WHOLESALER | TRADER | IMPORTER | RETAILER | HOBBYIST | CREATOR_REVIEWER | NA",
  "supply_side": true_if_one_of_first_5_else_false,
  "production_signals": ["short list of factory/warehouse/wholesale visual indicators you actually saw — be specific"],
  "scale_visible": "micro | small | medium | large | unclear",
  "estimated_inventory_pieces_visible": "<10 | 10-100 | 100-1000 | 1000+ | not-counted",
  "rc_car_present": true|false,
  "drift_rc_present": true|false,
  "products_seen": ["short descriptions of distinct products visible"],
  "shop_or_facility_signage_text": "any signage text you can read, else empty",
  "city_or_market_visible": "if a market/area is named in signage (e.g. 'Sadar Bazar', 'Crawford Market'), else empty",
  "vendor_grade": "hobby-grade | toy-grade | mixed | parts | not-a-product",
  "bch_relevance_1_10": 0-10 integer (10 = supply-side vendor selling drift-RC at grey-space scale; 0 = retailer or unrelated),
  "skip_if_retailer": true|false (true ONLY if vendor_type is RETAILER, HOBBYIST or CREATOR_REVIEWER and BCH should NOT pursue),
  "verdict_one_line": "1 sentence — vendor type + what they sell + supply-side relevance to BCH's grey-space drift sourcing"
}

Rules:
- Default to SUPPLY-SIDE generously when in doubt. If you see boxes of multiple identical units, lean WHOLESALER/DISTRIBUTOR over RETAILER.
- DO NOT classify vlog/review channels as supply-side just because they FILMED inside a warehouse. If the person on camera is a vlogger touring a vendor (not the vendor themselves), classify as CREATOR_REVIEWER and skip_if_retailer=true.
- shop_or_facility_signage_text is critical — if you can read the shop name, type it exactly.
- A MANUFACTURER who also runs a small wholesale showfloor still = MANUFACTURER.
- Drift-RC at sub-₹2,500 price band scores 10 ONLY if the vendor is supply-side AND the product matches; toy-grade wholesale at the right scale scores 6-8."""


def encode_image(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()


def classify_video(video_id, channel_title, frames, out_dir, max_retries=4):
    parts = [{"text": PROMPT}]
    for fr in frames[:5]:
        path = os.path.join(out_dir, fr["path"]) if not os.path.isabs(fr["path"]) else fr["path"]
        if not os.path.exists(path):
            continue
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": encode_image(path)}})

    body = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
    }).encode()

    last_err = ""
    for model in FALLBACK_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        for attempt in range(max_retries):
            req = urllib.request.Request(url, data=body, method="POST",
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                code = e.code
                err_body = e.read()[:300].decode("utf-8", "ignore")
                if code in (503, 429, 500) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt + 1)
                    continue
                last_err = f"{model} HTTP {code}: {err_body[:120]}"
                data = None
                break
            except Exception as e:
                last_err = f"{model}: {e}"
                data = None
                break
        if data is None:
            continue
        try:
            txt = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            last_err = f"{model}: empty/blocked"
            continue
        t = txt.strip()
        if t.startswith("```"):
            t = re.sub(r"^```\w*\n?", "", t)
            t = re.sub(r"\n?```\s*$", "", t)
        m = re.search(r"\{[\s\S]*\}", t)
        if not m:
            last_err = f"{model}: no JSON"
            continue
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError as e:
            s = m.group(0)
            s = re.sub(r",\s*([}\]])", r"\1", s)
            s += "}" * (s.count("{") - s.count("}"))
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                last_err = f"{model}: parse: {e}"
                continue
    return {"_error": last_err or "all models failed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input", required=True, help="vendors.json path")
    ap.add_argument("--out", dest="output", required=True, help="output JSON path")
    args = ap.parse_args()

    vendors = json.load(open(args.input))
    out_dir = os.path.dirname(os.path.abspath(args.input))

    jobs = []
    for c in vendors:
        for vd in c["videos"]:
            if vd.get("frames"):
                jobs.append({
                    "video_id": vd["videoId"],
                    "channel_title": c["channelTitle"],
                    "title": vd["title"],
                    "frames": vd["frames"],
                })

    results = {}
    if os.path.exists(args.output):
        results = json.load(open(args.output))
        before = len(jobs)
        jobs = [j for j in jobs if j["video_id"] not in results or results[j["video_id"]]["verdict"].get("_error")]
        print(f"[gemini] {before - len(jobs)} already classified, {len(jobs)} remaining")

    print(f"[gemini] supply-side classifier on {len(jobs)} videos, 3 workers, retries + model fallback")

    def worker(j):
        verdict = classify_video(j["video_id"], j["channel_title"], j["frames"], out_dir)
        return j["video_id"], j, verdict

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(worker, j) for j in jobs]
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            vid, j, verdict = fut.result()
            results[vid] = {"channel": j["channel_title"], "title": j["title"], "verdict": verdict}
            err = verdict.get("_error")
            if err:
                print(f"  [{i}/{len(jobs)}] {j['channel_title'][:30]:30s} {vid} ERROR: {err[:80]}")
            else:
                vt = verdict.get("vendor_type", "?")
                ss = "✓" if verdict.get("supply_side") else "✗"
                rel = verdict.get("bch_relevance_1_10", "?")
                print(f"  [{i}/{len(jobs)}] {j['channel_title'][:30]:30s} {vid} type={vt:14s} supply={ss} rel={rel}")

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {args.output}")

    by_type = {}
    for vid, r in results.items():
        vt = r["verdict"].get("vendor_type", "error")
        by_type.setdefault(vt, []).append(r["channel"])
    print("\n=== SUMMARY ===")
    for vt in sorted(by_type, key=lambda x: -len(by_type[x])):
        print(f"  {vt}: {len(by_type[vt])} ({', '.join(set(by_type[vt]))[:80]})")


if __name__ == "__main__":
    main()
