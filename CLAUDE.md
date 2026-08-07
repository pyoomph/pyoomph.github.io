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

Deployment is automatic once a change reaches `main` — see [Publishing](#publishing) below.

## Publishing

The live site is served from **`pyoomph/pyoomph.github.io`**, which is the `upstream` remote. `origin` is the fork `cdiddens/pyoomph.github.io`. Check with `git remote -v` before pushing anywhere — a push to `upstream/main` publishes immediately, with no review step.

The established flow (how PRs #19–#21 landed):

1. Commit the change — on a feature branch, or on the fork's `main`; both have been used.
2. `git push -u origin <branch>`
3. `gh pr create --repo pyoomph/pyoomph.github.io --base main --head cdiddens:<branch>`
4. Merge the PR. **Merging is what publishes the site**, so it is the user's call, not something to do unprompted.

The merge pushes to `upstream/main`, which triggers `.github/workflows/deploy.yml`: it installs the dependencies, runs `gen_page.sh` and force-pushes `_generated/` to the `gh-pages` branch via `JamesIves/github-pages-deploy-action`. That run takes ~20 s and is followed by GitHub's own "pages build and deployment" run. Check both with `gh run list --repo pyoomph/pyoomph.github.io`.

**On a PR the workflow builds but does not deploy.** `deploy.yml` triggers on `pull_request` to `main` as well as on push, but the deploy step is gated with `if: github.event_name != 'pull_request'`. So the PR check verifies that `gen_page.sh` still succeeds — a red X there means the build is genuinely broken, e.g. an upstream docs layout change tripping `gen_example_gallery.py` — and publishing happens only on the push to `main` after the merge.

That gate exists because a PR from a fork gets a read-only `GITHUB_TOKEN` regardless of the `permissions: contents: write` declaration; before it was added, every fork PR (#19–#22) ended with a 403 on the push to `gh-pages` and a red X that meant nothing.

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

## Finding new publications for `pubs.bib`

The About page lists publications that **use** pyoomph, which is a smaller set than the publications that *cite* it. New entries are found by looking at what cites the main paper (Diddens & Rocha, J. Comput. Phys. **518**, 113306, 2024, `10.1016/j.jcp.2024.113306`) and then screening each candidate.

1. **Collect citing works.** Three DOI-based indexes, all open and without authentication — query all three, they disagree:

   ```bash
   # OpenAlex (W4401074401 is the JCP paper)
   curl -sS "https://api.openalex.org/works?filter=cites:W4401074401&per-page=200"
   # Semantic Scholar
   curl -sS "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.jcp.2024.113306/citations?fields=title,year,externalIds,venue,authors&limit=100"
   # OpenCitations (-L is required, the endpoint redirects)
   curl -sSL "https://opencitations.net/index/coci/api/v1/citations/10.1016/j.jcp.2024.113306"
   ```

   Merge and dedupe on DOI. The same work routinely appears twice — as preprint (arXiv, SSRN) and as published version — and OpenAlex sometimes holds two records for one DOI. Because all three indexes are DOI-based, theses and non-DOI preprints are invisible to them; Google Scholar reports a somewhat higher count for that reason.

2. **Subtract** what is already in `pubs.bib` and what is already listed in **`pubs_excluded.md`** — both match on DOI, `grep -i` is enough.

3. **Screen the remainder**: the paper must actually *use* pyoomph, not merely cite it. Papers citing the JCP paper for bifurcation tracking, Marangoni modelling or multiphysics coupling in general are common and usually do not use the framework.

4. **Add** what passes to the top of `pubs.bib` (order is literal, see `gen_pubs.py` above), and **append what fails** to `pubs_excluded.md` with the date, so it is not screened again.

## Files under `_generated/` that are committed

`css/`, `media/` (minus `media/tutorial/`), `docs.html` and `pdf.html` (meta-refresh redirects to readthedocs), `google3a5a7a86d2ed869e.html` (Search Console verification) and `sitemap.xml` are hand-maintained and tracked in git. The build only *adds* the three page files plus `media/tutorial/` on top of them — never clean the directory.

The three built pages and the tutorial thumbnails are intentionally untracked (`.gitignore` is empty, so they show up in `git status`). Leave them uncommitted; CI regenerates them.
