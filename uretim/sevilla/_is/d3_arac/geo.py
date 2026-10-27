import json,urllib.request,urllib.parse,math
UA={"User-Agent":"corteqs-audit/1.0 (corteqssocial@gmail.com)"}
def dist(a,b,c,d): 
    R=6371000;p1,p2=math.radians(a),math.radians(c);dp=p2-p1;dl=math.radians(d-b)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2;return 2*R*math.asin(math.sqrt(h))
for q in ["Avenida Alcalde Luis Uruñuela 1, Sevilla","FIBES Sevilla"]:
    u="https://nominatim.openstreetmap.org/search?"+urllib.parse.urlencode({"q":q,"format":"json","limit":3})
    for r in json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30)):
        print(q,"|",r["display_name"][:90],r["lat"],r["lon"],round(dist(37.40444444,-5.9325,float(r["lat"]),float(r["lon"]))),"m")
u="https://www.wikidata.org/wiki/Special:EntityData/Q6057931.json"
e=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))["entities"]["Q6057931"]
print(e["labels"].get("es",{}).get("value"), e["claims"].get("P625",[{}])[0].get("mainsnak",{}).get("datavalue",{}).get("value"))
