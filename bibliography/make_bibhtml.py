import re
from pathlib import Path
import latexcodec  # noqa: F401  -- registers the "latex" codec used below
from pybtex.database.input import bibtex
from jinja2 import Template

TEMPLATE = "simple.html"
OUTDIR = Path("../templates")
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
        first_initials = " ".join(
            [name[0] + "." for name in person.get_part_as_text("first").split()]
        )
        last_name = person.get_part_as_text("last")
        authors.append(f"{last_name}, {first_initials}")
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
    return sorted(data, key=lambda x: (-int(x["year"]), x["author"]))


def render(bibfile, outfile, template):
    parser = bibtex.Parser()
    with open(bibfile, "r", encoding="utf-8") as f:
        bib_data = parser.parse_string(f.read())
    entries = get_bibdata(bib_data)
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(template.render({"entries": entries}))
    print(f"Generated {outfile} with {len(entries)} entries.")


if __name__ == "__main__":
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = Template(f.read())
    for bibfile in sorted(Path(".").glob("*.bib")):
        outfile = OUTDIR / OUTPATTERN.format(stem=bibfile.stem)
        render(bibfile, outfile, template)
