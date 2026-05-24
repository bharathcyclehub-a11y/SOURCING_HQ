#!/usr/bin/env python3
"""
LinkedIn industry-scan via Apify (no LinkedIn cookies needed).
Loads keys from scripts/keys.json (gitignored).
Scrapes posts via harvestapi/linkedin-post-search, deduplicates authors,
ranks by RC/toy industry relevance, prints + saves to scripts/rc_pipeline_output/.

Usage:
  python3 scripts/apify_linkedin_industry_scan.py
  python3 scripts/apify_linkedin_industry_scan.py --queries "RC India" "toy founder India"
  python3 scripts/apify_linkedin_industry_scan.py --max-per-query 20

Costs: ~$0.05-0.20 of Apify credit per run (well within the FREE $5/mo budget).
"""
import json
import os
import re
import sys
import time
import argparse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = ROOT / "rc_pipeline_output"
OUT.mkdir(exist_ok=True)

DEFAULT_QUERIES = [
    "RC car India hobby",
    "toy manufacturer India remote control",
    "RC drift India",
    "hobby grade RC India distributor",
    "Legend of Toys",
    "Mirana Innovations",
    "Tygatec RC",
    "MJX Hyper Go India",
    "toy startup India founder",
    "hobby RC India founder",
]

RC_DIRECT = re.compile(
    r"\b(rc\s*car|remote\s*control\s*car|hobby[\s-]?grade|rc\s*drift|rc\s*hobby|"
    r"drift\s*car|rc\s*scale|rc\s*racing|toy\s*manufacturer|toy\s*industry|"
    r"toy\s*brand|toy\s*startup|toy\s*founder|model\s*car|diecast|toy\s*car|"
    r"miniat|brushless\s*car|playshifu|skillmatics|smartivity|tamiya|kyosho|"
    r"arrma|traxxas|mjx|hyper\s*go|wltoys|rlaarlo|tygatec|mirana|webby\s*toys|"
    r"toyshine|legend\s*of\s*toys|veva\s*toys|baybee|kv\s*toys|funskool|hamley|"
    r"ok\s*play|toyzone|centy)",
    re.I,
)


def load_keys():
    """Load Apify keys from scripts/keys.json. Returns list of keys."""
    p = ROOT / "keys.json"
    if not p.exists():
        print(f"ERROR: {p} not found. Copy keys.example.json to keys.json and add your Apify key.")
        sys.exit(1)
    data = json.loads(p.read_text())
    keys = data.get("apify", [])
    valid = [k for k in keys if k and not k.startswith("apify_api_xxx")]
    if not valid:
        print("ERROR: no valid Apify keys in scripts/keys.json")
        sys.exit(1)
    return valid


def apify_call(token, queries, max_per_query):
    """Run harvestapi/linkedin-post-search sync. Returns list of post items."""
    url = (
        "https://api.apify.com/v2/acts/harvestapi~linkedin-post-search/"
        f"run-sync-get-dataset-items?token={token}&timeout=300&memory=512"
    )
    body = json.dumps(
        {
            "searchQueries": queries,
            "maxPosts": max_per_query,
            "postedLimit": "year",
            "sortBy": "relevance",
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def relevance(author):
    """Classify author by RC/toy industry signal strength."""
    info = (author.get("info") or "").lower()
    content = " ".join((p["content_excerpt"] or "") for p in author["posts"]).lower()

    if any(
        k in info
        for k in ["fmcg", "sekel", "cement", "pharma", "fintech", "real estate", "crypto"]
    ) and not any(k in info for k in ["toy", "hobby", "rc"]):
        return "NOISE"

    info_hits = len(RC_DIRECT.findall(info))
    content_hits = len(RC_DIRECT.findall(content))

    if info_hits >= 1:
        return "HIGH"
    if content_hits >= 3:
        return "HIGH"
    if content_hits >= 1 and any(
        k in info
        for k in ["founder", "ceo", "director", "journalist", "investor", "partner", "president"]
    ):
        return "MEDIUM"
    if content_hits >= 1:
        return "LOW"
    return "NOISE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", nargs="+", help="Override default search queries")
    ap.add_argument("--max-per-query", type=int, default=12, help="Posts per query (default 12)")
    args = ap.parse_args()

    queries = args.queries or DEFAULT_QUERIES
    print(f"Queries ({len(queries)}):")
    for q in queries:
        print(f"  - {q}")
    print(f"Max posts per query: {args.max_per_query}")
    print()

    keys = load_keys()
    print(f"Loaded {len(keys)} Apify key(s)")

    # Run with first key. (Rotation across 429 omitted for brevity — extend if needed.)
    print("Calling harvestapi/linkedin-post-search ...")
    t0 = time.time()
    posts = apify_call(keys[0], queries, args.max_per_query)
    elapsed = time.time() - t0
    print(f"Got {len(posts)} posts in {elapsed:.1f}s")

    # Save raw
    raw_path = OUT / f"linkedin_posts_{int(time.time())}.json"
    raw_path.write_text(json.dumps(posts, indent=2))
    print(f"Raw saved: {raw_path}")

    # Dedupe authors
    authors = {}
    for p in posts:
        a = p.get("author", {})
        if not a or a.get("type") != "profile":
            continue
        url = (a.get("linkedinUrl") or "").split("?")[0]
        if not url:
            continue
        if url not in authors:
            authors[url] = {
                "name": a.get("name"),
                "url": url,
                "public_id": a.get("publicIdentifier"),
                "info": a.get("info", ""),
                "posts": [],
                "engagement_total": 0,
            }
        eng = p.get("engagement") or {}
        likes = eng.get("likes", 0) or 0
        comments = eng.get("comments", 0) or 0
        authors[url]["posts"].append(
            {
                "query": p.get("query"),
                "content_excerpt": (p.get("content") or "")[:250].replace("\n", " "),
                "posted": (p.get("postedAt") or {}).get("postedAgoShort"),
                "likes": likes,
                "comments": comments,
                "post_url": p.get("linkedinUrl"),
            }
        )
        authors[url]["engagement_total"] += likes + comments

    for a in authors.values():
        a["relevance"] = relevance(a)

    scored = sorted(
        authors.values(),
        key=lambda x: (
            {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NOISE": 0}[x["relevance"]],
            x["engagement_total"],
        ),
        reverse=True,
    )

    ranked_path = OUT / f"linkedin_authors_ranked_{int(time.time())}.json"
    ranked_path.write_text(json.dumps(scored, indent=2))
    print(f"Ranked authors saved: {ranked_path}")

    print()
    print("=" * 70)
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "NOISE": 0}
    for a in scored:
        counts[a["relevance"]] += 1
    print(
        f"Found {len(scored)} unique authors → "
        f"{counts['HIGH']} HIGH / {counts['MEDIUM']} MEDIUM / "
        f"{counts['LOW']} LOW / {counts['NOISE']} NOISE"
    )
    print("=" * 70)

    for tier in ("HIGH", "MEDIUM"):
        print()
        print(f"--- {tier} ---")
        for a in scored:
            if a["relevance"] != tier:
                continue
            print(f"\n• {a['name']} ({a['engagement_total']} eng)")
            print(f"  {a['info'][:130]}")
            print(f"  {a['url']}")


if __name__ == "__main__":
    main()
