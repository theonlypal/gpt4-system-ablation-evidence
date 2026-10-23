# Verification report

Status: **PASS**. Verification date: 2026-10-22. Manuscript date: October 22, 2026. No new model calls or experimental data. Zenodo: **NOT DEPOSITED**.

The pinned CSV and original ZIP SHA-256 values matched. The complete raw audit checked 31,430 final trials, 31,484 retained raw attempts, 54 nonfinal attempts, and 62,968 event hashes. Frozen request/schedule reconstruction and classifier replay passed. Independent classification of 17,005 successful OpenAI responses agreed, with no returned-model mismatch.

`tables.py --csv /tmp/matrix-trial-level.csv` regenerated every result table and both figures. Prompt hashes matched the frozen archive. The setting-matched focal contrast is 298/300 V0 versus 0/90 across ablations; the 919/930 census, 890/900 core composite, and 592/600 low-budget subset remain separate. All 1,214 previously generated values and all existing numerical table files are unchanged.

All checks are offline evidence verification, not new provider execution.

## Reproduction

Analysis and manuscript-source commit: `32897d3487591533ef4cb441c66f5cbf2b843b4e`.

A fresh clone and a fresh download of the pinned CSV reproduced all 21 generated artifacts byte-for-byte. `git diff --exit-code -- generated` and all entries in `generated/SHA256SUMS` passed. The source CSV and archive hashes are specified in `PROVENANCE.md`.

The complete archive audit was executed from the fresh clone. All 14 tests passed using that audit's raw-receipt index. The clean-clone manuscript compiled successfully and passed the PDF validator. CSV-only verification omits the optional raw-index check when `RECEIPT_AUDIT` is absent; the full workflow below includes it.

## Executed checks

| Check | Result |
|---|---|
| CSV and original archive SHA-256 | PASS |
| Exact prompt strings and hashes | PASS |
| 31,430 final records and 31,484 raw attempts | PASS |
| 62,968 event hashes and final-slot bindings | PASS |
| Frozen request reconstruction and outcome replay | PASS |
| Independent OpenAI classification, 17,005 successful responses | PASS |
| All population filters, slot memberships, and competing outcomes | PASS |
| Four focal arms, six-model comparisons, no-system controls | PASS |
| Wilson score equation, exact boundary cases, symmetry, invalid-input rejection | PASS |
| 14 tests including the full raw-index test | PASS |
| 21 deterministic generated artifacts and both figures | PASS |
| 39 numerical macro occurrences and 88 PDF table rows | PASS |
| 21 citation keys, 10 live Zenodo titles/dates/DOIs | PASS |
| Compilation, PDF links, page-by-page visual inspection | PASS |
| Clean-clone generation, tests, archive audit, and PDF rebuild | PASS |

## Effect size and precision

Two-sided Wilson 95% intervals use `z = 1.9599639845400534`. Full-precision values are in `generated/precision.json`.

| Arm | V0/N | Observed rate | Wilson interval | Full minus arm, percentage points |
|---|---:|---:|---:|---:|
| Full prompt | 298/300 | 99.333333% | 97.602242%-99.816985% | 0 |
| No output restriction | 0/30 | 0% | 0%-11.351339% | 99.333333 |
| No embodiment | 0/30 | 0% | 0%-11.351339% | 99.333333 |
| No system message | 0/30 | 0% | 0%-11.351339% | 99.333333 |

These are binomial reference-model intervals, not dependence-adjusted coverage or intervals for rate differences. Shared provider and execution-window dependencies remain explicit.

Resolved numerical check: the initial boundary test detected a floating-point lower endpoint of approximately 1.39e-17 at zero successes. The implementation now returns the exact mathematical endpoint, zero; the all-success upper endpoint is likewise exactly one. The score-equation and boundary tests passed after correction. No source observations or classifications changed.

## Manuscript

- PDF: `paper/main.pdf`, 14 pages, author Rayan Pal, dated October 22, 2026.
- SHA-256: `ca8387140fb9afb58dd1037f5850a8c431c27f04007469415640ef8a44c464b0`.
- 39 empirical-data macro occurrences resolve to generated values.
- 88 table rows, including headers, match generated tables in extracted PDF text. Chronology dates, titles and DOI identifiers also match.
- 21 unique cited works resolve to 21 bibliography entries. The complete citation list is in `paper/references.tex`; the literature comparison is in `RELATED_WORK.md`.
- All 10 historical Zenodo record titles and publication dates match live record metadata.
- Final LaTeX log: no undefined citations, unresolved references, overfull boxes, underfull boxes or compilation errors.
- All pages rendered and visually checked. No clipped tables, overlapping text or missing glyphs. Executable examples retain literal quotation marks.
- Figure 1 immediately follows the abstract on page 1. Figure 2 displays exact no-system V0 and hello-control fractions on page 7. The chronology occupies landscape page 14. Scope is 131 words, followed by the two architectural subsections.
- The official OpenAI deprecations page confirms the scheduled October 23, 2026 shutdown of gpt-4-0613. The manuscript distinguishes July execution, October 21 replay, and October 22 reanalysis.
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

## Release provenance

Repository: https://github.com/theonlypal/gpt4-system-ablation-evidence

Revision release: https://github.com/theonlypal/gpt4-system-ablation-evidence/releases/tag/v2

The existing public `v1` tag and assets remain unchanged. Baseline commit: `a331f37349fee5bef830063b311c20026f6dc5b9`. The original PDF and manuscript source were preserved locally before editing; original PDF SHA-256: `627ad01dade30a723cb85cf4d5fa585b619c9f894e1bcf0fa8c8d479ed1bd8a3`.

The release includes the PDF, source ZIP, this report, related-work references, and asset SHA-256 manifest. The original Matrix CSV and archive are linked, not duplicated. No Zenodo deposit or DOI reservation was made. Unresolved verification issues: none.

## Evidence boundaries

- The principal comparison is the common 4,000-token, provider-default stratum. The pooled census is not its denominator.
- No-system controls are `Say hello.`, not unobserved speech/something/value cells.
- January's aggregate budget-dependent observation lacks the stop metadata needed for a V1 assignment. The later raw budget-stop receipt and the GPT-4 V0 observations have separate evidentiary roles.
- The October replay confirms only the full-prompt arm and is not pooled into this analysis.
- Provider-reported normal stopping does not expose native EOS logits, immutable serving weights or intention.
- The literature comparison is bounded and nonsystematic, not a priority proof.
- The release contains no raw corpus, credentials or private correspondence. Original evidence remains available from its hash-pinned public archive.
