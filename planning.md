# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

My domain: The UW-Madison Startup Ecosystem: Bridging University Policy and Student Practice.

This knowledge is valuable to student founders, as a lot of resources from the university, student orgs, and campus partners are siloed, and needs one concise place to retrieve all of it.

---

## Documents

Our pipeline ingests 23 distinct operational sources across the university, regional accelerator, and madison community landscape:

```text
+----+--------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------+
| #  | Source                                     | Description                                                                                                             | URL or location                                                                           |
+----+--------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------+
| 1  | Wisconsin Entrepreneurship Hub             | Main campus portal offering centralized frameworks and macro-level administrative infrastructure for university creators. |https://entrepreneurship.wisc.edu/                                                     |
| 2  | Empowering the Wisconsin Idea              | A 45-page foundational report by Jon Eckhardt establishing the systemic data, benchmark metrics, and strategic roadmap. | https://news.wisc.edu/content/uploads/2024/09/EmpoweringtheWisconsinIdea-Report-Final4-Accessible-3.pdf  |
| 3  | Tech Entrepreneurship Office               | The administrative branch specialized in commercializing academic research, helping technical teams spin out of labs.   | https://teo.wisc.edu/                                                                 |
| 4  | Entrepreneurship Science Lab               | Data-driven research unit tracking, assessing, and optimizing how student and academic entrepreneurship functions.     | https://eslab.wisc.edu/                                                                  |
| 5  | WARF - Starting a Company                  | Legal intellectual property policies, licensing guidelines, and disclosure protocols dictating invention constraints.  | https://www.warf.org/                                    |
| 6  | Weinert Center for Entrepreneurship        | Academic venture hub offering formal entrepreneurial pathways, the WAVE Practicum, and institutional milestone funding.  | https://business.wisc.edu/centers/weinert/                                             |
| 7  | Law & Entrepreneurship Clinic - Services   | Free professional legal services mapping out entity formation, intellectual property safety, and founder equity splits.| https://law.wisc.edu/uwle/services/                                                      |
| 8  | SBDC UW Madison                            | Structured business counseling, legal compliance guidance, and financial modeling tools for early small businesses.     | https://sbdc.wisc.edu/                                                                   |
| 9  | Tech Exploration Lab                       | A dynamic prototyping sandbox connecting applied AI and emerging technologies with real-world industry problems.        | https://techexplorationlab.wisc.edu/                                                    |
| 10 | Grainger Engineering Design Innovation Lab | Physical hardware makerspace offering advanced engineering tools, 3D printers, and technical fabrication equipment.     | https://making.engr.wisc.edu/                                                             |
| 11 | Startup Learning Community                 | Residential housing program designed to integrate entrepreneurship directly into the daily living environment.          | https://www.housing.wisc.edu/undergraduate/communities/startup/                        |
| 12 | TranscendUW                                | Cross-disciplinary innovation hub that organizes the premier student-run pitch competition and team matchmaking.        | https://www.transcenduw.com/                                                             |
| 13 | Women in Entrepreneurship UW Madison       | Student community dedicated to empowering female founders through skill-building workshops and executive networking.    | https://womeninentrepreneurship-uw.vercel.app/                                            |
| 14 | Badger Future Founders                     | High-momentum peer cohort designed exclusively to support active, elite undergraduate student operators running projects.| https://www.badgerfuturefounders.com/                                                    |
| 15 | StratoVC                                   | Student-run venture capital fund providing real investment checks, due diligence training, and pitch coaching.          | https://stratovc.com/                                                                     |
| 16 | BadgerVC                                   | Grassroots student venture initiative training founders in fundraising strategies and connecting them with VC networks.  | https://www.badgervc.com/                                                                 |
| 17 | StartingBlock Madison                      | Premier off-campus startup accelerator and collaborative coworking space bridging student talent with regional capital.  | https://www.startingblockmadison.org/                                                   |
| 18 | Sector67                                   | Community hackerspace offering heavy tooling, advanced physical equipment, and prototyping gear outside school hours.   | https://www.sector67.org/blog/                                                            |
| 19 | Capital Entrepreneurs                      | Grassroots professional network of local tech founders serving as an organic meetup hub for startup operators.          | https://capitalentrepreneurs.com/                                                         |
| 20 | 100state                                   | Diverse local coworking community focusing on civic engagement, young business professionals, and emerging builders.     | https://100state.com/                                                                     |
| 21 | Gener8tor gBeta Madison                    | Highly competitive, non-equity accelerator program designed to quickly prepare high-growth student ventures for seed VC. | https://www.gener8tor.com/gbeta/frontier-technology-accelerator/                           |
| 22 | Reddit UW-Madison Startup Search           | Unfiltered peer-to-peer forum threads revealing honest student opinions, troubleshooting, and advice on local resources. | https://www.reddit.com/r/UWMadison/search/?q=startup                                       |
| 23 | Transcript of Wisconsin Startup - Jon Eckhardt Podcast       | Conversational record logging precise tactical narratives of Jon Eckhardt and UW-Madison managing entrepreneurship on campus | Local File Asset                                                 |
+----+--------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------+

```

---

## Chunking Strategy

> **Update during implementation:** I dropped this four-archetype asymmetric plan for a single markdown-aware recursive splitter (~512 tokens, 15% overlap). Once Reddit was excluded, two of the four archetypes had no documents, so a uniform splitter covered the remaining web pages and the report. See the README for details.

**Chunk size:** Varying (Asymmetric Framework, depends on data type from 200 words to whole-document level)

**Overlap:** Varying (Asymmetric Framework, 10% to 50% overlap depending on text fluidity)

**Reasoning:**
I will utilize varying chunk size and overlap depending on four distinct source architectures:

1. Formal PDF Frameworks (Eckhardt PDF Report, WARF, Legal Clinic Rules): Semantic Parent-Child approach.

- Documents are divided into large parent chunks based on Markdown headers (~1,000–1,500 words) to anchor macro-context, while smaller child chunks (~200 words, 10% overlap) are indexed for precise vector matching. If a child chunk is retrieved, the entire parent context is passed to the LLM to prevent legal hallucinations.

2. Flat University Portals (Makerspace tool directories, Weinert program lists): Fixed-Size Token Chunking (~512 tokens)\*\* with a Medium Overlap (~10-15%)

- These pages serve primarily as reference directories packed with dense, localized keywords, room numbers, and contact points.
- This ensures fast keyword retrieval and guarantees that specific machinery or program names are not sliced in half at a chunk boundary line.

3. Conversational Transcripts (Startup Wisconsin Podcast): Sliding Window strategy with a 400-word chunk size and 40-50% overlap (150-200 words)

- Ensure conversational prompts and answers remain tightly bound in vector space.
- A podcast's insight might be scattered across several paragraphs separated by an unrelated anecdote.

4. Scraped Reddit Threads (r/UWMadison Startup Queries): Document-Level (Whole-Thread) Chunking

- The engineering value of a community forum lies in its collective consensus—the dialogue tree of questions, bad answers, and peer corrections. Slicing these would decouple answers from their validation.
- Keeping the core post and its immediate comment tree as a single indivisible asset, natively supported by our embedding model's large context ceiling.

---

## Retrieval Approach

     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

## Retrieval Approach

### Embedding Model

I'm using the BAAI/bge-m3, running locally on my MacBook Pro (32GB memory).

If this system were scaled to a massive production environment where local deployment limits were removed, the following architectural tradeoffs would guide my model choice:

- Context Length: better embedding models have a larger token limit, so it could better capture podcast transcripts
- Dimensional Accuracy: scalling dimensions means better subtle semantic relationship-mapping
- Domain-Specific Tokenization: scaling to an enteprise technical API (like a voyage.ai model) would be better at mapping technical vocab to campus entities

### Top-k Retrieval Configuration

top-k = 5
This balances context precision against model noise. Works well for all chunking methods I am using.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

+---+-----------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| # | Question | Expected answer |
+---+-----------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| 1 | If a student at UW-Madison is doing self-guided reserach and discovers something that could be monetizable and wants to turn it into a company, what should he do? | Start with the Tech Entrepreneurship Office (TEO), the campus bridge for turning research into a startup (commercial evaluation, IP/tech-transfer, investor and mentor connections); disclose any invention to WARF for IP/licensing. Use the Tech Exploration Lab for prototyping and Transcend UW for mentorship and pitch-competition funding. |
| 2 | What does Jon Eckhardt's report identify as the primary ecosystem challenge and what action item does it recommend? | Systemic fragmentation across campus silos. It recommends creating a centralized, unified Wisconsin Entrepreneurship Hub. |
| 3 | What specific service limits or prerequisites does the Law & Entrepreneurship Clinic establish for free student legal services? | Startups must clear an intake vetting showing they cannot afford private counsel and offer economic/operational value to WI. |
| 4 | I am a student at UW-Madison who likes venture capital and want to join an entrepreneurship club. What should I join? | BadgerVC — a student-led org that makes venture capital accessible to undergraduates through speaker events and workshops. For hands-on investing, also consider StratoVC, a student-run venture fund that makes real investments in idea-stage startups. |
| 5 | What specific off-campus Madison alternative provides heavy tooling and CNC machinery when Grainger Engineering Makerspace is closed? | Sector67. A non-profit community hackerspace operating outside university hours, calendar restrictions, and enrollment status. |
+---+-----------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------+

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. For the reddit one, the url i sent is just the titles of the relevant posts not the posts itself, so it may not be able to pull the necessary info. If the ingestion script does not actively follow each post link to extract the entire comment payload, the vector store will lack the data required to answer user queries truthfully.

   Resolution (during implementation): Reddit was evaluated and excluded. Reddit hard-blocks automated access — both `requests` against the `.json` endpoints and a headless Playwright browser returned HTTP 403. Beyond the access block, the actual `r/UWMadison` "startup" threads were low-signal (cofounder-hunting posts, off-topic questions, threads with 0–1 answers), so they would have injected retrieval noise rather than peer insight. No evaluation question depends on Reddit, so the corpus ships with the 21 high-signal institutional sources instead.

2. If the embedding model can only read the actually page of the url i sent, then many pages will be missing and the embedding model wont be abel to embed them. If a root page contains only a collection of external hyperlinks (pointing to separate pages for intake forms, eligibility requirements, or pricing), a simple scraper will only grab the link text. The underlying PDF downloads, secondary sub-directories, and sub-pages will remain entirely missing from the vector index.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

+-------------------------------------------------------------------------------------------------------------------------+
| LOCAL COMPUTE NODE (MacBook Pro M3 Pro) |
+-------------------------------------------------------------------------------------------------------------------------+
| 1. DOCUMENT INGESTION │ 2. CHUNKING ENGINE │ 3. EMBEDDING + VECTOR STORE │ 4. RETRIEVAL ENGINE |
| │ │ │ |
| [Static Univ. Portals] │ [Formal PDFs] │ [Text Chunks & Metadata] │ [User Query Input] |
| │ │ │ │ │ │ │ |
| ▼ │ ▼ │ ▼ │ ▼ |
| Beautiful Soup │ Semantic Parent-Child │ BAAI / bge-m3 │ Local Embed Vector |
| │ (200-1500w / 10% overlap) │ (1,024-Dim Vector Space) │ │ |
| [Dynamic Social Hubs] │ │ │ │ ▼ |
| │ │ [Flat Web Portals] │ ▼ │ ChromaDB Index |
| ▼ │ Fixed-Token (512 / 15%) │ ChromaDB │ (Vector Similarity) |
| Playwright │ │ (PersistentClient) │ │ |
| │ [Podcast Transcripts] │ │ ▼ |
| [PDFs & Transcripts] │ Sliding Window (400 / 50%) │ │ Top-k=5 Grounded |
| │ │ │ │ Context Blocks |
| ▼ │ [Reddit Community Thread] │ │ │ |
| Native Python │ Document-Level (Whole) │ │ │ |
+──────────────────────────┴─────────────────────────────┴─────────────────────────────────┼────────────────────────────+
│
│ (Payload: Query + Context)
▼
+-------------------------------------------------------------------------------------------------------------------------+
| CLOUD INFERENCE NODE (Groq LPU) |
+-------------------------------------------------------------------------------------------------------------------------+
| 5. GENERATION |
| |
| console.groq.com API Gateway |
| │ |
| ▼ |
| Llama 3.3 70B Versatile |
| (Strict System Grounding) |
| │ |
| ▼ |
| [Conversational Guide Answer] |
+-------------------------------------------------------------------------------------------------------------------------+

### Architectural Narrative & Lifecycle Dataflow

1. **Document Ingestion Layer:** This engine ingests multiple distinct data structures. Static `wisc.edu` institutional portals are targeted via a rapid **Beautiful Soup** scraper loop to strip layout boilerplate. Dynamic, JavaScript-heavy community spaces (such as `r/UWMadison` Reddit threads) are processed via a headless **Playwright** browser engine that actively handles DOM hydration and lazy-loaded element scroll limits. Transcripts and flat academic papers are parsed locally via native Python string tools.
2. **Asymmetric Chunking Layer:** Rather than using a uniform, one-size-fits-all character slice that breaks phrase parameters, an asymmetric router evaluates file extensions and origin metadata. Text streams are cleanly mapped to one of four specialized chunking engines (**Parent-Child Hierarchy**, **Fixed-Token Splitters**, **Sliding Windows**, or **Whole-Document Assemblies**) to maximize contextual retention.
3. **Local Embedding & Persistence Layer:** Sliced text objects are passed into an internal HuggingFace execution wrapper hosting the **bge-m3** model weights. The 32GB unified memory configuration enables sub-second local generation of highly descriptive 1,024-dimensional vectors. These arrays, bundled with strict lineage metadata tags (Source Domain, Hub Title, URL), are committed to the local filesystem via an in-process, non-relational **ChromaDB** deployment.
4. **Retrieval Engine:** When a user enters a query, the system transforms the string using the identical local `bge-m3` embedding model. ChromaDB performs a vector space similarity scan to rank and isolate the **Top-k = 5 closest context blocks**, ensuring highly relevant documents are recovered without cloud data exposure.
5. **Generative Synthesis Layer:** The matched data chunks are packed into a rigid system prompt template instructing the LLM to function under a zero-shot, anti-hallucination constraint. This text payload is dispatched to **Groq**. Utilizing serverless LPU (Language Processing Unit) acceleration, the **Llama 3.3 70B** model reads the grounded parameters and streams the finalized operational advice back to the workspace.

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

### 1. Ingestion and scraping

- **AI tool:** Claude Opus 4.8
- **Input:** The "Anticipated Challenges" section, which explains the difference between static `wisc.edu` HTML pages and JavaScript-heavy pages like Reddit. I'll ask for `BeautifulSoup` on the static pages and `Playwright` on the dynamic ones.
- **Expected output:** A Python script with two parts. A static scraper (`requests` + `BeautifulSoup`) that pulls the institutional pages, converts them to markdown (`<h1>` to `#`, `<ul>` to `-`), and strips nav/header/footer. A dynamic scraper (`Playwright`) for Reddit that scrolls to load comments and saves the text as JSON.
- **How I'll verify:** Run it on a few sources and check that the saved files contain real page text, not navigation boilerplate.

### 2. Chunking

- **AI tool:** Claude Opus 4.8
- **Input:** The "Chunking Strategy" section, with the source archetypes and the target chunk sizes and overlaps.
- **Expected output:** A chunking module that splits each document to the right size with the right overlap and never cuts a word in half.
- **How I'll verify:** Spot-check the chunk sizes and confirm no chunk ends mid-word.

### 3. Metadata for the vector store

- **AI tool:** Claude Opus 4.8
- **Input:** The "Retrieval Approach" section (the `BAAI/bge-m3` local model) and the fields I want tracked per chunk (source name, hub/category, exact URL).
- **Expected output:** Code that attaches that metadata to each chunk in the format ChromaDB expects, so an answer can be traced back to its source.
- **How I'll verify:** Confirm every chunk in the store carries its source and URL, and that a retrieved chunk maps back to a real document.

**Milestone 3 — Ingestion and chunking:**
1,158 chunks across 22 documents
**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
