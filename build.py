import sys
from staticjinja import Site

if __name__ == "__main__":
    watch = "--watch" in sys.argv
    site = Site.make_site(
        searchpath="templates",
        outpath="_site",
        staticpaths=["static/"],
    )
    site.render(use_reloader=watch)
