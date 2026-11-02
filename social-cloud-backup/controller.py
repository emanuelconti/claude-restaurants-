"""Publish only hash-approved queue items. No content is generated on the runner."""
import datetime as dt, hashlib, json, os, re, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parent
now=dt.datetime.now(ZoneInfo('Europe/Paris'))
if now>=dt.datetime(2026,11,6,2,tzinfo=ZoneInfo('Europe/Paris')):
 print('Temporary backup expired: nothing published.');sys.exit()
if '--validate' in sys.argv:
 manifest=json.loads((R/'queue.json').read_text())
 for item in manifest:
  folder=R/item['folder']
  assert folder.resolve().is_relative_to((R/'queue').resolve())
  for name,digest in item['sha256'].items():
   assert Path(name).name==name
   assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
 print(f'PASS: {len(manifest)} reviewed queue items; all asset hashes match. No credentials loaded or publications attempted.')
 sys.exit()
cfg=json.loads(os.environ['SOCIAL_BACKUP_ENV'])
for v in cfg.values():
 if len(str(v))>15 and os.environ.get('GITHUB_ACTIONS'):print('::add-mask::'+str(v))
cfg.update(GMS_PINTEREST_ENABLED='0',GMS_TIKTOK_ENABLED='0',GMS_YOUTUBE_PRIVACY='public')
(R/'private').mkdir(exist_ok=True);(R/'private/environment.json').write_text(json.dumps(cfg));os.chmod(R/'private/environment.json',0o600)
def run(b,script,*args):
 p=subprocess.run([sys.executable,str(R/'run.py'),b,script,*args],capture_output=True,text=True)
 print(p.stdout+p.stderr,flush=True)
 return p.returncode,p.stdout+p.stderr
brands={'sp':('INSTAGRAM_ACCESS_TOKEN','socialperks.es'),'sin':('INSTAGRAM_TOKEN_SINCRONIA','sincronia.live'),'gms':('INSTAGRAM_TOKEN_SOWLD','goodmessage_studio')}
manifest=json.loads((R/'queue.json').read_text())
statepath=R/'state.json';state=json.loads(statepath.read_text()) if statepath.exists() else {}
errors=[]
for b,(token,handle) in brands.items():
 code,out=run(b,'ig_publish.py','--token-env',token,'--check-token')
 if code or '@'+handle not in out:errors.append(b+': account check failed');continue
 if '--check' in sys.argv:continue
 code,recent=run(b,'ig_publish.py','--token-env',token,'--recent','30')
 if code:errors.append(b+': history unavailable');continue
 count=sum(1 for line in recent.splitlines() if re.match(r'\d{4}-\d\d-\d\dT',line) and dt.datetime.fromisoformat(line.split()[0]).astimezone(ZoneInfo('Europe/Paris')).date()==now.date())
 hours=[7,8,9,13,14,15,19,20];target=sum(now.hour>=h for h in hours)
 for item in manifest:
  if item['brand']!=b or item['date']>now.date().isoformat():continue
  folder=R/item['folder'];meta=json.loads((folder/'carousel.json').read_text())
  if any(hashlib.sha256((folder/n).read_bytes()).hexdigest()!=h for n,h in item['sha256'].items()):
   errors.append(b+': approved assets changed');break
  key=item['id']+':ig'
  if not state.get(key) and count<min(target,8):
   if meta['title'] in recent:state[key]='confirmed remotely'
   else:
    state[key]='held: publication attempt in progress';statepath.write_text(json.dumps(state,indent=2))
    code,out=run(b,'ig_publish.py','--token-env',token,'--date',item['date'],'--slot',str(item['slot']),'--out',str(R/'queue'/b),'--upload')
    if code or not ('published:' in out or 'already published:' in out):
     errors.append(b+': publish failed or ambiguous, held for reconciliation');break
    state[key]=out.strip();count+=1
   statepath.write_text(json.dumps(state,indent=2))
  if b=='gms':
   # The independent scripts read their own channel histories and keep their limits.
   for channel,script,extra in [('threads','threads_publish.py',[]),('youtube','youtube_publish.py',['--carousel-slot',str(item['slot']),'--publish']),('facebook','fb_publish.py',[])]:
    ck=item['id']+':'+channel
    if state.get(ck):continue
    if channel=='youtube':
     code,out=run(b,'backup_youtube_check.py')
     if code:errors.append('youtube identity check failed');continue
     if meta['title'][:62] in out:state[ck]='confirmed remotely';continue
    state[ck]='held: publication attempt in progress';statepath.write_text(json.dumps(state,indent=2))
    args=['--date',item['date'],'--out',str(R/'queue'/b)]
    if channel!='youtube':args+=['--slot',str(item['slot'])]
    code,out=run(b,script,*args,*extra)
    if 'too soon' in out.lower() or 'daily cap' in out.lower():state.pop(ck,None)
    elif code or not ('published:' in out or 'published (public):' in out or 'already published:' in out or 'uploaded:' in out):errors.append(channel+': check execution result; no blind retry')
    else:state[ck]=out.strip()
    statepath.write_text(json.dumps(state,indent=2))
  break # At most one queue item per brand per invocation.
if '--check' not in sys.argv:statepath.write_text(json.dumps(state,indent=2))
if errors:raise SystemExit('\n'.join(errors))
print('Cloud checks completed.' if '--check' in sys.argv else 'Approved queue checked; no unreviewed content published.')
