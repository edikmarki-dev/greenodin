"""stdin: @@i / ru / en (i — індекс у left.json на момент показу) → parts2/cNN.json"""
import sys,json,re
l=json.load(open('left.json')); name=sys.argv[1]
lines=sys.stdin.read().split('\n'); out={}; i=0
while i<len(lines):
    m=re.match(r'^@@(\d+)$',lines[i])
    if m: out[l[int(m.group(1))]]=[lines[i+1],lines[i+2]]; i+=3
    else: i+=1
json.dump(out,open(f'parts2/c{name}.json','w'),ensure_ascii=False,indent=0)
print('saved',len(out))
