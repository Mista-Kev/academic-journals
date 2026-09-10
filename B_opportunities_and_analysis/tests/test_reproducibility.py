"""Regression checks for a new output folder and Git checkout byte preservation."""
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from B_opportunities_and_analysis import build_event_table as builder
import project_data

ROOT = Path(__file__).resolve().parents[2]


class ReproducibilityTests(unittest.TestCase):
    def test_builder_creates_missing_parents_for_both_outputs(self):
        works = {'W1': ('2020-01-01', 'J1', 2020, 'T'),
                 'W2': ('2021-01-01', 'J2', 2021, 'T')}
        authors = {'W1': ['A1'], 'W2': ['A1']}
        index = builder.build_index(works, authors)
        with tempfile.TemporaryDirectory() as tmp:
            out_a = Path(tmp)/'B_opportunities_and_analysis/data/a.csv'
            out_b = Path(tmp)/'separate/nested/b.csv'
            self.assertFalse(out_a.parent.exists())
            self.assertFalse(out_b.parent.exists())
            stats, _, _ = builder.emit(index, authors, {'J1': 'P1', 'J2': 'P2'},
                                       ['J1', 'J2'], out_a, out_b)
            for path, key in ((out_a, 'rows_a'), (out_b, 'rows_b')):
                with path.open(newline='') as stream:
                    reader = csv.DictReader(stream)
                    rows = list(reader)
                self.assertEqual(reader.fieldnames, builder.COLUMNS)
                self.assertGreater(len(rows), 0)
                self.assertEqual(len(rows), stats[key])
                self.assertNotIn(b'\r\n', path.read_bytes())

    @unittest.skipUnless(shutil.which('git'), 'Git required for real checkout conversion')
    def test_autocrlf_checkout_preserves_every_tracked_manifest_file(self):
        tracked = set(subprocess.check_output(
            ['git', '-C', str(ROOT), 'ls-files', '-z']).decode().split('\0'))
        manifest = project_data.load_manifest(ROOT)
        items = [item for item in manifest['files'] if item['path'] in tracked]
        self.assertTrue(items)
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            env = {k: v for k, v in os.environ.items()
                   if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')}
            env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')

            def git(*args):
                subprocess.run(['git', '-c', 'core.attributesFile='+os.devnull, *args],
                               cwd=checkout, env=env, check=True, capture_output=True)

            git('init', '-q')
            git('config', 'core.autocrlf', 'false')
            if (ROOT/'.gitattributes').exists():
                shutil.copyfile(ROOT/'.gitattributes', checkout/'.gitattributes')
            for item in items:
                dest = checkout/item['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/item['path'], dest)
            (checkout/'unmanaged.txt').write_bytes(b'control\n')
            git('add', '.')
            for item in items:
                (checkout/item['path']).unlink()
            (checkout/'unmanaged.txt').unlink()
            git('config', 'core.autocrlf', 'true')
            git('checkout-index', '--all', '--force')
            self.assertEqual((checkout/'unmanaged.txt').read_bytes(), b'control\r\n')
            for item in items:
                with self.subTest(path=item['path']):
                    self.assertTrue(project_data.matches(checkout/item['path'], item))
            (checkout/'data-manifest.json').write_text(json.dumps({**manifest, 'files': items}))
            # Exercise the loader as well as comparing bytes. No source can hide a mismatch.
            project_data.ensure_data('all', root=checkout, verify_only=True)


if __name__ == '__main__':
    unittest.main()
