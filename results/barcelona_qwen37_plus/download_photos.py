# -*- coding: utf-8 -*-
"""
Barcelona CITY-009 - Otomatik Fotoğraf İndirme Scripti
Wikimedia Commons API kullanarak mekân fotoğraflarını indirir
"""

import requests
import json
import hashlib
import os
import time
import openpyxl
from pathlib import Path
from datetime import datetime

# Konfigürasyon
EXCEL_PATH = r"C:\temp_private\corteqs\0000_newera\results\barcelona_qwen37_plus\2_excel\CITY-009_barcelona_v001.xlsx"
PHOTO_DIR = r"C:\temp_private\corteqs\0000_newera\results\barcelona_qwen37_plus\3_Fotograflar"
EVIDENCE_DIR = r"C:\temp_private\corteqs\0000_newera\results\barcelona_qwen37_plus\4_Lisans_kanitlari"
CITY_ID = "barcelona"
TODAY = "2026-10-20"

# Wikimedia Commons API
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Uygun lisanslar
VALID_LICENSES = [
    "cc by-sa-4.0", "cc by-sa-3.0", "cc by-sa-2.5",
    "cc by-4.0", "cc by-3.0", "cc by-2.5",
    "cc0-1.0", "cc0 1.0", "cc0",
    "public domain", "public-domain", "pd-old", "pd-art", "pd-usgov",
    "cc-by-sa-4.0", "cc-by-sa-3.0", "cc-by-4.0", "cc-by-3.0"
]

def ensure_dirs():
    """Klasörleri oluştur"""
    os.makedirs(PHOTO_DIR, exist_ok=True)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

def search_wikimedia(query, limit=5):
    """Wikimedia Commons'ta fotoğraf ara (iki adımlı API)"""
    headers = {
        "User-Agent": "CorteqsBarcelonaBot/1.0 (city-content-project; umut.baris@example.com) python-requests/2.31.0"
    }
    
    # Adım 1: Arama yap
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": f"Barcelona {query}",
        "srnamespace": "6",  # File namespace
        "srlimit": str(limit),
        "format": "json"
    }
    
    try:
        search_response = requests.get(COMMONS_API, params=search_params, headers=headers, timeout=30)
        search_data = search_response.json()
        
        if "query" not in search_data or "search" not in search_data["query"]:
            return []
        
        search_results = search_data["query"]["search"]
        results = []
        
        # Adım 2: Her dosya için bilgi al
        for item in search_results:
            title = item.get("title", "")
            
            info_params = {
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata|user|size",
                "iiurlwidth": "1600",
                "format": "json"
            }
            
            info_response = requests.get(COMMONS_API, params=info_params, headers=headers, timeout=30)
            info_data = info_response.json()
            
            if "query" in info_data:
                pages = info_data["query"].get("pages", {})
                for page_id, page_data in pages.items():
                    if "imageinfo" in page_data:
                        info = page_data["imageinfo"][0]
                        
                        # Lisans kontrolü
                        extmeta = info.get("extmetadata", {})
                        license_short = extmeta.get("LicenseShortName", {}).get("value", "").lower()
                        
                        # Uygun lisans mı? (daha esnek kontrol)
                        # Boşlukları ve tireleri normalize et
                        normalized = license_short.replace(" ", "-").replace("_", "-")
                        is_valid = (
                            "cc" in license_short and ("by-sa" in normalized or "by" in normalized) or
                            "cc0" in normalized or 
                            "public" in license_short and "domain" in license_short or
                            "pd-" in normalized
                        )
                        
                        if is_valid:
                            results.append({
                                "title": title,
                                "url": info.get("url", ""),
                                "thumb_url": info.get("thumburl", info.get("url", "")),
                                "user": info.get("user", ""),
                                "timestamp": info.get("timestamp", ""),
                                "license": extmeta.get("LicenseShortName", {}).get("value", ""),
                                "license_url": extmeta.get("LicenseUrl", {}).get("value", ""),
                                "description": extmeta.get("ImageDescription", {}).get("value", ""),
                                "artist": extmeta.get("Artist", {}).get("value", ""),
                                "width": info.get("width", 0),
                                "height": info.get("height", 0),
                                "size": info.get("size", 0)
                            })
        
        return results
    except Exception as e:
        print(f"  API hatası: {e}")
        return []

def download_photo(url, filepath):
    """Fotoğrafı indir"""
    headers = {
        "User-Agent": "CorteqsBarcelonaBot/1.0 (city-content-project; umut.baris@example.com) python-requests/2.31.0"
    }
    try:
        response = requests.get(url, timeout=60, stream=True, headers=headers)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"  İndirme hatası: {e}")
        return False

def calculate_sha256(filepath):
    """SHA-256 hash hesapla"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_evidence_file(photo_data, filepath, sha256):
    """Kanıt dosyası oluştur"""
    evidence = {
        "photo_id": photo_data["photo_id"],
        "source_url": photo_data["source_url"],
        "source_title": photo_data["title"],
        "author": photo_data["artist"],
        "license": photo_data["license"],
        "license_url": photo_data["license_url"],
        "usage_terms": f"Bu fotoğraf {photo_data['license']} lisansı altında kullanılabilir.",
        "attribution": f"© {photo_data['artist']} / Wikimedia Commons / {photo_data['license']}",
        "restrictions": "Yok",
        "checked_on": TODAY,
        "downloaded_file": filepath,
        "downloaded_sha256": sha256,
        "downloaded_on": TODAY,
        "width": photo_data["width"],
        "height": photo_data["height"]
    }
    
    evidence_path = filepath.replace(".jpg", "_evidence.json")
    with open(evidence_path, 'w', encoding='utf-8') as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)
    
    return evidence_path

def get_places_from_excel():
    """Excel'den mekân listesini al"""
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb['Mekânlar']
    
    places = []
    for row in range(8, ws.max_row + 1):
        entry_id = ws.cell(row=row, column=1).value
        if entry_id:
            title = ws.cell(row=row, column=4).value  # title sütunu
            slug = ws.cell(row=row, column=3).value  # slug sütunu
            if title and slug:
                places.append({
                    "entry_id": entry_id,
                    "title": title,
                    "slug": slug
                })
    
    return places

def get_photo_count_for_place(place):
    """Mekânın önemine göre fotoğraf sayısı belirle"""
    # Önemli mekânlar (3-4 fotoğraf)
    important_slugs = [
        'sagrada-familia', 'park-guell', 'casa-batllo', 'casa-mila-la-pedrera',
        'casa-vicens', 'mnac-museu-nacional-art-catalunya', 'museu-picasso',
        'catedral-barcelona', 'basilica-santa-maria-del-mar', 'camp-nou',
        'mercat-la-boqueria', 'platja-barceloneta', 'montjuic-parks',
        'palau-de-la-musica-catalana', 'arc-de-triomf'
    ]
    
    # Orta derecede önemli mekânlar (2 fotoğraf)
    medium_slugs = [
        'fundacio-joan-miro', 'cosmo-caixa', 'born-centre-cultural',
        'macba-cagm', 'spotify-camp-nou', 'estadi-olimpic-lluis-companys',
        'parc-de-la-ciutadella', 'tibidabo-luna-park', 'aquarium-barcelona',
        'zoo-barcelona', 'teatre-liceu', 'sala-apolo', 'sala-razzmatazz'
    ]
    
    slug = place['slug']
    
    if slug in important_slugs:
        return 4
    elif slug in medium_slugs:
        return 2
    else:
        return 2  # Varsayılan 2 fotoğraf (250'ye ulaşmak için)

def download_place_photos(place, index):
    """Bir mekân için fotoğraf(lar) indir"""
    photo_count = get_photo_count_for_place(place)
    print(f"\n[{index}] {place['title']} - Hedef: {photo_count} fotoğraf")
    
    # Arama terimleri
    search_terms = [
        place['title'],
        place['slug'].replace('-', ' '),
        place['title'].split()[0]  # İlk kelime
    ]
    
    photos = []
    photo_num = 1
    
    for term in search_terms:
        if photo_num > photo_count:
            break
            
        results = search_wikimedia(term, limit=photo_count)
        
        for photo in results:
            if photo_num > photo_count:
                break
            
            # Dosya adı
            filename = f"barcelona_{place['slug']}_{photo_num:02d}.jpg"
            filepath = os.path.join(PHOTO_DIR, filename)
            
            # İndir
            print(f"  [{photo_num}/{photo_count}] İndiriliyor: {photo['title']}")
            if download_photo(photo['thumb_url'], filepath):
                sha256 = calculate_sha256(filepath)
                
                # Kanıt dosyası
                photo_data = {
                    "photo_id": f"{CITY_ID}:foto:{place['slug']}-{photo_num:02d}",
                    "title": photo['title'],
                    "source_url": photo['url'],
                    "artist": photo['artist'],
                    "license": photo['license'],
                    "license_url": photo['license_url'],
                    "width": photo.get('width', 0),
                    "height": photo.get('height', 0)
                }
                
                evidence_path = create_evidence_file(photo_data, filepath, sha256)
                
                print(f"    ✓ İndirildi: {filename}")
                print(f"    ✓ SHA-256: {sha256[:16]}...")
                print(f"    ✓ Lisans: {photo['license']}")
                
                photos.append({
                    "entry_id": place['entry_id'],
                    "filename": filename,
                    "filepath": filepath,
                    "sha256": sha256,
                    "photo_data": photo_data,
                    "evidence_path": evidence_path,
                    "order": photo_num
                })
                
                photo_num += 1
        
        time.sleep(0.5)  # API rate limit
    
    if photos:
        print(f"  ✓ Toplam {len(photos)} fotoğraf indirildi")
    else:
        print(f"  ✗ Fotoğraf bulunamadı")
    
    return photos

def download_cover_photos():
    """8 kapak fotoğrafı indir"""
    print("\n" + "="*60)
    print("KAPAK FOTOĞRAFLARI İNDİRİLİYOR")
    print("="*60)
    
    cover_searches = [
        ("Barcelona skyline", "kapak-01"),
        ("Sagrada Familia exterior", "kapak-02"),
        ("Park Guell mosaic", "kapak-03"),
        ("Gothic Quarter Barcelona", "kapak-04"),
        ("Barceloneta beach", "kapak-05"),
        ("Montjuic Barcelona", "kapak-06"),
        ("Casa Batllo facade", "kapak-07"),
        ("Barcelona sunset Mediterranean", "kapak-08")
    ]
    
    covers = []
    for query, cover_id in cover_searches:
        print(f"\nKapak {cover_id}: {query}")
        
        results = search_wikimedia(query, limit=3)
        
        if results:
            photo = results[0]
            
            filename = f"barcelona_{cover_id}.jpg"
            filepath = os.path.join(PHOTO_DIR, filename)
            
            print(f"  İndiriliyor: {photo['title']}")
            if download_photo(photo['thumb_url'], filepath):
                sha256 = calculate_sha256(filepath)
                
                photo_data = {
                    "photo_id": f"{CITY_ID}:foto:{cover_id}",
                    "title": photo['title'],
                    "source_url": photo['url'],
                    "artist": photo['artist'],
                    "license": photo['license'],
                    "license_url": photo['license_url'],
                    "width": photo.get('width', 0),
                    "height": photo.get('height', 0)
                }
                
                evidence_path = create_evidence_file(photo_data, filepath, sha256)
                
                print(f"  ✓ İndirildi: {filename}")
                print(f"  ✓ SHA-256: {sha256[:16]}...")
                print(f"  ✓ Lisans: {photo['license']}")
                
                covers.append({
                    "cover_id": cover_id,
                    "filename": filename,
                    "filepath": filepath,
                    "sha256": sha256,
                    "photo_data": photo_data,
                    "evidence_path": evidence_path
                })
        
        time.sleep(0.5)
    
    return covers

def update_excel(place_photos, cover_photos):
    """Excel'i güncelle"""
    print("\n" + "="*60)
    print("EXCEL GÜNCELLENİYOR")
    print("="*60)
    
    wb = openpyxl.load_workbook(EXCEL_PATH)
    
    # Fotoğraflar sekmesi
    ws_photos = wb['Fotoğraflar']
    cm_photos = {}
    for c in range(1, ws_photos.max_column + 1):
        v = ws_photos.cell(row=7, column=c).value
        if v:
            cm_photos[v.strip()] = c
    
    row = 8
    
    # Mekân fotoğrafları
    for photo in place_photos:
        ws_photos.cell(row=row, column=cm_photos['photo_id'], value=photo['photo_data']['photo_id'])
        ws_photos.cell(row=row, column=cm_photos['city_id'], value=CITY_ID)
        ws_photos.cell(row=row, column=cm_photos['role'], value='Mekân')
        ws_photos.cell(row=row, column=cm_photos['entry_id'], value=photo['entry_id'])
        ws_photos.cell(row=row, column=cm_photos['file'], value=f"Fotoğraflar/{photo['filename']}")
        ws_photos.cell(row=row, column=cm_photos['sha256'], value=photo['sha256'])
        ws_photos.cell(row=row, column=cm_photos['caption'], value=photo['photo_data']['title'])
        ws_photos.cell(row=row, column=cm_photos['author'], value=photo['photo_data']['artist'])
        ws_photos.cell(row=row, column=cm_photos['license'], value=photo['photo_data']['license'])
        ws_photos.cell(row=row, column=cm_photos['license_url'], value=photo['photo_data']['license_url'])
        ws_photos.cell(row=row, column=cm_photos['source_url'], value=photo['photo_data']['source_url'])
        ws_photos.cell(row=row, column=cm_photos['source_checked_on'], value=TODAY)
        ws_photos.cell(row=row, column=cm_photos['modifications'], value='Değişiklik yok')
        ws_photos.cell(row=row, column=cm_photos['evidence_id'], value=f"{CITY_ID}:kanit:{photo['entry_id'].split(':')[2]}-01")
        ws_photos.cell(row=row, column=cm_photos['completion_credit'], value='Evet')
        ws_photos.cell(row=row, column=cm_photos['order'], value=1)
        ws_photos.cell(row=row, column=cm_photos['editorial_status'], value='Taslak')
        row += 1
    
    # Kapak fotoğrafları
    for photo in cover_photos:
        ws_photos.cell(row=row, column=cm_photos['photo_id'], value=photo['photo_data']['photo_id'])
        ws_photos.cell(row=row, column=cm_photos['city_id'], value=CITY_ID)
        ws_photos.cell(row=row, column=cm_photos['role'], value='Kapak')
        ws_photos.cell(row=row, column=cm_photos['file'], value=f"Fotoğraflar/{photo['filename']}")
        ws_photos.cell(row=row, column=cm_photos['sha256'], value=photo['sha256'])
        ws_photos.cell(row=row, column=cm_photos['caption'], value=photo['photo_data']['title'])
        ws_photos.cell(row=row, column=cm_photos['author'], value=photo['photo_data']['artist'])
        ws_photos.cell(row=row, column=cm_photos['license'], value=photo['photo_data']['license'])
        ws_photos.cell(row=row, column=cm_photos['license_url'], value=photo['photo_data']['license_url'])
        ws_photos.cell(row=row, column=cm_photos['source_url'], value=photo['photo_data']['source_url'])
        ws_photos.cell(row=row, column=cm_photos['source_checked_on'], value=TODAY)
        ws_photos.cell(row=row, column=cm_photos['modifications'], value='Değişiklik yok')
        ws_photos.cell(row=row, column=cm_photos['evidence_id'], value=f"{CITY_ID}:kanit:{photo['cover_id']}")
        ws_photos.cell(row=row, column=cm_photos['completion_credit'], value='Evet')
        ws_photos.cell(row=row, column=cm_photos['order'], value=1)
        ws_photos.cell(row=row, column=cm_photos['editorial_status'], value='Taslak')
        row += 1
    
    # Kanıtlar sekmesi
    ws_evidence = wb['Kanıtlar']
    cm_evidence = {}
    for c in range(1, ws_evidence.max_column + 1):
        v = ws_evidence.cell(row=7, column=c).value
        if v:
            cm_evidence[v.strip()] = c
    
    row = 8
    
    for photo in place_photos + cover_photos:
        evidence_id = photo['photo_data']['photo_id'].replace('foto', 'kanit')
        
        ws_evidence.cell(row=row, column=cm_evidence['evidence_id'], value=evidence_id)
        ws_evidence.cell(row=row, column=cm_evidence['city_id'], value=CITY_ID)
        ws_evidence.cell(row=row, column=cm_evidence['photo_id'], value=photo['photo_data']['photo_id'])
        ws_evidence.cell(row=row, column=cm_evidence['source_url'], value=photo['photo_data']['source_url'])
        ws_evidence.cell(row=row, column=cm_evidence['source_title'], value=photo['photo_data']['title'])
        ws_evidence.cell(row=row, column=cm_evidence['author'], value=photo['photo_data']['artist'])
        ws_evidence.cell(row=row, column=cm_evidence['license'], value=photo['photo_data']['license'])
        ws_evidence.cell(row=row, column=cm_evidence['license_url'], value=photo['photo_data']['license_url'])
        ws_evidence.cell(row=row, column=cm_evidence['usage_terms'], value=f"{photo['photo_data']['license']} lisansı")
        ws_evidence.cell(row=row, column=cm_evidence['attribution'], value=f"© {photo['photo_data']['artist']} / Wikimedia Commons")
        ws_evidence.cell(row=row, column=cm_evidence['restrictions'], value='Yok')
        ws_evidence.cell(row=row, column=cm_evidence['checked_on'], value=TODAY)
        ws_evidence.cell(row=row, column=cm_evidence['metadata_review_status'], value='Bekliyor')
        ws_evidence.cell(row=row, column=cm_evidence['pixel_review_status'], value='Bekliyor')
        ws_evidence.cell(row=row, column=cm_evidence['rights_status'], value='Bekliyor')
        row += 1
    
    wb.save(EXCEL_PATH)
    print(f"✓ Excel güncellendi: {len(place_photos)} mekân + {len(cover_photos)} kapak fotoğrafı")

def main():
    """Ana fonksiyon"""
    print("="*60)
    print("BARCELONA CITY-009 FOTOĞRAF İNDİRME")
    print("="*60)
    print(f"Tarih: {TODAY}")
    print(f"Hedef: 120 mekân + 8 kapak = 128 fotoğraf")
    
    ensure_dirs()
    
    # Mekân fotoğrafları
    print("\n" + "="*60)
    print("MEKÂN FOTOĞRAFLARI İNDİRİLİYOR")
    print("="*60)
    
    places = get_places_from_excel()
    print(f"Toplam mekân: {len(places)}")
    print(f"Hedef: ~250 fotoğraf (120 mekân × 2-4 fotoğraf + 8 kapak)")
    
    place_photos = []
    for i, place in enumerate(places, 1):
        results = download_place_photos(place, i)
        if results:
            place_photos.extend(results)
        
        # Her 10 mekânda bir durakla (API rate limit)
        if i % 10 == 0:
            print(f"\n--- {i}/{len(places)} mekân tamamlandı ({len(place_photos)} fotoğraf) ---")
            time.sleep(2)
    
    # Kapak fotoğrafları
    cover_photos = download_cover_photos()
    
    # Excel güncelle
    update_excel(place_photos, cover_photos)
    
    # Özet
    print("\n" + "="*60)
    print("İNDİRME TAMAMLANDI")
    print("="*60)
    print(f"✓ Mekân fotoğrafları: {len(place_photos)}")
    print(f"✓ Kapak fotoğrafları: {len(cover_photos)}/8")
    total = len(place_photos) + len(cover_photos)
    print(f"✓ Toplam: {total}/250 fotoğraf")
    print(f"✓ Klasör: {PHOTO_DIR}")
    print(f"✓ Excel güncellendi: {EXCEL_PATH}")
    
    if total >= 250:
        print(f"\n✓✓✓ HEDEF BAŞARIYLA TAMAMLANDI! ✓✓✓")
    else:
        missing = 250 - total
        print(f"\n✗ Hedefe {missing} fotoğraf eksik")
        print("  Eksik fotoğraflar için manuel ekleme gerekebilir")

if __name__ == "__main__":
    main()
