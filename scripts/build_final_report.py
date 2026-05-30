#!/usr/bin/env python3
"""
build_final_report.py — Compile the final BCH vendor report from:
  - vendors.json   (YouTube discovery + contacts + frames)
  - gemini_verdicts.json (visual classification of frames)

Output: SOURCING_HQ/RC_RESEARCH/YT_DELHI_VENDORS_REPORT.md
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "yt_rc_output")
VENDORS = json.load(open(os.path.join(OUT_DIR, "vendors.json")))
VERDICTS = json.load(open(os.path.join(OUT_DIR, "gemini_verdicts.json")))

REPORT_PATH = "/Users/syedibrahim/Desktop/SOURCING_HQ/RC_RESEARCH/YT_DELHI_VENDORS_REPORT.md"

QUERIES = [
    "rc cars market in Delhi", "rc cars in Delhi",
    "rc car manufacturer in Delhi", "rc car wholesale in Delhi",
]

# absolute path -> relative-to-report path for image embedding
# Report lives at SOURCING_HQ/RC_RESEARCH/YT_DELHI_VENDORS_REPORT.md
# Frames live at SOURCING_HQ/scripts/yt_rc_output/frames/...
# So from RC_RESEARCH, frames are at ../scripts/yt_rc_output/frames/...
def img_rel(frame_path_or_relpath):
    """Turn 'frames/foo.jpg' or absolute -> path relative to RC_RESEARCH/."""
    if not frame_path_or_relpath:
        return ""
    if os.path.isabs(frame_path_or_relpath):
        # relative to OUT_DIR
        if frame_path_or_relpath.startswith(OUT_DIR):
            rel = os.path.relpath(frame_path_or_relpath, OUT_DIR)
        else:
            rel = frame_path_or_relpath
    else:
        rel = frame_path_or_relpath  # already relative to OUT_DIR
    return f"../scripts/yt_rc_output/{rel}"


def fmt_contacts(contacts):
    lines = []
    if contacts["phones"]:
        lines.append(f"- **📞 Phones:** {' · '.join(contacts['phones'])}")
    if contacts["whatsapp"]:
        lines.append(f"- **🟢 WhatsApp:** {' · '.join(contacts['whatsapp'])}")
    if contacts["emails"]:
        lines.append(f"- **✉️  Emails:** {' · '.join(contacts['emails'])}")
    if contacts["instagram"]:
        lines.append(f"- **📷 Instagram:** {' · '.join('@' + h for h in contacts['instagram'][:8])}")
    if contacts["websites"]:
        lines.append(f"- **🌐 Websites:** {' · '.join(contacts['websites'][:5])}")
    return lines


def channel_block(c, verdict_lookup, tier_label):
    """Render one channel block — top video frames + contacts + Gemini verdict."""
    out = []
    top_vid = c["videos"][0] if c["videos"] else None
    v_id = top_vid["videoId"] if top_vid else None
    verdict = verdict_lookup.get(v_id, {}).get("verdict", {}) if v_id else {}
    grade = verdict.get("grade", "not-classified")
    rel = verdict.get("bch_relevance_1_10", "?")
    one_liner = verdict.get("verdict_one_line", "")

    out.append(f"### {c['channelTitle']} — `{grade}` (BCH relevance {rel}/10)")
    out.append("")
    if one_liner:
        out.append(f"> **Gemini verdict:** {one_liner}")
        out.append("")
    out.append(f"- **Channel:** {c['channel_url']}  · **Subscribers:** {c['subscribers']:,}  · **Total channel views:** {c['channel_total_views']:,}")
    if c.get("custom_url"):
        out.append(f"- **Custom URL:** https://www.youtube.com/{c['custom_url']}")
    if c.get("country"):
        out.append(f"- **Country:** {c['country']}")
    out.append(f"- **Score signals:** primary `{c['primary_type']}` · keyword score {c['relevance_score']}")
    out.extend(fmt_contacts(c["contacts"]))

    if verdict.get("products_seen"):
        out.append(f"- **Products visible (Gemini):** {', '.join(verdict['products_seen'][:10])}")
    if verdict.get("scale_visible") and verdict["scale_visible"] not in ("unknown", "n/a", ""):
        out.append(f"- **Scale visible:** {verdict['scale_visible']}")
    if verdict.get("non_rc_present"):
        out.append(f"- **Non-RC items also present:** {', '.join(verdict['non_rc_present'][:8])}")
    if verdict.get("shop_signage_visible") and verdict.get("shop_name_on_signage"):
        out.append(f"- **Shop signage seen:** _{verdict['shop_name_on_signage']}_")

    out.append("")

    if c.get("channel_about"):
        about = c["channel_about"].strip()
        if about:
            out.append("<details><summary>Channel About</summary>")
            out.append("")
            out.append("> " + about.replace("\n", "\n> ")[:1000] + ("…" if len(about) > 1000 else ""))
            out.append("")
            out.append("</details>")
            out.append("")

    # Show top 1-2 videos with frames
    for vd in c["videos"][:2]:
        out.append(f"#### Video: [{vd['title']}]({vd['url']})")
        out.append(f"_{vd['viewCount']:,} views · published {vd['publishedAt'][:10]} · matched queries: {', '.join(vd['queries_matched'])}_")
        out.append("")
        # description snippet
        desc = vd.get("description", "").strip()
        if desc:
            out.append("<details><summary>Description (shop contacts often live here)</summary>")
            out.append("")
            out.append("```")
            out.append(desc[:2500] + ("…" if len(desc) > 2500 else ""))
            out.append("```")
            out.append("")
            out.append("</details>")
            out.append("")

        # thumbnail
        if vd.get("thumbnail_local"):
            out.append(f"**Thumbnail:** ![]({img_rel(vd['thumbnail_local'])})")
        elif vd.get("thumbnail"):
            out.append(f"**Thumbnail:** ![]({vd['thumbnail']})")
        out.append("")

        # frames
        if vd.get("frames"):
            out.append(f"**Extracted product frames** (yt-dlp + ffmpeg, evenly spaced across video):")
            out.append("")
            for fr in vd["frames"]:
                out.append(f"- @{fr['ts']}s — ![]({img_rel(fr['path'])})")
            out.append("")
    return out


def main():
    # join Gemini verdicts onto channels (by video_id of TOP video)
    md = []
    md.append("# YouTube RC-Car Vendor Report — Delhi (Hobby + Parts focus)")
    md.append("")
    md.append(f"_Generated by the BCH YouTube vendor pipeline. Source: 4 YouTube searches; visual classification by Gemini 2.5 Flash on extracted video frames._")
    md.append("")
    md.append(f"**Search queries used:**")
    for q in QUERIES:
        md.append(f"- `{q}` (regionCode IN, top 25 per query)")
    md.append("")
    md.append(f"**Pipeline stages:**")
    md.append(f"1. **Discovery** — YouTube Data API v3 → {len(VENDORS)} unique channels from 56 videos.")
    md.append(f"2. **Enrichment** — full video descriptions, channel-About text, top 30 comments per video.")
    md.append(f"3. **Contact extraction** — regex for Indian phone, WhatsApp, IG, email, websites against all combined text.")
    md.append(f"4. **Frame extraction** — yt-dlp + ffmpeg, 5 evenly-spaced frames per top video, 19/20 videos completed.")
    md.append(f"5. **Visual classification** — Gemini 2.5 Flash (with 2.0 fallback) examined frames → hobby-grade / toy-grade / mixed / parts-only / not-a-product verdict + BCH relevance 1-10.")
    md.append("")

    # Group channels by Gemini grade
    by_grade = defaultdict(list)
    for c in VENDORS:
        if not c["videos"]:
            continue
        vid = c["videos"][0]["videoId"]
        verdict = VERDICTS.get(vid, {}).get("verdict", {})
        if verdict.get("_error"):
            by_grade["not-classified"].append(c)
        else:
            grade = verdict.get("grade", "not-classified")
            by_grade[grade].append((c, verdict.get("bch_relevance_1_10", 0)))

    # sort each by relevance desc
    def sort_key(item):
        if isinstance(item, tuple):
            return -item[1]
        return 0

    for g in ["hobby-grade", "mixed", "parts-only", "toy-grade", "not-a-product", "not-classified"]:
        items = by_grade.get(g, [])
        if not items:
            continue
        items.sort(key=lambda x: -(x[1] if isinstance(x, tuple) else 0))

    md.append("---")
    md.append("")
    md.append("## Executive Summary")
    md.append("")
    md.append(f"| Grade (Gemini visual) | Channels | Notes |")
    md.append(f"|---|---|---|")
    for g in ["hobby-grade", "mixed", "parts-only", "toy-grade", "not-a-product"]:
        items = by_grade.get(g, [])
        notes = {
            "hobby-grade": "**TIER 1** — Genuine Tygatec-tier RC product visible. Strongest leads.",
            "mixed": "**TIER 2** — Both hobby + toy product visible. Worth investigating; some hobby SKUs likely stocked.",
            "parts-only": "**TIER 3** — Spare-parts supplier (motors/ESC/lipo/tires). Useful post-sale.",
            "toy-grade": "**TIER 4** — Toy-grade kid RC + battery jeeps. Low fit for hobby Mini Drift SKU but contacts logged for fallback / wholesale price discovery.",
            "not-a-product": "Video doesn't show RC product — skip.",
        }[g]
        md.append(f"| `{g}` | {len(items)} | {notes} |")
    md.append(f"| `not-classified` | {len(by_grade.get('not-classified', []))} | Gemini classification error after retries — review manually. |")
    md.append("")

    # All extracted phone numbers across all videos, with grade
    md.append("### Master contact list (all phone numbers, grouped by Gemini grade of source video)")
    md.append("")
    md.append("| Phone | Source channel | Source video | Grade |")
    md.append("|---|---|---|---|")
    seen_rows = set()
    grade_priority = {"hobby-grade": 0, "mixed": 1, "parts-only": 2, "toy-grade": 3, "not-a-product": 4, "not-classified": 5}
    # channel-level grade = grade of the channel's TOP video (the one we sent to Gemini)
    channel_grade = {}
    for c in VENDORS:
        if not c["videos"]:
            continue
        top_vid = c["videos"][0]["videoId"]
        v = VERDICTS.get(top_vid, {}).get("verdict", {})
        if v.get("_error") or not v:
            channel_grade[c["channelTitle"]] = "not-classified"
        else:
            channel_grade[c["channelTitle"]] = v.get("grade", "not-classified")
    rows = []
    for c in VENDORS:
        cg = channel_grade.get(c["channelTitle"], "not-classified")
        for vd in c["videos"]:
            from yt_rc_pipeline import extract_contacts
            v_contacts = extract_contacts(vd.get("description", ""))
            for ph in v_contacts["phones"]:
                row = (ph, c["channelTitle"], vd["title"][:60], cg)
                if row in seen_rows:
                    continue
                seen_rows.add(row)
                rows.append(row)
    # dedup again on (phone, channel) — keep first
    phone_chan_seen = set()
    deduped = []
    for r in rows:
        key = (r[0], r[1])
        if key in phone_chan_seen:
            continue
        phone_chan_seen.add(key)
        deduped.append(r)
    rows = deduped
    rows.sort(key=lambda r: (grade_priority.get(r[3], 99), r[0]))
    for ph, ch, vt, g in rows:
        md.append(f"| `{ph}` | {ch} | {vt} | `{g}` |")
    md.append("")
    md.append("---")
    md.append("")

    # tier sections
    for g, label in [
        ("hobby-grade", "TIER 1 — Hobby-grade (Tygatec-tier) verified by Gemini"),
        ("mixed", "TIER 2 — Mixed inventory (some hobby + some toy)"),
        ("parts-only", "TIER 3 — Parts / spares suppliers"),
        ("toy-grade", "TIER 4 — Toy-grade Delhi wholesale (low fit for Mini Drift, but logged for completeness)"),
        ("not-a-product", "Not a product (skip)"),
        ("not-classified", "Not classified (Gemini error — manual review needed)"),
    ]:
        items = by_grade.get(g, [])
        if not items:
            continue
        md.append(f"## {label}  ({len(items)})")
        md.append("")
        # sort by relevance
        items.sort(key=lambda x: -(x[1] if isinstance(x, tuple) else 0))
        for entry in items:
            c = entry[0] if isinstance(entry, tuple) else entry
            md.extend(channel_block(c, VERDICTS, g))
            md.append("---")
            md.append("")

    # Footer / methodology
    md.append("## Methodology notes")
    md.append("")
    md.append("- **Contact extraction confidence:** phone numbers came from YouTube video descriptions and channel About pages, which are owner-written. They are the same numbers a viewer of the video would call. WhatsApp links / shop-name context is preserved in each `<details>Description</details>` block above.")
    md.append("- **Frame extraction:** 5 frames per video, evenly spaced after a 10% margin from start/end to skip intros/outros. Files stored under `SOURCING_HQ/scripts/yt_rc_output/frames/<channel_slug>/`.")
    md.append("- **Gemini classifier:** prompted to identify product grade visible in the frames, scale (if shown), shop signage, and to score relevance to the BCH Mini RC Drift Car SKU. Verdicts are derived from images only — *we did not use them to inspect descriptions or audio*. Cross-reference the description block for shop-name / address ground truth.")
    md.append("- **Known false-positives in keyword scoring (pre-Gemini):** the keyword scorer over-rated Delhi market vlogs because they mention 'wholesale' / 'manufacturer' in descriptions while showing toy-grade product. Gemini visual classification corrected this — that's why the toy-grade tier has the most entries.")
    md.append("- **Shops mentioned by multiple creators** (signal of a real operating vendor):")
    md.append("  - **Milestone Impex** (Jhandewalan Cycle Market) — phones `+91-83830-83760` retail, `+91-98996-18848` wholesale — mentioned by Crazy Viner, Manish Dilliwala, Srv Vlogs, Explore Vlogs AR. Gemini graded **toy-grade**, so this shop is a toy importer, NOT a hobby-grade source.")
    md.append("  - **Sai Trading Toy** (Sadar Bazar) — `9540830834`, `7042897060`, `8130962388` — mentioned by INFINITY VLOGS + VLOGSTAN. Also toy-grade per Gemini.")
    md.append("")
    md.append("## What to do next")
    md.append("")
    md.append("1. **Call the 4 hobby-grade leads first** — Happy Here Films / WLtoys Official / Kevin Talbot / Freddy Collector and check which are *suppliers* vs *reviewers*. (Most reviewer channels won't sell — but Happy Here Films and the WLtoys factory both look like dealer/manufacturer leads.)")
    md.append("2. **Investigate the 3 mixed-inventory shops** — Vishal Creator (rel 8) is the highest-value mixed: he appears to film a shop that stocks both hobby and toy product. Manish Dilliwala / Explore Vlogs AR are the other two — confirm if Milestone Impex actually stocks hobby SKUs not visible in the filmed inventory.")
    md.append("3. **Nairatoystv (parts-only)** — call for spares pricing (motors/lipo/wheels for the Drift SKU bundle).")
    md.append("4. **Toy-grade contacts** — these are NOT hobby-grade sources but ARE Delhi wholesale toy importers. Possible use: 1) backup if Surat/Yiwu cycle vendors can't get RC, 2) market intelligence on toy-grade price floors so we can position the hobby SKU above them.")
    md.append("")

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(md))
    print(f"[output] {REPORT_PATH}")
    print(f"[output] {len(md)} lines written")

    print("\n=== Final tier counts ===")
    for g in ["hobby-grade", "mixed", "parts-only", "toy-grade", "not-a-product", "not-classified"]:
        print(f"  {g}: {len(by_grade.get(g, []))}")


if __name__ == "__main__":
    main()
