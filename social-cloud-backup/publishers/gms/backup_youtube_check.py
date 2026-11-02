import youtube_publish as Y
import channel_guard as G
import json

t=Y.access_token()
ch=G.http('GET',Y.API+'/channels?part=snippet,contentDetails&mine=true',t).get('items',[])
if len(ch)!=1 or ch[0]['id']!='UCsQQkWC_XVXr4_axBT-KZNA':
 raise SystemExit('FAIL: YouTube channel does not match the authorized Good Message Studio channel')
p=ch[0]['contentDetails']['relatedPlaylists']['uploads']
items=G.http('GET',Y.API+'/playlistItems?part=snippet,contentDetails&maxResults=15&playlistId='+p,t).get('items',[])
print('OK: @goodmessage_studio; refresh token accepted')
for i in items:
 print(i.get('contentDetails',{}).get('videoPublishedAt','?'),i['snippet']['title'])
