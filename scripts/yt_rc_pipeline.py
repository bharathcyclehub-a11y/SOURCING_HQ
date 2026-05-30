#!/usr/bin/env python3
"""
yt_rc_pipeline.py — YouTube RC-car-vendor discovery for BCH Delhi sourcing.

Flow:
  Stage 1 (discovery)  : YouTube Data API search across N queries -> candidate videos
  Stage 2 (enrichment) : video details + channel "About" + top comments
  Stage 3 (contacts)   : regex Indian phone + WhatsApp + IG + email + website
  Stage 4 (relevance)  : keyword scoring -> manufacturer / wholesaler / parts / hobby-retail / toy-retail / other
  Stage 5 (frames)     : yt-dlp download + ffmpeg frame extraction at product-reveal timestamps
  Stage 6 (report)     : write JSON + Markdown index per query and combined

Zero deps beyond stdlib + yt-dlp + ffmpeg on PATH. Keys from scripts/keys.json.

Usage:
  python3 yt_rc_pipeline.py --discover         # Stage 1-4 (no downloads), writes vendors.json
  python3 yt_rc_pipeline.py --frames TOPN      # Stage 5 for top N relevant channels
  python3 yt_rc_pipeline.py --all              # full pipeline (discover + frames for top 15)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(HERE, "keys.json")
DEFAULT_OUT_DIR = os.path.join(HERE, "yt_rc_output")
# OUT_DIR / FRAMES_DIR are now set in main() after parsing --out
OUT_DIR = DEFAULT_OUT_DIR
FRAMES_DIR = os.path.join(OUT_DIR, "frames")

QUERIES = [
    "rc cars market in Delhi",
    "rc cars in Delhi",
    "rc car manufacturer in Delhi",
    "rc car wholesale in Delhi",
]

RESULTS_PER_QUERY = 25
MAX_COMMENTS_PER_VIDEO = 30

# ── HTTP helper ─────────────────────────────────────────────────────────────

def http_json(url, timeout=60):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {"raw_error": str(e)}
        return e.code, body
    except Exception as e:
        return 0, {"raw_error": str(e)}


# ── YouTube Data API wrappers ──────────────────────────────────────────────

def yt_search(api_key, query, max_results=25):
    """Returns list of {videoId, title, channelId, channelTitle, publishedAt, description}."""
    base = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet", "q": query, "type": "video",
        "maxResults": str(min(max_results, 50)),
        "regionCode": "IN", "relevanceLanguage": "en",
        "key": api_key,
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    status, data = http_json(url)
    if status != 200:
        print(f"  [search] FAILED ({status}): {data}")
        return []
    out = []
    for it in data.get("items", []):
        sn = it.get("snippet", {})
        vid = it.get("id", {}).get("videoId") if isinstance(it.get("id"), dict) else None
        if not vid:
            continue  # skip non-video results (channels, playlists) that occasionally slip through type=video
        out.append({
            "videoId": vid,
            "title": sn.get("title", ""),
            "channelId": sn.get("channelId", ""),
            "channelTitle": sn.get("channelTitle", ""),
            "publishedAt": sn.get("publishedAt", ""),
            "description_snippet": sn.get("description", ""),
            "thumbnail": sn.get("thumbnails", {}).get("high", {}).get("url", ""),
        })
    return out


def yt_video_details(api_key, video_ids):
    """Returns dict videoId -> {duration, viewCount, likeCount, commentCount, full_description, tags}."""
    out = {}
    for chunk_start in range(0, len(video_ids), 50):
        chunk = video_ids[chunk_start:chunk_start + 50]
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(chunk),
            "key": api_key,
        }
        url = f"https://www.googleapis.com/youtube/v3/videos?{urllib.parse.urlencode(params)}"
        status, data = http_json(url)
        if status != 200:
            print(f"  [video_details] FAILED ({status}): {data}")
            continue
        for it in data.get("items", []):
            sn = it.get("snippet", {})
            st = it.get("statistics", {})
            cd = it.get("contentDetails", {})
            out[it["id"]] = {
                "description": sn.get("description", ""),
                "tags": sn.get("tags", []),
                "duration_iso": cd.get("duration", ""),
                "viewCount": int(st.get("viewCount", 0)),
                "likeCount": int(st.get("likeCount", 0)),
                "commentCount": int(st.get("commentCount", 0)),
            }
    return out


def yt_channel_details(api_key, channel_ids):
    """Returns dict channelId -> {title, description, country, customUrl, subs, views, videoCount}."""
    out = {}
    uniq = list(set(channel_ids))
    for chunk_start in range(0, len(uniq), 50):
        chunk = uniq[chunk_start:chunk_start + 50]
        params = {
            "part": "snippet,statistics,brandingSettings",
            "id": ",".join(chunk),
            "key": api_key,
        }
        url = f"https://www.googleapis.com/youtube/v3/channels?{urllib.parse.urlencode(params)}"
        status, data = http_json(url)
        if status != 200:
            print(f"  [channel_details] FAILED ({status}): {data}")
            continue
        for it in data.get("items", []):
            sn = it.get("snippet", {})
            st = it.get("statistics", {})
            br = it.get("brandingSettings", {}).get("channel", {})
            out[it["id"]] = {
                "title": sn.get("title", ""),
                "description": sn.get("description", ""),
                "country": sn.get("country", ""),
                "customUrl": sn.get("customUrl", ""),
                "publishedAt": sn.get("publishedAt", ""),
                "subscriberCount": int(st.get("subscriberCount", 0)),
                "viewCount": int(st.get("viewCount", 0)),
                "videoCount": int(st.get("videoCount", 0)),
                "branding_keywords": br.get("keywords", ""),
            }
    return out


def yt_comments(api_key, video_id, max_results=30):
    """Top-level comments sorted by relevance."""
    params = {
        "part": "snippet", "videoId": video_id,
        "maxResults": str(min(max_results, 100)),
        "order": "relevance", "key": api_key,
        "textFormat": "plainText",
    }
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?{urllib.parse.urlencode(params)}"
    status, data = http_json(url)
    if status != 200:
        return []
    out = []
    for it in data.get("items", []):
        c = it.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
        out.append({
            "author": c.get("authorDisplayName", ""),
            "text": c.get("textDisplay", ""),
            "likes": c.get("likeCount", 0),
        })
    return out


# ── Contact extraction ─────────────────────────────────────────────────────

# Indian mobile: starts 6/7/8/9, exactly 10 digits. Allow +91 / 91 prefix with separators.
PHONE_RE = re.compile(
    r"(?:(?:\+?91[\s\-]?)|(?:0)?)?([6-9]\d{2}[\s\-]?\d{3}[\s\-]?\d{4})\b"
)
WHATSAPP_RE = re.compile(
    r"(?:wa\.me/|api\.whatsapp\.com/send\?phone=|whatsapp\.com/[^\s]*phone=)(\+?91?\d{10})",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
INSTAGRAM_RE = re.compile(
    r"(?:instagram\.com/|@)([A-Za-z0-9._]{3,30})", re.IGNORECASE
)
WEBSITE_RE = re.compile(
    r"https?://(?!(?:www\.)?(?:youtube|youtu\.be|instagram|facebook|twitter|x\.com|whatsapp|wa\.me)\.[a-z]+)([A-Za-z0-9.\-]+\.[a-z]{2,})(?:/\S*)?",
    re.IGNORECASE,
)


def normalize_phone(raw):
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return "+91-" + digits[:5] + "-" + digits[5:]
    return None


def extract_contacts(text):
    if not text:
        return {"phones": [], "whatsapp": [], "emails": [], "instagram": [], "websites": []}
    phones, wa, emails, ig, sites = set(), set(), set(), set(), set()
    for m in PHONE_RE.findall(text):
        p = normalize_phone(m)
        if p:
            phones.add(p)
    for m in WHATSAPP_RE.findall(text):
        p = normalize_phone(m)
        if p:
            wa.add(p)
    for m in EMAIL_RE.findall(text):
        emails.add(m.lower())
    for m in INSTAGRAM_RE.findall(text):
        if m.lower() not in {"instagram", "reel", "reels"}:
            ig.add(m.lower())
    for m in WEBSITE_RE.findall(text):
        sites.add(m.lower())
    return {
        "phones": sorted(phones),
        "whatsapp": sorted(wa),
        "emails": sorted(emails),
        "instagram": sorted(ig),
        "websites": sorted(sites),
    }


# ── Relevance scoring ──────────────────────────────────────────────────────

HOBBY_GRADE_KW = [
    "brushless", "1:10", "1/10", "1:8", "1/8", "1:12", "1/12",
    "lipo", "li-po", "esc", "servo", "drift", "rally", "buggy",
    "crawler", "monster truck", "scale model", "hobby grade", "hobby-grade",
    "rc drift", "drift car", "rtr", "kit version", "tamiya", "kyosho",
    "traxxas", "axial", "wltoys", "mjx", "hbx", "zd racing",
]
TOY_GRADE_KW = [
    "kids toy", "kids gift", "children", "remote control toy",
    "rs 200", "rs 300", "rs 500", "rs 999", "₹200", "₹300", "₹500", "₹999",
    "below 1000", "cheap rc",
]
MANUFACTURER_KW = [
    "manufacturer", "manufacturing", "factory", "production", "oem",
    "private label", "white label", "moq", "minimum order",
    "bulk order", "container load", "custom mould",
]
WHOLESALER_KW = [
    "wholesale", "wholesaler", "distributor", "distribution",
    "dealer", "b2b", "trader", "trading", "import", "importer",
    "sadar bazaar", "khari baoli", "chandni chowk", "lajpat rai market",
]
RETAILER_KW = [
    "retail", "shop", "showroom", "store address", "visit our store",
    "open at", "timings", "available at",
]
PARTS_KW = [
    "spare parts", "spares", "rc parts", "motor", "esc only", "tyre",
    "wheel", "battery", "lipo battery", "charger", "gear", "differential",
    "shock absorber", "suspension",
]


def score_vendor(blob_lower):
    """Returns (primary_type, signals_dict, score)."""
    signals = {}
    for label, kws in [
        ("hobby_grade", HOBBY_GRADE_KW),
        ("toy_grade", TOY_GRADE_KW),
        ("manufacturer", MANUFACTURER_KW),
        ("wholesaler", WHOLESALER_KW),
        ("retailer", RETAILER_KW),
        ("parts", PARTS_KW),
    ]:
        hits = [k for k in kws if k in blob_lower]
        signals[label] = hits

    # primary type priority: manufacturer > wholesaler > parts > hobby-retail > toy-retail > retail > unknown
    if signals["manufacturer"]:
        primary = "MANUFACTURER"
    elif signals["wholesaler"]:
        primary = "WHOLESALER"
    elif signals["parts"]:
        primary = "PARTS_SUPPLIER"
    elif signals["hobby_grade"] and signals["retailer"]:
        primary = "HOBBY_RETAILER"
    elif signals["toy_grade"] or (signals["retailer"] and not signals["hobby_grade"]):
        primary = "TOY_RETAILER"
    elif signals["hobby_grade"]:
        primary = "HOBBY_HOBBYIST_OR_REVIEWER"
    else:
        primary = "UNKNOWN"

    # numeric relevance score for BCH RC Mini Drift play (hobby+manuf/whole/parts weighted)
    score = (
        len(signals["manufacturer"]) * 5 +
        len(signals["wholesaler"]) * 4 +
        len(signals["parts"]) * 3 +
        len(signals["hobby_grade"]) * 3 -
        len(signals["toy_grade"]) * 2
    )
    return primary, signals, score


def is_relevant_for_bch(primary, signals, score):
    """Per user filter: hobby-grade RC, parts/spares, manufacturers/importers only."""
    if primary in {"MANUFACTURER", "WHOLESALER", "PARTS_SUPPLIER"}:
        return True
    if primary == "HOBBY_RETAILER":
        return True
    if signals.get("hobby_grade") and score >= 3:
        return True
    return False


# ── Stage 5: frame extraction ──────────────────────────────────────────────

def download_video(video_id, out_dir):
    """yt-dlp -> mp4. Returns path or None."""
    os.makedirs(out_dir, exist_ok=True)
    out_template = os.path.join(out_dir, f"{video_id}.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "best[height<=480][ext=mp4]/best[height<=480]/best",
        "--no-playlist", "--no-warnings", "--quiet",
        "-o", out_template,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except subprocess.CalledProcessError as e:
        print(f"  [yt-dlp] failed for {video_id}: {e.stderr.decode()[:200]}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  [yt-dlp] timeout for {video_id}")
        return None
    # find what was written
    for ext in ("mp4", "mkv", "webm"):
        p = os.path.join(out_dir, f"{video_id}.{ext}")
        if os.path.exists(p):
            return p
    return None


def get_video_duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", path]
    try:
        r = subprocess.run(cmd, capture_output=True, check=True, timeout=20)
        return float(r.stdout.decode().strip())
    except Exception:
        return 0.0


def extract_frames(video_path, frames_dir, video_id, num_frames=5):
    """Extract frames spaced across the video duration."""
    os.makedirs(frames_dir, exist_ok=True)
    dur = get_video_duration(video_path)
    if dur < 2:
        return []
    # Evenly spaced, but skip first 1.5s (intro logo) and last 1s (outro)
    margin = min(1.5, dur * 0.1)
    span = max(dur - 2 * margin, 1)
    timestamps = [margin + (span * i / max(num_frames - 1, 1)) for i in range(num_frames)]
    saved = []
    for i, ts in enumerate(timestamps):
        out = os.path.join(frames_dir, f"{video_id}_f{i + 1}.jpg")
        cmd = ["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", video_path,
               "-frames:v", "1", "-q:v", "3", "-loglevel", "error", out]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            if os.path.exists(out):
                saved.append({"path": out, "timestamp_sec": round(ts, 2)})
        except Exception as e:
            print(f"  [ffmpeg] frame {i} failed for {video_id}: {e}")
    return saved


def download_thumbnail(url, dest):
    if not url:
        return None
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            with open(dest, "wb") as f:
                f.write(r.read())
        return dest
    except Exception:
        return None


# ── Orchestration ───────────────────────────────────────────────────────────

def load_keys():
    if not os.path.exists(KEYS_FILE):
        sys.exit(f"ERROR: {KEYS_FILE} not found")
    return json.load(open(KEYS_FILE))


def discover(api_key, queries, per_query):
    """Stages 1-4. Returns list of vendor records (one per unique channel)."""
    all_videos = {}  # videoId -> {query_found, search_meta}
    for q in queries:
        print(f"[search] '{q}' (top {per_query})")
        for v in yt_search(api_key, q, per_query):
            vid = v["videoId"]
            if vid in all_videos:
                all_videos[vid]["queries_matched"].append(q)
            else:
                v["queries_matched"] = [q]
                all_videos[vid] = v
        time.sleep(0.3)
    print(f"\n[discovery] {len(all_videos)} unique videos\n")

    # full video details
    print("[enrich] fetching video details + statistics")
    details = yt_video_details(api_key, list(all_videos.keys()))
    for vid, d in details.items():
        all_videos[vid].update(d)

    # channel details
    channel_ids = list({v["channelId"] for v in all_videos.values() if v.get("channelId")})
    print(f"[enrich] fetching {len(channel_ids)} channel profiles")
    channels = yt_channel_details(api_key, channel_ids)

    # comments per video (cap to videos that look promising — saves quota)
    print(f"[enrich] fetching top comments for {len(all_videos)} videos")
    for vid in list(all_videos.keys()):
        all_videos[vid]["top_comments"] = yt_comments(api_key, vid, MAX_COMMENTS_PER_VIDEO)
        time.sleep(0.1)

    # group by channel, build vendor record
    by_channel = defaultdict(list)
    for vid, v in all_videos.items():
        by_channel[v["channelId"]].append(v)

    vendors = []
    for chan_id, vids in by_channel.items():
        chan = channels.get(chan_id, {})
        # blob = all searchable text for this vendor
        text_parts = [
            chan.get("title", ""),
            chan.get("description", ""),
            chan.get("branding_keywords", ""),
        ]
        for v in vids:
            text_parts.append(v.get("title", ""))
            text_parts.append(v.get("description", ""))
            text_parts.append(v.get("description_snippet", ""))
            text_parts.extend(v.get("tags", []) or [])
            for c in v.get("top_comments", []):
                text_parts.append(c.get("text", ""))
        blob = "\n".join(text_parts)
        blob_lower = blob.lower()
        contacts = extract_contacts(blob)
        primary, signals, score = score_vendor(blob_lower)

        total_views = sum(v.get("viewCount", 0) for v in vids)
        vendors.append({
            "channelId": chan_id,
            "channelTitle": chan.get("title", "") or vids[0].get("channelTitle", ""),
            "channel_url": f"https://www.youtube.com/channel/{chan_id}",
            "custom_url": chan.get("customUrl", ""),
            "country": chan.get("country", ""),
            "subscribers": chan.get("subscriberCount", 0),
            "channel_total_views": chan.get("viewCount", 0),
            "channel_video_count": chan.get("videoCount", 0),
            "channel_about": chan.get("description", ""),
            "branding_keywords": chan.get("branding_keywords", ""),
            "primary_type": primary,
            "signals": signals,
            "relevance_score": score,
            "is_relevant": is_relevant_for_bch(primary, signals, score),
            "contacts": contacts,
            "videos": [
                {
                    "videoId": v["videoId"],
                    "url": f"https://www.youtube.com/watch?v={v['videoId']}",
                    "title": v.get("title", ""),
                    "viewCount": v.get("viewCount", 0),
                    "publishedAt": v.get("publishedAt", ""),
                    "duration_iso": v.get("duration_iso", ""),
                    "queries_matched": v.get("queries_matched", []),
                    "thumbnail": v.get("thumbnail", ""),
                    "description": v.get("description", ""),
                    "top_comments": v.get("top_comments", []),
                }
                for v in sorted(vids, key=lambda x: x.get("viewCount", 0), reverse=True)
            ],
            "top_video_views": vids[0].get("viewCount", 0) if vids else 0,
            "vendor_total_views_in_set": total_views,
        })

    vendors.sort(key=lambda v: (v["is_relevant"], v["relevance_score"], v["vendor_total_views_in_set"]), reverse=True)
    return vendors


def extract_frames_for_top(vendors, top_n):
    """For top N relevant vendors, download their top video + extract product frames."""
    os.makedirs(FRAMES_DIR, exist_ok=True)
    relevant = [v for v in vendors if v["is_relevant"]][:top_n]
    print(f"\n[frames] extracting for top {len(relevant)} relevant vendors\n")
    for i, v in enumerate(relevant, 1):
        if not v["videos"]:
            continue
        top_vid = v["videos"][0]
        video_id = top_vid["videoId"]
        print(f"[{i}/{len(relevant)}] {v['channelTitle']} -> {video_id}")
        chan_dir = os.path.join(FRAMES_DIR, re.sub(r"[^a-z0-9]+", "_", v["channelTitle"].lower()).strip("_") or v["channelId"])
        os.makedirs(chan_dir, exist_ok=True)
        # thumbnail
        thumb_path = os.path.join(chan_dir, f"{video_id}_thumb.jpg")
        download_thumbnail(top_vid.get("thumbnail", ""), thumb_path)
        # download + frames
        vid_path = download_video(video_id, chan_dir)
        if vid_path:
            frames = extract_frames(vid_path, chan_dir, video_id, num_frames=5)
            top_vid["frames"] = [{"path": os.path.relpath(f["path"], OUT_DIR), "ts": f["timestamp_sec"]} for f in frames]
            top_vid["thumbnail_local"] = os.path.relpath(thumb_path, OUT_DIR) if os.path.exists(thumb_path) else ""
            print(f"           {len(frames)} frames extracted")
            # clean up the video file (frames are what we need)
            try:
                os.remove(vid_path)
            except Exception:
                pass
        time.sleep(1)
    return vendors


def write_report(vendors):
    """Markdown report + JSON dump."""
    json_path = os.path.join(OUT_DIR, "vendors.json")
    with open(json_path, "w") as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {json_path}")

    md = ["# YouTube RC-Car Vendor Discovery — Delhi", ""]
    md.append(f"_Auto-generated by yt_rc_pipeline.py. {time.strftime('%Y-%m-%d %H:%M IST')}_")
    md.append("")
    md.append("**Search queries:** " + ", ".join(f"`{q}`" for q in QUERIES))
    md.append("")
    md.append(f"**Total unique YouTube channels found:** {len(vendors)}")
    relevant = [v for v in vendors if v["is_relevant"]]
    md.append(f"**Relevant to BCH (hobby-grade / parts / mfg / wholesale):** {len(relevant)}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Tier 1 — Relevant vendors (sorted by relevance score)")
    md.append("")

    for i, v in enumerate(relevant, 1):
        md.append(f"### {i}. {v['channelTitle']} — `{v['primary_type']}` (score {v['relevance_score']})")
        md.append("")
        md.append(f"- **Channel:** {v['channel_url']}")
        if v["custom_url"]:
            md.append(f"- **Custom URL:** https://www.youtube.com/{v['custom_url']}")
        md.append(f"- **Subscribers:** {v['subscribers']:,} · **Total channel views:** {v['channel_total_views']:,} · **Videos:** {v['channel_video_count']:,}")
        if v["country"]:
            md.append(f"- **Country:** {v['country']}")
        # contacts
        c = v["contacts"]
        if c["phones"]:
            md.append(f"- **📞 Phones:** {' / '.join(c['phones'])}")
        if c["whatsapp"]:
            md.append(f"- **🟢 WhatsApp:** {' / '.join(c['whatsapp'])}")
        if c["emails"]:
            md.append(f"- **✉️  Emails:** {' / '.join(c['emails'])}")
        if c["instagram"]:
            md.append(f"- **📷 Instagram:** {' / '.join('@' + h for h in c['instagram'][:5])}")
        if c["websites"]:
            md.append(f"- **🌐 Websites:** {' / '.join(c['websites'][:5])}")
        if not any(c.values()):
            md.append(f"- **Contacts:** none extracted from descriptions/comments (check channel About manually)")
        md.append("")
        # signals
        sig_strs = []
        for label, kws in v["signals"].items():
            if kws:
                sig_strs.append(f"`{label}`: {', '.join(kws[:5])}")
        if sig_strs:
            md.append("**Signals detected:** " + " · ".join(sig_strs))
            md.append("")
        # channel about
        if v["channel_about"]:
            md.append("**Channel About:**")
            md.append("> " + v["channel_about"].replace("\n", "\n> ")[:600] + ("…" if len(v["channel_about"]) > 600 else ""))
            md.append("")
        # top videos
        md.append(f"**Top video(s) matching queries:**")
        md.append("")
        for vd in v["videos"][:3]:
            md.append(f"- [{vd['title']}]({vd['url']}) — {vd['viewCount']:,} views · published {vd['publishedAt'][:10]}")
            md.append(f"  - Matched queries: {', '.join(vd['queries_matched'])}")
            # screenshots
            if vd.get("thumbnail_local"):
                md.append(f"  - **Thumbnail:** ![]({vd['thumbnail_local']})")
            elif vd.get("thumbnail"):
                md.append(f"  - **Thumbnail:** ![]({vd['thumbnail']})")
            if vd.get("frames"):
                md.append("  - **Extracted product frames (yt-dlp + ffmpeg):**")
                for fr in vd["frames"]:
                    md.append(f"    - @{fr['ts']}s — ![]({fr['path']})")
        md.append("")
        md.append("---")
        md.append("")

    md.append("## Tier 2 — Other channels found (low relevance / no signals)")
    md.append("")
    others = [v for v in vendors if not v["is_relevant"]]
    for v in others:
        c = v["contacts"]
        contact_parts = []
        if c["phones"]: contact_parts.append(f"📞 {c['phones'][0]}")
        if c["whatsapp"]: contact_parts.append(f"🟢 {c['whatsapp'][0]}")
        if c["instagram"]: contact_parts.append(f"📷 @{c['instagram'][0]}")
        contact_str = " · ".join(contact_parts) or "—"
        top_vid = v["videos"][0] if v["videos"] else None
        if top_vid:
            md.append(f"- **{v['channelTitle']}** (`{v['primary_type']}`, {v['subscribers']:,} subs) · {contact_str} · top: [{top_vid['title'][:60]}]({top_vid['url']}) ({top_vid['viewCount']:,} views)")
        else:
            md.append(f"- **{v['channelTitle']}** (`{v['primary_type']}`) · {contact_str}")
    md.append("")

    md_path = os.path.join(OUT_DIR, "YT_RC_DELHI_VENDORS.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md))
    print(f"[output] {md_path}")
    return md_path, json_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true", help="run discovery stages 1-4, no downloads")
    ap.add_argument("--frames", type=int, default=0, help="extract frames for top N relevant vendors")
    ap.add_argument("--all", action="store_true", help="discover + extract frames for top 15")
    ap.add_argument("--per-query", type=int, default=RESULTS_PER_QUERY)
    ap.add_argument("--queries", default="", help="override default queries (comma-sep)")
    ap.add_argument("--out", default=DEFAULT_OUT_DIR, help="output directory (override default)")
    ap.add_argument("--resume-from-json", action="store_true", help="skip discovery, load existing vendors.json")
    args = ap.parse_args()

    global OUT_DIR, FRAMES_DIR
    OUT_DIR = args.out
    FRAMES_DIR = os.path.join(OUT_DIR, "frames")

    if not (args.discover or args.frames or args.all):
        args.all = True

    keys = load_keys()
    yt_keys = keys.get("youtube", [])
    api_key = next((k for k in yt_keys if k and not k.startswith("PASTE_")), None)
    if not api_key:
        sys.exit("ERROR: no YouTube API key in keys.json")

    os.makedirs(OUT_DIR, exist_ok=True)

    queries = [q.strip() for q in args.queries.split(",") if q.strip()] or QUERIES

    if args.resume_from_json:
        vendors = json.load(open(os.path.join(OUT_DIR, "vendors.json")))
    else:
        vendors = discover(api_key, queries, args.per_query)
        # snapshot pre-frame discovery
        with open(os.path.join(OUT_DIR, "vendors.json"), "w") as f:
            json.dump(vendors, f, indent=2, ensure_ascii=False)

    print(f"\n[summary] {len(vendors)} unique channels found")
    relevant = [v for v in vendors if v["is_relevant"]]
    print(f"[summary] {len(relevant)} relevant for BCH")
    for v in relevant[:20]:
        print(f"  - {v['channelTitle']:40s} {v['primary_type']:25s} score={v['relevance_score']:3d}  subs={v['subscribers']:>8,}")

    frames_n = 15 if args.all else args.frames
    if frames_n > 0:
        vendors = extract_frames_for_top(vendors, frames_n)

    write_report(vendors)


if __name__ == "__main__":
    main()
