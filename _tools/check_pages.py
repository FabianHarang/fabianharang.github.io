"""Check the actual GitHub Pages/Jekyll output before release."""
from pathlib import Path
import sys
import build

output = Path(sys.argv[1])
for path, content in build.generate().items():
    assert (output / path).is_file(), f'Missing public route: {path}'
    assert (output / path).read_bytes() == content, f'Unexpected rendering change: {path}'
for private in ['_source', '_tools', 'AUTHORING.md', 'README.md', '.github', '.private-preview']:
    assert not (output / private).exists(), f'Non-public content in Pages output: {private}'
print('GitHub Pages routes, generated content and exclusions verified.')
