"""builds dark_mode.svg + light_mode.svg for the github profile readme.
needs env ACCESS_TOKEN (classic PAT: repo + read:user). no token = offline preview with dummy numbers.
"""
import os
from datetime import date, datetime
from html import escape
from pathlib import Path

import re

import requests

from tools.svgkit import Svg

# ---------- config: edit these ----------
USER = "elsayedelmandoh"
BIRTHDAY = date(2002, 1, 1)          # TODO: put your real birthday (uptime = age)
X_HANDLE = "aangparker"              # TODO: confirm (old readme had aangpy)
EMAIL = "elsayedelmandoh7@gmail.com"
LINKEDIN = "elsayed-elmandoh-b5849a1b8"
W = 60                               # char width of the right column
# ----------------------------------------

ROOT = Path(__file__).parent
API = "https://api.github.com/graphql"


def load_env(path):
    """Load KEY=VALUE lines into os.environ; real env vars win."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


load_env(ROOT / ".env")
TOKEN = os.environ.get("ACCESS_TOKEN")


def gql(query, variables):
    r = requests.post(API, json={"query": query, "variables": variables},
                      headers={"Authorization": f"bearer {TOKEN}"}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


OTHER_COLOR = "#8b949e"
TOP_LANGS = 6


def fetch_langs():
    """bytes per language over my non-fork repos -> [(name, color, bytes)] top 6 + other."""
    totals, cursor = {}, None
    while True:
        d = gql("""query($l:String!,$c:String){user(login:$l){repositories(first:100,after:$c,
            ownerAffiliations:OWNER,isFork:false){pageInfo{hasNextPage endCursor}
            nodes{languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}""",
                {"l": USER, "c": cursor})["user"]["repositories"]
        for repo in d["nodes"]:
            for e in repo["languages"]["edges"]:
                name = e["node"]["name"]
                color, size = totals.get(name, (e["node"]["color"], 0))
                totals[name] = (color, size + e["size"])
        if not d["pageInfo"]["hasNextPage"]:
            break
        cursor = d["pageInfo"]["endCursor"]
    return rank_langs([(n, c, b) for n, (c, b) in totals.items()])


def rank_langs(items):
    items = sorted(items, key=lambda x: -x[2])
    top, rest = items[:TOP_LANGS], sum(b for _, _, b in items[TOP_LANGS:])
    return top + ([("other", OTHER_COLOR, rest)] if rest else [])


def fetch_stats():
    if not TOKEN:
        print("no ACCESS_TOKEN -> offline preview with dummy numbers")
        return dict(repos=0, contributed=0, stars=0, commits=0, followers=0, add=0, dele=0,
                    contrib_total=0, calendar=[], langs=[])

    u = gql("""query($l:String!){user(login:$l){id createdAt
        followers{totalCount}
        repositories(ownerAffiliations:OWNER){totalCount}
        repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY]){totalCount}}}""",
            {"l": USER})["user"]
    uid = u["id"]

    # all repos i can commit to (owner / collaborator / org)
    repos, cursor = [], None
    while True:
        d = gql("""query($l:String!,$c:String){user(login:$l){repositories(first:100,after:$c,
            ownerAffiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER]){
            pageInfo{hasNextPage endCursor}
            nodes{name stargazerCount owner{login} defaultBranchRef{name}}}}}""",
                {"l": USER, "c": cursor})["user"]["repositories"]
        repos += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        cursor = d["pageInfo"]["endCursor"]

    stars = sum(r["stargazerCount"] for r in repos if r["owner"]["login"] == USER)

    # commits, year by year (api caps contributionsCollection at 1 year)
    commits = 0
    start_year = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).year
    for y in range(start_year, date.today().year + 1):
        c = gql("""query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){
            contributionsCollection(from:$f,to:$t){totalCommitContributions restrictedContributionsCount}}}""",
                {"l": USER, "f": f"{y}-01-01T00:00:00Z", "t": f"{y}-12-31T23:59:59Z"}
                )["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]

    # lines of code: sum additions/deletions of MY commits on each default branch
    add = dele = 0
    for r in repos:
        if not r["defaultBranchRef"]:
            continue
        cursor = None
        while True:
            h = gql("""query($o:String!,$n:String!,$uid:ID!,$c:String){repository(owner:$o,name:$n){
                defaultBranchRef{target{... on Commit{history(first:100,after:$c,author:{id:$uid}){
                pageInfo{hasNextPage endCursor} nodes{additions deletions}}}}}}}""",
                    {"o": r["owner"]["login"], "n": r["name"], "uid": uid, "c": cursor}
                    )["repository"]["defaultBranchRef"]["target"]["history"]
            for n in h["nodes"]:
                add += n["additions"]
                dele += n["deletions"]
            if not h["pageInfo"]["hasNextPage"]:
                break
            cursor = h["pageInfo"]["endCursor"]

    # contribution calendar, default last-year window
    cal = gql("""query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{
        totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}""",
              {"l": USER})["user"]["contributionsCollection"]["contributionCalendar"]
    calendar = [[dict(date=d["date"], count=d["contributionCount"], level=d["contributionLevel"])
                 for d in w["contributionDays"]] for w in cal["weeks"]]

    langs = fetch_langs()

    return dict(repos=u["repositories"]["totalCount"],
                contributed=u["repositoriesContributedTo"]["totalCount"],
                stars=stars, commits=commits, followers=u["followers"]["totalCount"],
                add=add, dele=dele, contrib_total=cal["totalContributions"], calendar=calendar, langs=langs)


def uptime():
    t = date.today()
    y, m, d = t.year - BIRTHDAY.year, t.month - BIRTHDAY.month, t.day - BIRTHDAY.day
    if d < 0:
        m -= 1
        prev_month_days = (date(t.year, t.month, 1) - date.resolution).day
        d += prev_month_days
    if m < 0:
        y -= 1
        m += 12
    return f"{y} years, {m} months, {d} days"


# ---------- svg rendering ----------
THEMES = {
    "dark_mode":  dict(bg="#161b22", text="#c9d1d9", key="#ffa657", val="#a5d6ff", cc="#616e7c", add="#3fb950", dele="#f85149"),
    "light_mode": dict(bg="#f6f8fa", text="#24292f", key="#953800", val="#0a3069", cc="#b6c2d0", add="#1a7f37", dele="#cf222e"),
}
esc = escape


def kv(key, segs):
    if isinstance(segs, str):
        segs = [(segs, "val")]
    vlen = sum(len(t) for t, _ in segs)
    pad = max(2, W - 5 - len(key) - vlen)
    val = "".join(f'<tspan class="{c}">{esc(t)}</tspan>' for t, c in segs)
    return (f'<tspan class="cc">. </tspan><tspan class="key">{esc(key)}</tspan>:'
            f'<tspan class="cc"> {"." * pad} </tspan>{val}')


def rule(title):
    return f'{esc(title)} <tspan class="cc">{"-" * (W - len(title) - 1)}</tspan>'


def build(theme, s):
    n = lambda x: f"{x:,}"
    rows = [
        rule(f"{USER}@elmandoh"),
        kv("Role", "NLP / LLM Engineer"),
        kv("Uptime", uptime()),
        kv("Host", "Queen's University, Kingston ON"),
        kv("Kernel", "LLMs, RAG, Agentic AI"),
        "",
        kv("Languages.Programming", "Python, SQL"),
        kv("Frameworks", "PyTorch, TensorFlow, LangGraph, FastAPI"),
        kv("AI.LLM", "Gemini, Groq, Ollama, QLoRA, Hugging Face"),
        kv("AI.RAG", "LangChain, ChromaDB, Streamlit, Gradio"),
        kv("AI.CV/RL", "YOLOv8, OpenCV, Stable-Baselines3"),
        kv("Infra", "Docker, AWS, Linux"),
        kv("Languages.Real", "Arabic, English, Russian"),
        "",
        kv("Hobbies.Mind", "Chess, 5GW/6GW warfare"),
        kv("Hobbies.Body", "Gym"),
        "",
        rule("- Contact"),
        kv("Email.Personal", EMAIL),
        kv("LinkedIn", LINKEDIN),
        kv("GitHub", USER),
        kv("X", f"@{X_HANDLE}"),
        "",
        rule("- GitHub Stats"),
        kv("Repos", [(n(s["repos"]), "val"), (" {Contributed: ", "text"), (n(s["contributed"]), "val"), ("}", "text")]),
        kv("Stars", n(s["stars"])),
        kv("Commits", n(s["commits"])),
        kv("Contributions", [(n(s["contrib_total"]), "val"), (" (last year)", "text")]),
        kv("Followers", n(s["followers"])),
        kv("Lines of Code on GitHub", [(n(s["add"] - s["dele"]), "val"), (" ( ", "text"),
                                       (f'{n(s["add"])}++', "add"), (", ", "text"),
                                       (f'{n(s["dele"])}--', "dele"), (" )", "text")]),
    ]
    ascii_lines = (ROOT / "ascii.txt").read_text().splitlines()
    c = THEMES[theme]
    height = max(len(rows) * 20, len(ascii_lines) * 14) + 50
    right = "".join(f'<tspan x="400" y="{30 + i * 20}">{r}</tspan>' for i, r in enumerate(rows))
    left = "".join(f'<tspan x="15" y="{30 + i * 14}">{esc(l)}</tspan>' for i, l in enumerate(ascii_lines))
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="990" height="{height}" font-size="16px">
<style>
.ascii {{ fill: {c['text']}; font-family: ConsolasFallback, Consolas, 'Courier New', monospace; font-size: 12px; }}
.main  {{ fill: {c['text']}; font-family: ConsolasFallback, Consolas, 'Courier New', monospace; }}
.key {{ fill: {c['key']}; }} .val {{ fill: {c['val']}; }} .cc {{ fill: {c['cc']}; }}
.add {{ fill: {c['add']}; }} .dele {{ fill: {c['dele']}; }} .text {{ fill: {c['text']}; }}
</style>
<rect width="990" height="{height}" fill="{c['bg']}" rx="15"/>
<text class="ascii" xml:space="preserve">{left}</text>
<text class="main" xml:space="preserve">{right}</text>
</svg>
"""


LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
HEAT = {
    "dark_mode":  ["#2d333b", "#0e6b2f", "#1a8f3d", "#2ea043", "#56d364"],
    "light_mode": ["#e1e4e8", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
}
CELL, GAP, PAD, TOP = 11, 3, 15, 34
STEP = CELL + GAP
LEFT, MONTH_H = 28, 16  # weekday-label gutter, month-label strip above grid
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MIN_MONTH_GAP = 3  # columns between month labels
MORE_W = 30  # generous estimate of "More" at 11px, keeps legend squares clear of it


def build_heatmap(theme, s):
    c, colors = THEMES[theme], HEAT[theme]
    total = s["contrib_total"]
    weeks = max(len(s["calendar"]), 53)
    gx, gy = PAD + LEFT, TOP + MONTH_H
    width = gx + weeks * STEP - GAP + PAD
    grid_bottom = gy + 7 * STEP - GAP
    height = grid_bottom + 40
    font = "font-family=\"-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif\""
    lbl = f'fill="{c["text"]}" fill-opacity=".7" font-size="10" {font}'
    rects, months, prev_month, last_x = [], [], None, None
    for x, week in enumerate(s["calendar"]):
        if week:
            m = int(week[0]["date"][5:7])
            if m != prev_month and (last_x is None or x - last_x >= MIN_MONTH_GAP):
                months.append(f'<text x="{gx + x * STEP}" y="{TOP + 10}" {lbl}>{esc(MONTHS[m - 1])}</text>')
                last_x = x
            prev_month = m
        for d in week:
            wd = (datetime.strptime(d["date"], "%Y-%m-%d").weekday() + 1) % 7  # Sunday=0
            lvl = LEVELS.index(d["level"]) if d["level"] in LEVELS else 0
            label = f'{d["count"]} contribution{"" if d["count"] == 1 else "s"} on {d["date"]}'
            rects.append(f'<rect x="{gx + x * STEP}" y="{gy + wd * STEP}" width="{CELL}" height="{CELL}" '
                         f'rx="2" fill="{colors[lvl]}"><title>{esc(label)}</title></rect>')
    days = "".join(f'<text x="{gx - 6}" y="{gy + r * STEP + 9}" text-anchor="end" {lbl}>{esc(n)}</text>'
                   for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    ly = grid_bottom + 15
    more_x = width - PAD
    lx = more_x - MORE_W - 6 - (5 * STEP - GAP)  # left edge of first legend square
    legend = "".join(f'<rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{col}"/>'
                     for i, col in enumerate(colors))
    title = esc(f"{total:,} contributions in the last year")
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="{width}" height="{height}" fill="{c['bg']}" rx="15"/>
<text x="{PAD}" y="22" fill="{c['text']}" font-size="14" {font}>{title}</text>
{"".join(months)}{days}
{"".join(rects)}
<text x="{lx - 6}" y="{ly + 10}" fill="{c['text']}" font-size="11" text-anchor="end" {font}>Less</text>
{legend}
<text x="{more_x}" y="{ly + 10}" fill="{c['text']}" font-size="11" text-anchor="end" {font}>More</text>
</svg>
"""


GEN = ROOT / "assets" / "generated"
HEAT_FILES = {"dark_mode": GEN / "contrib_dark.svg", "light_mode": GEN / "contrib_light.svg"}
TILE_W, TILE_GAP, TILE_X = 216, 16, 28


def tile(s, x, y, w, h, label, value, sub=None, size=30):
    s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="card"/>')
    s.text(x + 16, y + 28, label, 13, "mu")
    s.text(x + 16, y + 28 + size + 8, value, size, "ac", True, bold=True)
    if sub:
        s.text(x + 16, y + h - 12, sub, 12, "mu")


def build_stats(s):
    n = lambda x: f"{x:,}"
    svg = Svg(1200, 290, "github stats")
    tiles = [("repositories", n(s["repos"]), f'+ {n(s["contributed"])} contributed to'),
             ("stars", n(s["stars"]), None), ("commits", n(s["commits"]), None),
             ("followers", n(s["followers"]), None),
             ("contributions", n(s["contrib_total"]), "last year")]
    for i, (lab, val, sub) in enumerate(tiles):
        tile(svg, TILE_X + i * (TILE_W + TILE_GAP), 20, TILE_W, 100, lab, val, sub)
    net, add, dele = s["add"] - s["dele"], f'+{s["add"]:,}', f'-{s["dele"]:,}'
    svg.add(f'<rect x="{TILE_X}" y="136" width="1144" height="134" rx="10" class="card" '
            'style="stroke:var(--ac)" stroke-width="1.5"/>')
    svg.text(TILE_X + 20, 164, "lines of code", 13, "mu")
    svg.text(TILE_X + 20, 210, n(net), 40, "ac", True, bold=True)
    end = svg.text(TILE_X + 20, 248, add, 18, "ok", True)
    svg.text(end + 24, 248, dele, 18, "bad", True)
    svg.label = (f"github stats: {n(s['repos'])} repositories, {n(s['stars'])} stars, {n(s['commits'])} commits, "
                 f"{n(s['followers'])} followers, {n(s['contrib_total'])} contributions in the last year, "
                 f"{n(net)} net lines of code ({add} {dele})")
    return svg.render()


def streak_stats(calendar, today=None):
    """(current, longest) from weeks->days. current may end today or yesterday."""
    days = [d for w in calendar for d in w]
    if today:
        days = [d for d in days if d["date"] <= today]
    days.sort(key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    if days and days[-1]["count"] == 0:
        days = days[:-1]  # today still in progress
    current = 0
    for d in reversed(days):
        if d["count"] <= 0:
            break
        current += 1
    return current, longest


def build_streak(s):
    cur, best = streak_stats(s["calendar"], date.today().isoformat())
    svg = Svg(1200, 150, f"streak: current {cur} days, longest {best} days, "
                         f"{s['contrib_total']:,} contributions in the last year")
    w = (1144 - 2 * TILE_GAP) // 3
    for i, (lab, val, sub) in enumerate([("current streak", cur, "days"), ("longest streak", best, "days"),
                                         ("total contributions", s["contrib_total"], "last year")]):
        tile(svg, TILE_X + i * (w + TILE_GAP), 20, w, 110, lab, f"{val:,}", sub, 38)
    return svg.render()


COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
LEG_COLS, LEG_W = 4, 280


def build_langs(s):
    langs = s.get("langs") or []
    total = sum(b for _, _, b in langs)
    if not total:
        svg = Svg(1200, 110, "top languages: no data")
        svg.text(28, 36, "top languages", 14, "mu", True)
        svg.text(600, 72, "no data", 16, "mu", False, "middle")
        return svg.render()
    rows = (len(langs) + LEG_COLS - 1) // LEG_COLS
    svg = Svg(1200, 90 + rows * 28, "top languages: " + ", ".join(
        f"{n} {b * 100 / total:.1f}%" for n, _, b in langs))
    svg.text(28, 34, "top languages", 14, "mu", True)
    bx, bw = 28, 1144
    svg.add(f'<clipPath id="bc"><rect x="{bx}" y="48" width="{bw}" height="14" rx="7"/></clipPath>'
            '<g clip-path="url(#bc)">')
    x = bx
    fills = [c if c and COLOR_RE.match(c) else OTHER_COLOR for _, c, _ in langs]
    for fill, (_, _, b) in zip(fills, langs):
        w = bw * b / total
        svg.add(f'<rect x="{x:.2f}" y="48" width="{w:.2f}" height="14" fill="{fill}"/>')
        x += w
    svg.add("</g>")
    for i, ((name, _, b), fill) in enumerate(zip(langs, fills)):
        lx, ly = 28 + (i % LEG_COLS) * LEG_W, 96 + (i // LEG_COLS) * 28
        svg.add(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{fill}"/>')
        svg.text(lx + 18, ly, f"{name} {b * 100 / total:.1f}%", 14, "tx")
    return svg.render()

if __name__ == "__main__":
    stats = fetch_stats()
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "stats.svg").write_text(build_stats(stats), encoding="utf-8")
    (GEN / "streak.svg").write_text(build_streak(stats), encoding="utf-8")
    (GEN / "langs.svg").write_text(build_langs(stats), encoding="utf-8")
    for theme in THEMES:
        (ROOT / f"{theme}.svg").write_text(build(theme, stats), encoding="utf-8")
        HEAT_FILES[theme].write_text(build_heatmap(theme, stats), encoding="utf-8")
    print("done:", {k: v for k, v in stats.items() if k not in ("calendar", "langs")})
