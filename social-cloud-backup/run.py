#!/usr/bin/env python3
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FOLDERS={'gms':'publishers/gms','sp':'publishers/sp','sin':'publishers/sin'}
def main():
 brand,script,*args=sys.argv[1:]
 if brand not in FOLDERS or '/' in script or not script.endswith('.py'):raise SystemExit('Unsupported command')
 cfg=json.loads((ROOT/'private/environment.json').read_text())
 env=os.environ.copy();env.update(cfg)
 env['PYTHONUNBUFFERED']='1'
 try:
  import certifi
  env['SSL_CERT_FILE']=certifi.where()
 except ImportError:pass
 folder=ROOT/FOLDERS[brand]
 p=subprocess.run([sys.executable,str(folder/script),*args],cwd=folder,env=env,capture_output=True,text=True)
 out=p.stdout+p.stderr
 for val in sorted(cfg.values(),key=len,reverse=True):
  if len(val)>15:out=out.replace(val,'[REDACTED]')
 print(out,end='');return p.returncode
if __name__=='__main__':sys.exit(main())
