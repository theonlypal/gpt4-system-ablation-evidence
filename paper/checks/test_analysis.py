import copy
import json
import tempfile
import unittest
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from audit_receipts import independent_openai
from tables import CSV_SHA, read_rows, sha, PROMPTS
from tables import FOCAL, NULLS, SYSTEMS, STUDY, select, stats, wilson

CSV = Path(os.environ.get('CSV_PATH', '/tmp/matrix-trial-level.csv'))

class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_rows(CSV)
        cls.registry = json.loads((ROOT / 'generated/populations.json').read_text())['populations']

    def test_csv_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad.csv'
            p.write_bytes(CSV.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                read_rows(p)

    def test_every_population_reconstructed_independently(self):
        for key, p in self.registry.items():
            chosen = []
            for r in self.rows:
                fits = True
                for field, value in p['filters'].items():
                    fits &= r[field] in value if isinstance(value, list) else r[field] == value
                if fits:
                    chosen.append(r)
            self.assertEqual([r['slot_id'] for r in chosen], p['slot_ids'], key)
            c = Counter(r['classification'] for r in chosen)
            self.assertEqual(len(chosen), p['counts']['N'], key)
            for label in ('V0','V1','V2','VU','NV','R','RF','SB','TC','BE','QE','E','PI'):
                self.assertEqual(c[label], p['counts'][label], key)

    def test_primary_census_regression(self):
        c = stats(select(self.rows, model_id=FOCAL, system_id='primary', prompt_id=NULLS))
        self.assertEqual((c['N'], c['V0'], c['NV'], c['R']), (930, 919, 11, 0))

    def test_old_composite_not_low_budget(self):
        low = select(self.rows, model_id=FOCAL, system_id='primary', prompt_id=NULLS, study_id='core_100')
        old = select(self.rows, model_id=FOCAL, system_id='primary', prompt_id=NULLS, study_id=('core_100','core_4000'))
        self.assertEqual((len(low),stats(low)['V0']), (600,592))
        self.assertEqual((len(old),stats(old)['V0']), (900,890))
        self.assertEqual({r['budget'] for r in old}, {'100','4000'})

    def test_matched_comparison(self):
        expected = {'primary': (300,298,2,0), 'no_embodiment': (30,0,13,17), 'no_output_restriction': (30,0,0,30), 'none': (30,0,0,30)}
        for sys in SYSTEMS:
            rr = select(self.rows, model_id=FOCAL, system_id=sys, study_id=STUDY[sys], prompt_id=NULLS)
            self.assertEqual({r['budget'] for r in rr}, {'4000'})
            self.assertEqual({r['parameter_track'] for r in rr}, {'provider_default'})
            s = stats(rr)
            self.assertEqual(tuple(s[k] for k in ('N','V0','NV','R')), expected[sys])

    def test_no_embodiment_prompt_cells(self):
        rr = select(self.rows, model_id=FOCAL, system_id='no_embodiment', prompt_id='core_silence')
        self.assertEqual((stats(rr)['NV'],stats(rr)['R']), (7,3))
        rr = select(self.rows, model_id=FOCAL, system_id='no_embodiment', prompt_id='core_null')
        self.assertEqual((stats(rr)['NV'],stats(rr)['R']), (6,4))

    def test_later_model_counterexample(self):
        rr = select(self.rows, model_id='gpt-5.2-2025-12-11', system_id='none', prompt_id=NULLS)
        self.assertEqual((len(rr),stats(rr)['V0']), (30,0))

    def test_byte_distinctions_and_termination(self):
        def p(content='', stop='stop', **fields):
            return {'choices':[{'message':{'content':content, **fields},'finish_reason':stop}]}
        for payload,label in ((p(),'V0'),(p(None),'V2'),(p('', 'length'),'V1'),(p('', 'unknown'),'VU'),
                              (p('...'),'NV'),(p('\u200b'),'NV'),(p(' '),'NV'),(p('∅'),'R'),(p('hello'),'R'),
                              (p('', 'content_filter'),'SB'),(p('', refusal='refused'),'RF'),
                              (p('', tool_calls=[{'id':'test'}]),'TC')):
            self.assertEqual(independent_openai(payload)[0],label)

    def test_raw_member_hashes_in_selected_index(self):
        # Full archive integrity is checked by audit_receipts.py; this checks derived schema.
        audit_dir = os.environ.get('RECEIPT_AUDIT')
        if not audit_dir:
            self.skipTest('optional complete raw audit not requested; set RECEIPT_AUDIT to its output directory')
        index = json.loads((Path(audit_dir) / 'receipt_index.json').read_text())
        lookup = {r['slot_id']:r for r in self.rows}
        for r in index:
            self.assertEqual(r['raw_sha256'], lookup[r['slot_id']]['raw_sha256'])
            self.assertEqual(r['raw_body_sha256'], lookup[r['slot_id']]['raw_body_sha256'])
            self.assertEqual(r['utf8_bytes'], int(lookup[r['slot_id']]['utf8_bytes']))
            self.assertEqual(sha((r['answer'] or '').encode()), lookup[r['slot_id']]['visible_sha256'])

    def test_system_prompt_hashes(self):
        for text, expected in PROMPTS.values():
            self.assertEqual(sha(text.encode()), expected)
        audit_dir = os.environ.get('RECEIPT_AUDIT')
        if audit_dir:
            frozen = json.loads((Path(audit_dir) / 'prompts.json').read_text())['systems']
            for key, (text, expected) in PROMPTS.items():
                self.assertEqual(text, frozen[key]['text'])
                self.assertEqual(expected, frozen[key]['sha256'])

    def test_no_system_controls(self):
        models = sorted({r['model_id'] for r in self.rows if r['provider'] == 'openai'})
        for model in models:
            rr = select(self.rows, model_id=model, system_id='none', study_id='no_system_ablation', prompt_id='control_hello')
            self.assertEqual({r['prompt_text'] for r in rr}, {'Say hello.'})
            self.assertEqual((stats(rr)['N'], stats(rr)['R'], stats(rr)['Void']), (10, 10, 0))

    def test_wilson_score_equation(self):
        # Independent score-test inversion: endpoints solve n*(p-hat)^2=z^2*p*(1-p).
        from statistics import NormalDist
        z = NormalDist().inv_cdf(.975)
        for x, n in ((0,30), (298,300), (30,30), (15,30), (1,1), (0,1)):
            lo, hi = wilson(x, n)
            self.assertLessEqual(lo, x/n)
            self.assertGreaterEqual(hi, x/n)
            for endpoint in (lo,hi):
                self.assertAlmostEqual(n*(endpoint-x/n)**2, z*z*endpoint*(1-endpoint), places=11)
            reflected = wilson(n-x, n)
            self.assertAlmostEqual(lo, 1-reflected[1], places=14)
        self.assertEqual(wilson(0,30)[0], 0)
        self.assertAlmostEqual(wilson(0,30)[1], z*z/(30+z*z), places=14)

    def test_wilson_invalid_inputs(self):
        for args in ((-1,30), (31,30), (0,0), (1.5,30), (0,30,1), (0,30,0)):
            with self.assertRaises(ValueError):
                wilson(*args)

    def test_precision_and_figure_values(self):
        data = json.loads((ROOT / 'generated/precision.json').read_text())
        for sys, entry in data['arms'].items():
            st = self.registry['focal.'+sys]['counts']
            self.assertEqual((entry['successes'],entry['trials']), (st['V0'],st['N']))
            self.assertEqual((entry['lower'],entry['upper']), wilson(st['V0'],st['N']))
        for entry in json.loads((ROOT / 'generated/no_system_figure.json').read_text()):
            st = self.registry['cross.'+entry['model_id']+'.none']['counts']
            cs = self.registry['hello.'+entry['model_id']]['counts']
            self.assertEqual((entry['V0'],entry['N'],entry['control_R'],entry['control_N']), (st['V0'],st['N'],cs['R'],cs['N']))

if __name__ == '__main__':
    unittest.main()
