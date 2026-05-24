# TODO

Offene Punkte nach dem UFR-Theme-Umbau.

## Inhalte fehlen

- **2025WS Measure Theory — Lösungen**: die Übungstabelle verlinkt
  `static/2025WS_measure_theory/Tutorial1_Sol.pdf` … `Tutorial14_Sol.pdf`,
  diese Dateien fehlen aber im Verzeichnis (nur die Aufgabenblätter
  sind hochgeladen).

## Verwaiste Root-HTMLs (alte Pre-UFR-Theme-Optik, kein Template)

Diese Dateien sind aus dem neuen Menü nicht mehr verlinkt, existieren
aber noch im Root und haben das alte Layout. Jeweils entscheiden:
löschen oder als Template ins neue Layout überführen.

- `about.html`
- `projects.html`
- `mypapers.html`
- `2024ss_wtheorie.html`, `2024ws_stochproc.html` (frühere Kursseiten)
- `heinzel copy.html` (offensichtlich ein Backup, kann weg)

## Layout / Hygiene

- **Pro-Seite-`<title>`**: aktuell trägt jede Seite denselben festen
  Titel. Alle 15 Kind-Templates enthalten zwar
  `{% block title %}Home{% endblock %}`, aber `_base.html` definiert
  den Block bewusst nicht (sonst würde überall „Home" stehen). Wenn
  pro-Seite-Titel gewünscht: Block in `_base.html` definieren und in
  jedem Kind-Template eine sinnvolle Überschrift setzen.
- **Bilder-Metadaten auf Personen-Seiten**: `alt="nn"`,
  `title="nn_bild"` (Platzhalter aus dem alten WP-Export). Sollten
  durch echte Personennamen ersetzt werden (Accessibility).
- **Heinzels Foto**: `ec-hinzel-carola-1536x1152.jpg` ist Querformat
  und wirkt neben den Hochformat-Bildern der anderen klein. Entweder
  ein neues Hochformat-Foto oder `object-fit: cover` in einem festen
  270×355-Rahmen (würde am Rand leicht zuschneiden).
- **`<center>`-Tags** in den Kursseiten um die YouTube-iframes —
  deprecated, ginge mit `class="text-center"` o.ä.
- **Alte Theme-Assets aufräumen** (werden vom neuen Layout nicht
  mehr genutzt):
  - `static/unitheme.css` / `templates/static/unitheme.css` (altes
    UFR-WP-Theme)
  - `static/Bilder/plus-svgrepo-com.svg`,
    `static/Bilder/cross-svgrepo-com.svg` (Plus/Cross-Icons des
    alten Bootstrap-Akkordeons)
- **`static/Bilder/Stiefel.jpg`** ist im Repo, aber `stiefel.html`
  zeigt `nn.png`. Foto einbinden oder löschen.

## Hinweise (kein TODO, nur Doku)

- Die 2025WS-Vorlesung verwendet bewusst die 2024er-Folien und
  -Videos — die Links zeigen daher auf `static/2024WS_measure_theory/`
  (Folien-PDFs liegen nicht doppelt vor).
- `templates/publications_content.html` bleibt — wird von
  `bibliography/make_bibhtml.py` aus `bibliography/own-bib.bib`
  erzeugt und in `pfaffelhuber.html`s Publications-Akkordeon per
  `{% include %}` eingebunden.
