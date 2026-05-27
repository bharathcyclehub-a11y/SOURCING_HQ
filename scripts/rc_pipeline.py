#!/usr/bin/env python3
"""
rc_pipeline.py — RC competitor reel pipeline for BCH (SOURCING_HQ)
Ported from "bch content app instore" src/lib/video-pipeline.ts (v3).

Flow:  Apify (find top reels + view counts)  ->  Gemini (watch video, extract RC SKU JSON)  ->  JSON files
Stage 3 (Claude decode) is done in-session by Claude reading the JSON output.

Key rotation: each pool (apify, gemini) is used one key at a time; on a 429 /
quota-exhausted error the script advances to the next key and retries.

Zero dependencies — standard library only.

Usage:
    python3 rc_pipeline.py --handles highgeartoys,youcliq,daddydronesmumbai --count 5
    python3 rc_pipeline.py --hashtags rccars,rcdrift --count 10
    python3 rc_pipeline.py --reels https://www.instagram.com/reel/DVMbj0EjPxV/
    python3 rc_pipeline.py --handles highgeartoys --count 3 --dry-run

Flags:
    --handles    comma-separated Instagram handles (fetches their top reels by views)
    --hashtags   comma-separated hashtags (fetches top reels for each tag)
    --reels      comma-separated specific reel URLs (skips Apify discovery)
    --count N    reels per handle/hashtag (default 5)
    --out DIR    output directory (default scripts/rc_pipeline_output)
    --dry-run    Stage 1 only — list reels found, no download/Gemini
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(HERE, "keys.json")
DEFAULT_OUT = os.path.join(HERE, "rc_pipeline_output")

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]


# ── Key rotation ────────────────────────────────────────────────────────────

class KeyPool:
    """Holds a list of keys; advances to the next only on quota errors."""
    def __init__(self, name, keys):
        self.name = name
        self.keys = [k for k in keys if k and not k.startswith("PASTE_")]
        self.i = 0
        if not self.keys:
            sys.exit(f"ERROR: no usable keys in pool '{name}' — edit {KEYS_FILE}")

    def current(self):
        return self.keys[self.i]

    def rotate(self):
        """Move to next key. Returns False if all keys exhausted."""
        if self.i + 1 >= len(self.keys):
            return False
        self.i += 1
        print(f"  [{self.name}] quota hit — rotating to key #{self.i + 1}/{len(self.keys)}")
        return True


def is_quota_error(status, body):
    if status == 429:
        return True
    b = (body or "").lower()
    return "resource_exhausted" in b or "quota" in b or "rate limit" in b or "max data limit" in b


def http(method, url, headers=None, data=None, timeout=210):
    """Single HTTP call. Returns (status, body_bytes). Never raises on HTTP error."""
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()


# ── Stage 1: Apify — find top reels ─────────────────────────────────────────

def apify_run(pool, body):
    """Run apify~instagram-scraper, return dataset items. Rotates keys on quota."""
    while True:
        token = pool.current()
        status, raw = http(
            "POST",
            f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?waitForFinish=210&token={token}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(body).encode(),
        )
        if is_quota_error(status, raw.decode("utf-8", "ignore")):
            if pool.rotate():
                continue
            sys.exit("ERROR: all Apify keys exhausted")
        if status not in (200, 201):
            print(f"  [apify] run failed ({status}): {raw[:200].decode('utf-8','ignore')}")
            return []
        ds = json.loads(raw)["data"].get("defaultDatasetId")
        if not ds:
            return []
        s2, raw2 = http("GET", f"https://api.apify.com/v2/datasets/{ds}/items?format=json&token={token}")
        if is_quota_error(s2, raw2.decode("utf-8", "ignore")):
            if pool.rotate():
                continue
            sys.exit("ERROR: all Apify keys exhausted")
        items = json.loads(raw2) if s2 == 200 else []
        return items if isinstance(items, list) else []


def reels_from_items(items, count):
    """Filter to videos, dedup, sort by views desc, take top N."""
    seen, reels = set(), []
    for it in items:
        if not (it.get("type") == "Video" or it.get("videoUrl")):
            continue
        sc = it.get("shortCode") or ""
        if sc in seen:
            continue
        seen.add(sc)
        reels.append({
            "url": it.get("url") or f"https://www.instagram.com/reel/{sc}/",
            "shortCode": sc,
            "caption": (it.get("caption") or "").replace("\n", " "),
            "views": it.get("videoViewCount") or it.get("videoPlayCount") or 0,
            "likes": it.get("likesCount") or 0,
            "comments": it.get("commentsCount") or 0,
            "timestamp": it.get("timestamp") or "",
            "ownerUsername": it.get("ownerUsername") or "",
            "videoUrl": it.get("videoUrl"),
        })
    reels.sort(key=lambda r: (r["views"], r["likes"] + r["comments"]), reverse=True)
    return reels[:count]


def fetch_by_handle(pool, handle, count):
    h = handle.strip().lstrip("@").rstrip("/")
    m = re.search(r"instagram\.com/([A-Za-z0-9._]+)", h)
    if m:
        h = m.group(1)
    items = apify_run(pool, {
        "directUrls": [f"https://www.instagram.com/{h}/"],
        "resultsType": "posts", "resultsLimit": 200,
        "searchType": "user", "searchLimit": 1,
    })
    return reels_from_items(items, count)


def fetch_by_hashtag(pool, tag, count):
    tag = tag.strip().lstrip("#")
    items = apify_run(pool, {
        "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/"],
        "resultsType": "posts", "resultsLimit": 200,
        "searchType": "hashtag", "searchLimit": 1,
    })
    return reels_from_items(items, count)


def fetch_specific_reels(pool, urls):
    items = apify_run(pool, {
        "directUrls": [u.strip() for u in urls],
        "resultsType": "posts", "resultsLimit": 1, "addParentData": False,
    })
    return reels_from_items(items, len(urls))


# ── Stage 2: Gemini — watch video, extract RC SKU JSON ──────────────────────

EXTRACTION_PROMPT = r"""You are a video observation tool extracting signals from an Instagram reel about RC (remote-control) cars / toys.
Watch the ENTIRE video. Report ONLY what you SEE and HEAR — no opinions.
Return ONLY a valid JSON object (no markdown fences, no text outside it) with these exact keys:

{
  "rc_product": {
    "is_rc_product": true,
    "sku_type": "mini-drift-car / hobby-grade-rc / monster-truck / rock-crawler / rc-with-fpv-camera / diecast-static / other / NOT-A-PRODUCT",
    "body_shape": "the real car it imitates (e.g. Dodge Challenger, GTR, Supra) or 'generic'",
    "scale": "e.g. 1:24, 1:43, 1:10, or 'unknown'",
    "features_shown": ["drift","LED-lights","smoke","swappable-wheels","fpv-camera","speed","jumps","..."],
    "price_mentioned": "exact price text shown/spoken or empty",
    "price_inr": 0
  },
  "hook_category": "gifting-relationship / desk-room-aesthetic / price-reveal / comment-to-buy / speed-action / unboxing / other",
  "hook_window": {
    "first_3_seconds_visual": "exactly what happens visually 0:00-0:03",
    "first_3_seconds_audio": "exactly what is heard 0:00-0:03",
    "first_words_spoken": "exact first phrase",
    "pattern_interrupt": "what breaks expectation, or 'none'"
  },
  "transcript": [{"time":"MM:SS","speaker":"who","text":"exact words","language":"Hindi/English/Kannada/mixed"}],
  "visual_timeline": [{"time":"MM:SS","description":"<20 words, camera + action","energy":0}],
  "on_screen_text": [{"time":"MM:SS","text":"exact text","position":"top/center/bottom"}],
  "audio": {"has_music": true, "music_mood": "", "has_voice": true, "voice_tone": "", "sfx": ""},
  "ending": {"last_3_seconds": "", "cta_type": "tag-friend/follow/comment/DM/link-in-bio/none", "cta_exact_words": ""},
  "format": "skit/POV/storytime/demo/transformation/unboxing/other",
  "duration_seconds": 0,
  "what_makes_this_viral": "one sentence — the single mechanic driving the views"
}

Rules:
- If the video shows real full-size cars, AI content, or anything that is NOT an RC/toy product, set rc_product.is_rc_product=false and sku_type="NOT-A-PRODUCT".
- Limit visual_timeline to 15 entries. Keep transcript concise.
- Return ONLY the JSON object."""


def gemini_extract(pool, video_bytes):
    """Upload to Gemini File API, poll ACTIVE, run extraction. Rotates keys on quota."""
    while True:
        key = pool.current()
        # 1. upload
        status, raw = http(
            "POST",
            f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={key}",
            headers={"Content-Type": "video/mp4", "X-Goog-Upload-Protocol": "raw"},
            data=video_bytes,
        )
        if is_quota_error(status, raw.decode("utf-8", "ignore")):
            if pool.rotate():
                continue
            raise RuntimeError("all Gemini keys exhausted")
        if status != 200:
            raise RuntimeError(f"Gemini upload failed ({status}): {raw[:200].decode('utf-8','ignore')}")
        up = json.loads(raw)["file"]
        name, uri = up["name"], up["uri"]

        # 2. poll until ACTIVE
        for _ in range(30):
            time.sleep(2)
            s, r = http("GET", f"https://generativelanguage.googleapis.com/v1beta/{name}?key={key}")
            st = json.loads(r).get("state") if s == 200 else None
            if st == "ACTIVE":
                break
            if st == "FAILED":
                raise RuntimeError("Gemini video processing FAILED")
        else:
            raise RuntimeError("Gemini processing timeout")

        # 3. generate — model fallback chain
        last = ""
        for model in GEMINI_MODELS:
            body = json.dumps({
                "contents": [{"parts": [
                    {"fileData": {"mimeType": "video/mp4", "fileUri": uri}},
                    {"text": EXTRACTION_PROMPT},
                ]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 16384},
            }).encode()
            s, r = http(
                "POST",
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                headers={"Content-Type": "application/json"}, data=body,
            )
            txt = r.decode("utf-8", "ignore")
            if is_quota_error(s, txt):
                if pool.rotate():
                    break  # restart whole upload with new key
                raise RuntimeError("all Gemini keys exhausted")
            if s != 200:
                last = f"{model}: {txt[:160]}"
                continue
            try:
                cand = json.loads(r)["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                last = f"{model}: empty/blocked response"
                continue
            return parse_json(cand)
        else:
            raise RuntimeError(f"all Gemini models failed: {last}")
        # if we broke out due to rotate, loop restarts upload with the new key


def parse_json(text):
    """Parse Gemini JSON output with repair for truncation / fences."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```\w*\n?", "", t)
        t = re.sub(r"\n?```\s*$", "", t)
    m = re.search(r"\{[\s\S]*\}", t)
    if not m:
        return {"_parse_error": "no JSON found", "_raw": text[:500]}
    s = m.group(0)
    s = re.sub(r",\s*([}\]])", r"\1", s)  # trailing commas
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        repaired = re.sub(r',?\s*"[^"]*$', "", s)
        repaired += "]" * (repaired.count("[") - repaired.count("]"))
        repaired += "}" * (repaired.count("{") - repaired.count("}"))
        repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            return {"_parse_error": "unrepairable", "_raw": text[:500]}


def download(url):
    status, raw = http("GET", url, timeout=120)
    if status != 200 or len(raw) < 1000:
        raise RuntimeError(f"video download failed ({status}) — CDN link may have expired")
    return raw


# ── Orchestration ───────────────────────────────────────────────────────────

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def main():
    ap = argparse.ArgumentParser(description="RC competitor reel pipeline (Apify -> Gemini -> JSON)")
    ap.add_argument("--handles", default="", help="comma-separated IG handles")
    ap.add_argument("--hashtags", default="", help="comma-separated hashtags")
    ap.add_argument("--reels", default="", help="comma-separated specific reel URLs")
    ap.add_argument("--count", type=int, default=5, help="reels per handle/hashtag")
    ap.add_argument("--out", default=DEFAULT_OUT, help="output directory")
    ap.add_argument("--dry-run", action="store_true", help="Stage 1 only")
    args = ap.parse_args()

    if not os.path.exists(KEYS_FILE):
        sys.exit(f"ERROR: {KEYS_FILE} not found — copy keys.example.json to keys.json")
    keys = json.load(open(KEYS_FILE))
    apify_pool = KeyPool("apify", keys.get("apify", []))
    os.makedirs(args.out, exist_ok=True)

    # ── Stage 1: discover reels
    targets = []
    for h in filter(None, [x.strip() for x in args.handles.split(",")]):
        print(f"[apify] fetching top {args.count} reels for @{h}")
        for r in fetch_by_handle(apify_pool, h, args.count):
            targets.append(r)
    for t in filter(None, [x.strip() for x in args.hashtags.split(",")]):
        print(f"[apify] fetching top {args.count} reels for #{t}")
        for r in fetch_by_hashtag(apify_pool, t, args.count):
            targets.append(r)
    reel_urls = list(filter(None, [x.strip() for x in args.reels.split(",")]))
    if reel_urls:
        print(f"[apify] fetching {len(reel_urls)} specific reels")
        targets += fetch_specific_reels(apify_pool, reel_urls)

    # dedup by shortCode
    uniq, seen = [], set()
    for r in targets:
        if r["shortCode"] and r["shortCode"] not in seen:
            seen.add(r["shortCode"])
            uniq.append(r)
    print(f"\n[stage 1] {len(uniq)} unique reels discovered\n")
    for r in sorted(uniq, key=lambda x: x["views"], reverse=True):
        print(f"  {r['views']:>12,} views  @{r['ownerUsername']:24s} {r['url']}")

    if args.dry_run:
        print("\n[dry-run] stopping before download/Gemini.")
        return
    if not uniq:
        print("\nNothing to process.")
        return

    # ── Stage 2: Gemini extraction
    gemini_pool = KeyPool("gemini", keys.get("gemini", []))
    ok, fail = 0, 0
    print()
    for i, r in enumerate(uniq, 1):
        tag = f"[{i}/{len(uniq)}] @{r['ownerUsername']} {r['shortCode']}"
        if not r.get("videoUrl"):
            print(f"{tag} — SKIP (no videoUrl from Apify)")
            fail += 1
            continue
        try:
            print(f"{tag} — downloading + analyzing...")
            data = gemini_extract(gemini_pool, download(r["videoUrl"]))
            record = {
                "meta": {
                    "url": r["url"], "shortCode": r["shortCode"],
                    "owner": r["ownerUsername"], "views": r["views"],
                    "likes": r["likes"], "comments": r["comments"],
                    "timestamp": r["timestamp"], "caption": r["caption"],
                },
                "extraction": data,
            }
            fn = f"{r['views']:012d}_{slug(r['ownerUsername'])}_{r['shortCode']}.json"
            with open(os.path.join(args.out, fn), "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
            print(f"           saved {fn}")
            ok += 1
        except Exception as e:
            print(f"           FAILED: {e}")
            fail += 1
        time.sleep(2)

    print(f"\n[done] success {ok} | failed {fail} | output in {args.out}")
    print("Next: Claude reads the JSON files for Stage 3 (virality decode).")


if __name__ == "__main__":
    main()
