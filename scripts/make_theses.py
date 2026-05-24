"""Generate LaTeX sources and an aggregated HTML include from
templates/theses/current/_*.html.

For every active thesis topic partial we
  * convert the HTML body into LaTeX (small subset: p / a / em / strong /
    ul/li, MathJax \\(..\\) and \\[..\\] passed through, Unicode kept for
    xelatex),
  * render templates/theses/_latex/_wrapper.tex.j2 with the title +
    converted body and write templates/theses/_latex/<slug>.tex,
  * append the partial plus a "Download as PDF" link to
    templates/theses/_aggregated.html, which pfaffelhuber.html includes
    into its Theses accordion.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from jinja2 import Template

REPO = Path(__file__).resolve().parent.parent
CURRENT_DIR = REPO / "templates" / "theses" / "current"
LATEX_DIR = REPO / "templates" / "theses" / "_latex"
AGGREGATE = REPO / "templates" / "theses" / "_aggregated.html"
WRAPPER = LATEX_DIR / "_wrapper.tex.j2"


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

MATH_PATTERN = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.DOTALL)


def escape_latex(text: str) -> str:
    """Escape LaTeX-special characters, but leave inline math `\\(...\\)`
    (and display math `\\[...\\]`) untouched."""
    out = []
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
    """Walk a thesis partial and emit (title, body_latex)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.body_parts: list[str] = []
        self._in_title = False
        self._target = self.body_parts

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()

    @property
    def body(self) -> str:
        return "".join(self.body_parts).strip() + "\n"

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag == "h5":
            self._in_title = True
            self._target = self.title_parts
        elif tag == "p":
            pass
        elif tag == "a":
            href = attrs.get("href", "")
            self._target.append(rf"\href{{{href}}}{{")
        elif tag in ("em", "i"):
            self._target.append(r"\emph{")
        elif tag in ("strong", "b"):
            self._target.append(r"\textbf{")
        elif tag == "ul":
            self._target.append("\n\\begin{itemize}\n")
        elif tag == "ol":
            self._target.append("\n\\begin{enumerate}\n")
        elif tag == "li":
            self._target.append("  \\item ")
        elif tag == "br":
            self._target.append(r"\\ ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "h5":
            self._in_title = False
            self._target = self.body_parts
        elif tag == "p":
            self._target.append("\n\n")
        elif tag in ("a", "em", "i", "strong", "b"):
            self._target.append("}")
        elif tag == "ul":
            self._target.append("\n\\end{itemize}\n\n")
        elif tag == "ol":
            self._target.append("\n\\end{enumerate}\n\n")
        elif tag == "li":
            self._target.append("\n")

    def handle_data(self, data: str) -> None:
        # Collapse internal whitespace runs to single spaces, keep paragraph
        # boundaries via the explicit <p> handling above.
        text = re.sub(r"\s+", " ", data)
        self._target.append(escape_latex(text))


def convert(html_path: Path) -> tuple[str, str]:
    parser = HTMLToLatex()
    parser.feed(html_path.read_text(encoding="utf-8"))
    return parser.title, parser.body


def aggregated_snippet(slug: str, partial_name: str) -> str:
    return (
        f"{{% include 'theses/current/{partial_name}' %}}\n"
        f'<p><a href="static/theses/{slug}.pdf">Download as PDF</a></p>\n'
    )


def main() -> None:
    wrapper = Template(WRAPPER.read_text(encoding="utf-8"))
    aggregate_lines: list[str] = []

    partials = sorted(CURRENT_DIR.glob("_*.html"))
    if not partials:
        print("No thesis partials found in", CURRENT_DIR)

    for html_path in partials:
        slug = html_path.stem.lstrip("_")
        title, body = convert(html_path)
        tex_path = LATEX_DIR / f"{slug}.tex"
        tex_path.write_text(
            wrapper.render(subject=title, body=body),
            encoding="utf-8",
        )
        aggregate_lines.append(aggregated_snippet(slug, html_path.name))
        print(f"  {html_path.name}  ->  {tex_path.relative_to(REPO)}")

    AGGREGATE.write_text("<hr>\n".join(aggregate_lines), encoding="utf-8")
    print(f"Wrote {AGGREGATE.relative_to(REPO)} with {len(aggregate_lines)} entries.")


if __name__ == "__main__":
    main()
