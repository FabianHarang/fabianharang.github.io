#!/usr/bin/env python3
"""Generate committed static HTML. Python standard library only; no runtime JS."""
import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import shutil
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_source'
SITE = 'https://www.fabianharang.no'
NAME = 'Fabian Nøst Harang'
LINKS = {
    'bi_url': 'https://www.bi.no/en/about-bi/employees/department-of-data-science-and-analytics/fabian-andsem-harang/',
    'amor_url': 'https://www.bi.no/en/research/centres-groups-and-other-initiatives/center-for-applied-mathematics-and-operations-research/',
    'scholar_url': 'https://scholar.google.com/citations?user=BgOf4TgAAAAJ&hl=no',
    'arxiv_url': 'https://arxiv.org/search/?query=%22Fabian+Harang%22&searchtype=author&abstracts=show&order=-announced_date_first&size=50',
}
KINDS = {'research_note': 'Research note', 'expository_note': 'Expository note', 'commentary': 'Commentary'}
LANGUAGES = {'en': 'English', 'nb': 'Norwegian Bokmål', 'nn': 'Norwegian Nynorsk'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def shell(title, description, body, route, active='', language='en', extra=''):
    navigation = ' '.join(
        f'<a href="{href}"' + (' aria-current="page"' if label == active else '') + f'>{label}</a>'
        for label, href in [('Home', '/'), ('Research', '/research.html'),
                            ('Publications', '/publications.html'), ('Writing', '/writing.html')])
    return Template((SOURCE / 'site.html').read_text()).substitute(
        language=language, title=escape(title), description=escape(description, quote=True),
        canonical=SITE + route, body=body, navigation=navigation, head_extra=extra)


def publication(item):
    venue = item.get('journal_ref') or (item['venue'] if not item.get('code') else '')
    status = 'Published' if item.get('journal_ref') or item.get('doi') else 'arXiv record'
    year = f"First posted {item['preprint_year']}"
    links = f'<a href="{escape(item["arxiv"], quote=True)}">arXiv</a>'
    if item.get('doi'):
        links = f'<a href="https://doi.org/{escape(item["doi"], quote=True)}">Paper</a> · ' + links
    if item.get('code'):
        links += f' · <a href="{escape(item["code"], quote=True)}">Code</a>'
    return (f'<li id="{item["id"]}"><h3><a href="{escape(item["arxiv"], quote=True)}">{escape(item["title"])}</a></h3>'
            f'<p class="authors">{escape(item["authors"])}</p><p class="metadata">{status} · {year}</p>'
            + (f'<p class="venue">{escape(venue)}</p>' if venue else '')
            + f'<p class="paper-links">{links}</p>'
            + (f'<p>{escape(item["summary"])}</p>' if item.get('summary') else '') + '</li>')


def publication_list(items):
    return '<ul class="publication-list">' + ''.join(publication(p) for p in items) + '</ul>'


def validate_note(note, path):
    for field in ['title', 'slug', 'summary', 'body_html']:
        if not isinstance(note.get(field), str) or not note[field].strip():
            raise ValueError(f'{path}: missing {field}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', note['slug']):
        raise ValueError(f'{path}: slug must use lowercase words and hyphens')
    if not isinstance(note.get('authors'), list) or not note['authors'] or any(
            not isinstance(a, str) or not a.strip() for a in note['authors']):
        raise ValueError(f'{path}: supply confirmed authors')
    if note.get('language') not in LANGUAGES or note.get('kind') not in KINDS:
        raise ValueError(f'{path}: invalid language or kind')
    if note.get('research_status') not in [None, '', 'exploratory', 'working_draft']:
        raise ValueError(f'{path}: invalid research_status')
    try:
        published = date.fromisoformat(note['date_published'])
        if note.get('date_updated') and date.fromisoformat(note['date_updated']) < published:
            raise ValueError('revision precedes publication')
    except (ValueError, TypeError, KeyError) as error:
        raise ValueError(f'{path}: valid publication/revision dates required') from error
    if re.search(r'<h1\b', note['body_html'], re.I):
        raise ValueError(f'{path}: body headings start at h2; title is generated')
    assets = note.get('assets', [])
    if not isinstance(assets, list):
        raise ValueError(f'{path}: assets must be a list of relative file paths')
    for asset in assets:
        if not isinstance(asset, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', asset):
            raise ValueError(f'{path}: invalid asset path')
        candidate = (path.parent / asset).resolve()
        if not candidate.is_relative_to(path.parent.resolve()) or not candidate.is_file() or candidate.suffix in ['.html', '.js']:
            raise ValueError(f'{path}: missing or unsafe asset {asset}')


def public_notes(directory):
    notes = []
    slugs = set()
    for path in sorted(directory.glob('*/note.json')):
        note = read_json(path)
        if note.get('publication_state') not in ['draft', 'published'] or type(note.get('author_approved')) is not bool:
            raise ValueError(f'{path}: explicit publication_state and boolean author_approved required')
        if note['publication_state'] != 'published' or note['author_approved'] is not True:
            continue
        validate_note(note, path)
        if note['slug'] in slugs:
            raise ValueError(f'{path}: duplicate slug')
        slugs.add(note['slug'])
        notes.append((note, path))
    return sorted(notes, key=lambda pair: pair[0]['date_published'], reverse=True)


def note_body(note):
    maturity = {'exploratory': 'Exploratory note', 'working_draft': 'Working draft'}.get(note.get('research_status'))
    metadata = [KINDS[note['kind']], ', '.join(note['authors']), note['date_published'], LANGUAGES[note['language']]]
    if maturity:
        metadata.append(maturity)
    if note.get('date_updated'):
        metadata.append('Substantively revised ' + note['date_updated'])
    return (f'<article class="article-body"><h1>{escape(note["title"])}</h1>'
            f'<p class="metadata">{escape(" · ".join(metadata))}</p>'
            + note['body_html'].replace('{{assets}}', '/writing/notes/' + note['slug']) + '</article>')


def writing_entry(item):
    return (f'<li><h3><a href="{item["route"]}" lang="{item["language"]}">{escape(item["title"])}</a></h3>'
            f'<p class="metadata">{escape(KINDS[item["kind"]])} · {escape(item["date_published"])} · {LANGUAGES[item["language"]]}</p>'
            f'<p class="authors">{escape(", ".join(item["authors"]))}</p><p>{escape(item["summary"])}</p></li>')


def generate(notes_dir=None):
    publications = read_json(SOURCE / 'publications.json')
    notes = public_notes(notes_dir or SOURCE / 'notes')
    writing = read_json(SOURCE / 'writing.json')
    # This file describes only the preserved legacy article. New writing must
    # pass the note validator and approval gate; it cannot bypass them via a listing.
    if (len(writing) != 1 or writing[0].get('route') != '/ai/blog/ai-fondet.html'
            or writing[0].get('publication_state') != 'published'
            or writing[0].get('author_approved') is not True):
        raise ValueError('writing.json must retain the approved legacy article; add new writing through _source/notes')
    output = {}
    for note, path in notes:
        route = '/writing/notes/' + note['slug'] + '.html'
        writing.append(dict(note, route=route))
        output[route[1:]] = shell(note['title'] + ' | ' + NAME, note['summary'], note_body(note), route, 'Writing', note['language'])
        for asset in note.get('assets', []):
            output['writing/notes/' + note['slug'] + '/' + asset] = (path.parent / asset).read_bytes()
    writing.sort(key=lambda item: item['date_published'], reverse=True)
    entries = '<ul class="writing-list">' + ''.join(writing_entry(w) for w in writing) + '</ul>'
    # Always retain the legacy essay on the homepage as new notes are added.
    selected = writing[:2]
    legacy = next(w for w in writing if w['route'] == '/ai/blog/ai-fondet.html')
    if legacy not in selected:
        selected.append(legacy)
    values = {k: escape(v, quote=True) for k, v in LINKS.items()}
    values.update(selected_papers=publication_list([p for p in publications if p.get('selected')]),
                  selected_writing='<ul class="writing-list">' + ''.join(writing_entry(w) for w in selected) + '</ul>')
    home = Template((SOURCE / 'pages/home.html').read_text()).substitute(values)
    output['index.html'] = shell(NAME + ' — Research and writing', 'Stochastic analysis, signature methods and mathematical models for complex time series. Research, publications and writing by Fabian Nøst Harang.', home, '/', 'Home')
    research = Template((SOURCE / 'pages/research.html').read_text()).substitute(values)
    output['research.html'] = shell('Research | ' + NAME, 'Stochastic analysis, signature methods, applications and research collaborations.', research, '/research.html', 'Research')
    papers = '<h1>Publications</h1><p class="prose">Papers and preprints, with original author bylines and links to the listed arXiv versions. Journal details and the year first posted to arXiv are shown separately.</p>'
    papers += '<p class="text-links"><a href="' + escape(LINKS['scholar_url'], quote=True) + '">Google Scholar</a><a href="' + escape(LINKS['arxiv_url'], quote=True) + '">arXiv record</a><a href="mailto:fabian.harang@bi.no?subject=CV%20request">Request CV</a></p>'
    for title, items in [('Published work', [p for p in publications if p.get('journal_ref') or p.get('doi')]),
                         ('Further papers and preprints', [p for p in publications if not (p.get('journal_ref') or p.get('doi'))])]:
        if items:
            papers += '<section><h2>' + title + '</h2>' + publication_list(items) + '</section>'
    output['publications.html'] = shell('Publications | ' + NAME, 'Publications and preprints by Fabian Nøst Harang and coauthors.', papers, '/publications.html', 'Publications')
    output['writing.html'] = shell('Writing | ' + NAME, 'Research notes, explanations and commentary by Fabian Nøst Harang and coauthors.', '<div class="prose"><h1>Writing</h1>' + entries + '</div>', '/writing.html', 'Writing')
    article = (SOURCE / 'articles/ai-fondet.html').read_text()
    article = article.replace('<table ', '<div class="table-scroll" role="region" aria-label="Tabell 1" tabindex="0"><table ').replace('</table>', '</table></div>')
    schema = (SOURCE / 'articles/ai-fondet.schema.json').read_text()
    extra = '<meta property="og:type" content="article"><meta property="og:image" content="' + SITE + '/assets/network-cover.png"><script type="application/ld+json">' + schema + '</script>'
    output['ai/blog/ai-fondet.html'] = shell('KI-fondet | ' + NAME, 'En forsikring for europeisk suveren intelligens, av Andreas Ravndal Kostøl og Fabian Nøst Harang.', '<p class="article-nav" lang="en"><a href="/writing.html">Writing</a> · Commentary · Norwegian Bokmål</p><article class="article-body" id="article-content">' + article + '</article>', '/ai/blog/ai-fondet.html', 'Writing', 'nb', extra)
    output['ai/blog/ai-fondet.content.html'] = '''<!doctype html><html lang="nb"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width, initial-scale=1"><title>KI-fondet</title><link rel="canonical" href="https://www.fabianharang.no/ai/blog/ai-fondet.html"></head><body><p><a href="ai-fondet.html">Les KI-fondet</a></p><script>location.replace('ai-fondet.html' + location.hash);</script></body></html>'''
    output['404.html'] = shell('Page not found | ' + NAME, 'This page could not be found.', '<div class="prose"><h1>Page not found</h1><p>The page may have moved. Find <a href="/research.html">research</a>, <a href="/publications.html">publications</a> or <a href="/writing.html">writing</a>, or <a href="/">return home</a>.</p></div>', '/404.html', extra='<meta name="robots" content="noindex">')
    routes = ['/', '/research.html', '/publications.html', '/writing.html'] + [w['route'] for w in writing]
    output['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('  <url><loc>' + SITE + route + '</loc></url>\n' for route in routes) + '</urlset>\n'
    return {p: c if isinstance(c, bytes) else c.encode('utf-8') for p, c in output.items()}


def build(output_dir, check=False, notes_dir=None):
    output = generate(notes_dir)
    if (output_dir / '.private-preview').exists():
        raise ValueError('This directory contains a private preview; use a different directory for public output')
    manifest = SOURCE / 'generated.json' if output_dir.resolve() == ROOT else output_dir / '.build-manifest.json'
    previous = read_json(manifest) if manifest.exists() else []
    expected = json.dumps(sorted(output), indent=2) + '\n'
    if check:
        differences = [p for p, data in output.items() if not (output_dir / p).is_file() or (output_dir / p).read_bytes() != data]
        if not manifest.exists() or manifest.read_text() != expected:
            differences.append('_source/generated.json')
        if differences:
            raise ValueError('Generated files need rebuilding: ' + ', '.join(differences))
        return output
    # All content is validated before writing. Clean only recorded, generated note files.
    for old in previous:
        if old not in output and old.startswith('writing/notes/') and '..' not in Path(old).parts:
            (output_dir / old).unlink(missing_ok=True)
    for path, content in output.items():
        target = output_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    manifest.write_text(expected)
    if output_dir.resolve() != ROOT:
        for folder in ['assets', 'css']:
            shutil.copytree(ROOT / folder, output_dir / folder, dirs_exist_ok=True)
        for filename in ['robots.txt', 'CNAME']:
            shutil.copy2(ROOT / filename, output_dir / filename)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT)
    parser.add_argument('--preview-note', type=Path, help='Render one private draft to an external, local-only output folder')
    args = parser.parse_args()
    if args.preview_note:
        if args.output.resolve().is_relative_to(ROOT) or args.output.resolve() == ROOT.parent or ROOT.is_relative_to(args.output.resolve()):
            parser.error('Private previews must use a separate folder outside the repository')
        note = read_json(args.preview_note)
        # Publication date can be absent in a private draft preview.
        note = dict(note, date_published=note.get('date_published') or date.today().isoformat())
        validate_note(note, args.preview_note)
        if args.output.exists() and any(args.output.iterdir()):
            parser.error('Use a new or empty folder for each private preview')
        build(args.output)
        (args.output / '.private-preview').write_text('Local private preview. Do not publish this directory.\n')
        content = '<p class="private-preview">Private draft preview — not approved for publication. Any provisional date below is for layout only.</p>' + note_body(note)
        route = '/writing/notes/' + note['slug'] + '.html'
        target = args.output / route[1:]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(shell(note['title'] + ' — private preview', 'Private draft preview', content, route, language=note['language'], extra='<meta name="robots" content="noindex">'))
        for asset in note.get('assets', []):
            target = args.output / 'writing/notes' / note['slug'] / asset
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(args.preview_note.parent / asset, target)
        print('Private preview:', args.output / route[1:])
    else:
        build(args.output, args.check)
        print('Static output verified.' if args.check else 'Static output generated.')


if __name__ == '__main__':
    main()
