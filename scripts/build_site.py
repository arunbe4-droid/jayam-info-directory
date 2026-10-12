#!/usr/bin/env python3
"""Build a searchable public directory from strictly verified records only."""
import csv,json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));DATA=ROOT+"/data";SITE=ROOT+"/site"
def main():
    with open(DATA+"/resources.csv",newline="",encoding="utf-8-sig") as f:rows=list(csv.DictReader(f))
    # Only explicit verification statuses qualify for the public site. The master
    # uses descriptive statuses such as "Verified — official homepage"; accepting
    # those avoids incorrectly publishing zero records while preserving the review gate.
    def verified(x):
        status=(x.get("Verification Status","") or "").strip().casefold()
        explicit = status in {
            "verified", "verified official", "verified official destination",
            "verified official resource", "verified — official portal",
            "verified — official homepage", "verified — official homepage checked",
            "verified — official organisation/department source corroborates url",
            "verified — official corporate website", "verified — official service portal",
            "verified — official government references; homepage direct check limited",
            "verified — official government directory link",
            "official district index confirms listed url; live uptime not checked",
        }
        return explicit and (x.get("Official URL","") or "").startswith(("https://","http://"))
    public=[{"id":x.get("Resource ID",""),"category":x.get("Category / Scope",""),"name":x.get("Resource / Organisation",""),"url":x.get("Official URL",""),"checked":x.get("Last Checked",""),"verification_note":x.get("Verification Status","")} for x in rows if verified(x)]
    os.makedirs(SITE,exist_ok=True)
    with open(SITE+"/resources.json","w",encoding="utf-8") as f:json.dump(public,f,ensure_ascii=False,indent=2)
    page=r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Jayam Info — Official Resource Directory</title>
<style>:root{--m:#7b1e2b;--n:#24364b;--bg:#f5f7fa;--line:#d9e0e8}*{box-sizing:border-box}body{margin:0;background:var(--bg);font:16px system-ui;color:#202938}header{background:var(--m);color:white;padding:28px 18px}header div,main,footer{max-width:1100px;margin:auto}h1{margin:0;font-size:clamp(26px,4vw,38px)}header p{margin:8px 0 0}main{padding:20px 16px}.bar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}input,select{padding:12px;border:1px solid var(--line);border-radius:10px;font:inherit;background:white}input{flex:1;min-width:220px}select{min-width:190px}.meta{color:#667085;font-size:13px;margin:8px 0 16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.card,.empty{background:white;border:1px solid var(--line);border-radius:14px;padding:16px}.card{display:flex;flex-direction:column;gap:9px}.cat{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--m);font-weight:700}.card h2{font-size:17px;margin:0}.card a{color:var(--n);overflow-wrap:anywhere}.pill{background:#e8f4ea;color:#216e39;border-radius:99px;padding:4px 8px;font-size:11px;width:max-content}footer{padding:14px 16px 30px;color:#667085;font-size:12px;line-height:1.5}</style></head>
<body><header><div><h1>Jayam Info</h1><p>Official-source resource directory</p></div></header><main><div class="bar"><input id="q" type="search" placeholder="Search departments, resources or services"><select id="cat"><option value="">All categories</option></select></div><div class="meta" id="meta">Loading…</div><div id="grid" class="grid"></div></main>
<footer>Only records with an explicit verified-official status in the master are displayed. The status may indicate homepage verification or corroboration by an official government/organisation source. Reachability does not prove ownership or guarantee future uptime. Jayam Info is independent unless formally authorised by the relevant authority.</footer>
<script>fetch('./resources.json').then(r=>r.json()).then(rows=>{const q=document.querySelector('#q'),cat=document.querySelector('#cat'),grid=document.querySelector('#grid'),meta=document.querySelector('#meta');[...new Set(rows.map(x=>x.category).filter(Boolean))].sort().forEach(c=>{let o=document.createElement('option');o.value=c;o.textContent=c;cat.appendChild(o)});function draw(){let t=q.value.toLowerCase(),c=cat.value,shown=rows.filter(x=>(!c||x.category===c)&&(!t||(x.name+' '+x.category+' '+x.url).toLowerCase().includes(t)));meta.textContent=shown.length+' verified resources shown · '+rows.length+' total';grid.replaceChildren();if(!shown.length){let d=document.createElement('div');d.className='empty';d.textContent=rows.length?'No matching resources.':'No records currently meet the strict public verification rule; review the internal master.';grid.appendChild(d);return}shown.forEach(x=>{let a=document.createElement('article');a.className='card';let c=document.createElement('div');c.className='cat';c.textContent=x.category||'Other';let h=document.createElement('h2');h.textContent=x.name;let p=document.createElement('span');p.className='pill';p.textContent=x.verification_note||'Verification note unavailable';;let l=document.createElement('a');l.href=x.url;l.target='_blank';l.rel='noopener noreferrer';l.textContent='Open official website';a.append(c,h,p,l);grid.appendChild(a)})}q.addEventListener('input',draw);cat.addEventListener('change',draw);draw()}).catch(()=>document.querySelector('#meta').textContent='Directory data could not be loaded');</script></body></html>"""
    with open(SITE+"/index.html","w",encoding="utf-8") as f:f.write(page)
    print(f"Built public site with {len(public)} verified records from {len(rows)} master records.")
if __name__=="__main__":main()
