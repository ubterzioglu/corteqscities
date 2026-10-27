import json
rows=[
{"url":"https://denuncias.policia.es/OVD/","must_contain":["72 horas","091 o 112"],"title":"Oficina Virtual de Denuncias","publisher":"Dirección General de la Policía (Policía Nacional)","lang":"es","why":"Çevrimiçi suç duyurusunun koşulları, 72 saat içinde karakolda imza ve 091/112 uyarısı."},
{"url":"https://denuncias.policia.es/OVD/Oficinas.dgp?id_prov=29","must_contain":["MALAGA-CENTRO-OFICINA DE DENUNCIAS","AVDA. DE LA PALMILLA, 20"],"title":"Oficina Virtual de Denuncias: oficinas de denuncia, provincia de Málaga","publisher":"Dirección General de la Policía (Policía Nacional)","lang":"es","why":"Málaga ilindeki Policía Nacional suç duyurusu ofislerinin adresleri."},
{"url":"https://policialocal.malaga.eu/","must_contain":["Avd. de la Rosaleda, 19","092"],"title":"Policía Local del Ayuntamiento de Málaga","publisher":"Ayuntamiento de Málaga - Policía Local","lang":"es","why":"Yerel polis iletişim adresi ve 092 numarası."}
]
with open(r'C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\912613eb-ab28-44b8-b5f0-a261661e6f6a\scratchpad\gunluk_w\yeni_kaynak_1.jsonl','w',encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
