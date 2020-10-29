import json

data = {}
data['people'] = []

data['people'].append({
    'name': 'Admin',
    'pwd' : 'toor'
})
data['people'].append({
    'name': 'User01',
    'pwd': 'User01-Pa$$w0rd123'
})

data['people'].append({
    'name': 'User01',
    'pwd': 'User02-Pa$$w0rd123'
})

with open('/root/Desktop/Test.json','w') as outfile:
    json.dump(data,outfile)

outfile.close()

with open('/root/Desktop/Test.json','r') as infile:
    json.load(infile)
    output_f = format(' Name: {username:}\n Password: {pwd:}\n')
    for p in data['people']:
        print(output_f.format(username = p['name'], pwd = p['pwd']))