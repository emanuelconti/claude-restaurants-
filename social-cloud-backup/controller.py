"""Cloud publisher for exact assets that passed local visual QA."""
import datetime as dt,hashlib,json,os,re,subprocess,sys
from pathlib import Path
from policy import TZ,target,seen,count_today,next_item,gap_ok,parse_ig_history,local_now,selected_brands,QUEUE_DAYS,FB_RECOVERY_CRON,recovery_allowed,channel_plan,attempt_limit
R=Path(__file__).resolve().parent
now=dt.datetime.now(TZ)
if now>=dt.datetime(2026,11,6,2,tzinfo=TZ):
 print('Temporary backup expired: nothing published.');sys.exit()
manifest=json.loads((R/'queue.json').read_text())
def verify(item):
 folder=R/item['folder']
 assert folder.resolve().is_relative_to((R/'queue').resolve())
 for name,digest in item['sha256'].items():
  assert Path(name).name==name
  assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
 # Reel hashes are relative to the date folder, not to the carousel folder.
 for name,digest in item.get('reel_sha256',{}).items():
  p=R/'queue'/item['brand']/item['date']/'reel'/name
  assert Path(name).name==name and hashlib.sha256(p.read_bytes()).hexdigest()==digest
for item in manifest:verify(item)
if '--validate' in sys.argv or '--check' in sys.argv:
 import shutil
 if shutil.which('ffprobe'):
  videos=list((R/'queue/gms').rglob('*.mp4'))
  assert len(videos)==24,('Expected 24 reviewed videos',len(videos))
  for video in videos:
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-show_entries','format=duration','-of','json',str(video)],text=True))
   stream=probe['streams'][0]
   assert stream['width']==1080 and stream['height']==1920 and 0<float(probe['format']['duration'])<=60,str(video)
  print('PASS: 24 actual MP4 files are 1080x1920, valid duration under 60 seconds.')
if '--validate' in sys.argv:
 for day in ('2026-11-03','2026-11-04','2026-11-05'):
  for b in ('sp','sin','gms'):
   assert len([x for x in manifest if x['brand']==b and x['date']==day])==8,(b,day)
 print(f'PASS: {len(manifest)} reviewed queue items, eight per brand/day; asset hashes match. No credentials loaded or publications attempted.')
 sys.exit()
cfg=json.loads(os.environ['SOCIAL_BACKUP_ENV'])
for v in cfg.values():
 if len(str(v))>15 and os.environ.get('GITHUB_ACTIONS'):print('::add-mask::'+str(v))
cfg.update(GMS_PINTEREST_ENABLED='0',GMS_TIKTOK_ENABLED='0',GMS_YOUTUBE_PRIVACY='public')
(R/'private').mkdir(exist_ok=True);(R/'private/environment.json').write_text(json.dumps(cfg));os.chmod(R/'private/environment.json',0o600)
def run(b,script,*args,quiet=False):
 p=subprocess.run([sys.executable,str(R/'run.py'),b,script,*args],capture_output=True,text=True)
 text=p.stdout+p.stderr
 if not quiet or p.returncode:print(text,flush=True)
 return p.returncode,text
brands={'sp':('INSTAGRAM_ACCESS_TOKEN','socialperks.es'),'sin':('INSTAGRAM_TOKEN_SINCRONIA','sincronia.live'),'gms':('INSTAGRAM_TOKEN_SOWLD','goodmessage_studio')}
statepath=R/'state.json';state=json.loads(statepath.read_text()) if statepath.exists() else {}
errors=[]
def save():statepath.write_text(json.dumps(state,indent=2))
def history(b,channel):
 if channel=='ig':
  token,handle=brands[b]
  rc,out=run(b,'ig_publish.py','--token-env',token,'--check-token',quiet=True)
  if rc or '@'+handle not in out:raise RuntimeError('Instagram account check failed')
  rc,out=run(b,'ig_publish.py','--token-env',token,'--recent','50',quiet=True)
  if rc:raise RuntimeError('Instagram history unavailable')
  return parse_ig_history(out)
 rc,out=run('gms','cloud_channel_stats.py',channel,quiet=True)
 if rc:raise RuntimeError(channel+' identity/history unavailable')
 return json.loads(out)['posts']
cron=os.environ.get('BACKUP_CRON','')
recover='--recover-gms' in sys.argv
recover_today=recovery_allowed(now) and (recover or cron==FB_RECOVERY_CRON)
if recover and not recovery_allowed(now):
 raise SystemExit('The owner-authorized GMS catch-up exception has expired; nothing published.')
def process_channel(b,channel):
 tag=b+':'+channel
 try:
  posts=history(b,channel)
  brand_now=local_now(dt.datetime.now(dt.timezone.utc),b)
  if brand_now.date().isoformat() not in QUEUE_DAYS:
   print(tag+': outside approved local calendar days; skipped.');return False
  count=count_today(posts,brand_now,b)
  print(f'{tag}: identity verified; {count} posts today ({brand_now.tzinfo}, {brand_now.date()}).',flush=True)
  if '--check' in sys.argv:return False
  # Reconcile completed and ambiguous attempts against actual remote titles first.
  for item in manifest:
   if item['brand']==b and (found:=seen(item,channel,posts)):
    if channel=='youtube' and found.get('visibility')!='public':
     raise RuntimeError('An expected public YouTube upload is not public; do not upload it again. Check Google approval or processing status.')
    state[item['id']+':'+channel]='confirmed remotely: '+(found.get('url') or item['title'])
  save()
  held=[k for k,v in state.items() if k.endswith(':'+channel) and k.startswith(b+'-') and v.startswith('held:')]
  if held:raise RuntimeError('An earlier publication is ambiguous; reconcile it before sending another item')
  if count>=(8 if recover_today else min(target(brand_now,b),8)):return False
  if channel=='facebook' and not gap_ok(posts,brand_now,60):
   print(tag+': Facebook 60-minute gap respected; skipped.');return False
  item=next_item(manifest,b,channel,brand_now.date().isoformat(),state)
  if item is None:raise RuntimeError('No unused approved item for today while below target')
  verify(item);key=item['id']+':'+channel
  # Second remote read immediately before publication reduces overlap with Claude.
  latest=history(b,channel)
  fresh_now=local_now(dt.datetime.now(dt.timezone.utc),b)
  if fresh_now.date()!=brand_now.date():
   print(tag+': local date changed while checking; skipped.');return False
  if count_today(latest,fresh_now,b)>=(8 if recover_today else min(target(brand_now,b),8)):return False
  if seen(item,channel,latest):state[key]='confirmed remotely';save();return False
  if channel=='facebook' and not gap_ok(latest,fresh_now,60):return False
  state[key]='held: publication attempt started; reconcile remotely before retry';save()
  args=['--date',item['date'],'--out',str(R/'queue'/b)]
  reel=item.get('kind')=='reel'
  sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
  asset_base=f'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/{sha}/social-cloud-backup/'+item['folder']
  os.environ['GMS_PUBLIC_ASSET_BASE']=asset_base
  os.environ['GMS_PUBLIC_VIDEO_URL']=f'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/{sha}/social-cloud-backup/queue/gms/'+item['date']+'/reel/reel.mp4' if reel else ''
  if channel=='ig':
   script='reel_publish.py' if reel else 'ig_publish.py'
   args+=['--token-env',brands[b][0]]
   if not reel:args+=['--slot',str(item['slot']),'--base-url',asset_base]
  elif channel=='youtube':
   script='youtube_publish.py';args+=['--publish']
   if not reel:args+=['--carousel-slot',str(item['slot'])]
  else:
   script={'threads':'threads_publish.py','facebook':'fb_publish.py'}[channel];args+=['--slot',str(item['slot'])]
  rc,out=run(b,script,*args)
  success=any(x in out for x in ['published:','published (public):','already published:'])
  if rc or not success:
   # All errors retain a hold. A later remote read can reconcile a successful-but-uncertain request.
   raise RuntimeError('Publisher stopped or response was ambiguous. No automatic retry.')
  state[key]='success: '+out.strip();save()
  return True
  # A YouTube public request must actually produce a public video; publisher verifies status.
 except Exception as e:
  errors.append(tag+': '+str(e));print('ERROR '+errors[-1],flush=True);return False
for b in (('gms',) if recover else selected_brands(cron,os.environ.get('BACKUP_BRAND','all'))):
 for channel in channel_plan(b,cron,recover):
  for attempt in range(attempt_limit(b,channel,recover,now)):
   if not process_channel(b,channel):break
if errors:raise SystemExit('\n'.join(errors))
if '--check' in sys.argv:
 import urllib.request
 sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
 paths=['queue/'+b+'/2026-11-03/carousel-1/slide-01.jpg' for b in brands]+['queue/gms/2026-11-03/reel/reel.mp4']
 for path in paths:
  url=f'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/{sha}/social-cloud-backup/'+path
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=0-63'}),timeout=60) as response:header=response.read(64)
  assert header[4:8]==b'ftyp' if path.endswith('.mp4') else header[:3]==b'\xff\xd8\xff',path
 print('PASS: public cloud image and video URLs serve real JPEG/MP4 files.')
print('Cloud account checks completed.' if '--check' in sys.argv else 'Cloud approved queue processed with actual per-market counts and channel limits.')
