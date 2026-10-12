import json,sys
s=json.load(open('/home/claude/sitegen/tr/segments_v1.json'));b=json.load(open('/home/claude/sitegen/tr/batches.json'))
a,z=b[int(sys.argv[1])]
for i in range(a,z+1): print(f'[{i}] {s[i]}')
