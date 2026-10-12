import json,sys
l=json.load(open('left.json')); a,b=int(sys.argv[1]),int(sys.argv[2])
for i in range(a,min(b,len(l))): print(f'[{i}] {l[i]}')
