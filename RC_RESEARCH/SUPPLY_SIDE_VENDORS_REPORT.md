# Supply-Side RC Vendor Report — Manufacturers / Distributors / Wholesalers / Traders

**Generated:** 2026-05-30 evening
**For:** Syed (BCH Bangalore) — sourcing for ₹800–₹2,500 grey-space drift RC SKU
**Method:** YouTube Data API (20 supply-side queries) → frame extraction (yt-dlp + ffmpeg, 5 frames per top video) → Gemini 2.5 Flash Vision with a re-tuned prompt focused on production / wholesale / B2B signals (not retail showroom signals)

**Companion files:**
- Raw JSON: [`scripts/yt_rc_output_supply/gemini_supply_verdicts.json`](../scripts/yt_rc_output_supply/gemini_supply_verdicts.json)
- All channels: [`scripts/yt_rc_output_supply/vendors.json`](../scripts/yt_rc_output_supply/vendors.json) (246 channels discovered)
- Frames: [`scripts/yt_rc_output_supply/frames/`](../scripts/yt_rc_output_supply/frames/) (145 JPGs from 24 channel folders)
- Supply-side classifier: [`scripts/gemini_classify_supply_side.py`](../scripts/gemini_classify_supply_side.py)

---

## TL;DR — what changed vs prior reports

**12 of 24 classified channels are genuinely supply-side. Gemini surfaced specific shop names from signage that we couldn't extract from text alone — plus matching phone numbers visible in the shop signs themselves.**

Biggest single find: **Sai Trading Company has a "LIX MODEL" drift RC SKU visible in frame** (Gemini confirmed `drift_rc_present: true`). Phone `+91-79829-28315` already in our Delhi data — but now we have visual proof of the drift SKU on their shelf.

Cross-confirmed: **WLtoys Official** (rel=10, manufacturer, factory floor visible) — was rel=9 in yesterday's classification, score went up. Consistent across runs.

Brand-new supply-side find: **Xhy Toy Factory** (rel=9) — 209 subscribers but the frames show a real production line with 1000+ RC cars in WIP, blue mecanum wheels, branded blue boxes. Tiny YouTube footprint, real factory.

---

## Tier 1 — Manufacturers (Gemini-verified factory floor)

### 1. WLtoys Official — Shantou, China  (BCH rel **10/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | MANUFACTURER · supply_side ✓ |
| **Scale visible** | Large · 100-1000 inventory pieces in frame |
| **Production signals** | Factory floor (concrete + fluorescent tubes), assembly line workers at benches, multiple identical units in production stages, raw materials (ESCs, wires, batteries), blue industrial crates |
| **Drift RC present** | ✅ YES |
| **Products visible** | RC car chassis, RC car bodies, RC car remotes, LiPo batteries, ESCs |
| **Best contact** | aliexpress.com/store/911418260 · @wltoysofficial · wl-xks.com |
| **Video** | https://www.youtube.com/watch?v=o39ph0w5V5k |
| **Verdict** | Confirmed manufacturer with drift-grade product in production. Their video footer explicitly says "looking for dealers globally." This is the direct-China lead. |

### 2. Xhy Toy Factory — China (BCH rel **9/10**)  ★ NEW
| Field | Value |
|---|---|
| **Gemini vendor type** | MANUFACTURER · supply_side ✓ |
| **Scale visible** | Large · **1000+ inventory pieces visible** |
| **Production signals** | Factory floor (concrete + industrial lighting), workers at benches assembling, production-line packaging with blue boxes, dozens of identical RC cars lined up |
| **Drift RC present** | ✅ YES |
| **Products visible** | Black RC cars with **blue mecanum wheels**, blue product boxes (their packaging) |
| **Signage text Gemini read** | _"Toy Factory Daily Life"_ |
| **Channel** | 209 subscribers (brand-new YT presence) · @outlook.com in description |
| **Video** | https://www.youtube.com/watch?v=DRXSzWyOWvU |
| **Verdict** | Real factory, brand-new YouTube. **DM via @outlook.com address in their video description** — likely solo founder/marketer responding directly. Volume of inventory visible = serious production capacity. |

---

## Tier 2 — Wholesalers (B2B shops with explicit wholesale signage)

### 3. MITWAA VLOGS' featured shop — "Imported Toys ONLY WHOLESALE" (BCH rel **7/10**)  ★ NEW
| Field | Value |
|---|---|
| **Gemini vendor type** | WHOLESALER · supply_side ✓ |
| **Scale visible** | Large · 1000+ inventory pieces |
| **Signage text Gemini read** | _"Imported Toys / ONLY WHOLESALE / For Order: **9625218026, 8510888855**"_ |
| **Drift RC present** | ✅ YES |
| **Products visible** | Bugatti Divo RC car, other RC cars, bubble guns, dolls, toy trucks |
| **Phones from signage** | `+91-9625218026` + `+91-8510888855` (visible in frame — these are the shop's published numbers, not the vlogger's) |
| **Phone from description** | `+91-85108-88855` (matches signage) |
| **Channel** | MITWAA VLOGS — 1,020,000 subscribers |
| **Video** | https://www.youtube.com/watch?v=COF4V6yTWF8 |
| **Verdict** | Shop has explicit "ONLY WHOLESALE" signage with 2 phone numbers — this is the cleanest B2B signal Gemini surfaced this round. Call BOTH numbers. |

### 4. Kamal Enterprises — Teliwara Chowk Sadar Bazar Delhi (BCH rel **7/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | WHOLESALER · supply_side ✓ |
| **Scale visible** | Medium · 1000+ inventory pieces |
| **Signage text Gemini read** | _"Kamal Enterprises"_ |
| **Drift RC present** | ❌ NO (toy cars / dolls / trucks / airplanes) |
| **Phone from creator (INFINITY VLOGS desc)** | `+91-70654-19045` |
| **Channel** | INFINITY VLOGS — 253,000 subscribers |
| **Video** | https://www.youtube.com/watch?v=Qax4x5kRqrA |
| **Verdict** | This is the same Kamal Enterprises we logged at 2337 Teliwara Chowk Sadar Bazar in the Delhi scan + Zauba data. **Visual confirmation** of large inventory. Drift not visible — toy-grade general wholesaler. Useful for price-floor intel, not drift sourcing. |

### 5. Rashu Toys Pvt. Ltd. (brand: Fun Nation) (BCH rel **7/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | WHOLESALER · supply_side ✓ |
| **Scale visible** | Medium · 100-1000 pieces |
| **Production signals** | Stacks of identical product boxes, large blue crates, warehouse setting with industrial lighting |
| **Signage text Gemini read** | _"RASHU TOYS PVT. LTD."_ |
| **Drift RC present** | ❌ NO |
| **Products visible** | Remote control cars, RC car track sets |
| **Phone** | `+91-95996-26661` · website funnation.in |
| **Video** | https://www.youtube.com/watch?v=IOj211MIypE |
| **Verdict** | **Legal entity name newly surfaced: RASHU TOYS PVT. LTD.** (funnation.in is the brand). Searchable on MCA/Zauba for CIN + directors. Mid-scale toy wholesaler with RC SKUs in stock. |

### 6. Milestone Impex (via Crazy Viner) — Jhandewalan Cycle Market Delhi (BCH rel **7/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | WHOLESALER · supply_side ✓ |
| **Scale visible** | Medium · 1000+ pieces |
| **Signage text Gemini read** | _"Wholesale - 9899618848, Retail - 8383083760 / EXTRA 2.5% CHARGES PAYMENT THROUGH DEBIT CARD CREDIT CARD RUPAY CARD RUPAY UPI"_ |
| **Drift RC present** | ❌ NO (die-cast cars, RC cars, toy airplanes, inflatable pools, toy guns) |
| **Phones (from signage)** | Wholesale `+91-9899618848` + Retail `+91-83830-83760` |
| **Channel** | Crazy Viner — 36,700 subscribers |
| **Video** | https://www.youtube.com/watch?v=bBLjuSUeCPI |
| **Verdict** | Confirms what we already had — Milestone Impex with split wholesale/retail phone lines. Drift not visible in frame. Toy-grade wholesale. |

### 7. Anju Toys — Sadar Bazar Delhi (BCH rel **6/10**)  ★ NEW with full address
| Field | Value |
|---|---|
| **Gemini vendor type** | WHOLESALER · supply_side ✓ |
| **Scale visible** | Medium · 1000+ pieces |
| **Signage text Gemini read** | _"ANJU TOYS Wholesaler All Kinds OF BATTERY TOYS, DOLLS & CHINA / **5409/3, NEW MARKET, GHORE WALI SARAI S.B. Delhi 6**"_ |
| **Market** | NEW MARKET, GHORE WALI SARAI S.B. Delhi 6 (Sadar Bazar area) |
| **Drift RC present** | ❌ NO (battery toys, dolls, RC cars, toy bats, toy guns) |
| **Channel** | Business Ke Deewano — 171,000 subscribers · IG @businesskedeewano · IndiaMART storefront |
| **Video** | https://www.youtube.com/watch?v=qPP8BZospfA |
| **Verdict** | **Full street address visible on signage** (5409/3 New Market, Ghore Wali Sarai) — Shoaib can walk in. No phone in frame; need to phone-call or visit Business Ke Deewano's IndiaMART storefront. |

---

## Tier 3 — Traders (intermediate import/multi-brand)

### 8. Sai Trading Company — DRIFT RC CONFIRMED (BCH rel **7/10**)  ★ HIGH PRIORITY
| Field | Value |
|---|---|
| **Gemini vendor type** | TRADER · supply_side ✓ |
| **Scale visible** | Medium · 100-1000 pieces |
| **Signage text Gemini read** | _"Sai Trading Company"_ — boxes with **"LIX MODEL" branding** |
| **Drift RC present** | ✅ **YES** |
| **Products visible** | RC cars (various models incl. drift), toy drones, electronic toys |
| **Phone from creator (Business Funda desc)** | `+91-79829-28315` |
| **Channel** | Business Funda — **1,230,000 subscribers** (massive distribution potential) |
| **Video** | https://www.youtube.com/watch?v=cdIjehs2JOw |
| **Verdict** | **PRIORITY CALL.** Phone is the same Sai Trading Toy from prior Delhi work, but now Gemini confirms drift RC ("LIX MODEL" branded boxes) is visible in their inventory. Cross-validates: BCH grey-space drift exists somewhere in their stock — verify SKU + price by phone. |

### 9. JAKI FINDURIOUS CREATEFUN (via Travel With Business) — China trader (BCH rel **6/10**)  ★ NEW
| Field | Value |
|---|---|
| **Gemini vendor type** | TRADER · supply_side ✓ |
| **Scale visible** | Medium · 100-1000 pieces |
| **Signage text** | _"JAKI FINDURIOUS CREATEFUN"_ · business card with "International Trade Manager" title |
| **Drift RC present** | ❌ NO (boxed RC cars: police, urban car; drawing boards; dinosaur toys) |
| **Phone** | none extracted |
| **Channel** | Travel With Business — 95,900 subs · IG @travelwithbusiness · Google Docs link |
| **Video** | https://www.youtube.com/watch?v=fZvcMLey33s |
| **Verdict** | "International Trade Manager" business card = real China-side trader who sells INTO India. Channel description likely has trade-manager contact. Worth following up via IG @travelwithbusiness. |

### 10. Manjushree Impex (via SoniyaG Vlogs) (BCH rel **3/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | TRADER · supply_side ✓ |
| **Signage text** | _"Manjushree Impex"_ |
| **Drift / RC present** | ❌ NO — hair clips, scrunchies (wrong category entirely) |
| **Verdict** | Wrong category, skip. |

### 11. WHITE TOYS / CHANAK (via Aditi Toys) (BCH rel **3/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | WHOLESALER · supply_side ✓ |
| **Signage text** | _"WHITE TOYS, Min. Buying Quantity, CHANAK"_ (MOQ language visible) |
| **Drift / RC present** | ❌ NO — plastic doctor kit, fashion kit, electric robot, wooden blocks |
| **Verdict** | Real wholesaler ("Min. Buying Quantity" signage) but no RC product. Skip for drift, log for general toy intel. |

### 12. Xingfei Toys — sanitation truck manufacturer (BCH rel **0/10**)
| Field | Value |
|---|---|
| **Gemini vendor type** | MANUFACTURER · supply_side ✓ |
| **Products** | Toy sanitation trucks, water sprinkler trucks, garbage trucks |
| **Verdict** | Real Chinese manufacturer (xingfeitoys.com) but wrong product category. Skip. |

---

## ❌ Channels EXCLUDED by Gemini (filtered out as retail / hobbyist / reviewer / NA)

These are vlog or retail channels — useful for content strategy possibly, but NOT supply-side. Gemini's `skip_if_retailer: true` for all of these.

| Channel | Gemini type | Why skipped |
|---|---|---|
| Niranjan China | RETAILER | Customer-facing display, not factory |
| Happy Here Films | HOBBYIST | Personal Traxxas review content |
| Industrial Craft | CREATOR_REVIEWER | Vlogger tour content, not actual vendor |
| Deepoo Vlog | CREATOR_REVIEWER | Vlogger |
| FashionTIY | RETAILER | Online wholesale platform display (B2C-leaning) |
| VLOGSTAN | RETAILER | Customer-facing toy shop tours |
| Uzair Ali | CREATOR_REVIEWER | Reviewer |
| Journey Of Deepak | RETAILER | Retail tour content |
| Vyapar Guruji extra | NA | No product visible in frames |
| JourNey WithOut VisA | NA | Travel vlog |
| Engineer On Road | RETAILER | Retail/showroom content |
| Gyanvik Business | NA | Business advisory content, no shop |

---

## Recommended call sequence for Shoaib

Day 1 AM:
1. **Sai Trading Company** `+91-79829-28315` — drift confirmed in frame, "LIX MODEL" brand visible. Ask: "Aap LIX MODEL drift RC stock karte ho? Price + MOQ?"
2. **MITWAA shop "Imported Toys"** `+91-9625218026` and `+91-8510888855` — explicit ONLY WHOLESALE signage. Ask: Bugatti Divo RC + similar drift-pattern SKUs.

Day 1 PM:
3. **WLtoys Official** — message via aliexpress.com/store/911418260 (their video description says they're "looking for dealers globally"). Drift confirmed in production.
4. **Xhy Toy Factory** — DM via @outlook.com address in their video description. They have 1000+ inventory visible — likely 100-200 unit MOQ.

Day 2 AM:
5. **Rashu Toys Pvt. Ltd.** `+91-95996-26661` — verify CIN via MCA before calling. Mid-scale wholesale with RC SKUs.
6. **Business Funda channel** (the YouTuber, 1.23M subs) — DM and ask them to introduce to Sai Trading Company directly.

Day 2 PM:
7. **Travel With Business** IG @travelwithbusiness — DM, ask for the JAKI FINDURIOUS trade manager contact.
8. **Anju Toys** at 5409/3 New Market, Ghore Wali Sarai S.B. Delhi 6 — phone-discover or walk-in during the Sadar Bazar circuit.

Hold for later:
9. **Milestone Impex** `+91-9899618848` (wholesale line, visible on signage) — useful price-floor benchmark, no drift confirmed.
10. **Kamal Enterprises** via INFINITY VLOGS `+91-70654-19045` — drift not visible, toy-grade general wholesale only.

---

## What Gemini's new prompt added (vs the old hobby/toy classifier)

The supply-side classifier added 5 new structured fields per video:
- `vendor_type` (MANUFACTURER / DISTRIBUTOR / WHOLESALER / TRADER / IMPORTER / RETAILER / HOBBYIST / CREATOR_REVIEWER / NA)
- `supply_side: true|false` boolean (the decisive filter)
- `production_signals[]` — the specific factory/warehouse/wholesale visual indicators present
- `scale_visible` + `estimated_inventory_pieces_visible` — operation scale
- `shop_or_facility_signage_text` — the actual signage text Gemini OCR'd from the frame (this is where the shop names came from)
- `skip_if_retailer: true|false` — explicit BCH instruction whether to skip

The retail-channel filter worked: 12 of 24 channels were classified as RETAILER / HOBBYIST / CREATOR_REVIEWER / NA and excluded. The other 12 are the actionable supply-side leads above.

---

## Methodology + caveats

- **Searches used:** 20 supply-side YouTube queries (manufacturer/factory/wholesale-area/named-importers) × 25 results each = ~500 raw video matches → 387 unique → 246 channels → 24 frame-extracted (top 25 minus Business Bites which timed out on yt-dlp).
- **Quota:** ~2,000 YouTube API units + ~24 × 5 = ~120 Gemini calls. Within today's daily budgets.
- **What we did NOT do:** Manufacturer-direct outreach. That's the next step — these 12 channels feed into Shoaib's existing `01_PHONE_CALLS_THIS_WEEK.md` plus 3 new high-priority targets above (Sai Trading drift / MITWAA / Xhy Toy Factory).
- **Signal cross-validation:** WLtoys Official scored rel=9 yesterday (different prompt) and rel=10 today (supply-side prompt) — direction is consistent. Crazy Viner went from rel=2 (hobby-grade lens) to rel=7 (supply-side lens) — also consistent (they ARE a wholesaler, just toy-grade not hobby-grade).
- **What Gemini missed:** A few frames contained mixed retail+wholesale content; Gemini picked the dominant signal. If a frame shows a wholesale godown with retail counter visible, Gemini may classify as WHOLESALER even though the channel also retails. Cross-check with the phone-call before booking.
