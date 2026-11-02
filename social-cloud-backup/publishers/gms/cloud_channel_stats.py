"""Read-only, identity-checked histories for the three non-Instagram channels."""
import datetime as dt,json,os,sys
from zoneinfo import ZoneInfo
channel=sys.argv[1]
if channel=='threads':
 import threads_publish as T
 token=os.environ['THREADS_TOKEN_GMS'];me=T.call('GET','me',token,{'fields':'id,username'})
 if me.get('username')!='goodmessage_studio':raise SystemExit('Wrong Threads identity')
 posts=T.call('GET',str(me['id'])+'/threads',token,{'fields':'text,timestamp,permalink','limit':50}).get('data',[])
 rows=[{'title':(p.get('text') or '').split('\n',1)[0].strip(),'stamp':p.get('timestamp'),'url':p.get('permalink')} for p in posts]
elif channel=='facebook':
 import fb_publish as F
 page=os.environ['FB_PAGE_ID_GMS'];token=F.page_token(page,os.environ['FB_PAGE_TOKEN_GMS'])
 name=F.call('GET',page,token,{'fields':'name'}).get('name')
 if name!='Good Message Studio':raise SystemExit('Wrong Facebook Page identity')
 rows=[{'title':(p.get('message') or '').split('\n',1)[0].strip(),'stamp':p.get('created_time'),'url':p.get('permalink_url')} for p in F.recent(page,token)]
elif channel=='youtube':
 import youtube_publish as Y
 import channel_guard as G
 token=Y.access_token();items=G.http('GET',Y.API+'/channels?part=snippet,contentDetails&mine=true',token).get('items',[])
 if len(items)!=1 or items[0]['id']!='UCsQQkWC_XVXr4_axBT-KZNA':raise SystemExit('Wrong YouTube identity')
 pid=items[0]['contentDetails']['relatedPlaylists']['uploads']
 posts=G.http('GET',Y.API+'/playlistItems?part=snippet,contentDetails&maxResults=50&playlistId='+pid,token).get('items',[])
 rows=[{'title':p['snippet']['title'],'stamp':p.get('contentDetails',{}).get('videoPublishedAt'),'url':'https://www.youtube.com/shorts/'+p['contentDetails']['videoId']} for p in posts if p.get('contentDetails',{}).get('videoPublishedAt')]
 # Read actual visibility, not just the visibility requested at upload time.
 ids=','.join(p['contentDetails']['videoId'] for p in posts if p.get('contentDetails',{}).get('videoId'))
 status={}
 if ids:
  status={p['id']:p.get('status',{}) for p in G.http('GET',Y.API+'/videos?part=status&id='+ids,token).get('items',[])}
 for row in rows:
  row['visibility']=status.get(row['url'].rsplit('/',1)[-1],{}).get('privacyStatus','unknown')
else:raise SystemExit('Unsupported channel')
print(json.dumps({'channel':channel,'posts':rows}))
