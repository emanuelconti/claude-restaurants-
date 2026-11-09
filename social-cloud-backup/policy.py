import datetime as dt
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Europe/Paris')  # temporary-backup expiry and European brands
SINGAPORE = ZoneInfo('Asia/Singapore')
HOURS = (9, 11, 14, 16, 17, 18, 20, 22)
SIN_HOURS = (8, 10, 12, 14, 16, 18, 20, 21)
GMS_HOURS = (8, 10, 12, 14, 15, 18, 20, 21)
EU_CRON = '58 6-22 3-5 11 *'  # accepted only for older queued workflow events
SP_CRON = '47 9-23 * * *'  # 09:47-23:47 Madrid
SIN_CRON = '23 8-23 * * *'  # 08:23-23:23 Paris
FB_RECOVERY_CRON = '7,27,37,47,57 6-15 3 11 *'  # owner-authorized 3 November recovery only
GMS_CRON = '17 8-23 * * *'  # 08:17-23:17 Singapore, including recovery checks
WATCHDOG_CRON = '41 0-23 * * *'  # Independent UTC recovery; target() always uses each market's own clock.
QUEUE_DAYS = frozenset(('2026-11-03', '2026-11-04', '2026-11-05'))
STOP_SIGNALS = ('blocked', 'limit', 'spam', 'restricted', 'temporarily', 'too soon', 'quota')

def timezone_for(brand):
 return {'gms': SINGAPORE, 'sp': ZoneInfo('Europe/Madrid'), 'sin': TZ}[brand]

def local_now(now, brand):
 if now.tzinfo is None:
  raise ValueError('An aware timestamp is required')
 return now.astimezone(timezone_for(brand))

def target(now, brand='sp'):
 local = local_now(now, brand)
 minute = {'gms':17,'sp':47,'sin':23}[brand]
 hours = {'gms':GMS_HOURS,'sp':HOURS,'sin':SIN_HOURS}[brand]
 return sum((local.hour, local.minute) >= (hour, minute) for hour in hours)

def selected_brands(cron='', requested='all'):
 if cron:
  if cron in (WATCHDOG_CRON, '41 * * * *'): return ('sp', 'sin', 'gms')
  if cron == EU_CRON: return ('sp', 'sin')
  if cron == SP_CRON: return ('sp',)
  if cron == SIN_CRON: return ('sin',)
  if cron in (GMS_CRON, FB_RECOVERY_CRON): return ('gms',)
  raise ValueError('Unknown cloud schedule; refusing to publish')
 if requested == 'all': return ('sp', 'sin', 'gms')
 if requested in ('sp', 'sin', 'gms'): return (requested,)
 raise ValueError('Unknown brand')

def youtube_title(title): return (title[:62]+' | goodmessagestudio.com #Shorts')[:100]
def seen(item, channel, posts):
 wanted = youtube_title(item['title']) if channel == 'youtube' else item['title']
 return next((p for p in posts if p['title'] == wanted), None)
def count_today(posts, now, brand='sp'):
 day = local_now(now, brand).date()
 zone = timezone_for(brand)
 return sum(dt.datetime.fromisoformat(p['stamp'].replace('Z','+00:00')).astimezone(zone).date() == day for p in posts if p.get('stamp'))
def next_item(items, brand, channel, day, state):
 ordered = sorted(items, key=lambda x: x.get('publish_order', x.get('slot', 0)))
 return next((x for x in ordered if x['brand'] == brand and x['date'] == day and not state.get(x['id']+':'+channel)), None)
def gap_ok(posts, now, minutes):
 stamps = [dt.datetime.fromisoformat(p['stamp'].replace('Z','+00:00')) for p in posts if p.get('stamp')]
 return not stamps or (now-max(stamps)).total_seconds() >= minutes*60

def parse_ig_history(text):
 import re
 rows=[]
 for line in text.splitlines():
  if re.match(r'\d{4}-\d\d-\d\dT',line):
   parts=line.split(None,1)
   rows.append(dict(stamp=parts[0],title=parts[1].strip() if len(parts)>1 else ''))
 return rows


def recovery_allowed(now):
 return local_now(now, 'gms').date().isoformat() == '2026-11-03'

def channel_plan(brand, cron='', recover=False):
 if cron == FB_RECOVERY_CRON: return ('facebook',)
 return ('ig',) if brand != 'gms' else ('ig','threads','youtube','facebook','pinterest')

def daily_cap(channel, slots_due):
 """Posts allowed so far today on one channel. Threads (owner, 7 November): Meta kept removing posts
 as spam at eight a day, so it gets at most two, the lunch and evening slots, never close together."""
 if channel == 'threads': return sum(slots_due >= k for k in (3, 7))
 # Pinterest (owner, 9 November, Standard access approved): three Pins a day, morning, afternoon, evening.
 if channel == 'pinterest': return sum(slots_due >= k for k in (2, 5, 8))
 return min(slots_due, 8)

def attempt_limit(brand, channel, recover, now):
 # Explicit one-day exception requested by owner; Facebook never bypasses 60 minutes.
 return 8 if recover and recovery_allowed(now) and brand == 'gms' and channel != 'facebook' else 1


def count_known_posts(posts, now, brand, channel, items, state):
 """Include durable success receipts while the platform history is still catching up."""
 day=local_now(now,brand).date().isoformat()
 remote=[p for p in posts if (channel!='youtube' or p.get('visibility','public')=='public') and p.get('stamp') and dt.datetime.fromisoformat(p['stamp'].replace('Z','+00:00')).astimezone(timezone_for(brand)).date().isoformat()==day]
 remote_titles={p['title'] for p in remote}
 extra=0
 for item in items:
  if item['brand']!=brand or item['date']!=day:continue
  receipt=state.get(item['id']+':'+channel,'')
  if not receipt.startswith(('success:', 'confirmed remotely')):continue
  title=youtube_title(item['title']) if channel=='youtube' else item['title']
  if title not in remote_titles:extra+=1
 return len(remote)+extra
