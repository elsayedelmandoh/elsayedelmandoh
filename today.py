"""builds dark_mode.svg + light_mode.svg for the github profile readme.
needs env ACCESS_TOKEN (classic PAT: repo + read:user). no token = offline preview with dummy numbers.
"""
import os
from datetime import date, datetime
from html import escape
from pathlib import Path

import requests

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
TOKEN = os.environ.get("ACCESS_TOKEN")


def gql(query, variables):
    r = requests.post(API, json={"query": query, "variables": variables},
                      headers={"Authorization": f"bearer {TOKEN}"}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def fetch_stats():
    if not TOKEN:
        print("no ACCESS_TOKEN -> offline preview with dummy numbers")
        return dict(repos=0, contributed=0, stars=0, commits=0, followers=0, add=0, dele=0,
                    contrib_total=0, calendar=[])

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

    return dict(repos=u["repositories"]["totalCount"],
                contributed=u["repositoriesContributedTo"]["totalCount"],
                stars=stars, commits=commits, followers=u["followers"]["totalCount"],
                add=add, dele=dele, contrib_total=cal["totalContributions"], calendar=calendar)


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


def build_heatmap(theme, s):
    c, colors = THEMES[theme], HEAT[theme]
    total = s["contrib_total"]
    weeks = max(len(s["calendar"]), 53)
    width = PAD * 2 + weeks * STEP - GAP
    grid_bottom = TOP + 7 * STEP - GAP
    height = grid_bottom + 40
    rects = []
    for x, week in enumerate(s["calendar"]):
        for d in week:
            wd = (datetime.strptime(d["date"], "%Y-%m-%d").weekday() + 1) % 7  # Sunday=0
            lvl = LEVELS.index(d["level"]) if d["level"] in LEVELS else 0
            label = f'{d["count"]} contribution{"" if d["count"] == 1 else "s"} on {d["date"]}'
            rects.append(f'<rect x="{PAD + x * STEP}" y="{TOP + wd * STEP}" width="{CELL}" height="{CELL}" '
                         f'rx="2" fill="{colors[lvl]}"><title>{esc(label)}</title></rect>')
    ly = grid_bottom + 15
    lx = width - PAD - 5 * STEP + GAP
    legend = "".join(f'<rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{col}"/>'
                     for i, col in enumerate(colors))
    font = "font-family=\"-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif\""
    title = esc(f"{total:,} contributions in the last year")
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="{width}" height="{height}" fill="{c['bg']}" rx="15"/>
<text x="{PAD}" y="22" fill="{c['text']}" font-size="14" {font}>{title}</text>
{"".join(rects)}
<text x="{lx - 6}" y="{ly + 10}" fill="{c['text']}" font-size="11" text-anchor="end" {font}>Less</text>
{legend}
<text x="{lx + 5 * STEP + 3}" y="{ly + 10}" fill="{c['text']}" font-size="11" {font}>More</text>
</svg>
"""


HEAT_FILES = {"dark_mode": "contrib_dark.svg", "light_mode": "contrib_light.svg"}

if __name__ == "__main__":
    stats = fetch_stats()
    for theme in THEMES:
        (ROOT / f"{theme}.svg").write_text(build(theme, stats), encoding="utf-8")
        (ROOT / HEAT_FILES[theme]).write_text(build_heatmap(theme, stats), encoding="utf-8")
    print("done:", stats)
