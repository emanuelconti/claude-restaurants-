"""Cloud publisher for exact assets that passed local visual QA."""
import datetime as dt,hashlib,json,os,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from policy import TZ,target,seen,count_today,next_item,gap_ok,parse_ig_history,local_now,selected_brands,QUEUE_DAYS,FB_RECOVERY_CRON,recovery_allowed,channel_plan,attempt_limit,count_known_posts,STOP_SIGNALS
R=Path(__file__).resolve().parent
now=dt.datetime.now(TZ)
# Owner, 3 November: keep the cloud publisher running after the Claude quota reset.
manifest=json.loads((R/'queue.json').read_text())
def reel_folder(item):
 name=item.get('reel_dir','reel')
 assert Path(name).name==name and re.fullmatch(r'reel(-[1-8])?',name),name
 return R/'queue'/item['brand']/item['date']/name
def verify(item):
 folder=R/item['folder']
 assert folder.resolve().is_relative_to((R/'queue').resolve())
 for name,digest in item['sha256'].items():
  assert Path(name).name==name
  assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
 # Reel hashes are relative to the reel folder of the date (reel, reel-<slot>), not to the carousel folder.
 for name,digest in item.get('reel_sha256',{}).items():
  p=reel_folder(item)/name
  assert Path(name).name==name and hashlib.sha256(p.read_bytes()).hexdigest()==digest
for item in manifest:verify(item)
if '--validate' in sys.argv or '--check' in sys.argv:
 import shutil
 if shutil.which('ffprobe'):
  import media_checks as M
  expected=[]
  for x in manifest:
   if 'tiktok.mp4' in x['sha256']:expected.append((x,R/x['folder']/'tiktok.mp4',False))
   if x.get('kind')=='reel':expected.append((x,reel_folder(x)/'reel.mp4',True))
  actual={p.resolve() for p in (R/'queue').rglob('*.mp4')}
  assert actual=={p.resolve() for _,p,_ in expected},('Every MP4 must be a reviewed queue asset',len(actual),len(expected))
  assert all(x['brand']=='gms' or reel for x,_,reel in expected),'Only GMS has prebuilt Shorts'
  assert len([1 for x in manifest if x['brand']=='gms' and 'tiktok.mp4' not in x['sha256'] and x.get('kind')!='reel'])==0,'One reviewed video per GMS topic'
  for x,video,reel in expected:
   M.check_video(video,new_reel=reel and x.get('reel_dir','reel')!='reel',legacy_silent_ok=x['date']<'2026-11-04')
   if reel:M.check_reel_folder(reel_folder(x),x['title'])
  print(f'PASS: {len(expected)} actual MP4 files are 1080x1920 H.264 with decoded non-silent AAC audio (3 November legacy Shorts exempt); new reels are 30 fps, 15-30 s, with matching covers and captions.')
if '--validate' in sys.argv:
 assert len({x['id'] for x in manifest})==len(manifest),'Duplicate queue IDs'
 assert len({(x['brand'],x['title']) for x in manifest})==len(manifest),'Repeated brand/topic title'
 for b,day in {(x['brand'],x['date']) for x in manifest}:
  daily=[x for x in manifest if x['brand']==b and x['date']==day]
  assert len(daily)==8 and len({x['slot'] for x in daily})==8,(b,day)
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
owner_test='--owner-av-test-20261103' in sys.argv
if owner_test and not (dt.datetime(2026,11,3,20,tzinfo=dt.timezone.utc) <= dt.datetime.now(dt.timezone.utc) < dt.datetime(2026,11,4,0,tzinfo=dt.timezone.utc)):
 raise SystemExit('The dated owner audiovisual test has expired; nothing published.')
recover='--recover-gms' in sys.argv
recover_today=owner_test or (recovery_allowed(now) and (recover or cron==FB_RECOVERY_CRON))
if recover and not recovery_allowed(now):
 raise SystemExit('The owner-authorized GMS catch-up exception has expired; nothing published.')
def receipt_stamps(tag):
 # Facebook history can lag (Reels especially); the durable receipt also enforces the 60-minute gap.
 stamp=state.get('last_publish_utc:'+tag)
 return [dict(title='',stamp=stamp)] if stamp else []
CARDS_ENABLED=False
def facebook_format(item,state):
 # Owner, 5 November: about one Facebook post in three is clickable product cards (orders 2, 5, 8);
 # reels at lunch/evening (3, 7); reviewed editorial photo posts otherwise (1, 4, 6).
 order=item.get('publish_order',item['slot'])
 # 6 November evidence (check run 42155005771): the first card post passed its read-back at 02:33 UTC,
 # but 40 minutes later Meta's external image cache served 2 of 3 card pictures as 1x1 blanks, and older
 # posts flip between real and blank. External card pictures are not persistent, so cards stay OFF and
 # these slots use the native photo showcase (Meta-hosted photos, product URLs in the caption).
 if order in (2,5,8):return 'cards' if CARDS_ENABLED and not state.get('fb_cards_paused') else 'products'
 return 'editorial'
def process_channel(b,channel):
 tag=b+':'+channel
 block_key='platform_block:'+tag
 if state.get(block_key):
  print(tag+': paused after a platform restriction; no API retry until verified operator clearance.',flush=True)
  return False
 try:
  posts=history(b,channel)
  brand_now=local_now(dt.datetime.now(dt.timezone.utc),b)
  if '--check' not in sys.argv and not any(x['brand']==b and x['date']==brand_now.date().isoformat() for x in manifest):
   raise RuntimeError('Reviewed queue has no content for this market date; replenish it, never invent or repost')
  count=count_known_posts(posts,brand_now,b,channel,manifest,state)
  print(f'{tag}: identity verified; {count} posts today ({brand_now.tzinfo}, {brand_now.date()}).',flush=True)
  if '--check' in sys.argv:return False
  # Reconcile completed and ambiguous attempts against actual remote titles first.
  for item in manifest:
   if item['brand']==b and not state.get(item['id']+':'+channel,'').startswith('withdrawn:') and (found:=seen(item,channel,posts)):
    if channel=='youtube' and found.get('visibility')!='public':
     raise RuntimeError('An expected public YouTube upload is not public; do not upload it again. Check Google approval or processing status.')
    state[item['id']+':'+channel]='confirmed remotely: '+(found.get('url') or item['title'])
  save()
  held=[k for k,v in state.items() if k.endswith(':'+channel) and k.startswith(b+'-') and v.startswith('held:')]
  if held:raise RuntimeError('An earlier publication is ambiguous; reconcile it before sending another item')
  if count>=(8 if recover_today else min(target(brand_now,b),8)):return False
  if channel=='facebook' and not gap_ok(posts+receipt_stamps(tag),brand_now,60):
   print(tag+': Facebook 60-minute gap respected; skipped.');return False
  item=next_item(manifest,b,channel,brand_now.date().isoformat(),state)
  if item is None:raise RuntimeError('No unused approved item for today while below target')
  verify(item);key=item['id']+':'+channel
  # Second remote read immediately before publication reduces overlap with Claude.
  latest=history(b,channel)
  fresh_now=local_now(dt.datetime.now(dt.timezone.utc),b)
  if fresh_now.date()!=brand_now.date():
   print(tag+': local date changed while checking; skipped.');return False
  if count_known_posts(latest,fresh_now,b,channel,manifest,state)>=(8 if recover_today else min(target(brand_now,b),8)):return False
  if seen(item,channel,latest):state[key]='confirmed remotely';save();return False
  if channel=='facebook' and not gap_ok(latest+receipt_stamps(tag),fresh_now,60):return False
  state[key]='held: publication attempt started; reconcile remotely before retry';save()
  args=['--date',item['date'],'--out',str(R/'queue'/b)]
  reel=item.get('kind')=='reel'
  sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
  asset_base=f'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/{sha}/social-cloud-backup/'+item['folder']
  os.environ['GMS_PUBLIC_ASSET_BASE']=asset_base
  reel_dir=item.get('reel_dir','reel')
  reel_base=f'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/{sha}/social-cloud-backup/queue/{b}/{item["date"]}/{reel_dir}/'
  os.environ['REEL_PUBLIC_VIDEO_URL']=os.environ['GMS_PUBLIC_VIDEO_URL']=reel_base+'reel.mp4' if reel else ''
  os.environ['REEL_PUBLIC_COVER_URL']=reel_base+'cover.jpg' if reel and 'cover.jpg' in item.get('reel_sha256',{}) else ''
  if channel=='ig':
   script='reel_publish.py' if reel else 'ig_publish.py'
   args+=['--token-env',brands[b][0]]
   args+=['--reel-dir',reel_dir] if reel else ['--slot',str(item['slot']),'--base-url',asset_base]
  elif channel=='youtube':
   script='youtube_publish.py';args+=['--publish']
   args+=['--reel-dir',reel_dir] if reel else ['--carousel-slot',str(item['slot'])]
  elif channel=='facebook' and reel:
   script='fb_reel_publish.py';args+=['--reel-dir',reel_dir]
  elif channel=='facebook':
   script='fb_publish.py';args+=['--slot',str(item['slot']),'--format',facebook_format(item,state)]
  else:
   script='threads_publish.py';args+=['--slot',str(item['slot'])]
  rc,out=run(b,script,*args)
  if channel=='facebook':
   for marker in ('cards_withdrawn:','cards_unavailable:'):
    if marker in out:
     # Fail safe: stop trying the card format until an operator reviews the evidence.
     state['fb_cards_paused']=marker+' '+out.split(marker,1)[1].split('\n',1)[0].strip()[:300];save()
  success=any(x in out for x in ['published:','published (public):','already published:'])
  if rc or not success:
   if any(word in out.lower() for word in STOP_SIGNALS):
    state[block_key]='Platform restriction: operator verification required before clearing this lock.';save()
   # All errors retain a hold. A later remote read can reconcile a successful-but-uncertain request.
   raise RuntimeError('Publisher stopped or response was ambiguous. No automatic retry.')
  state[key]='success: '+out.strip()
  if channel=='facebook':state['last_publish_utc:'+tag]=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
  save()
  return True
  # A YouTube public request must actually produce a public video; publisher verifies status.
 except Exception as e:
  if any(word in str(e).lower() for word in STOP_SIGNALS):
   state[block_key]='Platform restriction: operator verification required before clearing this lock.';save()
  errors.append(tag+': '+str(e));print('ERROR '+errors[-1],flush=True);return False
if owner_test:
 # Owner explicitly requested exactly three new YouTube Shorts and one normal
 # Facebook carousel, once on 3 November evening. Same lock, identities,
 # hashes, remote dedupe, daily caps and Facebook gap as ordinary publication.
 for channel,ceiling in (('youtube',3),('facebook',1)):
  key='owner_av_test_20261103:'+channel
  while int(state.get(key,0)) < ceiling:
   if not process_channel('gms',channel):break
   state[key]=int(state.get(key,0))+1;save()
else:
 if 'gms' in (('gms',) if recover else selected_brands(cron,os.environ.get('BACKUP_BRAND','all'))):
  for post in json.loads((R/'facebook_withdraw.json').read_text()) if (R/'facebook_withdraw.json').exists() else []:
   key='withdrawn_fb:'+post['post_id']
   if not state.get(key):  # one attempt; Meta refuses deletion for New Pages Experience (6 Nov), so no hourly retries
    rc,out=run('gms','fb_publish.py','--withdraw',post['post_id'])
    state[key]=('withdrawn: ' if rc==0 else 'withdraw failed: ')+post['reason'];save()
 for b in (('gms',) if recover else selected_brands(cron,os.environ.get('BACKUP_BRAND','all'))):
  for channel in channel_plan(b,cron,recover):
   for attempt in range(attempt_limit(b,channel,recover,now)):
    if not process_channel(b,channel):break
if errors:raise SystemExit('\n'.join(errors))
if '--check' in sys.argv and os.environ.get('BACKUP_BRAND','all') in ('all','gms'):
 # Read-only evidence for the clickable product-card format; never publishes.
 rc,out=run('gms','fb_publish.py','--diagnose-cards')
 if rc:print('Facebook card diagnostics unavailable (exit %d); publishing is unaffected.'%rc)
if '--check' in sys.argv:
 import urllib.request
 sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
 paths=['queue/'+b+'/2026-11-03/carousel-1/slide-01.jpg' for b in brands]+['queue/gms/2026-11-03/reel/reel.mp4']
 paths+=[str(reel_folder(x).relative_to(R)/'reel.mp4') for x in manifest if x.get('reel_dir','reel')!='reel'][:3]
 for path in paths:
  url=f'https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/{sha}/social-cloud-backup/'+path
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=0-63'}),timeout=60) as response:header=response.read(64)
  assert header[4:8]==b'ftyp' if path.endswith('.mp4') else header[:3]==b'\xff\xd8\xff',path
 print('PASS: public cloud image and video URLs serve real JPEG/MP4 files.')
print('Cloud account checks completed.' if '--check' in sys.argv else 'Cloud approved queue processed with actual per-market counts and channel limits.')
