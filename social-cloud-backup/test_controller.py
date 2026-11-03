"""Exercise the actual publish/reconcile function without a network or credentials."""
import ast,datetime as dt,types,unittest
from pathlib import Path
from policy import *

class RecoveryControllerTests(unittest.TestCase):
 def fixture(self,channel,already=0):
  source=(Path(__file__).parent/'controller.py').read_text()
  fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='process_channel')
  now=dt.datetime(2026,11,3,14,30,tzinfo=SINGAPORE)
  class Clock:
   @staticmethod
   def now(zone):return now.astimezone(zone)
  posts=[dict(title=f'Other {n}',stamp=now.isoformat()) for n in range(already)]
  items=[dict(id=f'gms-{n}',brand='gms',date='2026-11-03',slot=n+1,title=f'Topic {n}',folder=f'queue/gms/2026-11-03/carousel-{n+1}') for n in range(8)]
  def run(brand,script,*args):
   slot=int(args[args.index('--slot')+1]);item=items[slot-1]
   posts.append(dict(title=item['title'],stamp=now.isoformat()))
   return 0,'published: https://example.com/'+item['id']
  ns=dict(dt=types.SimpleNamespace(datetime=Clock,timezone=dt.timezone),local_now=local_now,count_today=count_today,count_known_posts=count_known_posts,seen=seen,next_item=next_item,gap_ok=gap_ok,target=target,QUEUE_DAYS=QUEUE_DAYS,
   history=lambda b,c:list(posts),manifest=items,state={},save=lambda:None,errors=[],sys=types.SimpleNamespace(argv=['controller.py','--recover-gms']),recover_today=True,
   verify=lambda item:None,R=Path('/reviewed'),subprocess=types.SimpleNamespace(check_output=lambda *a,**kw:'reviewedcommit'),os=types.SimpleNamespace(environ={}),brands={'gms':('TOKEN_NAME','goodmessage_studio')},run=run)
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'controller.py','exec'),ns)
  return ns,posts
 def test_explicit_recovery_fills_only_missing_posts_up_to_eight(self):
  ns,posts=self.fixture('ig',2)
  for _ in range(8):
   if not ns['process_channel']('gms','ig'):break
  self.assertEqual(len(posts),8)
  self.assertEqual(len(ns['state']),6)
  self.assertEqual(ns['errors'],[])
 def test_facebook_does_not_bypass_existing_gap_in_recovery(self):
  ns,posts=self.fixture('facebook',1)
  self.assertFalse(ns['process_channel']('gms','facebook'))
  self.assertEqual(len(posts),1)
  self.assertEqual(ns['state'],{})

 def test_delayed_remote_history_cannot_cause_extra_uploads(self):
  ns,posts=self.fixture('ig',2)
  original=list(posts)
  ns['history']=lambda b,c:list(original)
  for _ in range(8):
   if not ns['process_channel']('gms','ig'):break
  self.assertEqual(len(posts),8)
  self.assertEqual(len(ns['state']),6)

if __name__=='__main__':unittest.main()
