#!/usr/bin/env python3
"""Fetch one reference report and emit untrusted factual text plus a stable fingerprint. No Site credentials."""
import hashlib,json,re,subprocess,sys
from html.parser import HTMLParser
from urllib.parse import urlparse
class ArticleParser(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[];self.links=[];self.href=None;self.anchor=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'):self.skip+=1
  if self.skip:return
  if tag=='a':self.href=dict(attrs).get('href','');self.anchor=[]
  if tag in ('p','li','h1','h2','h3','h4','h5','h6','tr','div'):self.parts.append('\n')
  if tag in ('td','th'):self.parts.append(' | ')
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip=max(0,self.skip-1)
  if self.skip:return
  if tag=='a' and self.href is not None:self.links.append([''.join(self.anchor).strip(),self.href]);self.href=None
  if tag in ('p','li','h1','h2','h3','h4','h5','h6','tr'):self.parts.append('\n')
 def handle_data(self,text):
  if not self.skip:
   self.parts.append(text)
   if self.href is not None:self.anchor.append(text)
def read_reference(url):
 u=urlparse(url)
 if u.scheme!='https' or u.netloc!='sarkariresult.com.cm' or not re.fullmatch(r'/[a-zA-Z0-9_-]+/?',u.path):raise ValueError('Only a reference article URL is allowed.')
 raw=subprocess.run(['curl','-fLsS','--max-time','35',url],check=True,capture_output=True,text=True).stdout
 p=ArticleParser();p.feed(raw);text=re.sub('[ \t]+',' ',re.sub(r'\n\s*\n+','\n',''.join(p.parts)))
 start=text.find('Post Date:');end=text.find('SOME USEFUL IMPORTANT LINKS')
 if start<0 or end<=start:raise ValueError('Article layout not recognized; review manually instead of guessing.')
 lines=[re.sub(r'\s+',' ',line).strip() for line in text[start:end].splitlines()]
 lines=[line for line in lines if line and not any(x in line for x in ('Download SarkariResult App','WhatsApp Telegram','SarkariResult.com.cm','You May Also Check'))]
 relevant='\n'.join(lines);official=[]
 for label,href in p.links:
  domain=urlparse(href).hostname or ''
  if href.startswith(('https://','http://')) and label and domain not in ('sarkariresult.com.cm','www.sarkariresult.com.cm') and not any(x in domain for x in ('whatsapp','instagram','facebook','youtube','t.me','play.google','twitter','x.com')):
   if href not in [link[1] for link in official]:official.append([label,href])
 fingerprint=hashlib.sha256((relevant+'\n'+json.dumps(sorted(x[1] for x in official),ensure_ascii=False)).encode()).hexdigest()
 return {'sourceUrl':url,'sourceFingerprint':fingerprint,'untrustedReferenceText':relevant,'officialLinksFromSource':official}
if __name__=='__main__':print(json.dumps(read_reference(sys.argv[1]),ensure_ascii=False,indent=2))
