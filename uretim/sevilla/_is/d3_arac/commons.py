import json,urllib.request,urllib.parse
UA={"User-Agent":"corteqs-audit/1.0 (corteqssocial@gmail.com)"}
def get(params):
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({**params,"format":"json","formatversion":"2"})
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
t="File:Palacio de Congresos y Exposiciones, Seville.jpg"
r=get({"action":"query","titles":t,"prop":"imageinfo|categories|revisions","iiprop":"url|user|timestamp|extmetadata|metadata|size|sha1","iiurlwidth":"800","rvprop":"user|timestamp","rvlimit":"5","rvdir":"newer","cllimit":"50"})
p=r["query"]["pages"][0]
ii=p["imageinfo"][0]
em=ii["extmetadata"]
for k in ["LicenseShortName","License","Artist","Credit","DateTimeOriginal","ImageDescription","UsageTerms","Restrictions"]:
    print(k,":",em.get(k,{}).get("value"))
print("user",ii["user"],ii["timestamp"],ii["width"],ii["height"],ii["sha1"])
print("thumb",ii.get("thumburl"))
md={m["name"]:m["value"] for m in ii.get("metadata") or []}
for k in ["Make","Model","DateTimeOriginal","GPSLatitude","GPSLongitude"]:
    print("exif",k,md.get(k))
print("cats",[c["title"] for c in p.get("categories",[])])
print("revs",p.get("revisions"))
u=ii["user"]
r2=get({"action":"query","list":"users","ususers":u,"usprop":"editcount|registration|groups"})
print(r2["query"]["users"])
r3=get({"action":"query","list":"allimages","aiuser":u,"aisort":"timestamp","ailimit":"500","aiprop":"timestamp"})
print("uploads (first page):",len(r3["query"]["allimages"]), "continue" in r3)
# ii history
r4=get({"action":"query","titles":t,"prop":"imageinfo","iiprop":"user|timestamp|comment","iilimit":"10"})
print(r4["query"]["pages"][0]["imageinfo"])
urllib.request.urlretrieve
data=urllib.request.urlopen(urllib.request.Request(ii["thumburl"],headers=UA),timeout=30).read()
open(r"C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\e1640e62-11af-476a-83cc-e29539d8a592\scratchpad\fibes_thumb.jpg","wb").write(data)
print("thumb bytes",len(data))
