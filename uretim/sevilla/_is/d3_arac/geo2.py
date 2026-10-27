import json,urllib.request,urllib.parse
UA={"User-Agent":"corteqs-audit/1.0 (corteqssocial@gmail.com)"}
for q in ["FIBES Sevilla","Palacio de Exposiciones y Congresos de Sevilla","Auditorio FIBES Sevilla"]:
    u="https://nominatim.openstreetmap.org/search?"+urllib.parse.urlencode({"q":q,"format":"json","limit":5,"extratags":1})
    for r in json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30)):
        print(q,"|",r["class"],r["type"],r["osm_type"],r["osm_id"],r["lat"],r["lon"],r.get("boundingbox"),(r.get("display_name") or "")[:60].encode("ascii","replace").decode())
u="https://nominatim.openstreetmap.org/reverse?"+urllib.parse.urlencode({"lat":37.40444444,"lon":-5.9325,"format":"json","zoom":18})
r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
print("REV",r.get("class"),r.get("type"),r.get("display_name","").encode("ascii","replace").decode())
