# Verification report

Status: **PASS**. Verification date: 2026-10-22. No new model calls were performed.

The pinned CSV and original ZIP SHA-256 values matched. The complete raw audit checked 31,430 final trials, 31,484 retained raw attempts, 54 nonfinal attempts, and 62,968 event hashes. Frozen request/schedule reconstruction and classifier replay passed. Independent classification of 17,005 successful OpenAI responses agreed, with no returned-model mismatch.

`tables.py --csv inputs/trial_level.csv` regenerated every result table and figure. Prompt hashes matched the frozen archive. The setting-matched focal contrast is 298/300 V0 versus 0/90 across ablations; the 919/930 census and 890/900 core composite remain separate. The latter includes both budgets, not the low-budget subset alone.

All checks are offline evidence verification, not new provider execution.

## Reproduction

Analysis commit: `849891ceee2a4a12bbd5ff76cf850fdb18cb3c00`.

A fresh public clone and a fresh download of the pinned CSV reproduced all 17 generated artifacts byte-for-byte. `git diff --exit-code -- generated` passed. The source CSV and archive hashes are specified in `PROVENANCE.md`; the generated-output hashes are in `generated/SHA256SUMS`.

The complete archive audit was executed from the fresh clone. All 11 regression tests then passed with the resulting raw-receipt index. The CSV-only test mode passes 10 tests and explicitly skips the optional raw-index check when `RECEIPT_AUDIT` is absent. It does not label that check as passed.

## Manuscript

- PDF: `paper/main.pdf`, 12 pages, author Rayan Pal.
- SHA-256: `627ad01dade30a723cb85cf4d5fa585b619c9f894e1bcf0fa8c8d479ed1bd8a3`.
- 33 empirical-data macro occurrences resolve to generated values.
- 83 table rows, including headers, match generated tables in extracted PDF text. Chronology dates, titles and DOI suffixes also match.
- 19 unique cited works resolve to 19 bibliography entries.
- All 10 historical Zenodo record titles and publication dates match live record metadata.
- Final LaTeX log: no undefined citations, unresolved references, overfull boxes, underfull boxes or compilation errors.
- All pages rendered and visually checked. No clipped tables, overlapping text or missing glyphs. Executable examples retain literal quotation marks.
- Model identifiers, source hashes, original prompts, and outcome denominators are preserved. Every empirical count in the manuscript is supplied through `tables.py` outputs.

## Commands

Python 3.12.14, ReportLab 4.4.9, pypdf 6.10.0, pdfTeX 1.40.29 (TeX Live 2026), and Poppler were used. Python 3.11 or later is required by the archive auditor.

Download the CSV and archive from the exact URLs in `PROVENANCE.md` to the paths below. Run from the repository root:

```sh
python3 -m pip install reportlab==4.4.9 pypdf==6.10.0
python3 tables.py --csv /tmp/matrix-trial-level.csv
git diff --exit-code -- generated
(cd generated && shasum -a 256 -c SHA256SUMS)
python3 paper/checks/audit_receipts.py \
  --csv /tmp/matrix-trial-level.csv \
  --archive /tmp/void-matrix-evidence-v1.0.0.zip \
  --out /tmp/matrix-raw-audit
CSV_PATH=/tmp/matrix-trial-level.csv \
RECEIPT_AUDIT=/tmp/matrix-raw-audit \
python3 -m unittest discover -s paper/checks -p 'test_*.py' -v
python3 paper/checks/validate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
python3 checks/validate_pdf.py
```

The release PDF hash identifies the distributed file. PDF rebuilds can differ in creation metadata across environments; the generated numerical tables and invariant figure have exact content hashes.

## Evidence boundaries

- The principal comparison is the common 4,000-token, provider-default stratum. The pooled census is not its denominator.
- No-system controls are `Say hello.`, not unobserved speech/something/value cells.
- January's aggregate budget-dependent observation lacks the stop metadata needed for a V1 assignment. The later raw budget-stop receipt and the GPT-4 V0 observations have separate evidentiary roles.
- The October replay confirms only the full-prompt arm and is not pooled into this analysis.
- Provider-reported normal stopping does not expose native EOS logits, immutable serving weights or intention.
- The literature comparison is bounded and nonsystematic, not a priority proof.
- The release contains no raw corpus, credentials or private correspondence. Original evidence remains available from its hash-pinned public archive.
