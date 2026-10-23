#!/usr/bin/env python3
import json
import re
from pathlib import Path
from pypdf import PdfReader

root = Path(__file__).resolve().parents[2]
pdf = PdfReader(root / 'paper/main.pdf')
norm = lambda s: re.sub(r'\s+', '', s)
text = norm('\n'.join(p.extract_text() for p in pdf.pages))
source = (root / 'paper/main.tex').read_text()
values = json.loads((root / 'generated/values.json').read_text())
used = re.findall(r'\\D\{([^{}]+)\}', source)
for key in used:
    value = norm(values[key].replace('\\%', '%').replace('\\_', '_'))
    if value not in text:
        raise SystemExit(f'Generated value missing from PDF: {key} = {value}')
checked = 0
for name in ('prompts', 'aggregate', 'focal', 'strata', 'controls', 'cross', 'cross_full', 'no_system_controls', 'precision'):
    for line in (root / 'generated' / (name + '.tex')).read_text().splitlines():
        if ' & ' not in line:
            continue
        clean = re.sub(r'\\textit\{([^}]+)\}', r'\1', line)
        clean = clean.replace('\\_', '_').replace('\\&', '&').replace('\\%', '%').replace('--', '–').replace('\\\\', '').replace('&', '')
        if norm(clean) not in text:
            raise SystemExit(f'Table row not found verbatim in PDF ({name}): {clean}')
        checked += 1
if '??' in text:
    raise SystemExit('Unresolved PDF reference')
assert 'October22,2026' in text, 'manuscript date missing'
assert source.index(r'\label{fig:ablation}') < source.index(r'\section{Introduction}'), 'Figure 1 not before introduction'
for fig, expected in [('ablation', 'Same model, same inputs'), ('no_system', 'Zero-byte continuation')]:
    assert norm(expected) in text, 'figure caption missing: ' + fig
for row in json.loads((root / 'generated/no_system_figure.json').read_text()):
    assert norm(row['model_id']) in text
    assert f"{row['V0']}/{row['N']}" in text
    assert f"{row['control_R']}/{row['control_N']}" in text
for entry in json.loads((root / 'generated/chronology.json').read_text()):
    assert norm(entry['title']) in text, 'chronology title absent: ' + entry['title']
    assert entry['date'] in text, 'chronology date absent: ' + entry['date']
    if entry['doi_suffix']:
        assert entry['doi_suffix'] in text, 'chronology DOI absent'
log = (root / 'paper/main.log').read_text()
for marker in ('undefined', 'Overfull', 'Underfull', 'LaTeX Error'):
    if marker in log:
        raise SystemExit('LaTeX diagnostic: ' + marker)
links = sorted({a.get_object().get('/A', {}).get('/URI') for p in pdf.pages for a in p.get('/Annots', []) if a.get_object().get('/A', {}).get('/URI')})
report = {'status':'PASS', 'pages':len(pdf.pages), 'generated_macro_occurrences':len(used),
          'generated_table_rows_including_headers':checked, 'external_links':links,
          'author':str(pdf.metadata.author), 'tex_warnings':0}
(root / '.local').mkdir(exist_ok=True)
(root / '.local/pdf_validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
