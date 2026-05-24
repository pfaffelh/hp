"""Render publications_content_<stem>.html for each bibliography/*.bib file.

Run from the repository root, or anywhere else — paths are resolved
relative to this file's location.
"""

import re
from pathlib import Path

import latexcodec  # noqa: F401  -- registers the "latex" codec used below
from jinja2 import Template
from pybtex.database.input import bibtex

REPO = Path(__file__).resolve().parent.parent
BIB_DIR = REPO / "bibliography"
OUTDIR = REPO / "templates"
TEMPLATE = OUTDIR / "_simple.html"
OUTPATTERN = "publications_content_{stem}.html"


def decode_latex(text):
    try:
        decoded = text.encode("ascii").decode("latex")
    except Exception:
        decoded = text
    return re.sub(r"[{}]", "", decoded)


def format_authors(persons):
    authors = []
    for person in persons:
        last = person.get_part_as_text("last").strip()
        first = person.get_part_as_text("first").strip()
        # BibTeX convention: `... and others` becomes a person with name "others"
        if last == "others" and not first:
            authors.append("et al.")
            continue
        first_initials = " ".join(n[0] + "." for n in first.split())
        authors.append(f"{last}, {first_initials}" if first_initials else last)
    return decode_latex(", ".join(authors))


def get_bibdata(bib_data):
    data = []
    for key, entry in bib_data.entries.items():
        data.append({
            "ID":      key,
            "type":    entry.type,
            "author":  format_authors(entry.persons.get("author", [])),
            "title":   decode_latex(entry.fields.get("title", "Kein Titel")),
            "journal": entry.fields.get("journal", ""),
            "volume":  entry.fields.get("volume", ""),
            "number":  entry.fields.get("number", ""),
            "pages":   entry.fields.get("pages", ""),
            "year":    entry.fields.get("year", ""),
            "note":    entry.fields.get("note", ""),
            "url":     entry.fields.get("journal_url", ""),
        })
    return sorted(
        data,
        key=lambda x: (
            0 if x["journal"].strip().lower() == "submitted" else 1,
            -int(x["year"]),
            x["author"],
        ),
    )


def render(bibfile, outfile, template):
    parser = bibtex.Parser()
    with open(bibfile, "r", encoding="utf-8") as f:
        bib_data = parser.parse_string(f.read())
    entries = get_bibdata(bib_data)
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(template.render({"entries": entries}))
    print(f"Generated {outfile.relative_to(REPO)} with {len(entries)} entries.")


if __name__ == "__main__":
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    for bibfile in sorted(BIB_DIR.glob("*.bib")):
        outfile = OUTDIR / OUTPATTERN.format(stem=bibfile.stem)
        render(bibfile, outfile, template)
