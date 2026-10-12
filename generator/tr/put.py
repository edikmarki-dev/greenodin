"""python3 put.py NN < file  — читає блоки '@@idx\nru\nen' і пише parts/bNN.json"""
import sys,json
k=int(sys.argv[1]); b=json.load(open('/home/claude/sitegen/tr/batches.json')); a,z=b[k]
t=sys.stdin.read().split('@@')[1:]; d={}
for blk in t:
    L=blk.strip('\n').split('\n'); idx=int(L[0]);
    if len(L)!=3: print('BAD block',idx,len(L)); continue
    d[str(idx)]=[L[1].strip(),L[2].strip()]
miss=[i for i in range(a,z+1) if str(i) not in d]
print('batch',k,'got',len(d),'of',z-a+1,'missing',miss)
json.dump(d,open(f'/home/claude/sitegen/tr/parts/b{k:02d}.json','w'),ensure_ascii=False)
