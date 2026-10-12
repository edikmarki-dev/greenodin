"""Автопереклад нових фрагментів із готових речень (якщо кожне речення вже перекладене) → parts2/auto.json"""
import json,re
ru=json.load(open('ru.json'));en=json.load(open('en.json'))
SP=re.compile(r'(?<=[.!?])\s+')
sent={'ru':{},'en':{}}
for k in ru:
    a=SP.split(k.strip()); r=SP.split(ru[k].strip()); e=SP.split(en[k].strip())
    if len(a)==len(r)==len(e):
        for x,y,z in zip(a,r,e): sent['ru'].setdefault(x,y); sent['en'].setdefault(x,z)
import os
done={}
for f in os.listdir('parts2'):
    if f.startswith('c'): done.update(json.load(open('parts2/'+f)))
miss=[m for m in json.load(open('missing_ru.json')) if m not in done]
auto={}
for m in miss:
    ss=SP.split(m.strip())
    if all(s in sent['ru'] for s in ss): auto[m]=[' '.join(sent['ru'][s] for s in ss),' '.join(sent['en'][s] for s in ss)]
json.dump(auto,open('parts2/auto.json','w'),ensure_ascii=False,indent=0)
left=[m for m in miss if m not in auto]
json.dump(left,open('left.json','w'),ensure_ascii=False,indent=0)
print('auto',len(auto),'left',len(left),sum(map(len,left)))
