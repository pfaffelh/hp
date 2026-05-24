# Personal Homepage Peter Pfaffelhuber

Die Seite wird per GitHub Actions aus den Templates gebaut und auf
GitHub Pages deployt: bei jedem Push auf `master` läuft
`.github/workflows/deploy.yml` und veröffentlicht das Ergebnis unter
[pfaffelh.github.io/hp](https://pfaffelh.github.io/hp/).

## Eine Änderung veröffentlichen

1. Template in `templates/` bearbeiten.
2. `git add templates/...; git commit -m "..."; git push`
3. Nach ein paar Sekunden/Minuten ist die neue Version live. Status
   siehst Du unter dem „Actions"-Tab des Repos.

## Lokal vorschauen, bevor man pusht

```bash
python3 build.py --watch
```

Rendert die Templates nach `_site/` und beobachtet sie auf
Änderungen. Vorschau im Browser über `_site/index.html` öffnen (oder
`python3 -m http.server -d _site` und dann
<http://localhost:8000>).

Mit Ctrl-C beenden. Das `_site/`-Verzeichnis ist gitignored.

## Publikationsliste

`templates/publications_content_*.html` werden aus
`bibliography/*.bib` erzeugt — die CI ruft dafür
`scripts/make_bibhtml.py` vor dem Build auf (Template: `bibliography/simple.html`).
Wenn Du nur die `.bib` änderst, reicht also auch ein Push; lokal
regenerieren geht mit `python scripts/make_bibhtml.py`.

## Abschlussarbeiten-Themen

Aktive Themen liegen als Markdown unter `templates/theses/current/_*.md`.
Erste Zeile `# Titel (Monat Jahr)`, der Rest beliebiges Markdown
(`[Text](URL)`, `*Hervorhebung*`, Bullet-Listen, MathJax `\(...\)`).

`scripts/make_theses.py` (läuft in CI vor dem Build) erzeugt daraus
- den aggregierten HTML-Block, der in Pfaffelhubers Theses-Akkordeon
  eingeblendet wird,
- eine LaTeX-Datei je Thema unter `templates/theses/_latex/<slug>.tex`,
  die anschließend zu einem CD-konformen PDF kompiliert und unter
  `static/theses/<slug>.pdf` ausgeliefert wird (Download-Link im
  Akkordeon).

Lokal regenerieren: `python scripts/make_theses.py`.

Thema abgeben: `.md`-Datei nach `templates/theses/archive/` verschieben.
