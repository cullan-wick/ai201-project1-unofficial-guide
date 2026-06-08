"""Single source of truth for the corpus.

Each source is transcribed from the table in planning.md. The orchestrator
(`run.py`) dispatches on `type`, and `slug` / `category` flow through into the
per-document frontmatter so the chunking and embedding stages can attach
provenance for source attribution.

type values:
    static_html  -> requests + BeautifulSoup -> markdown
    pdf          -> download + pdfplumber -> text
    reddit       -> Reddit .json endpoints (search -> per-thread)
    transcript   -> manual drop-in under documents/transcripts/ (auto-skipped)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    id: int
    name: str
    type: str       # static_html | pdf | reddit | transcript
    category: str
    url: str
    slug: str       # filesystem-safe; output written to documents/<slug>.md
    # Crawl scope override. None -> derive from the seed's directory path.
    # "" -> crawl the whole host (used when target pages sit outside the seed path).
    crawl_prefix: str | None = None


SOURCES: list[Source] = [
    Source(1, "Wisconsin Entrepreneurship Hub", "static_html", "campus-portal",
           "https://entrepreneurship.wisc.edu/", "wisconsin-entrepreneurship-hub"),
    Source(2, "Empowering the Wisconsin Idea (Eckhardt Report)", "pdf", "report",
           "https://news.wisc.edu/content/uploads/2024/09/EmpoweringtheWisconsinIdea-Report-Final4-Accessible-3.pdf",
           "empowering-the-wisconsin-idea"),
    Source(3, "Tech Entrepreneurship Office", "static_html", "campus-portal",
           "https://teo.wisc.edu/", "tech-entrepreneurship-office"),
    Source(4, "Entrepreneurship Science Lab", "static_html", "research",
           "https://eslab.wisc.edu/", "entrepreneurship-science-lab"),
    Source(5, "WARF - Starting a Company", "static_html", "legal",
           "https://www.warf.org/commercialize/starting-a-company/", "warf-starting-a-company",
           crawl_prefix=""),  # widen to whole warf.org: IP-policy pages sit outside /starting-a-company/
    Source(6, "Weinert Center for Entrepreneurship", "static_html", "campus-portal",
           "https://business.wisc.edu/centers/weinert/", "weinert-center"),
    Source(7, "Law & Entrepreneurship Clinic - Services", "static_html", "legal",
           "https://law.wisc.edu/uwle/services/", "law-entrepreneurship-clinic"),
    Source(8, "SBDC UW-Madison", "static_html", "business-support",
           "https://sbdc.wisc.edu/", "sbdc-uw-madison"),
    Source(9, "Tech Exploration Lab", "static_html", "makerspace",
           "https://techexplorationlab.wisc.edu/", "tech-exploration-lab"),
    Source(10, "Grainger Engineering Design Innovation Lab", "static_html", "makerspace",
           "https://making.engr.wisc.edu/", "grainger-design-innovation-lab"),
    Source(11, "Startup Learning Community", "static_html", "campus-portal",
           "https://www.housing.wisc.edu/undergraduate/communities/startup/", "startup-learning-community"),
    Source(12, "TranscendUW", "static_html", "student-org",
           "https://www.transcenduw.com/", "transcend-uw"),
    Source(13, "Women in Entrepreneurship UW-Madison", "static_html", "student-org",
           "https://womeninentrepreneurship-uw.vercel.app/", "women-in-entrepreneurship"),
    Source(14, "Badger Future Founders", "static_html", "student-org",
           "https://www.badgerfuturefounders.com/", "badger-future-founders"),
    Source(15, "StratoVC", "static_html", "funding",
           "https://stratovc.com/", "strato-vc"),
    Source(16, "BadgerVC", "static_html", "funding",
           "https://www.badgervc.com/", "badger-vc"),
    Source(17, "StartingBlock Madison", "static_html", "accelerator",
           "https://www.startingblockmadison.org/", "starting-block-madison"),
    Source(18, "Sector67", "static_html", "makerspace",
           "https://www.sector67.org/blog/", "sector67"),
    Source(19, "Capital Entrepreneurs", "static_html", "community",
           "https://capitalentrepreneurs.com/", "capital-entrepreneurs"),
    Source(20, "100state", "static_html", "community",
           "https://100state.com/", "100state"),
    Source(21, "Gener8tor gBETA Madison", "static_html", "accelerator",
           "https://www.gener8tor.com/gbeta/frontier-technology-accelerator", "gener8tor-gbeta"),
    # Source #22 (Reddit r/UWMadison startup threads) was evaluated and excluded:
    # Reddit hard-blocks automated access (403 via requests and headless browser),
    # and the available threads were low-signal (cofounder-hunting, off-topic, few
    # answers). No eval question depends on it. See planning.md.
    Source(23, "Student founder podcast transcripts", "transcript", "transcript",
           "", "podcast-transcripts"),
]
