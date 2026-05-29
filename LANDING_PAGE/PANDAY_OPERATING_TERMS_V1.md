# Operating Terms v1 — Pocket RC Cars + 4 Sub-Stores

**Between:** Syed Ibrahim (BCH) and Panday
**Effective:** From the day Panday confirms acceptance
**Doc purpose:** Make every assumption explicit so we don't fight later. Collaborative, not legal.

**Note:** Site 1 launches under standalone brand **"Pocket RC Cars"** (`pocketrccars.com`). Master umbrella brand for the 4 additional sites will be locked by **Day 18**; sub-stores 2-5 will inherit the master brand naming.

---

## 1 · Scope — What you're building

Five (5) standalone e-commerce sites under one master brand, plus one (1) shared admin dashboard.

| # | Site | Status |
|---|------|--------|
| 1 | Pocket RC Cars (`pocketrccars.com`) — RC vehicles | In scope, starts first |
| 2 | TBD category | In scope, brief sent ~Day 20 |
| 3 | TBD category | In scope |
| 4 | TBD category | In scope |
| 5 | TBD category | In scope |
| 6 | Master Admin Dashboard | In scope, single login managing all 5 sites |

**A site is considered "delivered" when ALL of these are true:**
- All sections in the per-site brief built and deployed to production domain
- Mobile LCP ≤ 2.5s on 4G test (Lighthouse mobile score ≥ 85)
- Payment gateway live, one ₹1 test transaction succeeds end-to-end
- Order shows correctly in master dashboard
- README + ENV doc + handoff doc committed to repo
- Syed has signed off via WhatsApp message: "Site X accepted"

---

## 2 · Compensation Structure

### Base pay — paid on site delivery (tiered)

| Sites completed (& accepted) | Base payout |
|------------------------------|-------------|
| 1 site delivered | ₹5,000 |
| 2 sites delivered | ₹10,000 |
| 3 sites delivered | ₹15,000 |
| 4 sites delivered | ₹17,500 |
| 5 sites delivered + master dashboard | ₹20,000 |

Base is paid on the **5th of the month following site delivery and acceptance.**

### Per-sale bonus — paid on hitting category targets

| Category | Per-unit bonus | Trigger |
|----------|----------------|---------|
| RC Cars | ₹10/unit | First 1,000 dispatched units (net of RTO/returns) inside any rolling 30-day window |
| Categories 2-5 | TBD per category, **agreed in writing BEFORE that site's development starts** | Same model — 1,000 dispatched units in a 30-day window |

**"Dispatched" means:** order placed → payment confirmed (prepaid) OR COD-OTP-verified → shipment label generated. Returns/RTOs that happen later do NOT claw back the bonus.

**Combo definition for the "3-units combo of 12 sales/day" math:** A single order containing 3 or more units (any SKU mix, same cart) counts as 3 units toward the 1,000 threshold.

**After hitting 1,000:** payout resets — next 1,000 units triggers next ₹10K. No cap.

### Optional retainer — after at least 3 sites are live

₹10,000/month maintenance retainer kicks in once 3 sites are live AND making sales (≥ 50 orders/month combined). Covers:
- Bugfixes
- Minor content updates
- Performance monitoring
- Up to 10 hours/month

Beyond 10 hours/month = ₹500/hour, pre-approved by Syed.

---

## 3 · Ownership

| Asset | Owned by |
|-------|----------|
| All domains | Syed (registrar account in Syed's email) |
| Razorpay / Shiprocket / Judge.me / GSTZen / Cloudflare / Vercel / Postgres / Meta Business / GA4 / Search Console accounts | Syed |
| GitHub repository | Syed's organization, Panday gets collaborator access |
| Source code & IP | Syed, 100%, including any AI-generated code |
| All product images, copy, brand assets | Syed |
| Master dashboard credentials | Syed (Panday admin during build, transferred at handoff) |

Panday must NOT register any account, domain, or service in his own name for the project. If accidentally done, transfer to Syed within 48 hours.

---

## 4 · Tech Stack (locked)

| Layer | Choice |
|-------|--------|
| Framework | Next.js 14+ / React / TypeScript |
| Styling | Tailwind + shadcn/ui |
| Hosting | Vercel (each site = separate Vercel project under shared org) |
| Database | Vercel Postgres / Neon (single multi-tenant DB shared across all 5 sites) |
| Auth (admin dashboard) | NextAuth with mobile OTP via MSG91 |
| Payments | Razorpay Magic Checkout — UPI Intent + COD with SMS OTP |
| Logistics | Shiprocket API |
| Reviews | Judge.me embed (free tier) |
| Analytics | Meta Pixel + GA4 + Microsoft Clarity (per site) |
| Email/SMS | MSG91 (transactional) |
| Image storage | Vercel Blob or Cloudinary free tier |
| Repo structure | Single monorepo or per-site repos — Panday's call, must be documented |

No Shopify, no WordPress, no Wix. Custom Next.js so we own everything.

---

## 5 · Image enhancement & SEO scope

| Item | What's included |
|------|------------------|
| Image enhancement | Background removal + color correction + WebP conversion for product hero shots. Cap: 50 images per site. AI tools (e.g. removebg, Photoroom) acceptable. No manual retouching beyond 50 images. |
| Technical SEO | Sitemap.xml, robots.txt, structured data (Product schema), canonical tags, OG tags, page speed optimization |
| On-page SEO | Title tags, meta descriptions, H1/H2 structure per Syed-supplied copy |
| Off-page SEO / backlinks / content marketing | NOT included — separate engagement |

---

## 6 · Communication & Approval

- All project communication via Syed only (WhatsApp + this repo)
- No 3rd party (vendors, agencies, other team members) talks to Panday without Syed in loop
- Daily 1-line WhatsApp update during active build days
- Weekly 30-min video call (proposed: Sunday evening)
- All scope changes / new features require Syed's WhatsApp written approval before coding begins
- Per-sale bonus rates for new categories must be agreed in writing before development starts on that site

---

## 7 · Timeline (proposed, lock in conversation)

| Phase | Days | Output |
|-------|------|--------|
| Site 1 — Pocket RC Cars | 1-20 | Full e-comm live on `pocketrccars.com` + base dashboard hookup |
| Site 2 brief from Syed | Day 18-20 | Category, SKUs, references shared |
| Site 2 build | Days 21-32 | Live |
| Sites 3, 4, 5 brief + build | Days 33-75 | Live |
| Master Dashboard polish | Days 60-75 | Multi-site admin complete |

Total estimated: 75 calendar days from kickoff to all 5 sites + dashboard. Adjust based on actual asset delivery from Syed.

---

## 8 · Termination & Handover

- Either side can exit with **7 days notice** at any time
- If Panday exits: he hands over all code, accounts access, and docs within 7 days. Base pay for completed sites paid out. No per-sale bonus on unfinished sites.
- If Syed exits: pays out base for completed sites + accrued per-sale up to that date.
- If Panday fails to deliver Site 1 by Day 30 (10-day grace from Day 20 target): Syed may terminate without payment.

---

## 9 · Confidentiality

- All briefs, data, vendor contacts, sales figures, and dashboard data are confidential
- Panday will not use BCH/Pocket/Mast code, designs, or strategy for any other client
- Panday MAY add the work to his portfolio post-launch with Syed's written permission

---

## 10 · Tools provided by Syed to Panday

- Claude Pro / Claude Code access (one seat, Syed's account or new account — to be decided)
- All paid API keys for the project (Razorpay, MSG91, GSTZen, etc.)
- Figma access if design files are created
- Access to product samples for photography (for Site 1)

---

## 11 · What's NOT included (out of scope for this engagement)

- Content writing (copy supplied by Syed per site)
- Photography / videography (raw assets supplied by Syed)
- Off-page SEO, backlinks, content marketing
- Paid ad campaign setup (Meta Ads / Google Ads management)
- Influencer outreach / UGC sourcing
- Customer support / order ops
- New feature requests not in the per-site brief (separately quoted)

---

## 12 · Acceptance & sign-off

By replying "Accepted" on WhatsApp, both Syed and Panday agree these terms apply to the engagement.

Any changes require a new dated version of this doc.

---

*Drafted 2026-05-29 · v1 · Subject to one round of edits before sign-off*
