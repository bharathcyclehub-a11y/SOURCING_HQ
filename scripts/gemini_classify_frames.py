#!/usr/bin/env python3
"""
gemini_classify_frames.py — Pass each video's extracted frames to Gemini for product classification.

Reads vendors.json, iterates videos that have frames, sends the frames as inline images
to Gemini 2.5 Flash, and returns a structured verdict per video.

Outputs gemini_verdicts.json — keyed by videoId.

Verdict shape per video:
{
  "products_seen": ["RC drift car", "RC monster truck", ...],
  "grade": "hobby-grade" | "toy-grade" | "mixed" | "parts-only" | "not-a-product",
  "scale_visible": "1:10" | "1:24" | "unknown" | "n/a",
  "rc_present": true,
  "non_rc_present": ["dolls", "battery jeep ride-on", "drones", ...],
  "bch_relevance_1_10": 7,
  "verdict_one_line": "Hobby-grade RC drift cars visible at ~1:10 scale; aligned with BCH Mini Drift play.",
  "shop_signage_visible": true,
  "shop_name_on_signage": "Milestone Impex" | ""
}
"""

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
VENDORS = os.path.join(HERE, "yt_rc_output", "vendors.json")
OUT = os.path.join(HERE, "yt_rc_output", "gemini_verdicts.json")
OUT_DIR = os.path.join(HERE, "yt_rc_output")

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_KEY}"

PROMPT = """You are a visual product analyst for an Indian RC-car / cycle retail business (BCH).
You are looking at frames extracted from a YouTube video about RC cars / toys in a Delhi market or shop.

Examine the frames carefully and report ONLY what is visible. Return ONLY a valid JSON object — no markdown fences, no text outside it.

Classification grades:
- "hobby-grade"   : real hobby RC (brushless, 1:10 / 1:8 scale, drift cars, rally, crawlers, FPV — Tygatec / WLtoys / Traxxas tier)
- "toy-grade"    : kid toys, sub-Rs 2000, plastic shells, simple proportional steering, generic Chinese imports
- "mixed"        : both grades visible in the same shop
- "parts-only"   : only spare parts (motors, ESCs, lipo, tires, gears) — no whole cars
- "not-a-product" : video doesn't actually show RC products (real cars, AI content, etc.)

BCH context: we are building a Mini RC Drift Car SKU (hobby-grade aspirational, ~1:24 to 1:18 scale,
LED + drift wheels). We want to find Delhi suppliers of hobby-grade product OR spare parts OR
manufacturers who could private-label our SKU. Toy-grade retailers are LOW priority.

Return ONLY this JSON:
{
  "products_seen": ["short description of each distinct product type visible"],
  "grade": "hobby-grade / toy-grade / mixed / parts-only / not-a-product",
  "scale_visible": "1:10 / 1:24 / unknown / n/a",
  "rc_present": true/false,
  "non_rc_present": ["dolls", "ride-on jeeps", "drones", "plush", "..."],
  "shop_signage_visible": true/false,
  "shop_name_on_signage": "exact text on signage if visible, else empty string",
  "bch_relevance_1_10": 0-10 integer (10 = perfect hobby-grade or parts/mfg lead; 0 = irrelevant),
  "verdict_one_line": "1 sentence summary for the BCH sourcing report"
}"""


def encode_image(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()


FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]


def classify_video(video_id, channel_title, frames, max_retries=4):
    """Send up to 5 frames to Gemini, return verdict dict. Retries on 503 + model fallback."""
    parts = [{"text": PROMPT}]
    for fr in frames[:5]:
        path = os.path.join(OUT_DIR, fr["path"]) if not os.path.isabs(fr["path"]) else fr["path"]
        if not os.path.exists(path):
            continue
        parts.append({
            "inlineData": {
                "mimeType": "image/jpeg",
                "data": encode_image(path),
            }
        })

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
                    time.sleep(2 ** attempt + 1)  # 2,3,5,9
                    continue
                last_err = f"{model} HTTP {code}: {err_body[:120]}"
                data = None
                break
            except Exception as e:
                last_err = f"{model}: {e}"
                data = None
                break
        if data is None:
            continue  # try next model

        try:
            txt = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            last_err = f"{model}: empty candidates / safety block"
            continue

        t = txt.strip()
        if t.startswith("```"):
            t = re.sub(r"^```\w*\n?", "", t)
            t = re.sub(r"\n?```\s*$", "", t)
        m = re.search(r"\{[\s\S]*\}", t)
        if not m:
            last_err = f"{model}: no JSON in response"
            continue
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError as e:
            # try to repair
            s = m.group(0)
            s = re.sub(r",\s*([}\]])", r"\1", s)
            s += "}" * (s.count("{") - s.count("}"))
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                last_err = f"{model}: json parse: {e}"
                continue
    return {"_error": last_err or "all models failed"}


def main():
    vendors = json.load(open(VENDORS))
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

    # resume: skip videos already classified successfully
    results = {}
    if os.path.exists(OUT):
        results = json.load(open(OUT))
        before = len(jobs)
        jobs = [j for j in jobs if j["video_id"] not in results or results[j["video_id"]]["verdict"].get("_error")]
        print(f"[gemini] {before - len(jobs)} videos already classified successfully — resuming with {len(jobs)} remaining")
    print(f"[gemini] classifying {len(jobs)} videos in parallel (max 3 workers, with retries + model fallback)...")

    def worker(j):
        verdict = classify_video(j["video_id"], j["channel_title"], j["frames"])
        return j["video_id"], j, verdict

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(worker, j) for j in jobs]
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            vid, j, verdict = fut.result()
            results[vid] = {
                "channel": j["channel_title"],
                "title": j["title"],
                "verdict": verdict,
            }
            err = verdict.get("_error")
            if err:
                print(f"  [{i}/{len(jobs)}] {j['channel_title'][:30]} {vid}  ERROR: {err[:80]}")
            else:
                g = verdict.get("grade", "?")
                rel = verdict.get("bch_relevance_1_10", "?")
                print(f"  [{i}/{len(jobs)}] {j['channel_title'][:30]:30s} {vid}  grade={g:14s} rel={rel}")

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {OUT}")

    # Summary
    print(f"\n=== SUMMARY ===")
    by_grade = {}
    for vid, r in results.items():
        g = r["verdict"].get("grade", "error")
        by_grade.setdefault(g, []).append(r["channel"])
    for g, chans in sorted(by_grade.items(), key=lambda x: -len(x[1])):
        print(f"  {g}: {len(chans)} videos  ({', '.join(chans[:5])}{'...' if len(chans) > 5 else ''})")


if __name__ == "__main__":
    main()
