import os
from pybtex.database.input import bibtex
from jinja2 import FileSystemLoader, Template

BIBFILE = "own-bib.bib"
TEMPLATE = "simple.html"
HTMLFile = "../templates/publications_content.html"

def decode_latex(text):
    """ Wandelt LaTeX-Akzente und andere Befehle in Unicode um """
    print(text)
    try:
        return text.encode("latex").decode("latex")
    except:
        return text
    
    
def format_authors(persons):
    """ Formatiert Autorennamen mit Initialen """
    authors = []
    for person in persons:
        first_initials = " ".join([name[0] + "." for name in person.get_part_as_text("first").split()])
        last_name = person.get_part_as_text("last")
        authors.append(f"{last_name}, {first_initials}")
    return decode_latex(", ".join(authors))

# BibTeX-Datei einlesen
def get_bibdata(bib_data):
    data = []
    for key, entry in bib_data.entries.items():
        data.append({
            "ID": key,
            "type" : entry.type,
            "author": format_authors(entry.persons.get("author", [])),
            "title": decode_latex(entry.fields.get("title", "Kein Titel")),
            "journal": entry.fields.get("journal", ""),
            "volume": entry.fields.get("volume", ""),
            "pages": entry.fields.get("pages", ""),
            "year": entry.fields.get("year", ""),
            "note": entry.fields.get("note", ""),
            "url": entry.fields.get("journal_url", ""),
        })
    entries = sorted(data, key=lambda x: (-int(x["year"]), x["author"]))
    return entries


parser = bibtex.Parser()
with open(BIBFILE, 'r', encoding='utf-8') as f:
    bib_content = f.read()  # 🔹 Dateiinhalt als String
    bib_data = parser.parse_string(bib_content)  # 🔹 Direkt in parse_string()
    entries = get_bibdata(bib_data)
print(entries)

# Lese den rohen Inhalt des Templates mit dem Loader
with open(TEMPLATE, 'r', encoding='utf-8') as f:
    template_content = f.read()

# Erstelle das Template-Objekt direkt aus dem geladenen Inhalt
template = Template(template_content)
rendered_html = template.render({'entries': entries})

# HTML-Datei speichern
with open(HTMLFile, "w", encoding="utf-8") as f:
    f.write(rendered_html)

print(f"🎉 HTML-Seite erfolgreich generiert: {HTMLFile}")
print(f"Es wurden {len(entries)} Einträge verarbeitet.")