#!/usr/bin/env python3
"""
vendor_dedup.py — Re-cluster YouTube discovery output BY UNIQUE SHOP, not by creator channel.

Reads yt_rc_output/vendors.json (channel-centric) and produces shops.json (vendor-centric):
- one record per unique phone-cluster
- shop name + address extracted from description context
- list of creators who filmed the shop (with video URLs)
- frame paths from those videos (for visual classification)
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "yt_rc_output", "vendors.json")
OUT = os.path.join(HERE, "yt_rc_output", "shops.json")
FRAMES_ROOT = os.path.join(HERE, "yt_rc_output")  # frames are relative to this


def extract_shop_context(description, phone):
    """Return up to 6 lines around the phone number — shop name, address etc."""
    if not description:
        return ""
    phone_digits = re.sub(r"\D", "", phone)[-10:]  # last 10 digits
    lines = description.split("\n")
    for i, line in enumerate(lines):
        ld = re.sub(r"\D", "", line)
        if phone_digits in ld:
            start = max(0, i - 5)
            end = min(len(lines), i + 3)
            return "\n".join(l for l in lines[start:end] if l.strip())
    return ""


def main():
    vendors = json.load(open(IN))

    # phone -> list of {creator_channel, creator_url, video_id, video_url, video_title,
    #                  video_views, video_thumb, frames[], context_snippet}
    shop_clusters = defaultdict(list)

    for c in vendors:
        for vd in c["videos"]:
            desc = vd.get("description", "")
            # collect all phones in this specific video's description
            from yt_rc_pipeline import extract_contacts
            v_contacts = extract_contacts(desc)
            for ph in v_contacts["phones"]:
                ctx = extract_shop_context(desc, ph)
                shop_clusters[ph].append({
                    "creator_channel": c["channelTitle"],
                    "creator_channel_url": c["channel_url"],
                    "creator_subs": c["subscribers"],
                    "video_id": vd["videoId"],
                    "video_url": vd["url"],
                    "video_title": vd["title"],
                    "video_views": vd["viewCount"],
                    "video_thumb_url": vd.get("thumbnail", ""),
                    "video_thumb_local": vd.get("thumbnail_local", ""),
                    "frames": vd.get("frames", []),
                    "context_snippet": ctx,
                    "queries_matched": vd["queries_matched"],
                })

    # Now also link "co-mentioned" phones — phones appearing in same description belong to same shop.
    # E.g. Milestone Impex has Retail 8383083760 + Wholesale 9899618848 in same description.
    # We merge phones whose context overlaps.

    # Build phone -> set of frozenset(coappearing phones)
    coappear = defaultdict(set)
    for c in vendors:
        for vd in c["videos"]:
            from yt_rc_pipeline import extract_contacts
            phones_in_video = extract_contacts(vd.get("description", ""))["phones"]
            for p in phones_in_video:
                for q in phones_in_video:
                    if p != q:
                        coappear[p].add(q)

    # Union-find merge
    parent = {p: p for p in shop_clusters}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for p, others in coappear.items():
        for q in others:
            if q in parent:
                union(p, q)
    groups = defaultdict(list)
    for p in shop_clusters:
        groups[find(p)].append(p)

    # Build final shop records
    shops = []
    for root, members in groups.items():
        all_mentions = []
        for p in members:
            for m in shop_clusters[p]:
                m["matched_phone"] = p
                all_mentions.append(m)
        # de-dup mentions by video_id
        seen = set()
        uniq_mentions = []
        for m in sorted(all_mentions, key=lambda x: x["video_views"], reverse=True):
            if m["video_id"] in seen:
                continue
            seen.add(m["video_id"])
            uniq_mentions.append(m)

        # Try to extract shop name from contexts: usually first non-phone line above phone
        shop_name_guess = ""
        address_guess = ""
        for m in uniq_mentions:
            ctx = m["context_snippet"]
            if not ctx:
                continue
            ctx_lines = [l.strip() for l in ctx.split("\n") if l.strip()]
            # shop name = first line that's not contact/address/url
            for line in ctx_lines:
                if any(skip in line.lower() for skip in [
                    "contact", "phone", "call", "whatsapp", "http", "email",
                    "address", "details", "watsapp", "shop details"
                ]):
                    continue
                if re.search(r"\d{10}", line.replace(" ","").replace("-","")):
                    continue
                if len(line) > 3 and len(line) < 80 and not line.startswith("#"):
                    shop_name_guess = line
                    break
            # address = a line mentioning sector/market/bazaar/road/delhi
            for line in ctx_lines:
                if any(k in line.lower() for k in [
                    "bazar", "bazaar", "market", "sector", "road", "delhi",
                    "nagar", "vihar", "rohini", "sadar", "chowk", "ghazipur",
                    "jhandewalan", "haridwar", "coimbatore", "ho ", "extn"
                ]):
                    address_guess = line
                    break
            if shop_name_guess:
                break

        creators = sorted({m["creator_channel"] for m in uniq_mentions})
        shops.append({
            "shop_id": f"shop_{len(shops)+1:02d}",
            "shop_name_guess": shop_name_guess,
            "address_guess": address_guess,
            "phones": sorted(members),
            "creator_count": len(creators),
            "creators": creators,
            "video_count": len(uniq_mentions),
            "total_views": sum(m["video_views"] for m in uniq_mentions),
            "mentions": uniq_mentions,
        })

    # rank: more creators mentioning = stronger signal
    shops.sort(key=lambda s: (s["creator_count"], s["total_views"]), reverse=True)

    with open(OUT, "w") as f:
        json.dump(shops, f, indent=2, ensure_ascii=False)
    print(f"[shops] {len(shops)} unique shops clustered")
    print(f"[output] {OUT}")
    print()
    for i, s in enumerate(shops[:20], 1):
        print(f"{i:2d}. {s['shop_name_guess'][:40]:40s} | {len(s['phones']):d} ph | {s['creator_count']:d} creator(s) | {s['total_views']:>12,} views")
        if s["address_guess"]:
            print(f"    📍 {s['address_guess'][:90]}")
        print(f"    📞 {', '.join(s['phones'])}")
    return shops


if __name__ == "__main__":
    main()
