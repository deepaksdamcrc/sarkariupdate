import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pages_sync',Path(__file__).resolve().parents[1]/'scripts/sync-pages.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SyncTests(unittest.TestCase):
 def fixture(self):return {'id':'12345678-1234-1234-1234-123456789012','title':'Latest exam update','content':'Updated official details.','category':'Result','status':'published','updatedAt':'2026-11-19T12:00:00Z','sourceUrl':'https://sarkariresult.com.cm/example/','sourceNote':'Private','automation':{'sourceFingerprint':'secret-metadata'},'verificationNote':'private evidence','links':[['Official','https://example.gov.in/'],['Reference','https://sarkariresult.com.cm/example/']]}
 def test_private_fields_and_drafts_not_exported(self):
  a=self.fixture();draft={**a,'id':'22345678-1234-1234-1234-123456789012','status':'draft'};result=m.sanitize_articles([a,draft]);self.assertEqual(len(result),1);self.assertNotIn('sarkariresult.com.cm',json.dumps(result));self.assertNotIn('sourceUrl',result[0]);self.assertNotIn('automation',result[0]);self.assertNotIn('verificationNote',result[0]);self.assertEqual(result[0]['links'],[['Official','https://example.gov.in/']]);self.assertTrue(result[0]['imageUrl'].startswith('covers/'))
 def test_duplicate_or_path_traversal_id_rejected(self):
  a=self.fixture()
  with self.assertRaises(ValueError):m.sanitize_articles([a,a])
  with self.assertRaises(ValueError):m.sanitize_articles([{**a,'id':'../../malicious'}])
 def test_build_includes_new_articles_and_local_assets(self):
  a=self.fixture();b={**a,'id':'22345678-1234-1234-1234-123456789012','title':'Newly published article'}
  with tempfile.TemporaryDirectory()as t:
   out=Path(t)/'_test_site';m.build_site([a,b],out);records=json.loads((out/'data/articles.json').read_text());self.assertEqual(len(records),2);self.assertEqual(records[1]['title'],'Newly published article');self.assertTrue((out/'covers'/f"{b['id']}.svg").exists());html=(out/'index.html').read_text();self.assertIn("new URL('data/articles.json',document.baseURI)",html);self.assertNotIn('sourceUrl',html);self.assertFalse((out/'worker').exists())
 def test_refresh_uses_new_dataset_and_failure_keeps_previous_site(self):
  a=self.fixture();b={**a,'id':'22345678-1234-1234-1234-123456789012','title':'A freshly published result'}
  with tempfile.TemporaryDirectory()as t:
   out=Path(t)/'_test_site';m.build_site([a],out);m.build_site([a,b],out);self.assertEqual(len(json.loads((out/'data/articles.json').read_text())),2);before=(out/'data/articles.json').read_bytes()
   with self.assertRaises(ValueError):m.build_site([],out)
   self.assertEqual((out/'data/articles.json').read_bytes(),before);self.assertNotIn('articles=[{',(out/'index.html').read_text())
 def test_fetch_never_sends_token_to_insecure_or_path_origin(self):
  for origin in ['http://example.test','https://user:pass@example.test','https://example.test/unsafe']:
   with self.assertRaises(ValueError):m.fetch_articles(origin,'fake-token')
if __name__=='__main__':unittest.main()
