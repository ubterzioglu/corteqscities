# Fotoğraf indirme + kanıt zinciri (Wikimedia Commons)
# Çıktı: ../eindhoven_qwen38_max/Fotoğraflar/*.webp
#         ../eindhoven_qwen38_max/Lisans kanıtları/*.json + orijinaller/*
#         photos_rows.json (Excel satırları)
import json, os, re, sys, time, hashlib, io
import requests
from PIL import Image

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "CorteqsCityResearch/1.0 (yerel sehir icerigi uretimi; lisans kanit zinciri) python-requests"}
S = requests.Session(); S.headers.update(UA)
ROOT = r"C:\temp_private\corteqs\0000_newera\eindhoven_qwen38_max"
FOT = os.path.join(ROOT, "Fotoğraflar")
KAN = os.path.join(ROOT, "Lisans kanıtları")
ORIG = os.path.join(KAN, "orijinaller")
for d in (FOT, KAN, ORIG):
    os.makedirs(d, exist_ok=True)

CHECKED_ON = "2026-10-20"

def api(params, tries=4):
    for i in range(tries):
        try:
            r = S.get(API, params=params, timeout=40)
            if r.status_code == 429:
                time.sleep(8); continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == tries - 1:
                return {"_error": str(e)}
            time.sleep(3 + i * 2)
    return {"_error": "retries"}

def strip_html(s):
    if not s: return ""
    s = re.sub(r'<[^>]+>', '', str(s))
    return re.sub(r'\s+', ' ', s).strip()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def usage_terms(lic):
    l = (lic or '').lower()
    if 'cc0' in l or 'public domain' in l or l.startswith('pd'):
        return "Kamu malı/CC0: atıf zorunlu değil; ticari kullanım ve türev serbest."
    if 'by-sa' in l:
        return "Atıf zorunlu (CC BY-SA): fotoğrafçı ve lisans belirtilmeli; ticari kullanım serbest; türev çalışmalar aynı lisansla paylaşılmalı."
    if 'by' in l:
        return "Atıf zorunlu (CC BY): fotoğrafçı ve lisans belirtilmeli; ticari kullanım ve türev serbest."
    return "Lisans metnini kaynak sayfadan doğrula."

def main():
    sel = json.load(open('photo_selection.json', encoding='utf-8'))
    # yer adları (caption için)
    places = {p['slug']: p for p in json.load(open('places_master.json', encoding='utf-8'))}
    districts = {d['slug']: d for d in json.load(open('districts_master.json', encoding='utf-8'))}

    # toplu imageinfo (tam kanıt kaydı)
    titles = [s['meta']['title'] for s in sel]
    info = {}
    for i in range(0, len(titles), 25):
        d = api({"action": "query", "titles": "|".join(titles[i:i+25]), "prop": "imageinfo",
                 "iiprop": "url|mime|size|sha1|extmetadata|timestamp", "iiurlwidth": "1600", "format": "json"})
        for pg in d.get('query', {}).get('pages', {}).values():
            ii = (pg.get('imageinfo') or [None])[0]
            if ii:
                info[pg['title']] = ii
        print(f"imageinfo {min(i+25,len(titles))}/{len(titles)}", flush=True)
        time.sleep(0.5)

    rows = []
    done = 0
    fail = []
    for s in sel:
        m = s['meta']
        t = m['title']
        key = s['file'].split('/')[-1]          # eindhoven_<x>_NN
        pid = s['photo_id']
        webp_rel = f"Fotoğraflar/{key}.webp"
        webp_abs = os.path.join(ROOT, "Fotoğraflar", key + ".webp")
        state = os.path.join(ROOT, "Lisans kanıtları", key + ".state.json")
        if os.path.exists(state):
            rows.append(json.load(open(state, encoding='utf-8')))
            done += 1
            continue
        ii = info.get(t)
        if not ii:
            fail.append((pid, t, 'no imageinfo')); continue
        em = ii.get('extmetadata', {})
        lic = strip_html(em.get('LicenseShortName', {}).get('value'))
        lic_url = strip_html(em.get('LicenseUrl', {}).get('value'))
        author = strip_html(em.get('Artist', {}).get('value'))
        desc = strip_html(em.get('ImageDescription', {}).get('value'))[:400]
        date_orig = strip_html(em.get('DateTimeOriginal', {}).get('value'))
        dl_url = ii.get('thumburl') or ii.get('url')
        # indirme (429'da geri çekilmeli tekrar)
        raw = None
        for attempt in range(6):
            try:
                r = S.get(dl_url, timeout=90)
                if r.status_code == 429:
                    wait = int(r.headers.get('Retry-After', '20')) + 10 + attempt * 20
                    print(f"429, waiting {wait}s for {pid}", flush=True)
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                raw = r.content
                break
            except Exception as e:
                if attempt == 5:
                    raise
                time.sleep(8 + attempt * 8)
        if raw is None:
            fail.append((pid, t, 'download: retries exhausted')); continue
        src_ext = os.path.splitext(ii.get('url', ''))[1].lower() or '.jpg'
        orig_rel = f"Lisans kanıtları/orijinaller/{key}{src_ext}"
        orig_abs = os.path.join(ROOT, orig_rel.replace('/', os.sep))
        with open(orig_abs, 'wb') as f:
            f.write(raw)
        orig_sha = sha256_bytes(raw)
        # webp dönüşümü
        try:
            im = Image.open(io.BytesIO(raw))
            im.load()
            if im.width > 1600 or im.height > 1600:
                im.thumbnail((1600, 1600), Image.LANCZOS)
            if im.mode not in ('RGB', 'RGBA'):
                im = im.convert('RGB')
            im.save(webp_abs, 'WEBP', quality=82, method=6)
        except Exception as e:
            fail.append((pid, t, f'convert: {e}')); continue
        web_sha = sha256_file(webp_abs)
        try:
            wim = Image.open(webp_abs); ww, wh = wim.size; wim.close()
        except Exception:
            ww, wh = None, None
        # caption
        eid = s['entry_id']
        if s['role'] == 'Kapak':
            caption = s.get('caption_hint', 'Eindhoven')
        elif eid and eid.startswith('eindhoven:mah-'):
            ds = eid.split('mah-')[-1]
            caption = districts.get(ds, {}).get('title', ds)
        else:
            ps = eid.split('eindhoven:')[-1] if eid else ''
            caption = places.get(ps, {}).get('title', ps)
        # kanıt json dosyaları
        src_ev_rel = f"Lisans kanıtları/{key}.source-evidence.json"
        lic_ev_rel = f"Lisans kanıtları/{key}.license-record.json"
        src_ev = {
            "photo_id": pid, "commons_file": t,
            "source_page": "https://commons.wikimedia.org/wiki/" + t.replace(' ', '_'),
            "original_file_url": ii.get('url'), "downloaded_file_url": dl_url,
            "api_imageinfo": ii, "checked_on": CHECKED_ON,
            "downloaded_sha256": orig_sha,
        }
        lic_ev = {
            "photo_id": pid, "commons_file": t,
            "license_short_name": lic, "license_url": lic_url,
            "usage_terms": usage_terms(lic),
            "author": author, "author_raw_html": em.get('Artist', {}).get('value'),
            "image_description": desc, "date_time_original": date_orig,
            "restrictions": em.get('Restrictions', {}).get('value'),
            "attribution": f"Fotoğraf: {author}, {lic}, Wikimedia Commons",
            "attribution_url": "https://commons.wikimedia.org/wiki/" + t.replace(' ', '_'),
            "checked_on": CHECKED_ON,
        }
        json.dump(src_ev, open(os.path.join(ROOT, src_ev_rel.replace('/', os.sep)), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(lic_ev, open(os.path.join(ROOT, lic_ev_rel.replace('/', os.sep)), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        row = {
            "photo_id": pid, "role": s['role'], "entry_id": eid, "media_key": s['media_key'],
            "file": webp_rel, "sha256": web_sha, "caption": caption, "author": author,
            "license": lic, "license_url": lic_url,
            "source_url": "https://commons.wikimedia.org/wiki/" + t.replace(' ', '_'),
            "capture_date": date_orig[:10] if date_orig else None,
            "source_checked_on": CHECKED_ON,
            "modifications": "Corteqs: Commons 1600px türev kopyası indirildi; WebP'ye dönüştürüldü (en çok 1600 px kenar).",
            "evidence_id": pid.replace(':foto:', ':kanit:'),
            "commons_title": t,
            "src_ev_rel": src_ev_rel, "src_ev_sha": sha256_file(os.path.join(ROOT, src_ev_rel.replace('/', os.sep))),
            "lic_ev_rel": lic_ev_rel, "lic_ev_sha": sha256_file(os.path.join(ROOT, lic_ev_rel.replace('/', os.sep))),
            "orig_rel": orig_rel, "orig_sha": orig_sha,
            "orig_url": ii.get('url'), "dl_url": dl_url,
            "web_w": ww, "web_h": wh,
            "usage_terms": usage_terms(lic),
            "attribution": f"Fotoğraf: {author}, {lic}, Wikimedia Commons",
            "restrictions": em.get('Restrictions', {}).get('value'),
            "api_sha1": ii.get('sha1'),
            "pixel_note": f"Otomatik eşleşme: Commons başlık/açıklama '{t[:60]}' mekân '{caption}' ile örtüşüyor. Kare indirildi, açıldı ve WebP türevi üretildi. İnsan piksel/mekân onayı bekliyor.",
        }
        rows.append(row)
        json.dump(row, open(state, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        done += 1
        if done % 10 == 0:
            print(f"downloaded {done}/{len(sel)}", flush=True)
        time.sleep(1.5)

    json.dump(rows, open('photos_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(fail, open('photos_fail.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("DONE", done, "fail", len(fail))
    for f in fail[:20]:
        print("  FAIL", f)

if __name__ == '__main__':
    main()
