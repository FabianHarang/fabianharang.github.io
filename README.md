# Fabian Nøst Harang

Static personal website for [www.fabianharang.no](https://www.fabianharang.no).

## Build and preview

```sh
python3 _tools/build.py
python3 _tools/build.py --check
python3 _tools/test_site.py
python3 _tools/build.py --output /tmp/harang-public-preview
python3 -m http.server 8000 --bind 127.0.0.1 --directory /tmp/harang-public-preview
```

Python 3's standard library is sufficient. There is no browser application framework or client-side content loader. See [AUTHORING.md](AUTHORING.md) for the note template, private previews, approval gate, publication and rollback workflow.

## Structure

```text
index.html
research.html
publications.html
writing.html
assets/
css/
ai/blog/
_source/     # approved content and templates, excluded from Pages
_tools/      # generator and validation, excluded from Pages
robots.txt
sitemap.xml
```

The site is published with GitHub Pages from `main` at `/`. Generated HTML is committed alongside its source. Feature branches and pull requests are for review; merging into `main` publishes the site. Keep unpublished drafts outside this public repository.
