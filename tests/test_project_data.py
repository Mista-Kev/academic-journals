import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import project_data as data


class SharedDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.source = Path(self.temp.name) / 'shared'
        self.root.mkdir(); self.source.mkdir()
        self.payload = b'author,value\nA1,0.5\n'
        self.item = {'path':'data/test.csv','bytes':len(self.payload),
                     'sha256':hashlib.sha256(self.payload).hexdigest(), 'groups':['q3'],'owner':'test'}
        self.manifest = {'format':1,'release':'fixture','files':[self.item]}
        (self.root/'data-manifest.json').write_text(json.dumps(self.manifest))
        (self.source/'data').mkdir();(self.source/'data/test.csv').write_bytes(self.payload)

    def test_shared_fetch_then_offline_reuse(self):
        data.ensure_data('q3',self.root,shared_root=self.source)
        (self.source/'data/test.csv').unlink()
        data.ensure_data('q3',self.root,shared_root=self.source)
        self.assertEqual((self.root/'data/test.csv').read_bytes(),self.payload)

    def test_configure_then_notebook_fetch_without_path_argument(self):
        with mock.patch.dict('os.environ', {}, clear=True):
            data.configure(self.source, 'q3', self.root)
            data.ensure_data('q3', self.root)
            (self.source/'data/test.csv').unlink()
            data.ensure_data('q3', self.root)
        self.assertEqual((self.root/'data/test.csv').read_bytes(), self.payload)

    def test_bad_shared_source_preserves_previous_configuration(self):
        path = self.root/'.shared-data.local.json'
        original = '{"shared_root": "previous-source"}'
        path.write_text(original)
        (self.source/'data/test.csv').write_bytes(b'wrong release')
        with mock.patch.dict('os.environ', {}, clear=True), self.assertRaises(data.DataError):
            data.configure(self.source, 'q3', self.root)
        self.assertEqual(path.read_text(), original)

    def test_configure_rejects_conflicting_environment_override(self):
        with mock.patch.dict('os.environ', {'ACADEMIC_JOURNALS_SHARED_ROOT': str(self.root)}):
            with self.assertRaisesRegex(data.DataError, 'points elsewhere'):
                data.configure(self.source, 'q3', self.root)
        self.assertFalse((self.root/'.shared-data.local.json').exists())

    def test_corrupt_transfer_never_becomes_an_input(self):
        (self.source/'data/test.csv').write_bytes(self.payload[:-1])
        with self.assertRaises(data.DataError):data.ensure_data('q3',self.root,shared_root=self.source)
        self.assertFalse((self.root/'data/test.csv').exists())
        self.assertEqual(list((self.root/'data').iterdir()),[])

    def test_existing_different_output_is_not_overwritten(self):
        (self.root/'data').mkdir();p=self.root/'data/test.csv';p.write_bytes(b'my experiment')
        with self.assertRaises(data.DataError):data.ensure_data('q3',self.root,shared_root=self.source)
        self.assertEqual(p.read_bytes(),b'my experiment')

    def test_stage_copies_only_declared_verified_files(self):
        data.ensure_data('q3',self.root,shared_root=self.source)
        (self.root/'private-notes.txt').write_text('do not share')
        target=Path(self.temp.name)/'delivery'
        data.stage(target,'q3',self.root)
        self.assertEqual((target/'data/test.csv').read_bytes(),self.payload)
        self.assertFalse((target/'private-notes.txt').exists())
        self.assertEqual(len(list(target.glob('delivery-*.json'))),1)

    def test_staging_conflict_fails_before_other_files_are_written(self):
        data.ensure_data('q3',self.root,shared_root=self.source)
        target=Path(self.temp.name)/'delivery';(target/'data').mkdir(parents=True)
        (target/'data/test.csv').write_bytes(b'other release')
        with self.assertRaises(data.DataError):data.stage(target,'q3',self.root)
        self.assertEqual((target/'data/test.csv').read_bytes(),b'other release')

    def test_manifest_cannot_escape_its_root(self):
        for path in ['../private','/tmp/private','data/../../private','data\\private','C:/private']:
            with self.subTest(path=path),self.assertRaises(data.DataError):data.safe_path(self.root,path)
        (self.root/'data').symlink_to(self.source/'data',target_is_directory=True)
        with self.assertRaises(data.DataError):data.safe_path(self.root,'data/test.csv')

    def test_login_page_is_not_downloaded_as_csv(self):
        response=mock.MagicMock();response.headers.get_content_type.return_value='text/html'
        with mock.patch('urllib.request.build_opener') as opener:
            opener.return_value.open.return_value=response
            with self.assertRaisesRegex(data.DataError,'login/web page'):data.download('https://example.com/file')
        response.close.assert_called_once()

    def test_urls_require_https_and_no_embedded_credentials(self):
        for url in ['http://example.com/file','https://user:secret@example.com/file','file:///tmp/data']:
            with self.subTest(url=url),self.assertRaises(data.DataError):data.download(url)

    def test_http_error_does_not_print_signed_url(self):
        config={'urls':{'data/test.csv':'https://example.com/file?secret=private'}}
        (self.root/'.shared-data.local.json').write_text(json.dumps(config))
        with mock.patch.object(data,'download',side_effect=OSError('https://example.com/?secret=private')):
            with self.assertRaises(data.DataError) as err:data.ensure_data('q3',self.root)
        self.assertNotIn('private',str(err.exception))

if __name__=='__main__':unittest.main()
