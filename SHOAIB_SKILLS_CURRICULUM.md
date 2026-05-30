# Shoaib — Skills Curriculum to Match (and Beat) Syed

**Purpose:** A reverse-engineered skill ladder for Shoaib to reach Syed's current operating level with Claude + BCH, then surpass it.
**Built from:** Audit of `~/Desktop/SOURCING_HQ/`, 5 production apps (bike-inventory, bch-kb-app, bch-sales-training, bch-youtube-engine, 2xg-earn-crm), and Syed's prompting style observed in-conversation.
**Owner:** Syed
**Date:** 2026-05-29

---

## START HERE — The 30-Day Plan

| Week | Focus | Output Shoaib Submits |
|---|---|---|
| 1 | Layer 4 (Prompting) + Layer 3 setup (API keys, Claude Code, git) | Working Claude Code with 5 sample prompts run + 1 API call to Anthropic + 1 to Zoho |
| 2 | Layer 2 (Research methodology) | A tiered supply doc for ONE new category (not RC) following [HOBBY_GRADE_SUPPLY_ONLY.md](HOBBY_GRADE_SUPPLY_ONLY.md) format |
| 3 | Layer 1 (Operating system) | Build Spec + Operating Terms + INDEX for that same category, mirroring [BCH_RC_BUILD_SPEC.md](BCH_RC_BUILD_SPEC.md) and [PANDAY_OPERATING_TERMS_V1.md](LANDING_PAGE/PANDAY_OPERATING_TERMS_V1.md) |
| 4 | Synthesis + Beyond | Pick ONE skill Syed does NOT do well yet and out-execute him on it |

**Rule:** Shoaib does NOT skip layers. Layer 4 first because it amplifies everything below.

---

## Skill Map — At a Glance

| # | Skill | Layer | Evidence File | Drill |
|---|---|---|---|---|
| 1 | Prompt with context-first structure | Prompting | This conversation | Rewrite 10 of Syed's prompts in his style |
| 2 | Demand a proposal before execution | Prompting | This conversation | Catch yourself saying "just do it" — replace with "tell me how" |
| 3 | Define output format upfront | Prompting | This conversation | Every prompt names a format |
| 4 | Use example-anchoring | Prompting | This conversation | Every abstract ask gets one concrete example |
| 5 | Manage API keys + secrets | Tech | `.env` files across all apps | Set up Zoho OAuth + Anthropic key from scratch |
| 6 | Use Claude Code as your IDE | Tech | [~/.claude/settings.json](~/.claude/settings.json) | Configure permissions, hooks, allowlist |
| 7 | Chain APIs (Zoho + Claude + YouTube + vidIQ) | Tech | [bch-youtube-engine](../bch-youtube-engine/) | Build a 2-API composed feature |
| 8 | Read a Prisma schema + run migrations | Tech | [bike-inventory/prisma](../bike-inventory/prisma/) | Schema-walk, then add one field end-to-end |
| 9 | Tier suppliers (A/B/C) before any outreach | Research | [HOBBY_GRADE_SUPPLY_ONLY.md](HOBBY_GRADE_SUPPLY_ONLY.md) | Tier a new category in <2 days |
| 10 | Dedupe + score call lists | Research | [RC_INDIA_EXECUTABLE_CALL_SHEET.md](RC_INDIA_EXECUTABLE_CALL_SHEET.md) | Take 500 contacts → score → top-50 list |
| 11 | One deep competitor > ten shallow | Research | [RC_RESEARCH/RC_CARS_LEGEND_OF_TOYS_DEEPDIVE.md](RC_RESEARCH/RC_CARS_LEGEND_OF_TOYS_DEEPDIVE.md) | Pick ONE competitor, map full playbook |
| 12 | Ground-truth validate before scaling | Research | `project_noida_toy_city_validation` memory | Find one "paper" claim, kill it |
| 13 | USB Rule — feature/price/story/content | Operating | [INDEX.md](INDEX.md) | Run USB on 20 SKUs, kill the ones without ≥1 |
| 14 | Positioning Arbitrage as a thesis | Operating | [OTHER_CATEGORIES/POSITIONING_ARBITRAGE_MASTER_RESEARCH.md](OTHER_CATEGORIES/POSITIONING_ARBITRAGE_MASTER_RESEARCH.md) | Find 5 new arbitrage candidates in different categories |
| 15 | Operating terms over equity for partners | Operating | [LANDING_PAGE/PANDAY_OPERATING_TERMS_V1.md](LANDING_PAGE/PANDAY_OPERATING_TERMS_V1.md) | Draft terms for a hypothetical vendor partnership |
| 16 | Build spec as 15-section checklist with acceptance criteria | Operating | [BCH_RC_BUILD_SPEC.md](BCH_RC_BUILD_SPEC.md) | Write a spec for any next project |
| 17 | INDEX-first folder hygiene | Operating | [INDEX.md](INDEX.md) | Reorganize one messy folder around an INDEX |
| 18 | Living plan, not scattered files | Operating | [EXECUTION/](EXECUTION/) | Maintain ONE 30-day plan, no new files |

---

## Layer 4 — Prompting & Communication (Start here)

Syed prompts in a recognizable shape. Match the shape and Claude gives you what Syed gets.

### Skill 1 — Context-first prompting
**What it is:** Open with WHY before WHAT. Tell Claude the business situation, the stakes, the constraint — before asking for output.
**Evidence:** In this very conversation, Syed opened with "I am getting Shoaib as my partner. I want him to have these skills." That single sentence reframed the entire task.
**Drill for Shoaib:** Take 10 of his own past one-line questions. Rewrite each in Syed's style: 2-3 sentences of context, then the ask.
**Success signal:** Claude stops asking clarifying questions.

### Skill 2 — Demand a proposal before execution
**What it is:** For non-trivial tasks, ask "tell me how we should proceed" before "do it."
**Evidence:** Syed's exact words in this thread.
**Why it matters:** Claude will charge ahead and produce bloat if you don't slow it down. The proposal step costs 30 seconds and saves an hour of re-work.
**Drill:** For one week, NEVER say "do X." Always say "tell me how you'd approach X."
**Success signal:** Fewer redo cycles. Claude's first attempt is 80% correct, not 40%.

### Skill 3 — Define output format upfront
**What it is:** Name the format: "make a list", "create a table", "write a markdown file under X/", "give me 3 sentences max."
**Evidence:** Syed wrote "create a list... that I can share with Shoaib." Format + recipient stated.
**Drill:** Every prompt names a format and a length.
**Success signal:** Outputs are usable as-is, not raw material.

### Skill 4 — Example-anchoring
**What it is:** When the request is abstract, give one concrete example so Claude knows what counts.
**Evidence:** Syed wrote "One skill you need to mention is to understand API keys. This is also a skill, so this is one example of a skill." That single anchor told me the granularity he wanted.
**Drill:** Every abstract prompt gets one concrete example.
**Success signal:** Output granularity matches expectation on the first try.

### What Syed does NOT do (yet) — Shoaib's chance to surpass:
- **Use saved skills/sub-agents systematically.** Syed has Claude Code installed but mostly prompts ad-hoc. Shoaib can master the `Skill` and `Agent` tools, sub-agents, MCP servers, and custom hooks to leapfrog.

---

## Layer 3 — Claude + Technical Literacy (the API-keys layer)

This is the layer Syed called out by name. It is the highest-ROI technical investment because almost no founder in BCH's segment has it.

### Skill 5 — Manage API keys + secrets
**What it is:** Know what an API key is, where it lives (`.env`), how to rotate it, why you NEVER commit it.
**Evidence:** Syed runs 5 apps with separate `.env` files holding `ANTHROPIC_API_KEY`, `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `GOOGLE_API_KEY`, Supabase tokens, etc.
**Drill:**
1. Create accounts at: Anthropic Console, Zoho Developer Console, Google Cloud Console, Supabase, vidIQ.
2. Generate keys for each.
3. Make a personal `.env` file. Add to `.gitignore`. Never commit.
4. Make ONE successful API call to each service using `curl` from terminal.
**Success signal:** Can debug an "invalid API key" error in <5 minutes without asking.

### Skill 6 — Use Claude Code as your IDE
**What it is:** Treat Claude Code as your primary development surface — not VS Code with Claude on the side.
**Evidence:** Syed's settings.json has 150+ permission allowlists, custom `SessionStart` hooks, and tracked directories spanning every app. He uses it for git, npm, prisma, curl, python — everything.
**Drill:**
1. Install Claude Code CLI + extension.
2. Configure permissions for `npm`, `git`, `npx`, `prisma` (use `/fewer-permission-prompts`).
3. Set up a custom skill or slash command of your own.
4. Run a real task (deploy a Next.js app, run a migration) ONLY through Claude Code.
**Success signal:** You don't open a terminal manually for a week.

### Skill 7 — Chain APIs (API composition)
**What it is:** The skill of stitching Zoho + Claude + YouTube + vidIQ into ONE feature that does something none of them do alone.
**Evidence:** [bch-youtube-engine](../bch-youtube-engine/) calls YouTube API for video data → vidIQ for keyword scores → Claude for title generation → stores in Postgres.
**Drill:** Build a 2-API feature. Suggestion: pull a Zoho contact → ask Claude to draft a follow-up message → save to file. <100 lines of code.
**Success signal:** Working endpoint that calls 2+ external APIs and produces useful output.

### Skill 8 — Read a Prisma schema and run migrations
**What it is:** Understand database schemas as code, run migrations safely, add fields without breaking things.
**Evidence:** All 5 production apps use Prisma. [bike-inventory/prisma/schema.prisma](../bike-inventory/prisma/schema.prisma) defines the inventory data model.
**Drill:**
1. Read the bike-inventory schema end to end. Explain every model in plain English.
2. Add a new field to one model. Run `prisma migrate dev`. Use it in code.
3. Roll it back.
**Success signal:** Comfortable opening any `.prisma` file and changing the data model.

### What Syed does NOT do (yet):
- **Test coverage.** None of the apps have meaningful tests. Shoaib can introduce Vitest + Playwright and become the QA leverage point.
- **Observability.** No structured logging, no error tracking (Sentry). Shoaib can own this.

---

## Layer 2 — Research Methodology

How Syed investigates a market without wasting calls or money.

### Skill 9 — Tier suppliers (A/B/C) before any outreach
**What it is:** Map the supply chain by role first. Gatekeepers (Tier A) unlock everyone downstream. Don't call 800 retailers — penetrate ONE distributor.
**Evidence:** [HOBBY_GRADE_SUPPLY_ONLY.md](HOBBY_GRADE_SUPPLY_ONLY.md) explicitly excludes retailers because "they buy FROM these 6 gatekeepers."
**Drill:** Pick any new category (e.g., kids' helmets, ergonomic chairs, scooters). Map A/B/C tiers in 2 days. <12 entities total.
**Success signal:** Can name the 3-5 gatekeepers for any category in <48 hours of research.

### Skill 10 — Dedupe + score call lists
**What it is:** Never call from a raw scraped list. Dedupe by phone/business name, score 2-9 by verification confidence, call Phase 1 (highest) first.
**Evidence:** [RC_INDIA_EXECUTABLE_CALL_SHEET.md](RC_INDIA_EXECUTABLE_CALL_SHEET.md) — 832 → 700+ scored entities with phased outreach.
**Drill:** Take any 500-row list (Justdial scrape, your own, whatever). Dedupe → score → produce top-50 Phase-1 list with single-sentence rationale per row.
**Success signal:** Call-to-meeting rate ≥15%.

### Skill 11 — One deep competitor > ten shallow
**What it is:** Pick THE competitor most worth understanding. Map them end-to-end (legal entity, founders, GST, SKUs, reviews, YouTube partner, Instagram metrics, why they're winning). Then write "Why this is OUR #1 opportunity."
**Evidence:** [RC_RESEARCH/RC_CARS_LEGEND_OF_TOYS_DEEPDIVE.md](RC_RESEARCH/RC_CARS_LEGEND_OF_TOYS_DEEPDIVE.md).
**Drill:** Pick one BCH competitor (Decathlon Bikes? Hero Lectro? Btwin?). Do a full deepdive in this format.
**Success signal:** You can predict their next 3 moves.

### Skill 12 — Ground-truth validate before scaling
**What it is:** When sources say "X exists" — go check. Trust paper claims at <30%.
**Evidence:** Syed's [memory](../../.claude/projects/-Users-syedibrahim-Desktop-SOURCING-HQ/memory/) on Noida Toy City: "YEIDA Sector 33 is paper, not operational." He killed a whole research thread by validating.
**Drill:** In your week-2 category, find ONE official/press claim that is widely repeated. Kill it or confirm it.
**Success signal:** You stop trusting press releases.

---

## Layer 1 — Operating System

How Syed structures the business. Slowest to learn, highest long-term leverage.

### Skill 13 — The USB Rule
**What it is:** Every SKU must have at least ONE of: Feature USB / Price USB / Story USB / Content USB. Without one, kill it.
**Evidence:** [INDEX.md](INDEX.md) — pocket bike example: folds (Feature) + imported (Story) + ride in-store (Content) = 25-30 units/month.
**Drill:** Take any 20 SKUs from BCH's catalog. Apply USB. Recommend which 5 to delist.
**Success signal:** Syed agrees with your delist list.

### Skill 14 — Positioning Arbitrage thesis
**What it is:** "₹65 sunglass in Surat becomes ₹1,000 in a glass display case." Map city wholesale markets → price multiples → channel fit.
**Evidence:** [OTHER_CATEGORIES/POSITIONING_ARBITRAGE_MASTER_RESEARCH.md](OTHER_CATEGORIES/POSITIONING_ARBITRAGE_MASTER_RESEARCH.md).
**Drill:** Find 5 new arbitrage candidates outside BCH's current categories. Each with: source city, source price, retail price, multiple, channel (Physical/D2C/Both).
**Success signal:** Syed funds one for a test buy.

### Skill 15 — Operating terms over equity for partners
**What it is:** When bringing in a delivery partner, vendor, contractor — write a sectioned operating terms doc. Scope, base pay, bonus triggers, ownership, termination clause. Not equity. Not vibes.
**Evidence:** [LANDING_PAGE/PANDAY_OPERATING_TERMS_V1.md](LANDING_PAGE/PANDAY_OPERATING_TERMS_V1.md) — 12 sections.
**Drill:** Draft operating terms for a hypothetical: "agency builds 3 landing pages over 6 weeks." Use the Panday template.
**Success signal:** Doc is signable as-is.

### Skill 16 — Build specs as 15-section checklists with acceptance criteria
**What it is:** No code starts without a spec. Spec has acceptance criteria (mobile LCP ≤2.5s, test transaction passes, handoff docs delivered).
**Evidence:** [BCH_RC_BUILD_SPEC.md](BCH_RC_BUILD_SPEC.md).
**Drill:** Write a build spec for any next project. Must have ≥10 sections and explicit acceptance criteria.
**Success signal:** A developer could quote a price from your spec alone.

### Skill 17 — INDEX-first folder hygiene
**What it is:** Every working folder gets a `START HERE` `INDEX.md` that routes to sub-files. No archaeology needed.
**Evidence:** [INDEX.md](INDEX.md).
**Drill:** Reorganize one of your existing messy folders around an INDEX.
**Success signal:** A new collaborator finds what they need in <60 seconds.

### Skill 18 — Living plan, not scattered files
**What it is:** ONE file holds Active / Backlog / Done. Moving a task to Done IS the log.
**Evidence:** [ARCHIVE/RC_30DAY_TO_10L_LIVING_PLAN.md](EXECUTION/).
**Drill:** Maintain a living plan for your Week 2-4 onboarding work. No new task files.
**Success signal:** You can answer "what's the status of X?" in <5 seconds.

---

## Common Traps Shoaib Should Avoid

1. **Trying to learn React/Next.js/TypeScript first.** Don't. Claude writes the code. You direct it. Skill 5 (API keys) and Skill 6 (Claude Code) matter more than knowing JSX.
2. **Building before researching.** Layer 2 (Research) precedes Layer 1 (Operating). A great spec for a bad category is wasted.
3. **Equity conversations before operating terms exist.** Always write the terms doc first. Equity follows execution, not promises.
4. **Treating Claude as a search engine.** It's a collaborator. Skills 1-4 are the difference.
5. **Skipping ground-truth validation.** Syed kept Noida Toy City out of the plan because he validated. Don't pitch projects on press releases.

---

## Where to Beat Syed

Once Shoaib has all 18 skills, here are the seams where he can surpass:

| Gap | Why it matters | How to win |
|---|---|---|
| Test coverage | All apps are untested. One bug in `bike-inventory` could lose a day of sales. | Introduce Vitest + Playwright. Own QA. |
| Observability | No Sentry, no structured logs, no uptime monitoring. | Wire up Sentry + a status page. |
| Sub-agents + MCP servers | Syed prompts ad-hoc. Shoaib can systematize. | Build 3 custom Claude Code skills + 1 MCP server. |
| Documentation discipline | INDEX exists for RC. Other folders are messier. | Apply INDEX hygiene to 3 other folders. |
| Customer-side research | Syed is supply-side strong. Customer interviews are thinner. | Run 20 customer interviews in Month 2. |

---

## How Syed and Shoaib Should Work Through This

1. **Weekly 60-min review:** Shoaib presents the week's drill output. Syed grades 1-10.
2. **Pair on ONE real task per week:** Shoaib drives Claude Code, Syed observes silently. Debrief afterwards.
3. **No solo deployments in first 30 days.** Every git push is reviewed.
4. **By day 30, Shoaib owns ONE category end-to-end** — research, spec, vendor terms, INDEX, living plan.

---

**Next action for Syed:** Decide which category Shoaib will own in Week 2-4 (NOT RC — Syed owns that). Suggested options: kids' helmets, fitness accessories, scooters, ergonomic seating. Pick one and seed the empty `SOURCING_HQ/<CATEGORY>/INDEX.md` for him.
