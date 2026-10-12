import json,glob,re
segs=json.load(open('segments_v1.json',encoding='utf-8'))
ru={};en={}
for f in sorted(glob.glob('parts/b*.json')):
    for k,(r,e) in json.load(open(f,encoding='utf-8')).items():
        s=segs[int(k)]
        m=re.match(r'^(\s*).*?(\s*)$',s,re.S); lead,trail=m.group(1),m.group(2)
        ru[s]=lead+r.strip()+trail; en[s]=lead+e.strip()+trail
json.dump(ru,open('ru.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(en,open('en.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(segs),len(ru),len(en))
