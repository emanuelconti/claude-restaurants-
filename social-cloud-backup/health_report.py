"""Daily public-result snapshots and a single changing queue-health alert."""
import base64,datetime as dt,json,os,subprocess,sys,urllib.request
from collections import defaultdict
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo
from policy import timezone_for
R=Path(__file__).resolve().parent
now=dt.datetime.now(dt.timezone.utc)
repo='emanuelconti/claude-restaurants-'
config=json.loads(os.environ['SOCIAL_BACKUP_ENV'])
config.update({k:os.environ[k] for k in ('PINTEREST_APP_ID_GMS','PINTEREST_APP_SECRET_GMS','PINTEREST_REFRESH_TOKEN_GMS','PINTEREST_BOARD_GMS','YOUTUBE_REFRESH_TOKEN_GMS','YOUTUBE_CLIENT_ID_GMS','YOUTUBE_CLIENT_SECRET_GMS') if os.environ.get(k)})
for v in config.values():
 if len(str(v))>15 and os.environ.get('GITHUB_ACTIONS'):print('::add-mask::'+str(v))
(R/'private').mkdir(exist_ok=True)
p=R/'private/environment.json';p.write_text(json.dumps(config));p.chmod(0o600)
manifest=json.loads((R/'queue.json').read_text())
state_path=R/'state.json'
platform_state=json.loads(state_path.read_text()) if state_path.exists() else {}
(R/'performance').mkdir(exist_ok=True)
health={'day_utc':now.date().isoformat(),'brands':{}}
for brand,variable,handle in [('sp','INSTAGRAM_ACCESS_TOKEN','socialperks.es'),('sin','INSTAGRAM_TOKEN_SINCRONIA','sincronia.live'),('gms','INSTAGRAM_TOKEN_SOWLD','goodmessage_studio')]:
 zone=timezone_for(brand);day=now.astimezone(zone).date();key=day.isoformat()
 path=R/'performance'/f'{brand}.json'
 old=json.loads(path.read_text()) if path.exists() else {}
 paused=any(k.startswith('platform_block:'+brand+':') and v for k,v in platform_state.items())
 if paused:print(f'Public metrics for {brand} retained while a platform restriction requires verification; no extra API probes.')
 if not paused and (old.get('market_date')!=key or old.get('schema_version')!=2):
  result=subprocess.run([sys.executable,str(R/'run.py'),brand,'performance_snapshot.py',brand,variable,handle,str(zone)],capture_output=True,text=True)
  if result.returncode:
   print(f'Public results unavailable for {brand}; publication remains independent.')
  else:
   try:
    snapshot=json.loads(result.stdout);snapshot['market_date']=key
    groups=defaultdict(list)
    for post in snapshot['posts']:
     age=(now-dt.datetime.fromisoformat(post['stamp'])).total_seconds()/3600
     if 24<=age<=168 and post['likes'] is not None and post['comments'] is not None:groups[post['local_hour']].append(post['likes']+post['comments'])
    snapshot['mature_hour_summary']=[{'local_hour':h,'posts':len(xs),'median_public_interactions':median(xs)} for h,xs in sorted(groups.items())]
    snapshot['timing_status']='insufficient comparable samples' if sum(len(v) for v in groups.values())<30 else 'editor review required before changing schedule'
    path.write_text(json.dumps(snapshot,indent=2)+'\n')
    lines=[f'# {brand}: daily measured results',f'Market date: {key}. Timezone: {zone}.',snapshot['limits'],f"Observed posts: {len(snapshot['posts'])}.",f"Timing: {snapshot['timing_status']}."]
    for row in snapshot['mature_hour_summary']:lines.append(f"Hour {row['local_hour']:02d}:00: n={row['posts']}, median public likes+comments={row['median_public_interactions']} (posts 24h to 7d old).")
    for channel,entry in snapshot.get('channels',{}).items():lines.append(f"{channel}: {entry['availability']}; observed posts={len(entry.get('posts',[]))}. Per-post public counters are in the JSON snapshot; missing counters are not zero.")
    lines.append('Primary editor adapts future reviewed themes, captions and local windows from this evidence. Do not infer purchase conversion, causality or demographic targeting from these counters.')
    (R/'performance'/f'{brand}.md').write_text('\n'.join(lines)+'\n')
   except (ValueError,KeyError):print(f'Invalid public-result response for {brand}; retained previous snapshot.')
 coverage=[]
 for offset in range(7):
  date=(day+dt.timedelta(days=offset)).isoformat()
  items=[x for x in manifest if x['brand']==brand and x['date']==date]
  coverage.append({'date':date,'approved_items':len(items)})
 contiguous=0
 for d in coverage:
  if d['approved_items']!=8:break
  contiguous+=1
 health['brands'][brand]={'timezone':str(zone),'market_date':key,'days_covered_including_today':contiguous,'coverage':coverage,'paused_channels':[k.split(':',2)[2] for k,v in platform_state.items() if k.startswith('platform_block:'+brand+':') and v]}
(R/'health.json').write_text(json.dumps(health,indent=2)+'\n')
needs=[f"{b}: {v['days_covered_including_today']} reviewed days including today ({v['timezone']})." for b,v in health['brands'].items() if v['days_covered_including_today']<3]
def api(method,path,body=None):
 token=os.environ.get('GH_TOKEN')
 if not token:return None
 data=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request('https://api.github.com/repos/'+repo+'/'+path,data=data,method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
if os.environ.get('GH_TOKEN'):
 title='Social publisher: reviewed queue needs attention'
 issues=api('GET','issues?state=open&per_page=100') or []
 existing=next((i for i in issues if i['title']==title and 'pull_request' not in i),None)
 if needs:
  body='Primary/backup editors must replenish the reviewed queue. Publishing never invents or repeats missing content.\n\n'+'\n'.join(needs)+'\n\nSee SOCIAL_CLOUD_RUNBOOK.md and social-cloud-backup/health.json on codex/social-cloud-backup. No secrets are included.'
  if not existing:api('POST','issues',{'title':title,'body':body})
  elif existing.get('body')!=body:api('PATCH',f"issues/{existing['number']}",{'body':body})
 elif existing:api('PATCH',f"issues/{existing['number']}",{'state':'closed'})
print('Market result snapshots and independent queue-coverage checks completed.')
