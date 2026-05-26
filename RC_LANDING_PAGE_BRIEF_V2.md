# RC CARS — LANDING PAGE BRIEF V2 (build-ready)
**BCH Bangalore | Syed Ibrahim | 2026-05-23**
**Companion to:** [RC_CONVERSION_INTELLIGENCE_BRIEF.md](RC_CONVERSION_INTELLIGENCE_BRIEF.md) (the research backbone — every claim here traces to that doc)
**Status:** Build-ready spec. Hand to engineer / designer / no-code builder.

---

## §0 — DECISIONS LOCKED (2026-05-23)

| # | Decision | Locked value |
|---|----------|--------------|
| 1 | Platform | **Next.js 16 / React 19 on Vercel** (user's existing stack) |
| 2 | Site structure | **Two pages:** (a) Consumer landing — open to all; (b) Retailer login → unlocks bulk-purchase page |
| 3 | Hero SKUs (3) | **1:64 Storm Mini · 1:43 Storm (hero) · 1:24 Storm Pro** |
| 4 | Landing cost band | **₹500 – ₹800 per unit** (1:64 ~ ₹500, 1:43 ~ ₹650, 1:24 ~ ₹800) |
| 5 | Reviews | Collected via post-purchase flow (SMS + email, see §6) |
| 6 | Domain | TBD — placeholder `bch.in/rc`. Vercel project will be domain-agnostic until provided. |
| 7 | Checkout | **Razorpay Magic Checkout** (locked) — 1-click, UPI Intent default, COD with OTP gating, ~99% UPI success |
| 8 | WhatsApp | **Direct `wa.me` deep links only — no BSP / no automation provider** (Interakt / Wati / Gallabox NOT in scope). BCH ops team handles WhatsApp manually. See §6 trade-off note. |
| 9 | OTP | **SMS OTP via MSG91 / Razorpay OTP** (since no WhatsApp BSP). ~₹0.15/OTP |
| 10 | Order target | **500 – 1,000 orders/day at scale** |

### Recommended retail price ladder (proposed — confirm)

| SKU | Scale | Landing cost | Retail | MRP (anchor) | Contribution margin* |
|-----|-------|-------------|--------|--------------|----------------------|
| Entry SKU | **1:64** | ₹500 | **₹799** | ~~₹1,499~~ (47% off) | ~₹165 |
| Hero SKU ⭐ | **1:43** | ₹650 | **₹1,199** | ~~₹2,499~~ (52% off) | ~₹419 |
| Premium SKU | **1:24** | ₹800 | **₹1,499** | ~~₹2,999~~ (50% off) | ~₹565 |

*Contribution after ₹85 shipping + ₹25 packaging + 2% gateway. Before ad spend + RTO leakage.

**Why this ladder works:** entry at ₹799 unlocks the "from ₹799" hero hook (was ₹999 before). 1:43 hero stays at the proven ₹999–1,199 magic threshold. 1:24 premium = the **gift hero** (the 1:24 Dodge Challenger-style reel pattern that drove the 12.5M view reel — see [RC_CARS_MINI_SKU_BATTLEPLAN.md](RC_CARS_MINI_SKU_BATTLEPLAN.md)).

---

## §1 — MISSION & KPI

### Single objective
Convert Instagram-reel traffic into orders. The page does ONE job: **turn a reel viewer into a paid order in under 90 seconds.**

### KPI hierarchy
| Tier | Metric | Target (steady state) |
|------|--------|----------------------|
| North star | Daily paid orders | 500 – 1,000 |
| Primary | Conversion rate (mobile, IG referral) | ≥ 4.5% |
| Primary | Blended ad ROAS | ≥ 3.0× by Month 3 |
| Secondary | AOV | ≥ ₹1,250 |
| Secondary | Prepaid share | ≥ 45% |
| Secondary | Blended RTO | ≤ 18% |
| Health | LCP (mobile, 4G) | ≤ 2.5 s |
| Health | Cart-to-checkout completion | ≥ 65% |

---

## §2 — AUDIENCE MAP

Three distinct buyers, **same product, three framings, three hero variants**. Detect by UTM source.

| Buyer | Trigger source | Hero variant key | Primary buy hook |
|-------|---------------|------------------|------------------|
| **A. Gifting buyer** (woman 22–34 buying for her car-lover man) | `utm_source=ig_gift` · `utm_source=ig_reel_couple` | `gift` | "The gift every car guy melts over" |
| **B. Parent buyer** (mom 30–42) | `utm_source=ig_parent` · `utm_source=meta_search` · `utm_source=google_search` | `parent` | "Swap his screen time for real play" |
| **C. Self-buyer enthusiast** (man 19–38) | `utm_source=yt_drift` · `utm_source=ig_drift` · `utm_source=reddit` | `enthusiast` | "1:24 drift. 4WD. Gyro. ₹1,499." |
| Default (no UTM / unknown) | — | `default` | "Mini RC drift cars from ₹799" |

Full demographics, emotional triggers, objections-with-counters, content formats → [RC_CONVERSION_INTELLIGENCE_BRIEF.md §2](RC_CONVERSION_INTELLIGENCE_BRIEF.md).

---

## §3 — SITE ARCHITECTURE

```
bch.in/rc                          ← Consumer landing page (single-page scroll)
   ├── /cart                       ← Cart drawer (overlay)
   ├── /checkout                   ← Checkout (Razorpay Magic / GoKwik 1-click)
   ├── /track                      ← Order tracking by phone + OTP
   └── /wholesale                  ← Retailer login (gated)
         ├── /wholesale/register   ← Registration form (6 fields)
         └── /wholesale/catalog    ← Bulk-pricing page (gated)
```

- **Mobile-first.** 95%+ of traffic will be mobile (IG reels). Desktop is a courtesy layout, not the target surface.
- **One-page scroll** for the consumer landing — every section flows into the next, sticky CTA bar persists.
- **Wholesale lives at a separate route** — completely different visual treatment, no consumer marketing chrome.

---

## §4 — CONSUMER LANDING PAGE (`/rc`)

### Component manifest (in scroll order)

| § | Component | Purpose | Sticky? |
|---|-----------|---------|---------|
| 4.1 | `<AnnouncementBar />` | Offer surfaced pre-hero | Yes (top) |
| 4.2 | `<Hero />` | Stop scroll + price + CTA in one thumb-screen | No |
| 4.3 | `<TrustStrip />` | Instant credibility | No |
| 4.4 | `<UspIconRow />` | 4 friction-killers | No |
| 4.5 | `<SkuLineup />` | The 3 hero SKUs as cards | No |
| 4.6 | `<OfferStack />` | Bundle ladder + free gift + prepaid discount | No |
| 4.7 | `<AudienceBlocks />` | 3 buyer-angle stories | No |
| 4.8 | `<InTheBox />` | Specs + components flat-lay | No |
| 4.9 | `<DemoVideo />` | Hero video looped, drift in action | No |
| 4.10 | `<ReviewWall />` | Daddy Drones-style social proof | No |
| 4.11 | `<UgcGrid />` | "As seen on Instagram" buyer grid | No |
| 4.12 | `<FAQ />` | 10 questions that kill carts | No |
| 4.13 | `<WholesaleBridge />` | "Running a shop? Get wholesale rate." | No |
| 4.14 | `<FinalCta />` | Last conversion attempt | No |
| 4.15 | `<Footer />` | Trust receipts | No |
| Float | `<StickyAddToCart />` | Always-visible mobile CTA bar | Yes (bottom) |
| Float | `<WhatsAppFab />` | Floating chat button | Yes (bottom-right) |

### §4.1 — `<AnnouncementBar />`
**Sticky top bar. 32px tall. Centred text. White-on-brand-red.**

```
Free Shipping ₹1,099+ · COD Available · 7-Day Free Replacement
```

Optional auto-rotating: ["Free Shipping ₹1,099+", "Pay online → ₹100 off", "Ships in 24 hrs from Bangalore"] every 5 s.

### §4.2 — `<Hero />` (above the fold)

```
┌─────────────────────────────────────┐
│  [Auto-play muted looped video]     │
│  10-sec drift loop on dark floor    │ <- 16:9 mobile, 70vh max
│  with LED tail-lights glowing       │
│                                     │
│  ★★★★★ 4.7 · 12,000+ orders        │ <- inline social-proof line
│  ─────────────────────────────────  │
│  Mini RC Drift Cars from ₹799       │ <- H1, big, 32px on mobile
│  1:24 · 1:43 · 1:64 scale · LED ·   │
│  Drift wheels · Gift-ready box      │
│                                     │
│  [ 🎁 Shop Hero — ₹1,199 ]          │ <- primary CTA, brand red
│  or DM us on WhatsApp →             │ <- secondary CTA, text link
│                                     │
│  ~~MRP ₹2,499~~ · 52% off · COD ✓  │ <- micro-anchor line
└─────────────────────────────────────┘
```

**Hero copy variants by `?utm_source`:**

| UTM | Headline | Subhead |
|-----|----------|---------|
| `ig_gift` | The Gift Every Car Guy Melts Over | Mini RC drift cars from ₹799 · Delivered gift-ready, dispatched in 24 hrs |
| `ig_parent` | Swap His Screen Time for Real Play | Mini RC drift cars from ₹799 · USB-C, 45-min runtime, drop-tested |
| `yt_drift` / `ig_drift` | 1:24 Drift. 4WD. Gyro. Yours for ₹1,499 | Hobby-grade build, toy-grade price · Spare parts pan-India in 3 days |
| Default | Mini RC Drift Cars from ₹799 | 1:24 · 1:43 · 1:64 scale · LED · Drift wheels · Gift-ready box |

**Hero asset spec:**
- Format: HLS `.m3u8` (adaptive bitrate) + MP4 fallback (`H.264, 1080p, 8-12s loop`)
- `<video>` attrs: `autoplay muted loop playsinline preload="auto" fetchpriority="high"`
- File ceiling: hero weight ≤ 350 KB (poster image ≤ 60 KB WebP q80, video preloaded segment ≤ 280 KB)
- Aspect on mobile: 9:16 with safe-zone centre, falls to 16:9 above 768px

**Primary CTA**: scrolls to §4.5 (SKU lineup) and pre-highlights the 1:43 hero card.
**Secondary CTA**: opens WhatsApp Business deep-link `https://wa.me/91XXXXXXXXXX?text=Hi%2C%20I%20want%20to%20order%20the%20mini%20RC%20drift%20car.`

### §4.3 — `<TrustStrip />` (inline below CTA)
Thin horizontal strip, no border, 14px text:
```
★★★★★ 4.7  ·  12,000+ orders shipped pan-India  ·  Featured in @daddydrones · @youcliq · @highgear
```
Stars come from real Judge.me / Loox aggregate once live. Pre-launch placeholder uses your IG follower-count: "Followed by 60K+ on Instagram".

### §4.4 — `<UspIconRow />` (4 icons, horizontal)

| Icon | Label |
|------|-------|
| 🔌 | USB-C charging · 30-min full charge |
| 💧 | Drop-tested 1.5m · Replaceable shell ₹99 |
| 🛡 | BIS certified · Age 6+ |
| 🇮🇳 | Assembled in India · GST-paid |

Each icon is a real SVG, not emoji, at 48×48 with brand-red accent.

### §4.5 — `<SkuLineup />` (the 3 hero SKUs)

Three cards in a horizontal scroll on mobile (snap-scroll), 3-column grid on desktop. **Middle card is the 1:43 hero** — visually larger, "MOST GIFTED" badge.

```
┌────────┐  ┌──────────┐  ┌────────┐
│ Card 1 │  │  Card 2  │  │ Card 3 │
│  1:64  │  │  1:43 ⭐ │  │  1:24  │
│        │  │MOST GIFTED│  │        │
│ ₹799   │  │ ₹1,199    │  │ ₹1,499 │
│ MRP    │  │  MRP      │  │ MRP    │
│ ₹1,499 │  │  ₹2,499   │  │ ₹2,999 │
│        │  │           │  │        │
│[Cart]  │  │  [Cart]   │  │ [Cart] │
└────────┘  └──────────┘  └────────┘
```

**Per-card content (component prop spec):**

```typescript
type SkuCard = {
  scale: '1:64' | '1:43' | '1:24';
  characterName: string;          // TBD — pick 3 named characters (LOT pattern)
  hero_image: string;             // WebP 800×800, q85
  alt_images: string[];           // 4 more — flat-lay, lifestyle, scale-vs-hand, livery options
  retail_inr: number;
  mrp_inr: number;
  bullets: [string, string, string, string];  // exactly 4
  badge?: 'MOST GIFTED' | 'NEW' | 'BESTSELLER';
  primary_cta: { label: string; action: 'add_to_cart' | 'buy_now' };
  body_shape: string;             // e.g., 'GTR-style', 'Challenger-style', 'Supra-style'
}
```

**Bullet templates per scale:**
- 1:64 — "Pocket size · Desk-friendly · LED tail-lights · Drift wheels"
- 1:43 — "Best for gifting · LED + smoke effect · Swappable wheels · Premium gift box"
- 1:24 — "4WD · Gyro stabilizer · LED full-body · Pro drift mode"

**The 3 character names — TBD by Syed:**
We need 3 named characters (like LOT's "Night Wolf", "Flare", "Iris"). Each one becomes a reel hero. Suggestion shape:
- 1:64 = `[Name] Mini` (single-word + Mini suffix)
- 1:43 = `[Name]` (the brand-defining name)
- 1:24 = `[Name] Pro` (Pro suffix)

Examples to choose from: Storm, Rogue, Blade, Phantom, Maverick, Drift, Apex, Vortex, Razor, Pulse, Onyx. **Lock the 3 names before page build — they're load-bearing for every reel and every section.**

### §4.6 — `<OfferStack />` (single visual block)

| Offer | Mechanic | Component |
|-------|----------|-----------|
| 🎁 **Free drift wheels** | "Extra set of swappable drift tyres FREE with every order" | Bullet line, green tick |
| 💳 **Prepaid ₹100 off** | "Pay online → ₹1,099 (saves ₹100 vs COD)" | Toggle on PDP between COD / Prepaid price |
| 📦 **Buy-2 bundle** | "Gift one + keep one — ₹1,999 (save ₹399 on 1:43 pair)" | Tile with quantity-break logic |
| ⚡ **Festival drop** | "Limited stock — only X left at this price" | Live counter (real, not fake) |
| 🚀 **LED+Smoke upgrade** | "+₹200 unlocks LED full-body + smoke effect" | Variant selector on PDP |

**Auto-apply at checkout** via Shopify Functions / GoKwik / Razorpay coupon engine (depending on stack chosen — see §6).

### §4.7 — `<AudienceBlocks />` (3 stacked story blocks)

Each block is a 2-column on desktop (image left / copy right), single-column on mobile. Embedded short reel (15s) per block.

#### Block A — The Gifting Story
- **Headline:** "Why every man wants one."
- **Subhead:** "The gift that doesn't sit in a drawer."
- **Asset:** 15s reel of the "she gifted you this" hook (POV reaction)
- **Bullets:** "Delivered gift-wrapped" · "Dispatch SMS to YOU, not him" · "Free same-day re-cancel if it ships late"
- **CTA:** [ Pick a gift → ] (scrolls to §4.5 with 1:43 highlighted)

#### Block B — The Parenting Story
- **Headline:** "Calm the back seat. Cut the screen time."
- **Subhead:** "Two reasons parents bought 10,000+ of these in 2026."
- **Two micro-sub-blocks:**
  - (i) **Car-ride survival** — 10s reel of restless kid → handed remote → silence. Honest framing only (no fake driving inside moving car).
  - (ii) **Screen-time swap** — 10s reel "Day 14 of replacing my kid's iPad with this ₹799 drift car." Honest claim: *better alternative to a screen*, not "educational."
- **CTA:** [ Order for your kid → ] (scrolls to §4.5 with 1:64 entry highlighted)

#### Block C — The Enthusiast Story
- **Headline:** "₹1,499. 4WD. Gyro. Tell me this is a toy."
- **Subhead:** "Starter hobby-grade. Spare parts pan-India in 3 days."
- **Asset:** 15s slo-mo drift on marble floor, neon underlight
- **Bullets:** "Brushed motor + gyro" · "Spare body shell ₹149 · Tyres ₹99 · Battery ₹199" · "JDM body shapes"
- **CTA:** [ Cart it. Drift it tonight. → ] (scrolls to §4.5 with 1:24 highlighted)

### §4.8 — `<InTheBox />` (kills the "is it worth ₹999?" objection visually)

**Flat-lay image (Skillmatics template):** every component of the kit laid flat on a neutral background — car body, remote, USB-C charger, battery × 2 (if applicable), spare drift wheels, manual, gift box.

**Adjacent: specs table.**

| Spec | 1:64 | 1:43 | 1:24 |
|------|------|------|------|
| Scale | 1:64 | 1:43 | 1:24 |
| Length | ~80 mm | ~100 mm | ~180 mm |
| Drive | 2WD | 2WD | 4WD |
| Top speed | 8 km/h | 12 km/h | 25 km/h |
| Battery life | 25 min | 35 min | 45 min |
| Charge time | 25 min | 30 min | 40 min |
| Range | 15 m | 20 m | 30 m |
| Age | 6+ | 8+ | 10+ |
| Charger | USB-C | USB-C | USB-C |
| LED | Tail | Tail + Headlight | Full body |
| Drift mode | Yes | Yes | Yes (with gyro) |

(Fill real numbers from final supplier samples before launch.)

### §4.9 — `<DemoVideo />` (full-width section)

15–25 sec demo loop showing the 1:24 drifting around obstacles, jumping a small ramp, LED lighting in dark. **Same HLS+MP4 pattern as hero.** This is the "motion proof" the hero can't carry alone — required because static images can't show what an RC car actually does.

Caption underneath: *"Real footage — no edit, no slowmo. Filmed in a Bangalore basement, Feb 2026."*

### §4.10 — `<ReviewWall />` ⭐ (the trust-at-scale moment)

Daddy Drones pattern. The single most-stealable element across all competitors.

**Block 1 — Counter (large, brand-red):**
```
12,000+
ORDERS SHIPPED ACROSS INDIA
```

**Block 2 — Aggregate rating (Judge.me / Loox widget):**
```
★★★★★ 4.7
2,341 verified buyer reviews
[ See all reviews → ]
```

**Block 3 — Rotating named, product-tagged, long-form reviews (carousel):**

Format per review:
```
┌─────────────────────────────────────────────────────┐
│ [Customer photo of the car they bought]             │
│                                                     │
│ ★★★★★                                              │
│ "Bought the 1:43 Storm for my husband's birthday.   │
│  He literally screamed. Now drifts it every day     │
│  in our living room. The LED lights are insane."    │
│                                                     │
│ — Priya M., Bangalore                               │
│   Verified buyer · 1:43 Storm · 23 March 2026       │
└─────────────────────────────────────────────────────┘
```

**Day-1 minimum:** 30 honest seed reviews with real customer photos. Source from a soft-launch to 50 friends/family at 50% off → write authentic 100-150 word reviews + photo. Without this, the page launches naked.

**Review collection automation (post-purchase):**
- D+5: WhatsApp message — *"Aapka order pohunch gaya? Reply with a photo + ★★★★★ rating, win ₹100 store credit."*
- D+10: Email — same ask, email-friendly version
- D+15: One last WhatsApp nudge
- Use Judge.me automation (free tier) for the review-collection flow.

### §4.11 — `<UgcGrid />` (Instagram-feed shoppable grid)

12–20 IG buyer reels, shoppable. Pulls from `@bch_rc` hashtag #BCHrc.

**Day-1 minimum:** seed with 12 reels from your own 8-account network (the architecture in [RC_CARS_MINI_SKU_BATTLEPLAN.md §5](RC_CARS_MINI_SKU_BATTLEPLAN.md)). After Month 1, real buyer reels start appearing.

### §4.12 — `<FAQ />` (10 questions, accordion)

Top 10 to ship:
1. **Is COD available?** Yes — pan-India, ₹49 fee on orders below ₹999. Pay online to save ₹100 instead.
2. **How long does the battery last?** 25–45 min depending on scale. USB-C charges in 25–40 min.
3. **What age is this for?** 6+ for 1:64, 8+ for 1:43, 10+ for 1:24. Adults love all three.
4. **What if it breaks?** 7-day Free Replacement on damage / defect — no questions asked.
5. **Where do you ship?** Pan-India. Bangalore / Mumbai / Delhi metros in 2-3 days. Tier-2/3 in 4-7 days.
6. **Can I gift-wrap it?** Yes — every order ships in a premium gift box. Add a handwritten note free at checkout.
7. **Does it work on carpet / tiles?** Yes both. Best drift on smooth floors (tiles, wood, marble).
8. **What's in the box?** Car · Remote · USB-C cable · Spare drift wheels · Gift box · Quick-start guide.
9. **Do you sell spare parts?** Yes — body shell ₹149, battery ₹199, wheels ₹99. Shipped from Bangalore in 3 days.
10. **Bulk / wholesale orders?** Visit `/wholesale` to register as a retailer and unlock bulk pricing.

Accordion default-collapsed. First question (COD) auto-open on first load.

### §4.13 — `<WholesaleBridge />` (full-width banner near footer)

Captures retailers who landed on the consumer page.

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   Running a shop? Get wholesale rate.           │
│                                                 │
│   MOQ 10 pcs · All-India dispatch ·             │
│   GST-verified resellers only                   │
│                                                 │
│   [ Apply for Wholesale Access → ]              │
│   or WhatsApp +91 XXXXX                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

CTA links to `/wholesale/register`.

### §4.14 — `<FinalCta />` (last-chance CTA)

Full-width, brand-red, large.

```
Order now — dispatched in 24 hrs from Bangalore.
[ 🎁 Shop the Hero — ₹1,199 ]
or DM us on WhatsApp →
```

### §4.15 — `<Footer />`

Standard, mobile-stacked. Sections:
- **Contact:** WhatsApp (tap-to-chat) · Email · Phone · Bangalore HQ address
- **Policies:** Shipping · Replacement · Privacy · Terms · Refund
- **Trust receipts:** CIN · GSTIN · BIS Cert # · Made in India tricolor
- **Payment icons (UPI FIRST, biggest):** UPI · PhonePe · GPay · Paytm · Visa · Mastercard · RuPay · Net Banking · Simpl · LazyPay
- **Socials:** IG · YouTube · WhatsApp Business

### Sticky overlays

**Bottom mobile CTA bar (always visible after hero scrolls):**
```
┌─────────────────────────────────────────┐
│  ₹1,199         [ Add to Cart ]         │
└─────────────────────────────────────────┘
```

**Bottom-right floating WhatsApp FAB** — `wa.me` deep link.

---

## §5 — RETAILER LOGIN + BULK PURCHASE FLOW

Concrete spec — finalised against B2B portal research (Udaan, IndiaMART, ApnaKlub, Shopify B2B, GSTZen / Surepass / Cashfree GSTIN APIs, Indian toy-trade margin norms).

### §5.1 — `/wholesale` (public catalog, gated pricing)

The wholesale landing page is **NOT a login wall.** Walling SEO and the curiosity loop both kills signups. Instead: **show MSRP and product photos publicly, gate only the trade tiers.** This is the consensus pattern across Udaan, IndiaMART, Amazon Business, and the Shopify B2B 2026 playbook.

**Unauthenticated view:**
```
┌─────────────────────────────────────────────────────────┐
│ BCH Wholesale — Bulk RC at trade rates                  │
│ MOQ from 12 pcs · Pan-India dispatch · GST-verified     │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ [1:64 Storm Mini]  [1:43 Storm ⭐]  [1:24 Storm Pro]    │
│  MRP ₹1,499         MRP ₹2,499         MRP ₹2,999       │
│  🔒 Login for       🔒 Login for       🔒 Login for     │
│     trade pricing      trade pricing      trade pricing │
│                                                         │
│ [ Register as a retailer (instant) ]                    │
│ Already registered? [ Login ]                           │
└─────────────────────────────────────────────────────────┘
```

The `🔒 Login for trade pricing` line is the single most-converting signup driver — it's the curiosity gap that gets the click.

### §5.2 — `/wholesale/register` (single-step 5-field form)

**Field order (mobile-first, top → bottom — LOCKED):**

| # | Field | Type / validation | Notes |
|---|-------|-------------------|-------|
| 1 | **Mobile number** | `inputmode="numeric"`, 10-digit starting 6–9, `+91` locked prefix | Triggers **SMS OTP** (MSG91 / Razorpay OTP). First because it's the most habitual field + the verification channel. |
| 2 | **Contact person name** | text, ≥ 2 chars | — |
| 3 | **Email** | regex `\S+@\S+\.\S+`, simple | For invoice + rate-list delivery. |
| 4 | **GSTIN** | regex `^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$`, 15 chars uppercase | On valid format → auto-verify via GSTZen API → auto-fills firm name (the "wow" moment). |
| 5 | **Firm name** | text, ≥ 3 chars | Auto-prefilled from GSTIN API response. User can edit if mismatched. Fuzzy-matched against GSTIN-returned legal name with 80% similarity threshold. |

**5 fields total** — confirmed with Syed 2026-05-23 (the earlier "firm number" field was a slip — meant "firm name", which is already field 5; no separate firm-number field needed).

**Validation pattern:** inline on blur. Real-time inline validation reduces form errors ~42% — use it. Don't block on every keystroke.

**Anti-bot:** Cloudflare Turnstile (free, invisible) on form submit. NOT reCAPTCHA v2 (too much friction). Plus honeypot field.

**Reseller terms checkbox** (single line, above submit): 
> ☐ I agree to BCH Retailer Terms (no MRP undercutting on marketplaces, no resale of trade pricing data).

This is the legal hook against price-list leaks and Amazon/Flipkart MRP-busting.

### §5.3 — GSTIN auto-verification + unlock flow

**Provider:** GSTZen (₹0.70/call, ₹3,500 / 5,000 calls). Alternatives: Surepass, Cashfree, Hyperverge, Masters India. Pick one — same API surface. At BCH's projected signup volume (~few hundred/month), cost is under ₹500/month.

**Flow on submit:**

```
User submits form
   ↓
GSTIN API call (5 sec)
   ↓
   ├── ACTIVE + legal name ≥ 80% similar to typed firm name
   │       → SMS OTP sent to mobile → user enters 6-digit code →
   │         instant unlock → redirect to /wholesale/catalog
   │       → Confirmation: SMS + email with login link
   │       → BCH ops team manually pings the new retailer on WhatsApp Web
   │         within 24 hr (welcome + rate-list PDF)
   │
   ├── ACTIVE + name mismatch
   │       → Hold for manual review. Show: "Your application is under review.
   │                  We'll confirm within 24 hours."
   │       → Internal alert in BCH ops dashboard; ops contacts retailer
   │         via WhatsApp Web manually.
   │
   └── INACTIVE / CANCELLED / API_FAILURE
           → Reject + show: "GSTIN not currently active. Please re-check or
                  WhatsApp us at +91 XXXXX for help." (wa.me deep link)
```

**~80% of submissions auto-unlock instantly.** ~15% go to manual review (resolved in 24 hr via WhatsApp). ~5% are bad GSTINs and bounce.

**Why this beats both "instant for everyone" and "always manual":** instant access for the 80% who are legit (the "WhatsApp 24-hr review" framing converts worse than instant); manual review as the fraud filter for the 20% (vs the alternative of letting bad GSTINs through and burning trade pricing).

### §5.4 — `/wholesale/login`

- **Login method:** Mobile + **SMS OTP** (no password). Reduces password-reset support load to zero.
- **Session:** NextAuth.js with credentials provider + JWT, refresh every 7 days. On Vercel.
- **Forgot password:** N/A — OTP-only.

### §5.5 — `/wholesale/catalog` (the bulk-pricing page, logged-in view)

**Layout principle:** table-first, image-secondary. This is a B2B page — efficiency over emotion. **Catalog, not form.** All 3 SKUs visible at once with quantity inputs per row, single cart checkout.

**Per-row template:**

```
┌──────────────────────────────────────────────────────────────────┐
│ [80x80 thumb]  1:43 STORM (Hero)                                 │
│                MRP ₹2,499 · Retail ₹1,199                        │
│                                                                  │
│  Tier              Per-unit     Your margin    Pack-of           │
│  12 pcs            ₹1,624       ₹875 / pc (35% off MRP)          │
│  48 pcs            ₹1,374       ₹1,125 / pc (45% off MRP)        │
│  144 pcs           ₹1,199       ₹1,300 / pc (52% off MRP)        │
│                                                                  │
│  [Qty: __12__]   [ Add to bulk cart ]                            │
└──────────────────────────────────────────────────────────────────┘
```

**Bulk pricing ladder — locked across all 3 SKUs:**

| Tier | MOQ (total mixed across SKUs) | Discount off MRP | Retailer margin |
|------|-------------------------------|------------------|-----------------|
| **Starter** | 12 units (1 inner carton) | 35% off MRP | 35% |
| **Standard** | 48 units (1 master carton) | 45% off MRP | 45% |
| **Distributor** | 144+ units | 52% off MRP | 52% |

**Concrete per-SKU prices (with real BCH economics):**

| SKU | MRP | Landing | Starter (12) | BCH margin | Standard (48) | BCH margin | Distributor (144) | BCH margin |
|-----|-----|---------|--------------|------------|---------------|------------|--------------------|------------|
| 1:64 Storm Mini | ₹1,499 | ₹500 | ₹974/pc | ₹474 | ₹824/pc | ₹324 | ₹719/pc | ₹219 |
| 1:43 Storm | ₹2,499 | ₹650 | ₹1,624/pc | ₹974 | ₹1,374/pc | ₹724 | ₹1,199/pc | ₹549 |
| 1:24 Storm Pro | ₹2,999 | ₹800 | ₹1,949/pc | ₹1,149 | ₹1,649/pc | ₹849 | ₹1,439/pc | ₹639 |

All tiers margin-positive. **Mixed-pallet ordering is enabled at the brand level (12 units total MOQ), NOT SKU level** — so a retailer can mix 4 × 1:64 + 4 × 1:43 + 4 × 1:24 to qualify for Starter tier. Critical for small shops who want to try the range.

**Framing rules (per Indian B2B norm):** lead with **per-unit net rate + "your margin in rupees"** — not % discount. ₹874 margin/pc on a ₹2,499 MRP item is concrete; "45% off" feels abstract.

**Page features:**
- ☑ All 3 SKUs visible (catalog)
- ☑ Per-row qty input + "Add to bulk cart"
- ☑ Single cart drawer combining mixed SKUs
- ☑ **Sticky WhatsApp button** ("Place order on WhatsApp instead →") — Tier-2/3 shopkeepers still prefer this channel
- ☑ **Downloadable rate-list PDF** with **watermark** (retailer firm name + timestamp). If the PDF leaks to a WhatsApp group, you know who leaked it.
- ☑ Live pincode-EDD ("Delivered to 560001 by Tue 28 May")
- ☑ Auto-tier upgrade visual ("Add 4 more pcs to unlock 45% margin")

### §5.6 — Payment terms & logistics (B2B specifics)

**Payment terms (locked — pending Syed's risk-appetite check):**

| Order value | Payment term | Notes |
|-------------|--------------|-------|
| Under ₹50,000 | **100% advance** via UPI / bank transfer | New retailers, all orders |
| ₹50,000 – ₹2,00,000 | **50% advance + 50% before dispatch** | New retailers |
| Above ₹2,00,000 | Same as above, escalate to founder approval | — |
| Any tier, repeat buyer (3+ successful prior orders) | **COD-on-pallet** eligible | Earned, not default |
| **Net-30** | ❌ NOT offered Day 1 — receivables risk for a new brand is unacceptable | Reconsider after Year 1 |

**Logistics (locked):**

| Tier | Freight |
|------|---------|
| Starter (12 pcs) | Buyer pays actual freight (Shiprocket calc, shown at checkout) |
| Standard (48 pcs) | **Landed (freight included in per-unit price)** |
| Distributor (144+ pcs) | **Landed + priority dispatch from Bangalore** |

Bake freight into the per-unit price from Standard tier and above. Indian retailers strongly prefer landed pricing ("price includes delivery to my shop"). FOB-buyer logic creates a negotiation surface; landed removes it.

### §5.7 — Data model (per-retailer record)

| Field | Source | Used in |
|-------|--------|---------|
| `firm_name` | GSTIN API or manual | Invoice + display |
| `contact_name` | Form | Personal address |
| `mobile` | Form + WhatsApp-OTP verified | OTP, order updates, broadcast |
| `email` | Form | Invoice + rate-list email |
| `gstin` | Form + API-verified | Tax invoice + uniqueness key |
| `firm_contact_line` | Form (optional) | Backup contact |
| `gstin_legal_name` | API | Audit + match check |
| `gstin_state` | API | Auto-set state code on invoice |
| `gstin_status` | API | Re-verify quarterly |
| `verified_at` | System | Audit |
| `tier_unlocked` | Auto-computed | Starter / Standard / Distributor — based on cumulative order qty |
| `total_orders`, `total_spend`, `last_order_at` | Order history | LTV scoring + tier promotion |
| `terms_accepted_at` | Form submit | Legal trail |

**Uniqueness constraint:** one account per GSTIN (DB-level). Blocks the "multiple accounts behind one entity" abuse pattern.

### §5.8 — Anti-abuse stack

- ☑ GSTIN API auto-verify (primary fraud filter — reject inactive/cancelled)
- ☑ Cloudflare Turnstile on form + on the catalog page (60 req/min/IP rate limit)
- ☑ Click-to-accept reseller terms (legal hook against MRP undercutting)
- ☑ PDF rate-list watermarked with firm name + timestamp
- ☑ One account per GSTIN (DB uniqueness)
- ☑ Manual review escalation for name-mismatch cases (24-hr WhatsApp window)

### §5.9 — Marketing the wholesale flow

- The consumer landing page §4.13 banner ("Running a shop? Get wholesale rate") is the primary funnel.
- Secondary: a "Wholesale" link in the footer of every consumer page.
- Outbound: WhatsApp broadcast to a curated list of toy-shop owners (sourced via IndiaMART seller scrape, your existing BCH cycle-shop network, and the bch warehouse contacts).
- An "Apply for Wholesale" CTA in every IG bio's link-in-bio aggregator.

---

## §6 — TECH STACK & INTEGRATIONS

### Core (Vercel-native)
- **Framework:** Next.js 16 App Router · React 19 · TypeScript
- **Hosting:** Vercel (your existing infra)
- **Styling:** Tailwind CSS + shadcn/ui components (matches your existing app stack from the BCH content app)
- **DB:** Vercel Postgres (or Neon) for products, orders, retailer accounts
- **Auth (retailer):** NextAuth.js with credentials provider + mobile OTP
- **CDN:** Vercel Edge Network (default)
- **Image optimisation:** Next/Image with WebP / AVIF auto-conversion
- **Animation:** Framer Motion (you already use it in the content app)

### Payment & checkout (consumer) — LOCKED
- **Razorpay Magic Checkout** (1-click, UPI Intent default, COD with OTP gating, ~99% UPI success)
- Razorpay also handles the **SMS OTP** for COD-gating + retailer-portal login (one provider for both — simpler ops)
- **Cart:** Custom Zustand store with localStorage persistence (Next.js client side)

### COD / RTO mitigation (adapted for "no WhatsApp BSP")
- ☑ **OTP gating** on every COD order (mandatory, via Razorpay SMS OTP)
- ⚠️ **Manual WhatsApp confirmation by BCH ops team** within 30 min of COD order (no automated 5-min ping since no BSP). Ops dashboard surfaces new COD orders + a "Open in WhatsApp Web" button per order.
- ☑ **Smart COD blocking** by pincode via **Shiprocket Smart COD** (ML scoring blocks high-RTO pincodes)
- ☑ **₹49 COD fee** on orders below ₹999 (suppresses thin-margin orders)
- ☑ **₹100 prepaid discount** auto-applied at checkout via Razorpay Magic coupon engine
- ⚠️ **Trade-off note:** without WhatsApp BSP automation, the **5-min auto-confirmation** that drops RTO from ~30% to ~18% requires manual ops handling. With 500–1,000 orders/day at peak, this means 2–3 dedicated ops people on WhatsApp Web during business hours. **Re-evaluate adding a BSP (Interakt / Gallabox) at the 200-orders/day point** when manual handling stops scaling.

### Shipping
- **Aggregator:** Shiprocket (default Indian D2C) — Delhivery, Bluedart, XpressBees auto-routing
- **EDD display on PDP**: pincode auto-detected from IP, fallback to user-input pill
- **Bangalore same-day** (if possible) — use Borzo / Dunzo for hyperlocal

### Reviews
- **Widget:** Judge.me (free tier — fits early stage). Loox if you want gallery UI later.
- **Collection automation (adapted — no WhatsApp BSP):** Judge.me's built-in **email + SMS** review-request flow at D+5 / D+10 / D+15. Trigger via Razorpay/Shiprocket order-delivered webhook. SMS via MSG91 (~₹0.15/SMS).
- ⚠️ Without WhatsApp automation, expect ~20–30% lower review-collection rate than a WhatsApp-driven flow. Compensate with: (a) handwritten thank-you card in every box with a QR to the review page, (b) ₹100 store credit for verified photo-review.

### WhatsApp — DIRECT WEB ONLY (no BSP, no automation)

**Locked:** BCH uses **WhatsApp Web manually** for all customer + retailer conversations. No BSP (Interakt / Wati / Gallabox / AiSensy not in scope).

**What's still possible (via `wa.me` deep links — no API needed):**
- ☑ "Chat on WhatsApp" floating button on every page (`wa.me/91XXXXXXXXXX?text=...`)
- ☑ Tap-to-chat from product cards (pre-fills "Hi, I want to order the 1:43 Storm")
- ☑ Wholesale-bridge CTA → opens WhatsApp with retailer intro template
- ☑ Cart-abandonment recovery via SMS + email (not WhatsApp)
- ☑ Order updates via SMS (delivery notifications via Shiprocket SMS)

**What's NOT possible without a BSP:**
- ❌ Automated 5-min COD confirmation message → use manual handling (see RTO note above)
- ❌ Abandoned-cart WhatsApp ping → use SMS instead (worse open-rate but workable)
- ❌ WhatsApp broadcast to past buyers (new launches, festival drops) → use SMS broadcast (MSG91 ~₹0.15/SMS) or email
- ❌ Review-collection D+5/D+10/D+15 on WhatsApp → use SMS + email (above)
- ❌ Comment-to-buy DM payload via WhatsApp → use **Instagram Manychat** (Instagram-native, NOT WhatsApp — still works perfectly for IG reel comments)
- ❌ Retailer registration confirmation on WhatsApp → use SMS + email + manual WhatsApp Web ping by ops

**Ops dashboard requirement:** because WhatsApp is manual, the BCH ops dashboard must surface:
- New orders that need COD confirmation (with a "Open WhatsApp Web" button per order, pre-filled message)
- New retailer registrations (manual welcome ping)
- Abandoned carts (manual recovery if value justifies)

**Comment-to-buy stays automated** because Instagram comment automation runs through Manychat-for-Instagram (or Manychat IG / native IG quick-replies) — that's a different system from WhatsApp Business API. So "Comment RC for link" → IG DM auto-reply with the landing-page URL still works without any WhatsApp BSP.

### Tracking
- **Meta Pixel + GA4 + Microsoft Clarity** (Clarity for free heatmaps + session replay)
- **Conversion API (CAPI) on Meta** for ad-platform attribution post-cookie-deprecation
- **UTM-driven hero variant** detection in the `<Hero />` component
- **Razorpay Insights / GoKwik dashboard** for checkout funnel analytics

### Marketplaces (Month 4+)
- **Amazon Seller Central** — replicate the LOT hero-SKU playbook
- **Flipkart Seller Hub** — same SKUs, gift-bundles enabled
- **Meesho** — for sub-₹999 tier-3 audience
- **Quick commerce:** Blinkit / Instamart / Zepto via Shiprocket Q-Commerce

---

## §7 — COPY BANK

### Hero headlines (A/B test inventory)
| Variant | Use case |
|---------|----------|
| Mini RC Drift Cars from ₹799 | Default |
| The Gift Every Car Guy Melts Over | Gifting |
| Drift Cars That Survive a 5-Year-Old | Parent |
| 1:24 Drift. 4WD. Gyro. Yours for ₹1,499 | Enthusiast |
| RC Cars Start at ₹799 — LED, Drift, Gift-Ready | Generic festive |
| Trusted by 12,000+ Indians. Now starting ₹799 | Trust-forward |
| The Most-Gifted RC Car of 2026 | Bandwagon |

### Sub-headlines (paired)
- "1:24 · 1:43 · 1:64 scale · LED · Drift wheels · Gift-ready box · COD pan-India"
- "Delivered gift-wrapped, dispatched in 24 hrs from Bangalore"
- "USB-C charge · 45-min runtime · BIS-certified · 6-month warranty"
- "Hobby-grade build, toy-grade price · Spare parts in 3 days"

### CTA wording (proven across competitors)
- Primary: `🎁 Shop Hero — ₹1,199`
- Bundle: `Get the Buy-2 Bundle — ₹1,999 (save ₹399)`
- Secondary: `WhatsApp us to order →`
- Mobile sticky: `Add to Cart`
- Final: `Order now — dispatched in 24 hrs`

### Trust microcopy (one-liners scattered across page)
- "Free Replacement on Damage / Defect"
- "Ships in 24 hrs from Bangalore"
- "Pay online → ₹100 off"
- "10,000+ Bangalore orders in 2026"
- "BIS-certified · Age 6+"
- "Same-day in Bangalore, 2-3 days in metros"

### Hindi-English code-switch microcopy (per audience)
- Gifting: *"Bata bhi nahi paayegi, smile rok bhi nahi paayega"*
- Parent: *"Bina screen ke 45 minute peace"*
- Enthusiast: *"Bro, drift karna hai office mein"*
- Generic trust: *"Aapka order safe hai — 7-day Free Replacement"*

### Festival landing-page variants (ship 3 by Q1)
1. Children's Day (Nov 14) — `/rc/childrens-day`
2. Diwali — `/rc/diwali-gift`
3. Karwa Chauth — `/rc/karwa-chauth-gift`

(Same component tree, hero copy + assets swapped.)

---

## §8 — IMAGE & ASSET CHECKLIST

| Asset | Spec | Status |
|-------|------|--------|
| Hero loop video (mobile 9:16, desktop 16:9) | HLS .m3u8 + MP4 H.264 1080p, ≤280 KB initial segment, 10-12s loop | TODO — shoot at BCH Bangalore basement |
| 3 SKU hero shots (white-bg studio) | 1500×1500 WebP q90, transparent variant for PNG | TODO — studio shoot, all 3 scales |
| 3 SKU flat-lay (all components laid out) | 1500×1200 WebP q90 | TODO — studio shoot |
| 3 SKU lifestyle shots (in-use) | 1500×1500 WebP q85, kid + adult versions | TODO — UGC + studio |
| 3 SKU scale-vs-hand shots | 1500×1500 WebP q85 | TODO |
| Demo drift loop (full-width section) | 1080p MP4 H.264, 15-25s, looped, muted | TODO |
| OG image (social share unfurl) | 1200×630 PNG, gift-box hero shot | TODO |
| Favicon | 32×32 ICO + 192/512 PNG | TODO |
| 4 USP icons (custom SVG, brand-red) | Inline SVG | TODO — designer |
| Payment-method icon row | SVG sprite | Source from Razorpay docs |
| UGC seed grid (12 reels) | Embedded IG reel oEmbed | Compile from existing 8-account network |
| Review seed photos (30 reviews) | 800×800 buyer photo + 100-150 word quote | TODO — soft-launch to 50 friends/family first |

---

## §9 — LAUNCH CHECKLIST (10-day countdown)

| Day | Build | Marketing |
|-----|-------|-----------|
| **−10** | Lock 3 character names · Confirm supplier samples · Finalise SKU prices | Brief content team on hero shoot |
| **−9** | Studio shoot — 3 SKU hero + flat-lay + lifestyle + scale-vs-hand | — |
| **−8** | Shoot drift demo loop + 15s reels per audience block | — |
| **−7** | Build Next.js scaffold · components 4.1–4.5 · Razorpay/GoKwik integration | Soft-launch link to 50 friends/family at 50% off |
| **−6** | Components 4.6–4.10 · Judge.me + Interakt + WhatsApp Business setup | Collect 30 seed reviews + 12 UGC reels |
| **−5** | Components 4.11–4.15 · sticky CTA + WhatsApp FAB · footer · meta pixel | — |
| **−4** | Wholesale flow (`/wholesale/register`, `/login`, `/catalog`) | Brief retailer outreach for 10 pre-launch wholesale leads |
| **−3** | Performance pass: LCP < 2.5s · image optimisation · lazy load · CAPI | Schedule Day-0 reel drops across the 8-account network |
| **−2** | QA on real devices: iOS / Android / mobile data · COD flow · UPI flow | Pre-warm IG comments — last 24 hr of "Coming soon" content |
| **−1** | Final smoke test · soft-traffic from one micro-creator (₹1,000 budget) · monitor LCP / RTO / cart-completion | Comment-to-buy DM automation tested live |
| **DAY 0** | Launch | Full IG reel barrage + Manychat DMs live + first paid Meta ads at ₹1,500/day |

---

## §10 — POST-LAUNCH OPTIMISATION PLAN

### Week 1 — Stabilise
- Monitor LCP, RTO, cart-abandonment, conversion-rate hourly for first 72 hrs
- WhatsApp 5-min confirmation must be hitting every COD order
- Pause any reel-creator combo with > 25% RTO
- Boost (₹500–1k) reels that already crossed 50K organic views

### Week 2 — A/B test
- Hero headline variants (default vs gifting vs parent vs enthusiast)
- CTA button colour (brand-red vs green)
- Bundle position (above offer stack vs in SKU cards)
- Trust-strip placement (under hero vs sticky)

### Month 1 — Learn
- Surface top-5 PDP exit points via Microsoft Clarity heatmaps
- Compare cart-completion across COD vs prepaid users
- Identify top 3 viral reels → land their hooks in the hero variant pool
- Begin Amazon Seller Central onboarding for Month-2 launch

### Month 2 — Marketplace launch
- Amazon SKU pages with 600-review target by Month 6 (LOT pattern)
- Flipkart Big Billion Days prep
- Quick-commerce (Blinkit / Zepto) for impulse SKUs

### Month 3 — Retention
- Spare-parts launch (₹99 wheels, ₹149 shell, ₹199 battery, ₹499 expansion track)
- D+30 WhatsApp broadcast to existing buyers with the upsell pack
- Target LTV:CAC = 3:1 by D+60 repeat rate

---

## §11 — OPEN QUESTIONS

### ✅ Closed on 2026-05-23
1. ~~SKU character names~~ → **Storm Mini (1:64) · Storm (1:43, hero) · Storm Pro (1:24)**
2. ~~"Firm number" field~~ → was a slip; meant **firm name** which is already field 5. Wholesale form is **5 fields, not 6.**
3. ~~Checkout provider~~ → **Razorpay Magic** (locked)
4. ~~WhatsApp BSP~~ → **None — direct `wa.me` only.** Re-evaluate at 200 orders/day if manual handling stops scaling.
5. ~~Platform~~ → **Next.js on Vercel** (locked)

### ⏳ Still open
6. **Domain** — Syed to provide. Vercel project will be domain-agnostic until then. Affects SEO + DM payload.
7. **Sample inventory ETA** — when do final supplier samples land in Bangalore? Without these, the studio shoot can't happen and Day −10 in §9 slips.
8. **Soft-launch list** — 50 names for the friends-and-family pre-order at 50% off (yields the 30 seed reviews + 12 UGC reels needed for Day 0).
9. **Bulk pricing ladder** — accept the locked 35 / 45 / 52% off MRP at MOQ 12 / 48 / 144 in §5.5? Or tune.
10. **Payment terms** — accept 100% advance for <₹50K, 50-50 for ₹50K–2L, no Net-30 Day-1 in §5.6? Confirm.
11. **MRP values** — brief uses ₹1,499 / ₹2,499 / ₹2,999 as anchor MRPs. Confirm or tune. Affects all wholesale-tier math in §5.5.

---

*Compiled from RC_CONVERSION_INTELLIGENCE_BRIEF.md + 7 parallel research agents + 27-site competitor scrape. Ready for engineering / no-code build on Next.js + Vercel.*
