# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The source for the static website <https://pyoomph.github.io> (the pyoomph finite element framework's homepage). There is no site generator framework: pages are produced by `cat`-ing HTML fragments together, with two Python scripts injecting generated sections.

## Build

```bash
python -m pip install pybtex pybtex-docutils pillow beautifulsoup4 requests
bash gen_page.sh
```

`gen_page.sh` writes into `_generated/` and is the only build step. There are no tests, no linter, and no local dev server — open `_generated/index.html` in a browser to check output (relative paths to `css/` and `media/` resolve correctly from there).

Deployment is automatic: `.github/workflows/deploy.yml` runs the same commands on every push/PR to `main` and publishes `_generated/` to GitHub Pages via `JamesIves/github-pages-deploy-action`.

## How pages are assembled

Every page is `header.html` + body fragments + `footer.html`. Only those two files contain `<html>`/`<head>`/`<body>` — all other `*.html` files in the repo root are **fragments** and are invalid standalone HTML. The nav menu lives in `header.html`.

| Output | Composition |
|---|---|
| `_generated/index.html` | header + `index1.html` + `gen_example_gallery.py` output + `index2.html` + footer |
| `_generated/about.html` | header + `about.html` + `gen_pubs.py` output + footer |
| `_generated/installation.html` | header + `installation.html` + footer |

Both Python scripts write the HTML snippet to **stdout**; `gen_page.sh` splices it in via process substitution. Any diagnostic printing must go to stderr or it lands in the page.

## `gen_example_gallery.py`

Scrapes the tutorial overview table from <https://pyoomph.readthedocs.io/en/latest/>, downloads each thumbnail, resizes it to 200×150 with Pillow into `_generated/media/tutorial/`, and emits a `<ul class="horizontal-media-scroller">` gallery.

- **Requires network access.** It hard-fails if the readthedocs landing page does not contain exactly one `<table>` — i.e. an upstream docs layout change breaks the site build.
- `skip_image_download = False` near the top can be flipped to `True` to reuse already-downloaded thumbnails while iterating on markup.
- `test_gallery.html` is a saved copy of the upstream table, kept for offline styling experiments; it is not part of any build.

## `gen_pubs.py`

Renders `pubs.bib` into the numbered publication list on the About page.

- **Order is the literal order of entries in `pubs.bib`** — the year-based sort is deliberately disabled (see the commented-out line). Add new publications at the top of the file. The `<li value=...>` numbering counts down from the total.
- Every entry needs `year`; non-`incollection` entries also need `volume` and `pages` or the script raises and the build fails.
- Journal names are shortened via the `abbrevs` dict (lowercase key → abbreviation); add an entry there rather than editing the `.bib`. A `journal` starting with `arXiv` renders as *submitted*.
- PDF link: `eprint` (labelled "arXiv preprint" if the URL contains arxiv.org, else "Open Access"), otherwise a local `pdf/<citekey>.pdf` if present.

## Files under `_generated/` that are committed

`css/`, `media/` (minus `media/tutorial/`), `docs.html` and `pdf.html` (meta-refresh redirects to readthedocs), `google3a5a7a86d2ed869e.html` (Search Console verification) and `sitemap.xml` are hand-maintained and tracked in git. The build only *adds* the three page files plus `media/tutorial/` on top of them — never clean the directory.

The three built pages and the tutorial thumbnails are intentionally untracked (`.gitignore` is empty, so they show up in `git status`). Leave them uncommitted; CI regenerates them.
