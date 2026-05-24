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

`templates/publications_content.html` wird aus
`bibliography/pfaffelhuber.bib` erzeugt — die CI ruft dafür
`bibliography/make_bibhtml.py` vor dem Build auf. Wenn Du nur die
`.bib` änderst, reicht also auch ein Push; lokal regenerieren geht
mit `cd bibliography && python make_bibhtml.py`.
