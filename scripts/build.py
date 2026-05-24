"""Render the Jinja templates with staticjinja.

Paths resolve relative to this file's location, so you can run the
script from anywhere — `python scripts/build.py` from the repo root
or `python build.py --watch` from inside `scripts/` both work.

With --watch the renderer keeps running and rebuilds on every change
under templates/; otherwise it does a single one-shot build. Assets
under static/ are not handled here — the CI workflow (or you, locally)
copies `static/` into `_site/static/` after the render.
"""

import sys
from pathlib import Path

from staticjinja import Site

REPO = Path(__file__).resolve().parent.parent


if __name__ == "__main__":
    watch = "--watch" in sys.argv
    site = Site.make_site(
        searchpath=str(REPO / "templates"),
        outpath=str(REPO / "_site"),
    )
    site.render(use_reloader=watch)
