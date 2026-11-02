import datetime as dt
from zoneinfo import ZoneInfo
TZ=ZoneInfo('Europe/Paris')
HOURS=(7,8,9,13,14,15,19,20)
def target(now):return sum(now.hour>=h for h in HOURS)
def youtube_title(title):return (title[:62]+' | goodmessagestudio.com #Shorts')[:100]
def seen(item,channel,posts):
 wanted=youtube_title(item['title']) if channel=='youtube' else item['title']
 return next((p for p in posts if p['title']==wanted),None)
def count_today(posts,now):
 return sum(dt.datetime.fromisoformat(p['stamp'].replace('Z','+00:00')).astimezone(TZ).date()==now.date() for p in posts if p.get('stamp'))
def next_item(items,brand,channel,day,state):
 return next((x for x in items if x['brand']==brand and x['date']==day and not state.get(x['id']+':'+channel)),None)
def gap_ok(posts,now,minutes):
 stamps=[dt.datetime.fromisoformat(p['stamp'].replace('Z','+00:00')) for p in posts if p.get('stamp')]
 return not stamps or (now-max(stamps)).total_seconds()>=minutes*60
