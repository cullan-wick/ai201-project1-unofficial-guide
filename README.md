# The Unofficial Guide — Project 1

A retrieval-augmented guide to the UW–Madison startup ecosystem: crawl siloed
campus + community resources, embed them locally, and answer founder questions
grounded strictly in the retrieved sources.

---

## Domain

**The UW–Madison startup ecosystem — bridging university policy and student practice.**

Resources for student founders are scattered across university offices, legal
clinics, makerspaces, student orgs, accelerators, and off-campus community
spaces. Each publishes its own page, and there is no single place that connects
institutional policy (WARF IP rules, Weinert programs, the Law &
Entrepreneurship Clinic) to the practical "where do I actually go" knowledge a
founder needs. This system consolidates 21 of those sources (plus a founder
podcast transcript) into one queryable, source-attributed guide — useful
precisely because the knowledge is real, authoritative, and otherwise siloed.

---

## Document Sources

21 web/PDF sources were ingested (Reddit was evaluated and excluded — see Failure
Case Analysis), plus one manually collected podcast transcript. Each web source
is **crawled multi-page** (not just its landing page): starting from the seed
URL, the crawler follows in-scope links up to **depth 3 / 50 pages per source**,
staying on the same host and under the seed's path (WARF widened to its whole
host). All pages of a source are concatenated into one document, each delimited
by a `## [page] <url>` header so the exact page stays attributable.

| #   | Source | Type | URL |
| --- | ------ | ---- | --- |
| 1 | Wisconsin Entrepreneurship Hub | Web (crawled) | https://entrepreneurship.wisc.edu/ |
| 2 | Empowering the Wisconsin Idea (Eckhardt Report) | PDF | https://news.wisc.edu/content/uploads/2024/09/EmpoweringtheWisconsinIdea-Report-Final4-Accessible-3.pdf |
| 3 | Tech Entrepreneurship Office | Web (crawled) | https://teo.wisc.edu/ |
| 4 | Entrepreneurship Science Lab | Web (crawled) | https://eslab.wisc.edu/ |
| 5 | WARF — Starting a Company | Web (crawled, whole host) | https://www.warf.org/commercialize/starting-a-company/ |
| 6 | Weinert Center for Entrepreneurship | Web (crawled) | https://business.wisc.edu/centers/weinert/ |
| 7 | Law & Entrepreneurship Clinic — Services | Web (crawled) | https://law.wisc.edu/uwle/services/ |
| 8 | SBDC UW–Madison | Web (crawled) | https://sbdc.wisc.edu/ |
| 9 | Tech Exploration Lab | Web (crawled) | https://techexplorationlab.wisc.edu/ |
| 10 | Grainger Engineering Design Innovation Lab | Web (crawled) | https://making.engr.wisc.edu/ |
| 11 | Startup Learning Community | Web (crawled) | https://www.housing.wisc.edu/undergraduate/communities/startup/ |
| 12 | TranscendUW | Web (crawled, SPA/Playwright) | https://www.transcenduw.com/ |
| 13 | Women in Entrepreneurship UW–Madison | Web (crawled, SPA) | https://womeninentrepreneurship-uw.vercel.app/ |
| 14 | Badger Future Founders | Web (crawled, SPA/Playwright) | https://www.badgerfuturefounders.com/ |
| 15 | StratoVC | Web (crawled, SPA) | https://stratovc.com/ |
| 16 | BadgerVC | Web (crawled) | https://www.badgervc.com/ |
| 17 | StartingBlock Madison | Web (crawled) | https://www.startingblockmadison.org/ |
| 18 | Sector67 | Web (crawled) | https://www.sector67.org/blog/ |
| 19 | Capital Entrepreneurs | Web (crawled) | https://capitalentrepreneurs.com/ |
| 20 | 100state | Web (crawled) | https://100state.com/ |
| 21 | Gener8tor gBETA Madison | Web (crawled) | https://www.gener8tor.com/gbeta/frontier-technology-accelerator |
| 22 | Jon Eckhardt — Startup Wisconsin (podcast transcript) | Transcript (manual) | local file |

**Result:** 22 documents, **260,627 words**. Crawl yields ranged widely —
WARF, TEO, SBDC, Tech Exploration Lab, Grainger, BadgerVC, StartingBlock, and
100state hit the 50-page cap, while Weinert, Sector67, Gener8tor, the Startup
Learning Community, and Badger Future Founders returned a single in-scope page
(their sub-pages aren't linked under the seed's path).

Ingestion uses `requests` + BeautifulSoup for static pages (converted to
markdown via `markdownify`, with nav/header/footer stripped), `pdfplumber` for
PDFs (both the registered report and any PDFs discovered mid-crawl), and a
Playwright headless-browser fallback that fires per page when a static fetch
returns too little text (recovering JavaScript-rendered SPA pages). The crawler
honors `robots.txt` and skips asset files and common crawler traps.

---

## Chunking Strategy

**Chunk size:** ~2,000 characters (≈ 512 tokens)

**Overlap:** 300 characters (≈ 15%)

**Why these choices fit your documents:**
A single **markdown-aware recursive splitter** is used for the whole corpus. It
splits in priority order — markdown headers → paragraphs → sentences → words —
greedily packing structural blocks up to the target size and never cutting a
word in half. The corpus mixes short pages with long crawled documents and one
16k-word report, so a structure-aware splitter keeps small sections intact while
cleanly segmenting long material. The ~512-token target sits comfortably inside
bge-m3's 8,192-token ceiling, and the 15% overlap preserves context across
boundaries. Sizes are measured in characters as a cheap, deterministic proxy for
tokens (English ≈ 4 chars/token), avoiding a tokenizer dependency at chunk time.

Preprocessing before chunking: HTML stripped of `script`/`nav`/`header`/
`footer`/`aside` and converted to markdown; PDFs extracted page-by-page; each
document stored with YAML frontmatter (source, url, type, category) that is
copied onto every chunk for source attribution.

**Final chunk count:** **1,158 chunks** across 22 documents (up from 136 before
multi-page crawling — an 8.5× increase).

---

## Embedding Model

**Model used:** `BAAI/bge-m3` (1,024-dimensional), run **locally** via
`sentence-transformers` on Apple Silicon (MPS backend). Embeddings are
L2-normalized and stored in a persistent **ChromaDB** collection using cosine
similarity.

Retrieval is **diversity-aware**: it over-fetches a candidate pool of 24, then
keeps the best chunks in similarity order while allowing at most **2 chunks per
source**, filling a final **top-k = 8**. This was added after the multi-page
crawl, because high-page-count sources were otherwise flooding the top-k (see
Failure Case Analysis).

**Production tradeoff reflection:**
If deployed for real users with cost no object, the model choice would weigh:

- **Context length** — bge-m3's 8,192-token window already handles long report
  sections; a larger window would matter more for full-document chunks.
- **Dimensionality / accuracy** — 1,024 dims capture subtle semantic links
  (mapping casual phrasing like "how to split equity" to formal clinic
  documentation). A larger API model could push precision further.
- **Domain tokenization** — campus acronyms (WARF, Weinert, gBETA, Grainger)
  are niche; a model with stronger domain vocabulary (e.g. `voyage-3-large`)
  would relate these entities more reliably.
- **Latency & privacy** — running locally keeps queries on-device and removes
  per-call cost, at the price of a slower cold start (the ~2.2GB model loads
  once). An API model trades that for a smaller local footprint but adds latency
  and per-query cost.

---

## Grounded Generation

Generation uses **`openai/gpt-oss-120b` via the Groq API** (temperature 0).

**System prompt grounding instruction:**
The model is given the retrieved chunks as a numbered, source-labeled context
block and instructed:

> Answer the user's question using ONLY the numbered SOURCES provided.
> - Use only facts found in the SOURCES. Do not add outside knowledge.
> - Cite the source number(s) you used inline, like [1] or [2][3].
> - If the SOURCES do not contain the answer, say exactly: "I don't have
>   information on that in my sources." Do not guess.

This is enforced structurally as well as textually: the user message contains
only `SOURCES:` (the top-8 chunks, each prefixed with `[n] Source: <name> (<url>)`)
followed by the question — the model never sees the full corpus, only the
retrieved context. Temperature 0 keeps answers deterministic.

**How source attribution is surfaced in the response:**
Each context chunk is numbered and labeled with its source name and URL, so the
model's inline `[n]` citations map directly to a real source. The query
interface (`rag/query.py`) also prints the retrieved sources with their cosine
similarity scores, so a user sees exactly what grounded the answer.

---

## Evaluation Report

Run via `python -m rag.evaluate` against the 22-document / 1,158-chunk store with
diversity-aware retrieval.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does WARF claim IP for a dorm-built software MVP on personal devices/Wi-Fi? | No — dorm use isn't "substantial university resources"; student owns the IP. | "I don't have information on that in my sources." | Partially relevant (WARF pages top-ranked) | Inaccurate (honest refusal — rule not in crawled pages) |
| 2 | Eckhardt report's primary ecosystem challenge + recommended action? | Systemic fragmentation across silos; recommends a centralized Wisconsin Entrepreneurship Hub. | "I don't have information on that in my sources." | Off-target (Eckhardt buried at ~rank 30; ESL chunks dominate) | Inaccurate (regressed — retrieval dilution) |
| 3 | Service limits/prerequisites for the Law & Entrepreneurship Clinic's free services? | Intake vetting: can't afford private counsel + economic value to WI. | Detailed and specific: limited to early-stage/"nascent" founders who lack access to counsel and **have not taken significant outside investor funding**; matters must offer **educational value** to law students; **excludes litigation, pure tax, and international law**. [1][2] | Relevant (clinic pages dominate) | Accurate (richer than the expected answer — crawl reached the eligibility sub-pages) |
| 4 | Which course framework qualifies a student for Weinert Venture Fund equity? | The WAVE Practicum (Wisconsin Applied Ventures in Entrepreneurship). | "I don't have information on that in my sources." | Relevant (Weinert page top-ranked) | Inaccurate (honest refusal — Weinert crawled only 1 page; WAVE-equity link absent) |
| 5 | Off-campus Madison alternative for heavy tooling/CNC when Grainger is closed? | Sector67, a non-profit community hackerspace open outside university hours. | "I don't have information on that in my sources." | Off-target (Sector67 buried at ~rank 40; Grainger's 50 pages flood the results) | Inaccurate (regressed — retrieval dilution) |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 1 accurate (Q3), 4 honest refusals. Grounding behaved correctly
throughout — the system **refused rather than hallucinated** whenever the
retrieved context didn't contain the answer. The headline finding is that
**multi-page crawling was a net trade-off, not a pure win**: it gave Q3 the depth
it needed (reaching the clinic's eligibility sub-pages), but the volume it added
*buried* the small high-signal sources that the smaller pre-crawl corpus had
surfaced (Q2, Q5). Q1 and Q4 remained content/reachability gaps that crawling
did not close.

For reference, the **pre-crawl** (136-chunk, one-page-per-source) corpus scored
1 accurate (Q5), 2 partially accurate (Q2, Q3), 2 refusals (Q1, Q4) — so the
crawl traded Q2/Q5 for a much stronger Q3.

---

## Failure Case Analysis

**Question that failed:** Q5 — "What off-campus Madison alternative provides
heavy tooling/CNC machinery when Grainger Engineering Makerspace is closed?"
(Expected: Sector67.)

**What the system returned:** "I don't have information on that in my sources."
(Notably, the pre-crawl corpus answered this **correctly**.)

**Root cause (tied to a specific pipeline stage):** This is a **retrieval-
dilution failure introduced by the ingestion stage**, not a generation failure.
Sector67 was crawled to a single in-scope page, while Grainger, SBDC, and
StartingBlock each crawled to ~50 pages. For the question's phrasing
("...when Grainger makerspace is closed"), those high-volume sources produce many
chunks the embedding model scores as more relevant than Sector67's lone page. We
measured Sector67's best chunk at **rank ~40** in the full store — far below the
top-k. Diversity-aware retrieval (cap of 2 chunks/source, candidate pool of 24)
fixed *flooding* but cannot reach a rank-40 chunk; the answer is simply
out-competed. Q2 (Eckhardt at ~rank 30, out-competed by the 16-page
Entrepreneurship Science Lab crawl) failed the same way.

**What you would change to fix it:** Balance the corpus. A **selective crawl** —
deep only for sources whose answers live on sub-pages (Law Clinic, WARF), and a
single page for high-volume community/maker/VC sites — keeps Q3's gain without
burying Q2/Q5. Alternatively, add a **cross-encoder re-ranker** over a large
candidate pool (e.g. top-100) so a high-signal but lower-cosine chunk can be
promoted. (Q1/Q4 are a different, harder problem: the IP-ownership rule wasn't
reachable within 50 WARF pages, and Weinert's WAVE page isn't linked under its
crawl path — both need targeted source collection, not retrieval tuning.)

---

## Spec Reflection

**One way the spec helped you during implementation:**
The five concrete evaluation questions in `planning.md` were the most valuable
artifact. Because each had a specific expected answer, they turned "is it
working?" into a measurable check — and, critically, they're what *revealed* the
retrieval-dilution regression. Without testable targets, the multi-page crawl
would have looked like an unambiguous improvement (8.5× more content); the eval
showed it actually traded two correct answers for one.

**One way your implementation diverged from the spec, and why:**
The spec called for a four-way *asymmetric* chunking router; after Reddit was
excluded and the live corpus reduced to web pages + a report, a single
markdown-aware recursive splitter covered everything, so the router would have
been complexity without benefit. The larger divergence was adding a **multi-page
crawler** (the spec assumed single-page fetches) to chase the depth that Q1/Q4
needed — and then discovering that aggressive crawling *hurt* retrieval, which
motivated the diversity-aware retriever. The generation model was also set to
`openai/gpt-oss-120b` on Groq rather than the spec's Llama 3.3 70B.

---

## AI Usage

**Instance 1 — Multi-page crawler**

- _What I gave the AI:_ The Anticipated Challenges section of `planning.md`
  (Challenge #2: root pages link out to sub-pages/PDFs a shallow scraper misses)
  and a target of depth 3 / 50 pages, crawling all sources.
- _What it produced:_ A BFS crawler (`ingest/crawler.py`) with same-host + path
  scoping, robots.txt handling, PDF routing, an SPA Playwright fallback, and
  per-source caps, plus a diversity-aware retriever after the crawl flooded the
  top-k.
- _What I changed or overrode:_ I directed keeping the full crawl despite the
  Q2/Q5 regression, choosing to document the dilution trade-off honestly rather
  than dial the crawl back.

**Instance 2 — Source curation (Reddit)**

- _What I gave the AI:_ The source list and the Reddit search URL.
- _What it produced:_ A Reddit fetcher (`.json` endpoints, with a Playwright
  fallback).
- _What I changed or overrode:_ After Reddit hard-blocked automated access
  (403 for both requests and a headless browser) *and* the available threads
  proved low-signal, I directed dropping Reddit entirely rather than forcing
  noisy data into the index — documented in `planning.md`.
