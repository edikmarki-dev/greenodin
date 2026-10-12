import json,sys,glob
s=json.load(open('/home/claude/sitegen/tr/segments_v1.json'));b=json.load(open('/home/claude/sitegen/tr/batches.json'))
for f in sorted(glob.glob('/home/claude/sitegen/tr/parts/b*.json')):
    k=int(f[-7:-5]);a,z=b[k]
    try: d=json.load(open(f))
    except Exception as e: print(f,'BAD JSON',e);continue
    miss=[i for i in range(a,z+1) if str(i) not in d]; extra=[i for i in d if not a<=int(i)<=z]
    bad=[i for i,v in d.items() if not(isinstance(v,list) and len(v)==2 and all(v))]
    if miss or extra or bad: print(f,'miss',miss,'extra',extra,'bad',bad)
print('ok')
