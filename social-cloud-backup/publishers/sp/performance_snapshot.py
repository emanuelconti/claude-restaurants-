"""Read public post counters only. No advertising actions or private audience exports."""
import datetime as dt,json,os,sys
from zoneinfo import ZoneInfo
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"gms"))
import ig_publish as IG
brand,variable,expected,zone=sys.argv[1:]
token=os.environ[variable]
if token.startswith('EAA'):IG.API='https://graph.facebook.com/v21.0'
identity={'gms':'INSTAGRAM_USER_ID_SOWLD','sin':'SINCRONIA_IG_ID','sp':'INSTAGRAM_USER_ID'}
known=os.environ.get(identity[brand]) or IG.KNOWN_IG_IDS.get(variable)
if known:os.environ['INSTAGRAM_USER_ID']=known
os.environ['IG_STRICT_ACCOUNT']='1'
user,handle=IG.resolve(token,expected)
if handle!=expected:raise SystemExit('Account mismatch')
posts=IG.call('GET',str(user)+'/media',token,{'fields':'caption,timestamp,like_count,comments_count,permalink','limit':50}).get('data',[])
rows=[]
for p in posts:
 if not p.get('timestamp'):continue
 stamp=dt.datetime.fromisoformat(p['timestamp'].replace('Z','+00:00')).astimezone(ZoneInfo(zone))
 rows.append({'title':(p.get('caption') or '').split('\n')[0],'stamp':stamp.isoformat(),'local_hour':stamp.hour,'likes':p.get('like_count'),'comments':p.get('comments_count'),'url':p.get('permalink')})
print(json.dumps({'brand':brand,'account':handle,'timezone':zone,'posts':rows,'limits':'Public likes/comments only; no reach, saves, demographics, sales or conversion claimed.'}))
