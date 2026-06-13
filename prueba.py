import json, hashlib
data = json.load(open('data/partidos.json'))
data['admin_hash'] = hashlib.sha1('mundial2026'.encode()).hexdigest()
json.dump(data, open('data/partidos.json', 'w'), ensure_ascii=False, indent=2)
print('hash reseteado')