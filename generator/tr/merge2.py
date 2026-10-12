import json,glob,re
for lang,i in (('ru',0),('en',1)):
    d=json.load(open(f'{lang}.json',encoding='utf-8'))
    for f in sorted(glob.glob('parts2/*.json')):
        for k,v in json.load(open(f,encoding='utf-8')).items():
            m=re.match(r'^(\s*).*?(\s*)$',k,re.S)
            d[k]=m.group(1)+v[i].strip()+m.group(2)
    json.dump(d,open(f'{lang}.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(lang,len(d))
