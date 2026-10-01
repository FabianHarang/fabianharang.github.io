"""Regression checks for article preservation, links, and the publication gate."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import build


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.ids = []
        self.links = []
        self.images = []
        self.h1 = 0
        self.feed(text)

    def handle_data(self, text):
        self.text.append(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag in ['a', 'link', 'img', 'script']:
            ref = attrs.get('href') or attrs.get('src')
            if ref:
                self.links.append(ref)
        if tag == 'img':
            self.images.append(attrs)

    def digest(self):
        return hashlib.sha256(' '.join(' '.join(self.text).split()).encode()).hexdigest()


def article_body(text):
    return text.split('<article class="article-body" id="article-content">', 1)[1].split('</article>', 1)[0]


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build.generate()
        cls.documents = {p: Document(v.decode()) for p, v in cls.output.items() if p.endswith('.html')}

    def test_article_preservation(self):
        baseline = build.read_json(build.SOURCE / 'preservation.json')
        article = Document(article_body(self.output['ai/blog/ai-fondet.html'].decode()))
        self.assertEqual(article.digest(), baseline['text_sha256'])
        self.assertEqual(article.ids, baseline['ids'])
        self.assertEqual([hashlib.sha256(i['src'].encode()).hexdigest() for i in article.images], baseline['image_sha256'])
        self.assertEqual([x for x in article.links if not x.startswith('data:')], baseline['links'])
        for image in article.images:
            self.assertTrue(image.get('alt'))
        for name, digest in baseline['assets'].items():
            self.assertEqual(hashlib.sha256((build.ROOT / name).read_bytes()).hexdigest(), digest)

    def test_publications_and_legacy_fragments(self):
        baseline = build.read_json(build.SOURCE / 'preservation.json')
        pubs = build.read_json(build.SOURCE / 'publications.json')
        preserved = [{k: p[k] for k in ['title', 'authors', 'arxiv', 'preprint_year']} for p in pubs]
        self.assertEqual(preserved, baseline['publications'])
        for anchor in baseline['homepage_ids']:
            self.assertIn(anchor, self.documents['index.html'].ids)
        for page in ['index.html', 'writing.html']:
            self.assertIn('/ai/blog/ai-fondet.html', self.documents[page].links)

    def test_html_and_internal_links(self):
        for path, doc in self.documents.items():
            if path.endswith('.content.html'):
                continue
            self.assertEqual(doc.h1, 1, path)
            self.assertEqual(len(doc.ids), len(set(doc.ids)), path)
            self.assertIn('main', doc.ids)
            for ref in doc.links:
                url = urlsplit(urljoin('https://www.fabianharang.no/' + path, ref))
                if url.scheme not in ['http', 'https'] or url.netloc != 'www.fabianharang.no':
                    continue
                target = unquote(url.path).lstrip('/') or 'index.html'
                self.assertTrue(target in self.output or (build.ROOT / target).is_file(), f'{path}: {ref}')
                if url.fragment and target in self.documents:
                    self.assertIn(unquote(url.fragment), self.documents[target].ids, f'{path}: {ref}')

    def test_publication_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            source = directory / 'notes' / 'example'
            source.mkdir(parents=True)
            path = source / 'note.json'
            note = dict(title='Gate fixture', slug='gate-fixture', authors=['Test author'], kind='research_note',
                        language='en', publication_state='draft', author_approved=False, date_published='2026-01-01',
                        summary='Unique fixture summary.', body_html='<p>UNRELEASED_SENTINEL</p>', assets=['fixture.txt'])
            (source / 'fixture.txt').write_text('PRIVATE_ASSET_SENTINEL')
            for state, approved in [('draft', False), ('draft', True), ('published', False)]:
                note.update(publication_state=state, author_approved=approved)
                path.write_text(json.dumps(note))
                files = build.generate(directory / 'notes')
                all_output = b''.join(files.values())
                self.assertNotIn(b'UNRELEASED_SENTINEL', all_output)
                self.assertNotIn(b'PRIVATE_ASSET_SENTINEL', all_output)
                self.assertNotIn(b'gate-fixture', all_output)
            note.update(publication_state='published', author_approved=True)
            path.write_text(json.dumps(note))
            public = directory / 'public'
            files = build.build(public, notes_dir=directory / 'notes')
            self.assertIn('writing/notes/gate-fixture.html', files)
            self.assertIn('writing/notes/gate-fixture/fixture.txt', files)
            note['publication_state'] = 'draft'
            path.write_text(json.dumps(note))
            build.build(public, notes_dir=directory / 'notes')
            self.assertFalse((public / 'writing/notes/gate-fixture.html').exists())
            self.assertFalse((public / 'writing/notes/gate-fixture/fixture.txt').exists())

    def test_invalid_public_note_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            source = directory / 'notes' / 'bad'
            source.mkdir(parents=True)
            (source / 'note.json').write_text(json.dumps({'publication_state': 'published', 'author_approved': True}))
            with self.assertRaises(ValueError):
                build.build(directory / 'output', notes_dir=directory / 'notes')
            self.assertFalse((directory / 'output').exists())

    def test_sources_excluded_and_no_private_notes_in_repo(self):
        config = (build.ROOT / '_config.yml').read_text()
        for directory in ['_source', '_tools', 'AUTHORING.md', 'README.md']:
            self.assertIn('  - ' + directory, config)
        for path in (build.SOURCE / 'notes').glob('*/note.json'):
            note = build.read_json(path)
            self.assertEqual(note['publication_state'], 'published', 'Keep private drafts outside this public repository')
            self.assertIs(note['author_approved'], True)
        self.assertFalse(any(p.startswith(('_source/', '_tools/')) for p in self.output))

    def test_private_preview_cannot_be_reused_for_public_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            (output / '.private-preview').write_text('Private')
            with self.assertRaises(ValueError):
                build.build(output)
            self.assertFalse((output / 'index.html').exists())

    def test_note_assets_cannot_escape_the_note_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            note_dir = directory / 'notes' / 'example'
            note_dir.mkdir(parents=True)
            (directory / 'notes' / 'private.txt').write_text('Private attachment')
            note = dict(title='Asset fixture', slug='asset-fixture', authors=['Test author'],
                        kind='research_note', language='en', publication_state='published',
                        author_approved=True, date_published='2026-01-01', summary='Fixture',
                        body_html='<p>Fixture</p>', assets=['../private.txt'])
            (note_dir / 'note.json').write_text(json.dumps(note))
            with self.assertRaises(ValueError):
                build.build(directory / 'output', notes_dir=directory / 'notes')
            self.assertFalse((directory / 'output').exists())


if __name__ == '__main__':
    unittest.main()
