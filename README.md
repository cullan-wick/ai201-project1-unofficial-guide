# The Unofficial Guide — Project 1

A retrieval-augmented guide to the UW-Madison startup ecosystem. It crawls siloed
campus and community resources, embeds them locally, and answers founder
questions using only the retrieved sources.

---

## Domain

The UW-Madison startup ecosystem, and how university policy connects to what
students actually do.

Resources for student founders are spread across university offices, legal
clinics, makerspaces, student orgs, accelerators, and off-campus coworking
spaces. Each one runs its own website, and nothing ties the institutional side
(WARF IP rules, Weinert programs, the Law & Entrepreneurship Clinic) to the
practical "where do I actually go" question a student has. This system pulls 21
of those sources (plus one founder podcast transcript) into a single guide you
can query, with the source of every answer shown. The knowledge is real and
authoritative; it's just scattered.

---

## Document Sources

21 web/PDF sources were ingested plus one manually collected podcast transcript.
Reddit was evaluated and dropped (see Failure Case Analysis). Each web source is
crawled across multiple pages. From the origin URL the crawler follows in-scope
links up to a depth of 3 and a cap of 50 pages per source, staying on the same host
and under the origin URL's path. WARF is widened to its whole host. All pages of
a source are concatenated into one document, each delimited by a `## [page] <url>`
header so the exact page is still traceable.

| #   | Source                                          | Type                          | URL                                                                                                     |
| --- | ----------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1   | Wisconsin Entrepreneurship Hub                  | Web (crawled)                 | https://entrepreneurship.wisc.edu/                                                                      |
| 2   | Empowering the Wisconsin Idea (Eckhardt Report) | PDF                           | https://news.wisc.edu/content/uploads/2024/09/EmpoweringtheWisconsinIdea-Report-Final4-Accessible-3.pdf |
| 3   | Tech Entrepreneurship Office                    | Web (crawled)                 | https://teo.wisc.edu/                                                                                   |
| 4   | Entrepreneurship Science Lab                    | Web (crawled)                 | https://eslab.wisc.edu/                                                                                 |
| 5   | WARF - Starting a Company                       | Web (crawled, whole host)     | https://www.warf.org/commercialize/starting-a-company/                                                  |
| 6   | Weinert Center for Entrepreneurship             | Web (crawled)                 | https://business.wisc.edu/centers/weinert/                                                              |
| 7   | Law & Entrepreneurship Clinic - Services        | Web (crawled)                 | https://law.wisc.edu/uwle/services/                                                                     |
| 8   | SBDC UW-Madison                                 | Web (crawled)                 | https://sbdc.wisc.edu/                                                                                  |
| 9   | Tech Exploration Lab                            | Web (crawled)                 | https://techexplorationlab.wisc.edu/                                                                    |
| 10  | Grainger Engineering Design Innovation Lab      | Web (crawled)                 | https://making.engr.wisc.edu/                                                                           |
| 11  | Startup Learning Community                      | Web (crawled)                 | https://www.housing.wisc.edu/undergraduate/communities/startup/                                         |
| 12  | TranscendUW                                     | Web (crawled, SPA/Playwright) | https://www.transcenduw.com/                                                                            |
| 13  | Women in Entrepreneurship UW-Madison            | Web (crawled, SPA)            | https://womeninentrepreneurship-uw.vercel.app/                                                          |
| 14  | Badger Future Founders                          | Web (crawled, SPA/Playwright) | https://www.badgerfuturefounders.com/                                                                   |
| 15  | StratoVC                                        | Web (crawled, SPA)            | https://stratovc.com/                                                                                   |
| 16  | BadgerVC                                        | Web (crawled)                 | https://www.badgervc.com/                                                                               |
| 17  | StartingBlock Madison                           | Web (crawled)                 | https://www.startingblockmadison.org/                                                                   |
| 18  | Sector67                                        | Web (crawled)                 | https://www.sector67.org/blog/                                                                          |
| 19  | Capital Entrepreneurs                           | Web (crawled)                 | https://capitalentrepreneurs.com/                                                                       |
| 20  | 100state                                        | Web (crawled)                 | https://100state.com/                                                                                   |
| 21  | Gener8tor gBETA Madison                         | Web (crawled)                 | https://www.gener8tor.com/gbeta/frontier-technology-accelerator                                         |
| 22  | Startup Wisconsin - Jon Eckhardt interview      | Transcript (manual)           | local file                                                                                              |

The crawl produced 22 documents totaling 260,627 words. Page counts varied a lot.

---

## Chunking Strategy

**Chunk size:** ~2,000 characters (≈ 512 tokens)

**Overlap:** 300 characters (≈15%)

**Why these choices fit the documents:**
One markdown-aware recursive splitter handles the whole corpus. It splits in
priority order: markdown headers first, then paragraphs, then sentences, then
words. It packs structural blocks up to the target size and never cuts a word in
half. For the mix of short pages, long crawled documents, and one 16k-word
report, a structure-aware splitter keeps small sections intact and still
segments long material cleanly. The ~512-token target sits well inside bge-m3's
8,192-token limit, and the 15% overlap carries context across boundaries.

**Final chunk count:** 1,158 chunks across 22 documents

---

## Sample Chunks

Five chunks from different source documents, pulled straight from
`documents/_chunks.jsonl`. Each one keeps the `## [page] <url>` header the crawler
adds, so the exact page is traceable.

1. WARF - Starting a Company (`warf-starting-a-company::0`)

   > LAUNCH YOUR STARTUP NOW. You've solidified your idea, done your due diligence
   > and drafted your business plan. It's time to take the next step. When you work
   > with WARF, we share your goal: to advance UW-Madison technologies from lab to
   > market…

2. Law & Entrepreneurship Clinic - Services (`law-entrepreneurship-clinic::3`)

   > …clients who would otherwise be unlikely to obtain qualified legal advice. This
   > usually means the applicant has not received a significant round of outside
   > funding or financing from investors. We are also interested in whether the
   > matter is a good educational fit for our students…

3. BadgerVC (`badger-vc::0`)

   > Where Badgers Meet Venture Capital. BadgerVC is a student led organization at
   > UW-Madison dedicated to making venture capital accessible to undergraduates.
   > Through speaker events, workshops, and discussions, we help students learn how
   > investors evaluate startups…

4. Grainger Engineering Design Innovation Lab (`grainger-design-innovation-lab::0`)

   > Unlock your creative potential at the Grainger Engineering Design Innovation
   > Lab! Located in two buildings on the engineering campus, the lab gives students
   > access to 3D printers, laser cutters, and fabrication equipment…

5. Empowering the Wisconsin Idea / Eckhardt Report (`empowering-the-wisconsin-idea::0`)
   > The Future of Entrepreneurship at the University of Wisconsin-Madison. Our
   > stakeholders and global community form a thriving environment where research
   > and entrepreneurship embrace boldness, risk, and discovery…

A note on chunk quality: since each source is crawled across many pages, some
chunks capture page boilerplate (cookie notices, nav menus, calendar feeds)
instead of real content. The boilerplate tags are stripped before chunking, but
some still gets through and shows up as low-value chunks. That is one of the costs
of crawling for breadth, and one reason retrieval uses a reranker.

---

## Embedding Model

**Model used:** `BAAI/bge-m3` (1,024-dimensional), run locally with
`sentence-transformers` on Apple Silicon (MPS). Embeddings are
stored in a ChromaDB vector database using cosine similarity.

**Retrieval pipeline:** bi-encoder, then reranker, then diversity filter.

1. The bge-m3 bi-encoder retrieves a candidate pool of 60.
2. A cross-encoder reranker (`BAAI/bge-reranker-v2-m3`) re-scores each
   `(query, chunk)` pair for more relevance.
3. A diversity filter keeps the best reranked chunks but allows at most 2 chunks
   from any single source, filling a final top-k of 8.

The reranker and diversity filter were both added after the multi-page crawl,
because the crawl's volume flooded the top-k and pushed small on-target sources
out (see Failure Case Analysis).

**Production tradeoff reflection:**
For a real deployment with no cost limit, the model choice comes down to a few
tradeoffs:

- **Context length.** bge-m3's 8,192-token window already covers long report
  sections. A larger window matters more if you index whole documents at once.
- **Dimensionality and accuracy.** 1,024 dimensions pick up subtle links, like
  mapping a casual "how to split equity" to formal clinic language. A larger API
  model could push precision further.
- **Domain vocabulary.** Campus acronyms (WARF, Weinert, gBETA, Grainger) are
  niche. A model trained with stronger domain coverage, such as `voyage-3-large`,
  would relate these entities more reliably.
- **Latency and privacy.** Running locally keeps queries on-device and has no
  per-call cost, but the cold start is slow (the bi-encoder and reranker are each
  about 2.2GB and load once). An API model is lighter locally but adds latency and
  per-query cost.

---

## Retrieval Test Results

Three queries run through `rag.retriever.retrieve`, showing the top returned
chunks with their cosine similarity.

**Query 1: "What does StartingBlock Madison offer student founders?"**

| Rank | Source                | Sim  | Chunk excerpt                                                                                           |
| ---- | --------------------- | ---- | ------------------------------------------------------------------------------------------------------- |
| 1    | StartingBlock Madison | 0.71 | "…you can try out StartingBlock before becoming a member: a free trial day for interested individuals…" |
| 2    | StartingBlock Madison | 0.68 | "…coworking space and the Spark Building on East Washington Avenue…"                                    |
| 3    | Capital Entrepreneurs | 0.66 | "…as chief scientist at Pivotal. Quickstep has developed a unique data processing technology…"          |
| 4    | Capital Entrepreneurs | 0.60 | "The Doyenne Group is a networking/mentoring group for women entrepreneurs…"                            |

_Why these are relevant:_ The top two chunks are the right answer. Both come from
StartingBlock's own pages and cover what was asked: membership, the free trial
day, and the coworking space. Ranks 3 and 4 fall to Capital Entrepreneurs, which
is still in the local-startup domain but about other organizations.

**Query 2: "How do I get involved with BadgerVC?"**

| Rank | Source                 | Sim  | Chunk excerpt                                                                            |
| ---- | ---------------------- | ---- | ---------------------------------------------------------------------------------------- |
| 1    | BadgerVC               | 0.64 | "…learn how you can get involved. We're excited to meet you! View Event → Info Meeting…" |
| 2    | BadgerVC               | 0.60 | "BEGIN:VEVENT … DTSTART:20260220 …" (a calendar-feed chunk)                              |
| 3    | Tech Exploration Lab   | 0.58 | "…Faculty Director Kevin Ponto talks to students about their virtual reality project…"   |
| 4    | Badger Future Founders | 0.59 | "Join Badger Future Founders and connect with fellow UW-Madison students…"               |

**Query 3: "What tools and equipment does the Grainger makerspace have?"**

| Rank | Source                                          | Sim  | Chunk excerpt                                                                                                    |
| ---- | ----------------------------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------- |
| 1    | Grainger Engineering Design Innovation Lab      | 0.64 | "Unlock your creative potential at the Grainger Engineering Design Innovation Lab! Located in two buildings…"    |
| 2    | Grainger Engineering Design Innovation Lab      | 0.45 | "…book the scanner of your choice based on availability. Consider checking out this user guide for 3D scanning…" |
| 3    | Empowering the Wisconsin Idea (Eckhardt Report) | 0.49 | "…Gener8tor's portfolio includes CS Nest, a mentoring program…"                                                  |
| 4    | SBDC UW-Madison                                 | 0.49 | "…The Wisconsin SBDC Network is a proud part of the Office of Business & Entrepreneurship…"                      |

_Why these are relevant:_ Both top chunks come from the Grainger lab's own pages
and speak directly to equipment, first the lab overview and then the 3D-scanner
booking page. There's a clear similarity gap (0.64 down to 0.45) once the
on-target chunks run out, and ranks 3 and 4 fall off to unrelated sources. The reranker
helps because it re-scores the pool so the Grainger chunks stay on top.
Query 2 shows the opposite case. Its rank-2 chunk is a raw calendar feed
(`VEVENT`) that the crawler ingested, an example of the boilerplate noise.

---

## Grounded Generation

Generation uses `openai/gpt-oss-120b` through the Groq API, at temperature 0.

**System prompt grounding instruction:**
The model gets the retrieved chunks as a numbered, source-labeled block and these
rules:

> Answer the user's question using ONLY the numbered SOURCES provided.
>
> - Use only facts found in the SOURCES. Do not add outside knowledge.
> - Cite the source number(s) you used inline, like [1] or [2][3].
> - If the SOURCES do not contain the answer, say exactly: "I don't have
>   information on that in my sources." Do not guess.

Grounding is enforced structurally as well as in the prompt. The user message
contains only `SOURCES:` (the top-8 chunks, each prefixed with
`[n] Source: <name> (<url>)`) followed by the question. The model never sees the
full corpus, only the retrieved context. Temperature 0 keeps answers
deterministic.

**How source attribution shows up:**
Every context chunk is numbered and labeled with its source name and URL, so the
model's inline `[n]` citations point at a real source. The query interface
(`rag/query.py`) also prints the retrieved sources with similarity scores, so you
can see what the answer was built from.

---

## Example Responses

Two in-scope answers with source attribution in the text, and one out-of-scope
query that triggers the refusal.

**Example 1 — "What is gBETA Madison and does it take equity?"**

> gBETA Madison is a free, early-stage pre-accelerator run by the
> nationally-ranked gener8tor accelerator. It is a short (six- to seven-week)
> program that gives selected teams one-on-one mentorship, investor pitch
> sessions, and other resources to help them prepare for venture funding [1].
> Because the program is funded by partners, gBETA charges no fees and takes no
> equity from the five companies selected for each cohort [1][3].

Sources: [1] Capital Entrepreneurs · [2][3] Gener8tor gBETA Madison · [4][5]
StartingBlock Madison · [6] Wisconsin Entrepreneurship Hub · [7][8] 100state

**Example 2 — "How can a student join the Startup Learning Community?"**

> A student joins by completing these steps before the deadline (typically May 1
> for admitted students) [1]: sign the University Residence Halls contract and pay
> the advance deposit in My UW Housing; rank "StartUp Learning Community" first in
> hall preferences; prioritize learning communities over residence halls; and set
> a random or preferred roommate. Once submitted, the student is considered for
> placement [1].

Sources: [1][6] Startup Learning Community · [2][3] 100state · [4] TranscendUW ·
[5] Badger Future Founders · [7] StartingBlock Madison · [8] Tech Exploration Lab

**Out-of-scope — "How much does a UW-Madison dorm meal plan cost?"**

> I don't have information on that in my sources.

Meal-plan pricing isn't in the startup corpus, so the retrieved chunks (SBDC, the
Eckhardt report, WARF) don't contain the answer and the model returns its fixed
refusal string instead of guessing.

---

## Query Interface

The interface is a command-line script, `rag/query.py`.

**Input:** one natural-language question. There are two modes:

- One-off: `python -m rag.query "your question"`
- Interactive: `python -m rag.query`, then type at the `> ` prompt (empty line or
  Ctrl-C to quit).

**Output fields:**

- **Answer:** the grounded response text, with inline `[n]` citations.
- **Sources retrieved:** a numbered list of the chunks given to the model. Each
  line shows the source name, a similarity score (`1 − cosine distance`), and the
  source URL.

**Sample interaction:**

```
> How do I get involved with BadgerVC?

BadgerVC is a student-led organization at UW-Madison that makes venture capital
accessible to undergraduates through speaker events, workshops, and discussions.
To get involved, attend one of their info meetings (held on campus, Thursdays
6-7pm) and sign up as a member on their site. [1]

Sources retrieved:
  [1] BadgerVC                 (sim 0.64)  https://www.badgervc.com/
  [2] BadgerVC                 (sim 0.60)  https://www.badgervc.com/
  [3] Tech Exploration Lab     (sim 0.58)  https://techexplorationlab.wisc.edu/
  [4] Badger Future Founders   (sim 0.59)  https://www.badgerfuturefounders.com/
  ...
```

---

## Evaluation Report

Run with `python -m rag.evaluate` against the 22-document / 1,158-chunk store,
using the reranked, diversity-aware retrieval

| #   | Question                                                                                                 | Expected answer                                                                                                                                                                   | System response (summarized)                                                                                                                                                       | Retrieval quality                                                                        | Response accuracy                                               |
| --- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| 1   | If a self-guided student researcher discovers something monetizable, how do they turn it into a company? | Start with the Tech Entrepreneurship Office (TEO) for commercial assessment and IP/tech-transfer; prototype at the Tech Exploration Lab; use Transcend UW for mentorship/funding. | TEO for commercial assessment plus mentorship and network; Tech Exploration Lab "Self-directed Innovation" for prototyping; Transcend UW competition; NSF I-Corps. [2][4][5][6]    | Relevant (TEO, Tech Exploration Lab, Transcend, ESL)                                     | Accurate                                                        |
| 2   | Eckhardt report's primary ecosystem challenge and recommended action?                                    | Systemic fragmentation across silos; recommends a centralized Wisconsin Entrepreneurship Hub.                                                                                     | Identified capital / lack of domain-specific funding as the chief obstacle; recommended raising the quantity and quality of investable companies. [5]                              | Partially relevant (ESL chunks dominate; Eckhardt promoted to ranks 3/5 by the reranker) | Partially accurate (different challenge surfaced than expected) |
| 3   | Service limits/prerequisites for the Law & Entrepreneurship Clinic's free services?                      | Intake vetting: can't afford private counsel, and offers economic value to WI.                                                                                                    | Listed eligibility groups: faculty/staff "outside activities" (with disclosure), student-athlete NIL (NCAA and WI-law conditions), and nascent/early-stage entrepreneurs only. [1] | Relevant (clinic pages top-ranked)                                                       | Accurate (more detailed than the expected answer)               |
| 4   | A student who likes venture capital wants to join an entrepreneurship club. What should they join?       | BadgerVC (student-led VC education); StratoVC for hands-on investing.                                                                                                             | BadgerVC (Thursdays 6-7pm, VC education for undergrads); StratoVC student fund for hands-on investing; Badger Future Founders for broader networking. [1][5][2]                    | Relevant (BadgerVC, StratoVC, Badger Future Founders)                                    | Accurate                                                        |
| 5   | Off-campus Madison alternative for heavy tooling/CNC when Grainger is closed?                            | Sector67, a non-profit community hackerspace open outside university hours.                                                                                                       | Incorrect. Claimed the "MGE Innovation Center" offers CNC and heavy tooling, a fabricated detail. Sector67 was never retrieved. [8]                                                | Off-target (Sector67 buried around rank 40; Grainger/SBDC chunks dominate)               | Inaccurate (hallucination, see Failure Case)                    |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Q5, "What off-campus Madison alternative provides heavy
tooling/CNC machinery when Grainger Engineering Makerspace is closed?" (Expected:
Sector67.)

**What the system returned:** A confident but fabricated answer, claiming the "MGE
Innovation Center" provides CNC and heavy tooling. The expected source, Sector67,
never appeared in the retrieved context.

**Root cause:** a retrieval failure that then caused a generation failure. Two
things compound.

1. Retrieval dilution from the crawl. Sector67 was crawled to a single in-scope
   page, while Grainger, SBDC, and StartingBlock each reached about 50 pages. Those
   high-volume sources produce many chunks that the embedding model, and even
   the cross-encoder reranker, score as more relevant than Sector67's one page.
2. Generation over-reach. With no good source in context, the model latched onto a
   plausible but wrong chunk (Capital Entrepreneurs mentioning the MGE Innovation
   Center) and invented the CNC machine tools detail, it into a hallucination.

**What I would change:** (a) Make the web crawler have less depth and max pages for
high-volume community sites, and more for WARF and dense webpages.
(b) If the top reranked relevance score is below a threshold, force the "I don't
have information" refusal instead of hallucinating.

---

## Spec Reflection

**One way the spec helped:**
It helped me guide the AI into what tools I wanted it to use. I specifically wanted
it to use Playwright for web-crawling and it did after I prompted it to.

**One way the implementation diverged, and why:**
The spec assumed single-page fetches and a four-way varying chunking router.
Instead the AI decided that a one markdown-aware recursive splitter would be
better, since two of the four document types had no documents once Reddit was
dropped, and added a multi-page crawler to reach the depth that policy questions
needed.Generation also runs on `openai/gpt-oss-120b` via Groq rather than the
spec's Llama 3.3 70B.

---

## AI Usage

**Instance 1 — Multi-page crawler and retrieval tuning**

- _What I gave the AI:_ The Anticipated Challenges section of `planning.md`
  (Challenge #2: root pages link out to sub-pages and PDFs that a shallow scraper
  misses) and a target of depth 3 / 50 pages, crawling all sources.
- _What it produced:_ A web crawler (`ingest/crawler.py`) with path
  scoping, robots.txt handling, PDF routing, and an SPA Playwright fallback(decided by me). After
  the crawl flooded the top-k, it added diversity-aware retrieval and a
  cross-encoder reranker (`rag/reranker.py`).
- _What I changed or overrode:_ I kept the full crawl despite the Q2/Q5
  regression, and chose to document the dilution tradeoff rather than dial the
  crawl back.

**Instance 2 — Source curation (Reddit)**

- _What I gave the AI:_ The source list and the Reddit search URL.
- _What it produced:_ A Reddit fetcher using the `.json` endpoints, with a
  Playwright fallback.
- _What I changed or overrode:_ Reddit blocked automated access (403 from both
  plain requests and a headless browser from Playwright), and the threads that were reachable were
  low-signal. I dropped Reddit entirely and noted that in `planning.md`.
