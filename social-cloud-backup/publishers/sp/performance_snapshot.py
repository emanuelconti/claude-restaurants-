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
known=IG.KNOWN_IG_IDS.get(variable) or os.environ.get(identity[brand])
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

channels={}
if brand=='gms':
 try:
  import fb_publish as F
  page=os.environ['FB_PAGE_ID_GMS'];ft=F.page_token(page,os.environ['FB_PAGE_TOKEN_GMS'])
  fb=F.call('GET',page+'/posts',ft,{'fields':'message,created_time,permalink_url,reactions.limit(0).summary(true),comments.limit(0).summary(true),shares','limit':30}).get('data',[])
  channels['facebook']={'availability':'available','posts':[{'title':(p.get('message') or '').split('\n')[0],'stamp':p.get('created_time'),'url':p.get('permalink_url'),'reactions':p.get('reactions',{}).get('summary',{}).get('total_count'),'comments':p.get('comments',{}).get('summary',{}).get('total_count'),'shares':p.get('shares',{}).get('count')} for p in fb]}
 except Exception as error:
  channels['facebook']={'availability':'unavailable with current grant','reason':type(error).__name__}
  if type(error).__name__!='Stop':
   try:
    history=F.recent(page,ft)
    channels['facebook'].update(availability='history available; engagement not available with current grant',posts=[{'title':(p.get('message') or '').split('\n')[0],'stamp':p.get('created_time'),'url':p.get('permalink_url')} for p in history])
   except Exception:pass
 try:
  import youtube_publish as Y
  import channel_guard as G
  yt=Y.access_token();ch=G.http('GET',Y.API+'/channels?part=contentDetails&mine=true',yt).get('items',[])
  if len(ch)!=1 or ch[0]['id']!='UCsQQkWC_XVXr4_axBT-KZNA':raise RuntimeError('YouTube identity mismatch')
  pid=ch[0]['contentDetails']['relatedPlaylists']['uploads']
  uploads=G.http('GET',Y.API+'/playlistItems?part=contentDetails&maxResults=30&playlistId='+pid,yt).get('items',[])
  ids=','.join(p['contentDetails']['videoId'] for p in uploads)
  videos=G.http('GET',Y.API+'/videos?part=snippet,statistics,status&id='+ids,yt).get('items',[]) if ids else []
  channels['youtube']={'availability':'available','posts':[{'title':p['snippet']['title'],'stamp':p['snippet']['publishedAt'],'visibility':p['status']['privacyStatus'],'views':p.get('statistics',{}).get('viewCount'),'likes':p.get('statistics',{}).get('likeCount'),'comments':p.get('statistics',{}).get('commentCount'),'url':'https://www.youtube.com/shorts/'+p['id']} for p in videos]}
 except Exception as error:channels['youtube']={'availability':'unavailable with current grant','reason':type(error).__name__}
 try:
  import threads_publish as T
  tt=os.environ['THREADS_TOKEN_GMS'];me=T.call('GET','me',tt,{'fields':'id,username'})
  if me.get('username')!='goodmessage_studio':raise RuntimeError('Threads identity mismatch')
  threads=T.call('GET',str(me['id'])+'/threads',tt,{'fields':'id,text,timestamp,permalink','limit':20}).get('data',[])
  threadrows=[];insights=True
  for post in threads:
   counters={}
   if insights:
    try:
     values=T.call('GET',post['id']+'/insights',tt,{'metric':'likes,replies,reposts,quotes'}).get('data',[])
     counters={v['name']:(v.get('values') or [{}])[0].get('value') for v in values}
    except Exception:insights=False
   threadrows.append({'title':(post.get('text') or '').split('\n')[0],'stamp':post.get('timestamp'),'url':post.get('permalink'),'public_interactions':counters or None})
  channels['threads']={'availability':'available' if insights else 'history available; engagement not available with current grant','posts':threadrows}
 except Exception as error:channels['threads']={'availability':'unavailable with current grant','reason':type(error).__name__}

print(json.dumps({'schema_version':2,'channels':channels,'brand':brand,'account':handle,'timezone':zone,'posts':rows,'limits':'Public likes/comments only; no reach, saves, demographics, sales or conversion claimed.'}))
