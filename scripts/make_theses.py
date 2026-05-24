"""Generate per-topic LaTeX sources and an aggregated HTML include from
templates/theses/current/_*.md.

For every active thesis topic we
  * parse the Markdown source: first `# heading` becomes the subject,
    the rest is the body,
  * convert the body to HTML (Markdown -> HTML), then to LaTeX via a
    small in-house walker; MathJax `\\(...\\)` / `\\[...\\]` regions
    are stashed before Markdown sees them so the backslashes survive,
  * render the LaTeX wrapper template under _latex/ with subject +
    body, writing templates/theses/_latex/<slug>.tex (compiled by CI),
  * append the rendered HTML plus a "Download as PDF" link to
    templates/theses/_aggregated.html, which pfaffelhuber.html
    includes in its Theses accordion.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import markdown
from jinja2 import Template

REPO = Path(__file__).resolve().parent.parent
CURRENT_DIR = REPO / "templates" / "theses" / "current"
LATEX_DIR = REPO / "templates" / "theses" / "_latex"
AGGREGATE = REPO / "templates" / "theses" / "_aggregated.html"
WRAPPER = LATEX_DIR / "_wrapper.tex.j2"


# ---------- Markdown -> HTML, preserving MathJax math --------------------

MATH_PATTERN = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.DOTALL)
MATH_PLACEHOLDER = "@@@MATH{}@@@"


def md_to_html(text: str) -> str:
    stash: list[str] = []

    def stash_math(m: re.Match[str]) -> str:
        stash.append(m.group(0))
        return MATH_PLACEHOLDER.format(len(stash) - 1)

    protected = MATH_PATTERN.sub(stash_math, text)
    html = markdown.markdown(protected, extensions=["extra"])
    for i, math in enumerate(stash):
        html = html.replace(MATH_PLACEHOLDER.format(i), math)
    return html


def split_title_body(md_text: str) -> tuple[str, str]:
    """Pull the first `# heading` line off the top, return (title, body_md)."""
    lines = md_text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            body = "\n".join(lines[i + 1:]).strip()
            return title, body
    raise ValueError("Markdown source has no `# Title` line")


# ---------- HTML -> LaTeX (subset we actually use) -----------------------

LATEX_ESCAPES = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    """Escape LaTeX-special characters outside of inline/display math."""
    out: list[str] = []
    last = 0
    for m in MATH_PATTERN.finditer(text):
        out.append(_escape_plain(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_escape_plain(text[last:]))
    return "".join(out)


def _escape_plain(s: str) -> str:
    return "".join(LATEX_ESCAPES.get(c, c) for c in s)


class HTMLToLatex(HTMLParser):
    """Emit LaTeX from a thesis body (no <h1>; produced by markdown)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    @property
    def body(self) -> str:
        return "".join(self.parts).strip() + "\n"

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag == "p":
            return
        if tag == "a":
            self.parts.append(rf"\href{{{attrs.get('href', '')}}}{{")
        elif tag in ("em", "i"):
            self.parts.append(r"\emph{")
        elif tag in ("strong", "b"):
            self.parts.append(r"\textbf{")
        elif tag == "ul":
            self.parts.append("\n\\begin{itemize}\n")
        elif tag == "ol":
            self.parts.append("\n\\begin{enumerate}\n")
        elif tag == "li":
            self.parts.append("  \\item ")
        elif tag == "br":
            self.parts.append(r"\\ ")
        elif tag == "code":
            self.parts.append(r"\texttt{")
        elif tag == "pre":
            self.parts.append("\n\\begin{verbatim}\n")
        elif tag == "h1":
            # Shouldn't appear: caller already stripped the title heading.
            self.parts.append(r"\textbf{")

    def handle_endtag(self, tag: str) -> None:
        if tag == "p":
            self.parts.append("\n\n")
        elif tag in ("a", "em", "i", "strong", "b", "code", "h1"):
            self.parts.append("}")
        elif tag == "ul":
            self.parts.append("\n\\end{itemize}\n\n")
        elif tag == "ol":
            self.parts.append("\n\\end{enumerate}\n\n")
        elif tag == "pre":
            self.parts.append("\n\\end{verbatim}\n\n")
        elif tag == "li":
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(escape_latex(re.sub(r"\s+", " ", data)))


def html_to_latex(html: str) -> str:
    p = HTMLToLatex()
    p.feed(html)
    return p.body


# ---------- aggregated HTML include for the website ---------------------

def aggregated_entry(slug: str, body_html: str) -> str:
    return (
        f"<h5>{TITLES[slug]}</h5>\n"
        f"{body_html}\n"
        f'<p><a href="static/theses/{slug}.pdf">Download as PDF</a></p>\n'
    )


TITLES: dict[str, str] = {}


def main() -> None:
    wrapper = Template(WRAPPER.read_text(encoding="utf-8"))
    aggregate_entries: list[str] = []

    sources = sorted(CURRENT_DIR.glob("_*.md"))
    if not sources:
        print("No thesis Markdown sources found in", CURRENT_DIR)

    for md_path in sources:
        slug = md_path.stem.lstrip("_")
        title, body_md = split_title_body(md_path.read_text(encoding="utf-8"))
        body_html = md_to_html(body_md)
        body_latex = html_to_latex(body_html)

        tex_path = LATEX_DIR / f"{slug}.tex"
        tex_path.write_text(
            wrapper.render(subject=title, body=body_latex),
            encoding="utf-8",
        )

        TITLES[slug] = title
        aggregate_entries.append(aggregated_entry(slug, body_html))
        print(f"  {md_path.name}  ->  {tex_path.relative_to(REPO)}")

    AGGREGATE.write_text("<hr>\n".join(aggregate_entries), encoding="utf-8")
    print(f"Wrote {AGGREGATE.relative_to(REPO)} with {len(aggregate_entries)} entries.")


if __name__ == "__main__":
    main()
