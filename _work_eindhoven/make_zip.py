# Paket ZIP
import zipfile, os, datetime

ROOT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max"
OUT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max_v001.zip"
n = 0
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for dp, _, fs in os.walk(ROOT):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, os.path.dirname(ROOT))
            z.write(p, rel)
            n += 1
print('zipped', n, 'files ->', OUT, os.path.getsize(OUT) // (1 << 20), 'MB')
