import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from delivery_tools import audit, create_web_copy, digest, export_attributions, local_file

class DeliverySafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        folder = self.root / 'Fotoğraflar'; folder.mkdir()
        image = folder / 'test.jpg'; Image.new('RGB', (1900, 1200), '#aabbcc').save(image)
        self.photo = {'photo_id':'test:1', 'author':'Test <author>', 'caption':'Test', 'license':'CC BY 4.0', 'license_url':'https://creativecommons.org/licenses/by/4.0/', 'source_url':'https://commons.wikimedia.org/wiki/File:Test.jpg', 'file':'Fotoğraflar/test.jpg', 'sha256':digest(image)}
        self.row = {'photo_id':'test:1', 'original_file':self.photo['file'], 'original_sha256':self.photo['sha256'], 'author_url':'', 'original_file_url':'https://upload.wikimedia.org/test.jpg', 'downloaded_file_url':'https://upload.wikimedia.org/test.jpg'}
        self.row = create_web_copy(self.root, self.row)
    def tearDown(self): self.temp.cleanup()
    def test_derivative_preserves_source_and_resumes_identically(self):
        self.assertEqual(digest(self.root/self.photo['file']), self.photo['sha256'])
        self.assertEqual(self.row['web_width'],1600)
        self.assertEqual(create_web_copy(self.root,self.row)['web_sha256'],self.row['web_sha256'])
        self.assertTrue(audit(self.root,[self.photo],[self.row])['structural_passed'])
    def test_escape_and_symlink_are_rejected(self):
        for value in ('../outside.jpg','/etc/passwd'):
            with self.assertRaises(ValueError):local_file(self.root,value)
        (self.root/'escape').symlink_to(self.root.parent)
        with self.assertRaises(ValueError):local_file(self.root,'escape/outside.jpg')
    def test_tampered_or_missing_file_is_reported(self):
        (self.root/self.photo['file']).write_bytes(b'not an image')
        self.assertFalse(audit(self.root,[self.photo],[self.row])['structural_passed'])
    def test_license_restrictions_and_lookalike_domains_fail(self):
        for label,url in [('CC BY-NC 4.0',self.photo['license_url']),('CC BY-ND 4.0',self.photo['license_url']),('CC BY 4.0','https://creativecommons.org.example.com/licenses/by/4.0/'),('CC BY 3.0',self.photo['license_url'])]:
            photo={**self.photo,'license':label,'license_url':url}
            self.assertFalse(audit(self.root,[photo],[self.row])['structural_passed'])
    def test_duplicate_ids_and_orphan_provenance_fail(self):
        self.assertFalse(audit(self.root,[self.photo,self.photo],[self.row])['structural_passed'])
        self.assertFalse(audit(self.root,[self.photo],[self.row,{**self.row,'photo_id':'missing'}])['structural_passed'])
    def test_attribution_escapes_html_and_has_no_javascript_link(self):
        export_attributions(self.root,[self.photo],[{**self.row,'author_url':'javascript:alert(1)'}])
        html=(self.root/'Teslimler/fotograf-atif-onizleme.html').read_text()
        self.assertNotIn('href="javascript:',html)
        self.assertIn('Test &lt;author&gt;',html)
        self.assertIn(self.photo['license_url'],html)
        self.assertIn('Gösterilen web kopyası:',html)
        self.assertIn('en çok 1600 px',html)

if __name__=='__main__':unittest.main()
