import contextlib,io,json,os,runpy,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
class SnapshotTests(unittest.TestCase):
 def run_snapshot(self, response=None, fail=False):
  calls=[]
  def call(method,path,token,params):
   calls.append(path)
   if path.endswith('/media'):return {'data':[{'id':str(i),'timestamp':'2026-11-18T10:00:00Z','media_product_type':'REELS','like_count':2,'comments_count':1} for i in range(2)]}
   if fail:raise RuntimeError('permission unavailable')
   return {'data':response or []}
  ig=types.SimpleNamespace(KNOWN_IG_IDS={},resolve=lambda *x:('own','socialperks.es'),call=call)
  stream=io.StringIO()
  with patch.dict(sys.modules,{'ig_publish':ig}),patch.dict(os.environ,{'TEST_TOKEN':'test'}),patch.object(sys,'argv',['snapshot','sp','TEST_TOKEN','socialperks.es','Europe/Madrid']),contextlib.redirect_stdout(stream):
   runpy.run_path(str(Path(__file__).parent/'publishers/sp/performance_snapshot.py'))
  return json.loads(stream.getvalue()),calls
 def test_views_zero_is_observed_not_missing(self):
  data,_=self.run_snapshot([{'name':'views','values':[{'value':0}]}]);self.assertEqual(data['posts'][0]['views'],0);self.assertIsNone(data['posts'][0]['reach']);self.assertEqual(data['posts'][0]['format'],'REELS')
 def test_denied_insights_preserve_public_metrics_and_stop_probing(self):
  data,calls=self.run_snapshot(fail=True);self.assertEqual(len(calls),2);self.assertTrue(all(x['views'] is None for x in data['posts']));self.assertEqual(data['posts'][0]['likes'],2)
 def test_total_value_and_missing_stay_distinct(self):
  data,_=self.run_snapshot([{'name':'views','total_value':{'value':42}}]);self.assertEqual(data['posts'][0]['views'],42);self.assertIsNone(data['posts'][0]['saves'])
