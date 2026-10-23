#!/usr/bin/env python3
"""Reject hand-entered empirical numerals and unresolved generated data macros."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = (root / 'paper/main.tex').read_text()
values = json.loads((root / 'generated/values.json').read_text())
used = re.findall(r'\\D\{([^{}]+)\}', source)
missing = sorted(set(used) - values.keys())
if missing:
    raise SystemExit(f'Unknown generated data macros: {missing}')
body = source.split(r'\begin{document}', 1)[1]
body = re.sub(r'\\D\{[^{}]+\}', '', body)
body = re.sub(r'\\cite[pt]?\{[^{}]+\}|\\(?:ref|label)\{[^{}]+\}', '', body)
body = re.sub(r'\\setlength\{[^{}]+\}\{[^{}]+\}', '', body)
body = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}', '', body, flags=re.S)
body = re.sub(r'https?://[^}\s]+', '', body)
body = re.sub(r'\b[0-9a-f]{40,64}\b', '', body)
body = re.sub(r'GPT-(?:3\.5|4(?:-0613)?|5\.[256])|PCCG-[12]', '', body)
body = re.sub(r'UTF-8|SHA-256|V[012]', '', body)
body = re.sub(r'core\\_\d+|equivalence\\_\d+', '', body)
body = re.sub(r'void-matrix-evidence-v1\.0\.0/study/', '', body)
body = re.sub(r'October 21|Section 4\.1', '', body)
leftovers = [(i, s) for i, s in enumerate(body.splitlines(), 1) if re.search(r'\d', s)]
if leftovers:
    raise SystemExit(f'Unapproved literal numerals in manuscript body: {leftovers}')
for name in re.findall(r'\\input\{(\.\./generated/[^{}]+)\}', source):
    path = root / 'paper' / (name if name.endswith('.tex') else name + '.tex')
    if not path.exists():
        raise SystemExit(f'Missing generated input {path}')
print(f'PASS: {len(used)} generated data macro references; no hand-typed empirical numerals in manuscript body.')
print('Allowlisted non-count numerals: model identifiers, taxonomy labels, byte/hash terminology, study IDs, URLs, hashes, and executable command examples.')

references = (root / 'paper/references.tex').read_text()
cited = {key for group in re.findall(r'\\cite[pt]?\{([^}]+)\}', source) for key in group.split(',')}
bib = re.findall(r'\\bibitem\[[^]]+\]\{([^}]+)\}', references)
assert len(bib) == len(set(bib)), 'duplicate reference key'
assert cited <= set(bib), 'missing references: ' + str(cited - set(bib))
print(f'PASS: {len(cited)} cited works resolve to {len(bib)} unique references.')
