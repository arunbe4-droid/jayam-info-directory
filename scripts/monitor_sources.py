#!/usr/bin/env python3
"""Monitor official discovery pages. Never auto-approves a candidate."""
import csv,hashlib,json,os,re,time
from datetime import datetime,timezone
from urllib.parse import urljoin,urlparse,urldefrag
import requests
import certifi
from bs4 import BeautifulSoup
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DATA=os.path.join(ROOT,"data")
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def rj(p,d):
    if not os.path.exists(p): return d
    with open(p,encoding="utf-8") as f:return json.load(f)
def wj(p,d):
    with open(p,"w",encoding="utf-8") as f:json.dump(d,f,ensure_ascii=False,indent=2)
def rc(p):
    if not os.path.exists(p):return [],[]
    with open(p,newline="",encoding="utf-8-sig") as f:
        x=csv.DictReader(f);return x.fieldnames or [],list(x)
def wc(p,h,rows):
    with open(p,"w",newline="",encoding="utf-8-sig") as f:
        x=csv.DictWriter(f,fieldnames=h,extrasaction="ignore");x.writeheader();x.writerows(rows)
def canon(u):
    u=urldefrag((u or "").strip())[0];p=urlparse(u)
    return u.rstrip("/") if p.scheme in ("http","https") and p.netloc else ""
def main():
    sources=rj(DATA+"/sources.json",[]);state=rj(DATA+"/source_state.json",{})
    _,events0=rc(DATA+"/change_log.csv");_,oldc=rc(DATA+"/candidates.csv");_,resources=rc(DATA+"/resources.csv")
    known={canon(r.get("Official URL","")) for r in resources if canon(r.get("Official URL",""))}
    candidates={canon(c.get("candidate_url","")):c for c in oldc if canon(c.get("candidate_url",""))}
    s=requests.Session()
    s.verify=certifi.where()
    s.headers["User-Agent"]="JayamInfoOfficialResourceMonitor/2.0"
    t=now();events=[];added=0
    for src in sources:
        try:
            r=s.get(src["url"],timeout=25,allow_redirects=True);body=r.text[:5000000]
            soup=BeautifulSoup(body,"html.parser");title=soup.title.get_text(" ",strip=True) if soup.title else ""
            txt=re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
            links={}
            for a in soup.find_all("a",href=True):
                u=canon(urljoin(r.url,a.get("href","")))
                if u: links.setdefault(u,re.sub(r"\s+"," ",a.get_text(" ",strip=True))[:200])
            th=hashlib.sha256(txt.encode("utf-8",errors="ignore")).hexdigest()
            lh=hashlib.sha256("|".join(sorted(links)).encode()).hexdigest()
            old=state.get(src["source_id"],{})
            if r.status_code>=400:
                ev="SOURCE_HTTP_WARNING";details=f"HTTP {r.status_code}; retry before treating as unavailable."
            elif not old:
                ev="SOURCE_BASELINE";details=f"Initial baseline; title={title}; links={len(links)}."
            elif old.get("text_hash")!=th or old.get("link_hash")!=lh:
                ev="SOURCE_CHANGED";details=f"Page content or links changed; prior links={old.get('link_count')}, current={len(links)}. Review source manually."
            else: ev=""
            if ev: events.append({"event_time_utc":t,"event_type":ev,"resource_id":src["source_id"],"resource_name":src["name"],"url":src["url"],"http_status":r.status_code,"evidence_url":r.url,"details":details})
            state[src["source_id"]]={"checked_at_utc":t,"requested_url":src["url"],"final_url":r.url,"http_status":r.status_code,"title":title,"text_hash":th,"link_hash":lh,"link_count":len(links)}
            for u,label in links.items():
                # IGOD listing parser only proposes same-domain detail links; never treats generic navigation as a resource.
                path=urlparse(u).path.lower();host=urlparse(u).hostname or ""
                if src["type"]=="organization_list":
                    eligible=host.endswith("igod.gov.in") and u!=canon(src["url"]) and any(x in path for x in ("/org/","/organization/","/organizations/","/website/","/websites/"))
                else:
generic={"home","about us","contact us","login","sign in","privacy policy","terms","search","sitemap","profile","organization structure","district centres","state project profile","skip to main content","accessibility","help","feedback","screen reader access","copyright","disclaimer","website policies","hyperlinking policy","archive","faq","faqs","careers","tenders","news","events","gallery","photo gallery","site map"}
                    eligible=u!=canon(src["url"]) and bool(label.strip()) and label.strip().lower() not in generic
                if not eligible or u in known or u in candidates:continue
                candidates[u]={"candidate_id":"CAND-"+hashlib.sha256(u.encode()).hexdigest()[:12].upper(),"first_seen_utc":t,"last_seen_utc":t,"source_id":src["source_id"],"source_name":src["name"],"source_page_url":src["url"],"candidate_label":label or "(unlabelled)","candidate_url":u,"candidate_host":urlparse(u).hostname or "","official_status":"PENDING_REVIEW","review_note":"Discovered from configured source. Confirm identity, official ownership and duplicates before adding."}
                added+=1;events.append({"event_time_utc":t,"event_type":"NEW_LINK_CANDIDATE","resource_id":candidates[u]["candidate_id"],"resource_name":label,"url":u,"http_status":"","evidence_url":src["url"],"details":"Candidate only; not verified or added to canonical registry."})
        except Exception as e:
            events.append({"event_time_utc":t,"event_type":"SOURCE_FETCH_WARNING","resource_id":src["source_id"],"resource_name":src["name"],"url":src["url"],"http_status":"","evidence_url":src["url"],"details":f"{type(e).__name__}: {e}. A timeout is not proof a site is dead."})
        time.sleep(.4)
    wj(DATA+"/source_state.json",state)
    wc(DATA+"/candidates.csv",["candidate_id","first_seen_utc","last_seen_utc","source_id","source_name","source_page_url","candidate_label","candidate_url","candidate_host","official_status","review_note"],list(candidates.values()))
    wc(DATA+"/change_log.csv",["event_time_utc","event_type","resource_id","resource_name","url","http_status","evidence_url","details"],events0+events)
    print(f"Checked {len(sources)} source pages; new candidates={added}; logged events={len(events)}. Nothing auto-approved.")
if __name__=="__main__":main()
