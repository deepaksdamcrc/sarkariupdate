#!/usr/bin/env python3
"""Publish a safe static copy of the verified article feed; never export admin state."""
import argparse,datetime,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,build_opener,HTTPRedirectHandler
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={'Result','Admit Card','Latest Jobs','Answer Key','Admission','Syllabus'}
FIELDS={'id','title','content','category','status','updatedAt','organization','notification','subtitle','ageLimit','eligibility','selection','howTo','officialUrl','deadline','coverLabel','coverDetail','dates','fees','vacancies','links','faqs'}
REF=re.compile(r'https?://(?:www\.)?sarkariresult\.com\.cm[^\s<>\"\x27)\]]*|(?:www\.)?sarkariresult\.com\.cm',re.I)
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None

def clean(value):
 if isinstance(value,str):return REF.sub('',value)
 if isinstance(value,list):return [clean(x)for x in value]
 return value

def reference_url(url):
 host=(urlparse(str(url)).hostname or '').lower()
 return host=='sarkariresult.com.cm' or host.endswith('.sarkariresult.com.cm')

def sanitize_articles(rows):
 if not isinstance(rows,list) or len(rows)>5000:raise ValueError('Invalid article feed.')
 safe=[];seen=set()
 for record in rows:
  if not isinstance(record,dict):raise ValueError('Invalid article record.')
  if record.get('status')!='published':continue
  ident=record.get('id','')
  if not re.fullmatch(r'[a-f0-9-]{36}',ident) or ident in seen:raise ValueError('Invalid or duplicate article ID.')
  if record.get('category')not in CATEGORIES or not isinstance(record.get('title'),str) or not record['title'].strip() or not isinstance(record.get('content'),str):raise ValueError('Invalid article content.')
  seen.add(ident);article={k:clean(v)for k,v in record.items()if k in FIELDS}
  article['links']=[clean(row)for row in record.get('links',[])if isinstance(row,list)and len(row)==2 and isinstance(row[1],str)and row[1].startswith(('https://','http://'))and not reference_url(row[1])]
  if reference_url(record.get('officialUrl','')):article['officialUrl']=''
  article['imageUrl']='covers/'+ident+'.svg';safe.append(article)
 safe.sort(key=lambda a:a.get('updatedAt',''),reverse=True)
 if not safe:raise ValueError('The published feed is empty; keep the last successful deployment.')
 return safe

def fetch_articles(origin,token):
 u=urlparse(origin)
 if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):raise ValueError('SARKARI_SOURCE_URL must be an HTTPS origin without a path.')
 if not token:raise ValueError('Set the SARKARI_SOURCE_TOKEN repository secret before running the workflow.')
 request=Request(origin.rstrip('/')+'/api/articles',headers={'OAI-Sites-Authorization':'Bearer '+token,'Accept':'application/json','User-Agent':'SarkariUpdate-GitHubPagesSync/1.0'})
 with build_opener(NoRedirect()).open(request,timeout=45)as response:
  raw=response.read(20*1024*1024+1)
  if len(raw)>20*1024*1024:raise ValueError('Article feed too large.')
 return json.loads(raw)

def render_index(template):
 lines=template.splitlines();found=0
 for i,line in enumerate(lines):
  if line.startswith('async function load(){'):
   lines[i]="async function load(){const r=await fetch(new URL('data/articles.json',document.baseURI),{cache:'no-store'});if(!r.ok)throw Error('Updates load nahi ho sake. Refresh karke try karein.');articles=await r.json();render();routeArticle()}";found+=1
  if line.startswith('function sourceMarkup('):lines[i]="function sourceMarkup(a){return ''}"
 if found!=1:raise ValueError('Unexpected page structure; refusing to replace article loader.')
 result='\n'.join(lines)
 # Site-relative assets must stay below /sarkariupdate/, including on project Pages.
 result=result.replace("a.id?'/covers/'+a.id+'.svg'","a.id?'covers/'+a.id+'.svg'")
 return result.replace('href="/"','href="./"')

def build_site(rows,output):
 articles=sanitize_articles(rows)
 output=Path(output).resolve()
 if output==ROOT or ROOT in output.parents and output.name not in ('_site','_test_site'):raise ValueError('Choose a separate output directory named _site or _test_site.')
 # Build into a temporary directory, then replace only our generated artifact.
 with tempfile.TemporaryDirectory(prefix='sarkari-pages-')as tmp:
  staging=Path(tmp);(staging/'data').mkdir();(staging/'covers').mkdir()
  (staging/'data/articles.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  (staging/'index.html').write_text(render_index((ROOT/'index.html').read_text(encoding='utf-8')),encoding='utf-8')
  (staging/'.nojekyll').write_text('',encoding='utf-8')
  (staging/'data/sync.json').write_text(json.dumps({'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'publishedArticles':len(articles)},indent=2)+'\n',encoding='utf-8')
  subprocess.run(['node',str(ROOT/'scripts/render-page-covers.mjs'),str(staging/'data/articles.json'),str(staging/'covers')],check=True)
  if output.exists():shutil.rmtree(output)
  shutil.copytree(staging,output)
 return articles

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--input',help='Local published feed for tests/bootstrap; no credentials needed.');parser.add_argument('--output',default='_site');args=parser.parse_args()
 rows=json.loads(Path(args.input).read_text(encoding='utf-8'))if args.input else fetch_articles(os.environ.get('SARKARI_SOURCE_URL','https://sarkari-update-hub.foggyfoal.chatgpt.site'),os.environ.get('SARKARI_SOURCE_TOKEN',''))
 articles=build_site(rows,args.output);print('Prepared GitHub Pages: '+str(len(articles))+' published articles with local covers. No admin credentials, drafts or source backlinks exported.')
if __name__=='__main__':
 try:main()
 except Exception as error:
  # Never echo request headers, tokens or an entire remote response.
  print('Content sync failed ('+type(error).__name__+'). Check the source connection and Actions secrets; previous deployment remains unchanged.',file=sys.stderr);sys.exit(1)
