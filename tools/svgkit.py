"""tiny svg helper shared by tools/build_assets.py and today.py (stdlib only).
one file per asset: css variables = light by default, dark via prefers-color-scheme."""
from html import escape as esc

SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CHAR_W = 0.6  # width estimate per char, in em

CSS = f"""svg{{--bg:#f6f8fa;--bd:#d0d7de;--tx:#1f2328;--mu:#656d76;--ac:#0969da;--ac2:#0891b2;--ok:#1a7f37;--bad:#cf222e;--g1:#ffffff;--g2:#dbeafe}}
@media (prefers-color-scheme: dark){{svg{{--bg:#161b22;--bd:#30363d;--tx:#e6edf3;--mu:#8b949e;--ac:#38bdf8;--ac2:#22d3ee;--ok:#3fb950;--bad:#f85149;--g1:#0d1117;--g2:#0c2a43}}}}
text{{font-family:{SANS}}}
.m{{font-family:{MONO}}}
.b{{font-weight:700}}
.tx{{fill:var(--tx)}}.mu{{fill:var(--mu)}}.ac{{fill:var(--ac)}}.ok{{fill:var(--ok)}}.bad{{fill:var(--bad)}}
.card{{fill:var(--bg);stroke:var(--bd)}}
.chip{{fill:none;stroke:var(--ac)}}
.bar{{fill:var(--ac)}}
.ln{{stroke:var(--bd);fill:none}}"""


SANS_W = 0.48  # avg lowercase advance for system sans fonts; mono keeps CHAR_W


def text_width(t, size, mono=True):
    return (CHAR_W if mono else SANS_W) * size * len(t)


class Svg:
    def __init__(self, w, h, label, frame=True, rx=12):
        self.w, self.h, self.label, self.parts = w, h, label, []
        if frame:
            self.add(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx}" class="card"/>')

    def add(self, xml):
        self.parts.append(xml)

    def text(self, x, y, t, size=14, cls="tx", mono=False, anchor="start", bold=False):
        wd = text_width(t, size, mono)
        lo, hi = {"start": (x, x + wd), "middle": (x - wd / 2, x + wd / 2), "end": (x - wd, x)}[anchor]
        assert lo >= 0 and hi <= self.w, f"text overflows {self.w}px: {t!r} ({lo:.0f}..{hi:.0f})"
        c = " ".join([cls] + (["m"] if mono else []) + (["b"] if bold else []))
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        self.add(f'<text x="{x:g}" y="{y:g}" font-size="{size}" class="{c}"{a}>{esc(t)}</text>')
        return hi

    def chip(self, x, y, label, size=12, pad=10, h=24):
        """pill with accent border; returns right edge x."""
        wd = text_width(label, size) + 2 * pad
        assert x + wd <= self.w, f"chip overflows: {label!r}"
        self.add(f'<rect x="{x:g}" y="{y:g}" width="{wd:g}" height="{h}" rx="{h / 2:g}" class="chip"/>')
        self.text(x + wd / 2, y + h / 2 + size * 0.35, label, size, "tx", True, "middle")
        return x + wd

    def render(self):
        return (f"<?xml version='1.0' encoding='UTF-8'?>\n"
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.label, quote=True)}">\n'
                f"<title>{esc(self.label)}</title>\n<style>\n{CSS}\n</style>\n"
                + "\n".join(self.parts) + "\n</svg>\n")
