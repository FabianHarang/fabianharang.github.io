# Writing and publication workflow

The public site is static HTML. Python 3 (standard library only) generates the shared navigation, homepage selections, bibliography, Writing index, articles and sitemap. GitHub Pages continues to serve the committed files from `main` at the repository root.

## Edit existing content

- Biography and research: `_source/pages/`.
- Bibliography and homepage paper selections: `_source/publications.json`. Keep original bylines and version-specific arXiv links. `preprint_year` is the first-posted year; `journal_ref` gives the separate journal citation. Record the primary metadata URL in `metadata_sources`.
- Existing writing listings: `_source/writing.json`.
- KI-fondet: `_source/articles/ai-fondet.html`. Preserve its URL, section IDs, coauthors, dates, references and embedded figures. Its structured metadata is in the adjacent JSON file. A layout edit does not change its substantive revision date.
- Shared layout: `_source/site.html` and `css/site.css`.

Run `python3 _tools/build.py` after editing sources. Commit the source and generated changes together; do not independently edit generated pages. Run `python3 _tools/build.py --check` and `python3 _tools/test_site.py` before a pull request. The article regression baseline in `_source/preservation.json` covers the original public text and assets. Change its expected values only after an intentional, author-approved content revision has been reviewed.

## Start a private note

This repository is public. Keep drafts, collaborator correspondence, private experiments and preview folders **outside the repository**. The blank `_source/note-template.json` contains no proposed scientific content.

1. Copy the template to a new external folder as `note.json`.
2. Fill in the title, stable lowercase slug, authors, language (`en`, `nb` or `nn`), kind (`research_note`, `expository_note` or `commentary`), summary and `body_html`. Keep `publication_state: "draft"` and `author_approved: false`.
3. Use `research_status: "exploratory"` or `"working_draft"` only where accurate; omit it for ordinary commentary. A status is not a peer-review designation.
4. In HTML, start headings at `h2`; the page title is generated. Use paragraphs, lists, descriptive links and ordinary citation links to inspected references. For equations, use native MathML with defined notation and an accompanying explanation. For code use `<pre><code>…</code></pre>` with escaped angle brackets. Wrap wide tables in `<div class="table-scroll" tabindex="0" role="region" aria-label="Descriptive table name">…</div>` for local keyboard scrolling.
5. Put images, notebooks and attachments in the note's folder and list their relative filenames in `assets`. Refer to them in HTML as `{{assets}}/filename.png`. Give images descriptive alt text; provide captions and sources. Only listed assets belonging to an approved note are copied. Never include private data in a notebook's saved outputs or attachments.

The gate requires both `publication_state == "published"` and `author_approved == true`. A public note must have a real title, slug, author list, supported language and kind, summary, body and ISO publication date. Missing assets, duplicate slugs and invalid metadata fail the build before output is written.

## Preview privately

Use a fresh external output folder each time:

```sh
python3 _tools/build.py --preview-note /absolute/private-note/note.json --output /tmp/harang-note-preview
python3 -m http.server 8000 --bind 127.0.0.1 --directory /tmp/harang-note-preview
```

Visit `http://127.0.0.1:8000/writing/notes/YOUR-SLUG.html`. Preview pages carry a draft banner. An absent publication date uses a clearly provisional date for layout only. The local interface is bound to the loopback address; do not expose it through a tunnel or upload the folder. A marker prevents reusing a private preview directory as a public build. `noindex` is only a secondary hint; privacy comes from keeping the folder local and outside the public repository.

## Approve and publish a note

Review claims, authorship, citations, maturity, data/attachment rights and any coauthor or student permissions. Confirm that experimental results were actually produced and that limitations are clear. Once the author has approved publication:

1. Set the real `date_published` (ISO `YYYY-MM-DD`), `publication_state: "published"`, and `author_approved: true`.
2. Copy **only the approved note and its listed assets** into `_source/notes/SLUG/note.json` and its folder. Never commit the private draft history. CI rejects unapproved notes in this public source folder.
3. Run the build and tests, inspect the generated page, homepage, Writing index, images, equations, references and mobile layout. The shared metadata updates all listings automatically.
4. Review the diff in a pull request. Merging into `main` is the production release; a feature-branch push and draft pull request do not publish the Pages site.

Do not invent a date or approval merely to pass validation. Preserve `date_published` on later edits; set `date_updated` only for substantive revisions. State material corrections in the note. For a withdrawal, prefer replacing the content with an author-approved explanation at the same URL, keeping the original date and linking to any replacement. Simply changing to draft removes the generated note and its listed assets on the next build, but **cannot erase public Git history or cached copies**.

## Public preview, hosting and rollback

`python3 _tools/build.py --output /tmp/harang-public-preview` exports only public pages and assets. Serve that directory locally, using the same command as above. Source files, tooling, metadata templates and this guide are excluded from GitHub Pages by `_config.yml`; private drafts must still never enter the public repository. CI runs the actual Jekyll Pages build and checks its exclusions before merge.

No current approved CV PDF is included. The site retains Request CV by email. Add a CV page/link only when the author supplies an approved public file; do not use the redesign date as its revision date.

After an approved release, verify the homepage, Research, Publications, Writing and `/ai/blog/ai-fondet.html` on the live domain. To roll back, revert the merge commit on `main` with GitHub's Revert action (or revert the squash commit), review that revert, and merge it. GitHub Pages rebuilds the previous version. Do not reset or force-push history. The pre-redesign baseline is commit `be75b9a`.
