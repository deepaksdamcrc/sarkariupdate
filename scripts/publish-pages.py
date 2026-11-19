#!/usr/bin/env python3
"""Mirror published content into this repository using the caller's existing GitHub connection.
Reads source_url and service_token from stdin only; never stores those credentials.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read_connection():
 if not sys.stdin.isatty():return json.load(sys.stdin)
 import termios
 fd=sys.stdin.fileno();old=termios.tcgetattr(fd);hidden=termios.tcgetattr(fd);hidden[3]&=~termios.ECHO;termios.tcsetattr(fd,termios.TCSANOW,hidden)
 print('Ready for source connection JSON on stdin (input hidden).',flush=True)
 try:return json.loads(sys.stdin.readline())
 finally:termios.tcsetattr(fd,termios.TCSANOW,old)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--push',action='store_true',help='Commit generated public files and push a fast-forward to main.');args=parser.parse_args();cfg=read_connection()
 spec=importlib.util.spec_from_file_location('pages_sync',ROOT/'scripts/sync-pages.py');sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)
 rows=sync.fetch_articles(cfg['source_url'],cfg['service_token'])
 request=sync.Request(cfg['source_url'].rstrip('/')+'/api/automation/state',headers={'OAI-Sites-Authorization':'Bearer '+cfg['service_token'],'X-Sarkari-Automation':cfg['service_token'],'Accept':'application/json'})
 with sync.build_opener(sync.NoRedirect()).open(request,timeout=45)as response:state=json.load(response)
 if not state.get('enabled',False):print('Publishing is paused by the owner; GitHub mirror unchanged.');return
 articles=sync.build_site(rows,ROOT/'_site');staging=ROOT/'_site'
 files=[Path('index.html'),Path('data/articles.json'),*map(lambda p:p.relative_to(staging),(staging/'covers').glob('*.svg'))]
 changed=any(not(ROOT/p).exists()or(ROOT/p).read_bytes()!=(staging/p).read_bytes()for p in files)
 snapshot=(staging/'data/articles.json').read_bytes();changed=changed or not(ROOT/'export/published-articles.json').exists()or(ROOT/'export/published-articles.json').read_bytes()!=snapshot
 if not changed:print('Already current: '+str(len(articles))+' published articles. No commit or deployment needed.');return
 for p in [*files,Path('data/sync.json'),Path('.nojekyll')]:
  dest=ROOT/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(staging/p,dest)
 (ROOT/'export').mkdir(exist_ok=True);(ROOT/'export/published-articles.json').write_bytes(snapshot)
 print('Updated repository files: '+str(len(articles))+' published articles and local illustrated covers.',flush=True)
 if args.push:
  subprocess.run(['git','add','--','index.html','data','covers','export/published-articles.json','.nojekyll'],cwd=ROOT,check=True)
  subprocess.run(['git','-c','user.name=Sarkari Update','-c','user.email=sarkari-update@users.noreply.github.com','commit','-m','Update published exam articles'],cwd=ROOT,check=True)
  subprocess.run(['git','push','origin','HEAD:main'],cwd=ROOT,check=True)
  print('Pushed public content to main; the existing GitHub Pages branch build will deploy it.',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('Publishing failed ('+type(error).__name__+'). No source credential was saved. Inspect repository access or source availability; never force-push.',file=sys.stderr);sys.exit(1)
