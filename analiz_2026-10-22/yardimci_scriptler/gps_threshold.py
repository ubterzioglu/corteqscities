import json, sys, statistics as st
S = sys.argv[1]
d = json.load(open(S + "/photo_meta.json", encoding="utf-8"))
g = [(p["idx"], p["gps_km"]) for p in d if p.get("gps_km") is not None]
print("photos", len(d), "with gps_km", len(g))
vals = sorted(v for _, v in g)
def pct(q): return vals[min(len(vals)-1, int(q*len(vals)))]
print("median %.2f  p75 %.2f  p90 %.2f  max %.1f" % (st.median(vals), pct(.75), pct(.9), vals[-1]))
for t in (0.5, 1, 2, 3, 5, 12, 50):
    n = sum(v > t for v in vals); print(f"  > {t:>4} km: {n:3d} photos ({100*n/len(vals):.0f}% of GPS-tagged)")
# audit-confirmed bad photos (# = idx)
bad = {255:"Zweeloo yanlis sehir", 258:"Seattle sise", 22:"otoyol", 140:"yanlis su kulesi", 156:"kilise org", 158:"kilise org",
       232:"istasyon plaket", 233:"istasyon plaket", 240:"pazar heykel", 241:"pazar cephe", 2:"kapak ic mekan", 136:"yagliboya",
       26:"tablo", 28:"tablo", 148:"HTC levha", 149:"HTC levha", 247:"De Bergen", 248:"De Bergen", 249:"De Bergen"}
m = {p["idx"]: p for p in d}
print("\naudit-confirmed bad photos -> gps_km")
caught1 = caught12 = tagged = 0
for k, why in bad.items():
    v = m[k].get("gps_km"); print(f"  #{k:<4} {why:22} gps_km={v}")
    if v is not None:
        tagged += 1; caught1 += v > 1; caught12 += v > 12
print(f"of {len(bad)} bad photos: {tagged} have GPS; >1km catches {caught1}, >12km catches {caught12}")
good_flagged = [k for k, v in g if v > 1 and k not in bad]
print(f"photos NOT in audit bad list but >1 km: {len(good_flagged)} of {len(g)} GPS-tagged -> false-positive load for 1 km rule")
