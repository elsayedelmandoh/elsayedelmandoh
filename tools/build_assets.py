"""writes the static readme svgs into assets/ (stdlib only, offline, re-runnable).
usage: python3 tools/build_assets.py"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svgkit import Svg, text_width  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 1200
REPO = "https://github.com/elsayedelmandoh/"


def wrap(t, width):
    return textwrap.wrap(t, width, break_long_words=False)


def save(name, svg):
    (OUT / name).write_text(svg.render() if hasattr(svg, "render") else svg, encoding="utf-8")


# ---------- banner / divider / headers / footer ----------
def banner():
    s = Svg(W, 320, "elsayed elmandoh - nlp/llm engineer, rag pipelines, agentic ai", frame=False)
    s.add('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
          '<stop offset="0" style="stop-color:var(--g1)"/><stop offset="1" style="stop-color:var(--g2)"/></linearGradient>'
          '<linearGradient id="ul" x1="0" x2="1"><stop offset="0" style="stop-color:var(--ac)"/>'
          '<stop offset="1" style="stop-color:var(--ac2)"/></linearGradient>'
          '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
          '<path d="M40 0H0V40" fill="none" style="stroke:var(--bd)" stroke-opacity=".6"/></pattern></defs>')
    s.add(f'<rect width="{W}" height="320" fill="url(#bg)"/><rect width="{W}" height="320" fill="url(#grid)"/>')
    layers, xs = [4, 5, 5, 3], [830, 930, 1030, 1130]
    pos = [[(x, 160 + (i - (n - 1) / 2) * 52) for i in range(n)] for x, n in zip(xs, layers)]
    for a, b in zip(pos, pos[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                s.add(f'<line x1="{x1}" y1="{y1:g}" x2="{x2}" y2="{y2:g}" style="stroke:var(--ac)" stroke-opacity=".22"/>')
    k = 0
    for layer in pos:
        for (x, y) in layer:
            pulse = ('<animate attributeName="opacity" values="1;.35;1" dur="3.2s" '
                     f'begin="{(k % 5) * 0.6:g}s" repeatCount="indefinite"/>')
            s.add(f'<circle cx="{x}" cy="{y:g}" r="6" style="fill:var(--ac)">{pulse}</circle>')
            k += 1
    name = "elsayed elmandoh"
    end = s.text(60, 140, name, 64, "tx", True, bold=True)
    s.add(f'<rect x="{end + 8:g}" y="92" width="6" height="52" rx="2" style="fill:var(--ac)">'
          '<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></rect>')
    s.add('<rect x="60" y="158" width="220" height="4" rx="2" fill="url(#ul)"/>')
    s.text(60, 210, "nlp/llm engineer · rag pipelines · agentic ai", 26, "ac", True)
    s.text(60, 254, "m.sc. ai & data science @ queen's university · kingston, canada", 18, "mu")
    return s


def divider():
    s = Svg(W, 12, "divider", frame=False)
    s.add('<defs><linearGradient id="d" x1="0" x2="1"><stop offset="0" style="stop-color:var(--ac);stop-opacity:0"/>'
          '<stop offset=".3" style="stop-color:var(--ac)"/><stop offset=".7" style="stop-color:var(--ac2)"/>'
          '<stop offset="1" style="stop-color:var(--ac2);stop-opacity:0"/></linearGradient></defs>')
    s.add(f'<rect x="0" y="5" width="{W}" height="2" fill="url(#d)"/>')
    return s


def header(title):
    s = Svg(W, 56, title, frame=False)
    s.add('<rect x="0" y="12" width="6" height="32" rx="3" class="bar"/>')
    end = s.text(22, 38, title, 28, "tx", True, bold=True)
    s.add(f'<line x1="{end + 20:g}" y1="28" x2="{W}" y2="28" class="ln" stroke-width="1"/>')
    return s


def footer():
    s = Svg(W, 90, "disappear. grow. until u become the connection u once wished u had..", frame=False)
    s.add(f'<line x1="400" y1="20" x2="800" y2="20" class="ln"/>')
    s.text(W / 2, 58, "disappear. grow. until u become the connection u once wished u had..", 18, "mu", True, "middle")
    return s


# ---------- about / focus ----------
def about():
    paras = [
        "nlp/llm engineer with 2+ years of production ml: rag pipelines and end-to-end nlp systems. "
        "m.sc. in ai & data science (a+) at queen's university, canada.",
        "thesis: minimallm, verbosity-aware decoding for llms (sponsored by deloitte). a training-free logits "
        "processor cut output tokens 25-35% on mistral-7b, llama-3.1-8b and qwen2.5-3b. an audit showed it was "
        "learned early stopping, so i built an entailment-licensed sentence-elision method that beats "
        "matched-length truncation.",
        "languages: arabic, english, russian (basics).  off-keyboard: chess, gym, reading about 5gw/6gw warfare.",
    ]
    lines = [wrap(p, 140) for p in paras]
    h = 40 + sum(len(l) * 24 + 12 for l in lines)
    s = Svg(W, h, " ".join(paras))
    y = 42
    for block in lines:
        for ln in block:
            s.text(30, y, ln, 16, "tx")
            y += 24
        y += 12
    return s


def focus():
    items = [
        "finishing the queen's m.sc. thesis on verbosity-aware llm decoding (minimallm, deloitte-sponsored)",
        "building rag systems and ai agents",
        "data science for smart-city / geospatial ai (spaceeye-geoai)",
    ]
    s = Svg(W, 40 + 40 * len(items), "current focus: " + "; ".join(items))
    for i, t in enumerate(items):
        y = 46 + i * 40
        s.add(f'<circle cx="38" cy="{y - 6}" r="5" style="fill:var(--ac)"/>')
        s.text(58, y, t, 17, "tx")
    return s


# ---------- project cards ----------
CARDS = {
    "spaceeye": ("spaceeye-geoai", "spaceeye-geoai",
                 "ranks 12 coded r7 compounds for an inspection committee from free public satellite data (earth "
                 "engine). three clocks (k2/k3/k6), streamlit dashboard + hybrid rag chatbot.",
                 ["chromadb", "duckdb", "gemini", "streamlit"]),
    "russ": ("russ", "russ-rag-based-tutor-for-specific-subjects-genai-queens",
             "private offline rag tutor over course pdfs. citation-backed answers, zero cloud leakage. built for "
             "queen's.", ["langchain", "chromadb", "hf embeddings"]),
    "atari": ("atari-rl-benchmarking", "atari-rl-benchmarking",
              "dqn, ppo and a custom discretesac on pong, breakout, space invaders. reproducible pipeline, "
              "tensorboard, mp4 playback.", ["pytorch", "gymnasium", "sb3"]),
    "cloud-chatbot": ("cloud chatbot", "cisc886-cloud-based-conversational-chatbot",
                      "tinyllama 1.1b fine-tuned with qlora (4-bit) on aws. spark on emr, served with ollama on ec2, "
                      "openwebui coding assistant.", ["aws", "qlora", "spark", "ollama"]),
    "speech": ("speech emotion", "lightweight-speech-emotion-recognition-on-open-datasets",
               "6-class ser on ravdess. 1d cnn on log-mel (~150k params, <1ms cpu inference) vs mfcc+svm, "
               "speaker-disjoint evaluation.", ["pytorch", "librosa", "scikit-learn"]),
    "sentiment": ("sentiment-sleuth", "sentiment-sleuth",
                  "traditional ml sentiment pipeline. sgd champion: acc 0.8903, f1 0.8902. live hugging face demo.",
                  ["sgd", "tf-idf", "nltk"]),
}


def card(title, repo, desc, chips):
    s = Svg(380, 200, f"{title}: {desc} ({', '.join(chips)})")
    s.add('<rect x="0" y="16" width="4" height="26" rx="2" class="bar"/>')
    s.text(20, 36, title, 19, "ac", True, bold=True)
    lines = wrap(desc, 46)
    assert len(lines) <= 4, (title, lines)
    for i, ln in enumerate(lines):
        s.text(20, 66 + i * 18, ln, 12, "tx")
    x = 20
    for c in chips:
        x = s.chip(x, 140, c, 11, 8, 22) + 6
    s.text(360, 184, "github ->", 12, "ac", True, "end")
    return s


# ---------- stack ----------
STACK = [
    ("languages", ["python", "sql"]),
    ("ml / dl", ["pytorch", "tensorflow", "keras", "scikit-learn"]),
    ("nlp & llm", ["hugging face", "langchain", "langgraph", "spacy", "nltk", "gensim", "rag", "prompt engineering"]),
    ("cv & rl", ["yolov8", "opencv", "stable-baselines3"]),
    ("apps & infra", ["gemini", "groq", "ollama", "qlora", "fastapi", "streamlit", "gradio", "docker", "git",
                      "linux", "aws"]),
    ("data", ["mysql", "sqlite", "duckdb", "chromadb"]),
]


def stack():
    s = Svg(W, 30 + 46 * len(STACK), "toolbox: " + "; ".join(f"{g}: {', '.join(c)}" for g, c in STACK))
    for i, (group, chips) in enumerate(STACK):
        y = 28 + i * 46
        s.text(28, y + 17, group, 14, "mu", True)
        x = 170
        for c in chips:
            x = s.chip(x, y, c, 13, 12, 26) + 10
    return s


# ---------- timelines ----------
def timeline(label, entries):
    """entries: (date|None, title, subtitle, [paragraphs]); returns Svg."""
    layout, y = [], 30
    for date, title, sub, paras in entries:
        top, rows = y, []
        if date:
            rows.append((y + 8, date, 13, "ac", True, False)); y += 24
        rows.append((y + 10, title, 18, "tx", False, True)); y += 24
        rows.append((y + 6, sub, 13, "mu", False, False)); y += 26
        for p in paras:
            for ln in wrap(p, 158):
                rows.append((y + 8, ln, 14, "tx", False, False)); y += 20
            y += 6
        layout.append((top, rows)); y += 20
    s = Svg(W, y, label)
    s.add(f'<line x1="28" y1="{layout[0][0] + 6}" x2="28" y2="{y - 24}" style="stroke:var(--ac)" stroke-opacity=".5" stroke-width="2"/>')
    for top, rows in layout:
        s.add(f'<circle cx="28" cy="{top + 6}" r="6" style="fill:var(--bg);stroke:var(--ac)" stroke-width="2"/>')
        for ry, t, size, cls, mono, bold in rows:
            s.text(54, ry + size * 0.35, t, size, cls, mono, bold=bold)
    return s


EXPERIENCE = [
    ("oct - nov 2026", "data scientist", "administrative capital for urban development · new capital, egypt", [
        "smart-city iot/gis data cleaning and integration (python, sql/duckdb), documented quality checks with pii "
        "masking (law 151/2020), kpi pipeline with variance and root-cause analysis.",
        "built the ai component of spaceeye-geoai: inspection-file agent with verification log, complaints "
        "classifier, dashboard search/filters/map click, chatbot integration (python, streamlit, fastapi, duckdb, "
        "chromadb, gemini, scikit-learn, google earth engine data)."]),
    ("sep 2025 - present", "digilians program", "egyptian military academy / mcit · new capital, egypt", [
        "selected from 40k+ applicants to enroll in the m.sc. at queen's university.",
        "workshops with deloitte (pre-training vs fine-tuning, rag architectures, passive chatbots to active ai "
        "agents, etl/elt for genai, mlops lifecycle), ibm (resume building, networking, star interviews) and dotpy "
        "(startup fundamentals, freelancing); sessions at cairo ict (cyshield) on ai agents and at edex on ai in "
        "drones, air defense and defense systems."]),
    ("oct 2024 - jun 2025", "head of artificial intelligence", "international modern school sayed galal · cairo, egypt", [
        "joined as ai teacher (oct - nov 2024); promoted to head of ai (dec 2024 - jun 2025), leading ai curriculum "
        "development and integration for the school's technology program and the ai teaching team.",
        "taught python and ai to years 5-8 and grades 7-10 across american and british curricula; trained 25 "
        "students in 5 teams for the british council code club competition; ran internal competitions to prepare "
        "students for the code challenge championship (scratch, python, ai)."]),
    ("aug 2023 - aug 2025", "machine learning engineer", "electro pi · new cairo, egypt", [
        "designed and shipped 15+ production ml systems (harmful-prompt detector for llms, customer-service "
        "chatbot, code-quality evaluator, medical image analysis, automated eda, automated ml).",
        "semantic search engine (tf-idf, lsi, labse) at 87% map; sentiment pipeline (naive bayes + lstm, nltk) at "
        "93% test accuracy; zero-code automl and autoeda platforms.",
        "completed 11 specialization tracks (python, eda, ml, dl, cv, nlp, llms, rag, prompt engineering, "
        "langchain)."]),
    ("oct 2022 - feb 2023", "ai instructor", "huawei ict academy · egypt", [
        "ai instructor (dec 2022 - feb 2023): hcia, python & machine learning for 30 students; authored session "
        "plans, assignments and labs.",
        "ai intern (oct - nov 2022): completed huawei's hcia course (ai, machine learning, deep learning) and "
        "explored huawei's ai services and tools."]),
]
EDUCATION = [
    ("jan - nov 2026", "m.sc. artificial intelligence & data science (a+)", "queen's university · kingston, canada", [
        "thesis: minimallm, verbosity-aware decoding for llms. supervisor: dr. rahatara ferdousi. sponsor: deloitte "
        "(mentor collaboration bridging academic llm research with enterprise ai deployment)."]),
    ("apr - aug 2024", "aspire leaders program", "harvard university", []),
    ("oct 2020 - jul 2024", "b.sc. artificial intelligence", "egyptian russian university (eru) · cairo", [
        "studied ml, dl, nlp, cv; russian language 1 & 2 (a+ in both); represented eru in ai competitions at auc, "
        "nile university, military technical college and air defense college.",
        "graduation project linkedup: academic networking platform for the egyptian education sector connecting "
        "students, teachers and universities with relevant jobs via recommendations (python, django, rest apis, ml, "
        "cosine similarity)."]),
]


# ---------- certs ----------
CERTS = [
    ("aws certified cloud practitioner", "aws", []),
    ("aws academy graduate: machine learning for natural language processing", "aws academy", []),
    ("aws machine learning foundations", "aws", []),
    ("aws academy cloud foundations", "aws academy", []),
    ("machine learning specialization", "stanford / deeplearning.ai",
     ["supervised machine learning: regression and classification", "advanced learning algorithms",
      "unsupervised learning, recommenders, reinforcement learning"]),
    ("tools of the trade: linux and sql", "google", []),
    ("introduction to data engineering", "ibm", []),
    ("python for data science, ai & development", "ibm", []),
    ("langchain", "electro pi", []),
    ("natural language processing", "electro pi", []),
    ("computer vision", "electro pi & kaggle", []),
]


def certs():
    colw, cols, placed = 560, [30, 30], []
    for name, issuer, subs in CERTS:
        nl = wrap(name, 56)
        h = 22 * len(nl) + (20 if issuer else 0) + 20 * len(subs) + 22
        c = 0 if cols[0] <= cols[1] else 1
        placed.append((c, cols[c], nl, issuer, subs))
        cols[c] += h
    s = Svg(W, max(cols) + 6, "certifications: " + "; ".join(n + (f" ({i})" if i else "") for n, i, _ in CERTS))
    for c, y, nl, issuer, subs in placed:
        x = 30 + c * (colw + 40)
        top = y
        for ln in nl:
            y += 22
            s.text(x + 18, y - 2, ln, 14, "tx", bold=True)
        if issuer:
            y += 20
            s.text(x + 18, y - 4, issuer, 12, "mu")
        for sub in subs:
            y += 20
            s.text(x + 34, y - 4, "- " + sub, 12, "tx")
        s.add(f'<rect x="{x}" y="{top + 4}" width="4" height="{y - top - 8}" rx="2" class="bar"/>')
    return s


# ---------- competitions ----------
def competitions():
    feats = [
        ("arabic abstractive summarization", "icmtc-23 · military technical college",
         "fine-tuned mt5. rouge r1 0.10 / r2 0.02 / rl 0.08", "repo: Arabic_Abstractive_Summarization"),
        ("terrorist detection", "itc-23 · air defense college",
         "yolov8x + autodistill: civilian/military and weapon detection",
         "0.738 map50 / 0.637 map50-95 · repo: detect-terrorists"),
    ]
    also = ["medgenius - 16th ugrf competition", "su real life competition", "itc-egypt adc competition",
            "artificial intelligence competition (aic)", "egyptian startup olympics"]
    s = Svg(W, 270, "competitions: " + "; ".join(" - ".join(f) for f in feats) + "; also: " + "; ".join(also))
    for i, (t, ev, d1, d2) in enumerate(feats):
        x = 30 + i * 580
        s.add(f'<rect x="{x}" y="24" width="560" height="120" rx="10" class="card"/>')
        s.add(f'<rect x="{x}" y="38" width="4" height="26" rx="2" class="bar"/>')
        s.text(x + 20, 58, t, 18, "ac", True, bold=True)
        s.text(x + 20, 84, ev, 13, "mu")
        s.text(x + 20, 110, d1, 13, "tx")
        s.text(x + 20, 132, d2, 12, "mu", True)
    s.text(30, 184, "also participated", 14, "mu", True)
    x, y = 30, 198
    for lab in also:
        if x + text_width(lab, 12) + 20 > W - 30:
            x, y = 30, y + 34
        x = s.chip(x, y, lab, 12, 10, 26) + 10
    return s


# ---------- connect buttons ----------
CONNECT = [("github", "github"), ("linkedin", "linkedin"), ("email", "email"), ("x", "x"),
           ("huggingface", "hugging face"), ("kaggle", "kaggle"), ("spotify", "spotify")]


def button(label):
    s = Svg(112, 52, label, frame=False)
    s.add('<rect x="1" y="1" width="110" height="50" rx="10" class="card" style="stroke:var(--ac)" stroke-width="1.5"/>')
    s.text(56, 31, label, 14, "tx", True, "middle", True)
    return s


def placeholder(label):
    s = Svg(600, 80, label, frame=False)
    s.text(300, 44, "snake generates on the next workflow run", 16, "mu", True, "middle")
    return s


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "generated").mkdir(exist_ok=True)
    save("banner.svg", banner())
    save("divider.svg", divider())
    for key, title in [("about", "about"), ("focus", "current focus"), ("projects", "projects"),
                       ("activity", "activity"), ("stack", "toolbox"), ("experience", "experience"),
                       ("education", "education"), ("certs", "certifications"),
                       ("competitions", "competitions"), ("connect", "connect")]:
        save(f"h-{key}.svg", header(title))
    save("about.svg", about())
    save("focus.svg", focus())
    for key, (title, repo, desc, chips) in CARDS.items():
        save(f"card-{key}.svg", card(title, repo, desc, chips))
    save("stack.svg", stack())
    save("experience.svg", timeline("experience: " + "; ".join(f"{e[1]} ({e[2]})" for e in EXPERIENCE), EXPERIENCE))
    save("education.svg", timeline("education: " + "; ".join(f"{e[1]} ({e[2]})" for e in EDUCATION), EDUCATION))
    save("certs.svg", certs())
    save("competitions.svg", competitions())
    for key, label in CONNECT:
        save(f"connect-{key}.svg", button(label))
    save("footer.svg", footer())
    for name in ("snake.svg", "snake-dark.svg"):  # action overwrites these; never clobber real output
        p = OUT / "generated" / name
        if not p.exists():
            p.write_text(placeholder("snake generates on the next workflow run").render(), encoding="utf-8")
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
