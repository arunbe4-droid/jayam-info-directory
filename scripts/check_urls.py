#!/usr/bin/env python3
"""Checks website reachability; does not change verification status."""
import csv,os,concurrent.futures
from datetime import datetime,timezone
import requests
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));DATA=os.path.join(ROOT,"data")
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def read(p):
    with open(p,newline="",encoding="utf-8-sig") as f:r=csv.DictReader(f);return r.fieldnames or [],list(r)
def write(p,h,rows):
    with open(p,"w",newline="",encoding="utf-8-sig") as f:w=csv.DictWriter(f,fieldnames=h,extrasaction="ignore");w.writeheader();w.writerows(rows)
def check(x):
    u=(x.get("Official URL") or "").strip();r={"checked_at_utc":now(),"resource_id":x.get("Resource ID",""),"resource_name":x.get("Resource / Organisation",""),"requested_url":u,"final_url":"","http_status":"","result":"","note":""}
    if not u.startswith(("https://","http://")):r.update(result="SKIPPED_NO_URL",note="No URL");return r
    s=requests.Session();s.headers["User-Agent"]="JayamInfoURLChecker/2.0"
    try:
        try:q=s.head(u,timeout=15,allow_redirects=True)
        except requests.RequestException:q=None
        if q is None or q.status_code in (403,405,429,501) or q.status_code>=500:q=s.get(u,timeout=20,allow_redirects=True,stream=True)
        r["final_url"]=q.url;r["http_status"]=q.status_code
        if 200<=q.status_code<400:r.update(result="RESPONDS",note="Responded at check time; not proof of official ownership or future uptime.")
        elif q.status_code in (401,403,405,429):r.update(result="RESTRICTED_OR_RATE_LIMITED",note="Automated access may be restricted; inspect manually.")
        elif q.status_code>=500:r.update(result="SERVER_ERROR",note="Retry before changing status.")
        elif q.status_code>=400:r.update(result="HTTP_ERROR",note="Confirm manually and retry before marking retired.")
        else:r.update(result="REVIEW",note="Unexpected response.")
        q.close()
    except Exception as e:r.update(result="FETCH_ERROR",note=f"{type(e).__name__}: {e}; one failure is not proof the site is dead.")
    return r
def main():
    _,rs=read(DATA+"/resources.csv");targets=[r for r in rs if (r.get("Official URL") or "").startswith(("https://","http://"))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(check,targets))
    p=DATA+"/url_checks.csv";h=["checked_at_utc","resource_id","resource_name","requested_url","final_url","http_status","result","note"]
    _,old=read(p);write(p,h,old+results)
    counts={}
    for r in results:counts[r["result"]]=counts.get(r["result"],0)+1
    print(f"Checked {len(results)} URLs: {counts}. Verification labels unchanged.")
if __name__=="__main__":main()
