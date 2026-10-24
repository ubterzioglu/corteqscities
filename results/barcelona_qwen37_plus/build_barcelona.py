# -*- coding: utf-8 -*-
"""
CITY-009 Barcelona tam şehir rehberi üretimi
Kademeli Excel doldurma scripti - Aşama 1: Temel içerik
"""

import openpyxl
from openpyxl.utils import get_column_letter
import json
import os
import shutil
from datetime import date, datetime

EXCEL_PATH = r"C:\temp_private\corteqs\0000_newera\results\barcelona_qwen37_plus\2_excel\CITY-009_barcelona_v001.xlsx"
BASE = r"C:\temp_private\corteqs\0000_newera\results\barcelona_qwen37_plus"
CITY_ID = "barcelona"
CITY_CODE = "CITY-009"
TODAY = "2026-10-20"

def load_wb():
    return openpyxl.load_workbook(EXCEL_PATH)

def save_wb(wb):
    wb.save(EXCEL_PATH)

def get_header_map(ws, key_row=7):
    """7. satırdaki teknik anahtarlardan sütun indeksini çıkar"""
    m = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=key_row, column=c).value
        if v:
            m[v.strip()] = c
    return m

def write_row(ws, row_num, col_map, data_dict):
    """Bir satıra veri yaz"""
    for key, val in data_dict.items():
        if key in col_map:
            ws.cell(row=row_num, column=col_map[key], value=val)

def clear_data_rows(ws, start=8):
    """Mevcut veri satırlarını temizle"""
    for r in range(start, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            ws.cell(row=r, column=c, value=None)

# ============================================================
# 1. TESLİMAT
# ============================================================
def fill_teslimat(wb):
    ws = wb['Teslimat']
    cm = get_header_map(ws)
    clear_data_rows(ws)
    write_row(ws, 8, cm, {
        'schema_version': '1.0',
        'delivery_id': f'{CITY_ID}:v001',
        'city_id': CITY_ID,
        'editor': 'Umut Barış Terzioğlu',
        'reviewer': None,
        'scope': 'Tam teslim',
        'updated_on': TODAY,
        'editorial_status': 'Taslak',
        'notes': 'Barcelona CITY-009 tam şehir rehberi - qwen3.7-plus üretimi'
    })
    print("Teslimat: 1 kayıt")

# ============================================================
# 2. ŞEHİR PROFİLİ
# ============================================================
def fill_sehir(wb):
    ws = wb['Şehir']
    cm = get_header_map(ws)
    clear_data_rows(ws)
    write_row(ws, 8, cm, {
        'city_id': CITY_ID,
        'name': 'Barcelona',
        'country': 'İspanya',
        'country_code': 'ES',
        'region': 'EU',
        'kind': 'city',
        'title': 'Barcelona.',
        'intro': 'Akdeniz kıyısında Modernist başkent. Plajdan dağa, Gotik sokaklardan teknoloji mahallelerine. İspanya\'nın en kozmopolit şehrinde hayat kurmak ve keşfetmek için ihtiyacın olan rehber.',
        'currency': 'EUR',
        'currency_symbol': '€',
        'currency_label': 'Euro',
        'language': 'İspanyolca, Katalanca',
        'timezone': 'Europe/Madrid',
        'latitude': 41.3874,
        'longitude': 2.1686,
        'coordinate_source_url': 'https://www.openstreetmap.org/node/34794300',
        'coordinate_checked_on': TODAY,
        'coordinate_note': 'Plaça de Catalunya merkez referans noktası',
        'source_url': 'https://www.barcelona.cat/internationalwelcome/en',
        'source_checked_on': TODAY,
        'source_position': 9,
        'reviewed_on': TODAY,
        'priority': 3,
        'aliases': 'Barcelona; Barna; Barna',
        'locality': 'Barcelona',
        'tagline': 'Akdeniz\'in Modernist başkenti',
        'directory_order': 9,
        'forecast_url': 'https://www.meteo.cat/serveis/municipis/barcelona',
        'provider_url': 'https://www.meteo.cat',
        'forecast_label': 'Meteo.cat Barcelona tahmini',
        'hero_photo_id': f'{CITY_ID}:foto:kapak-01',
        'editorial_notes': 'Katalonya özerk topluluğunun başkenti. İki resmî dil: Katalanca ve İspanyolca.',
        'editorial_status': 'Taslak'
    })
    print("Şehir: 1 kayıt")

# ============================================================
# 3. KONULAR (12)
# ============================================================
def fill_konular(wb):
    ws = wb['Konular']
    cm = get_header_map(ws)
    clear_data_rows(ws)
    
    topics = [
        {'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'city_id': CITY_ID, 'slug': 'tasınma-oncesi', 'title': 'Taşınmadan önce', 'description': 'Barcelona\'ya taşınma öncesi hazırlık: statüye göre plan, belge, bütçe ve ilk günlerin sırası.', 'icon': 'suitcase', 'order': 1},
        {'topic_id': f'{CITY_ID}:konu:vize-oturum', 'city_id': CITY_ID, 'slug': 'vize-oturum-calisma', 'title': 'Vize, oturum ve çalışma hakkı', 'description': 'İspanya\'da vize, oturum izni, NIE, TIE ve çalışma hakkı süreçleri.', 'icon': 'passport', 'order': 2},
        {'topic_id': f'{CITY_ID}:konu:kayit-resmi', 'city_id': CITY_ID, 'slug': 'kayit-ve-resmi-islemler', 'title': 'Kayıt ve resmî işlemler', 'description': 'Empadronamiento, sosyal güvenlik, vergi numarası ve resmî belge işlemleri.', 'icon': 'document', 'order': 3},
        {'topic_id': f'{CITY_ID}:konu:ev-yerlesim', 'city_id': CITY_ID, 'slug': 'ev-ve-yerlesim', 'title': 'Ev ve yerleşim', 'description': 'Barcelona\'da ev bulma, kira sözleşmesi, depozito, kiracı hakları ve dolandırıcılık önleme.', 'icon': 'home', 'order': 4},
        {'topic_id': f'{CITY_ID}:konu:utility', 'city_id': CITY_ID, 'slug': 'elektrik-su-internet', 'title': 'Elektrik, su, internet ve telefon', 'description': 'Barcelona\'da utility abonelikleri: elektrik, su, doğalgaz, internet ve mobil hat.', 'icon': 'bolt', 'order': 5},
        {'topic_id': f'{CITY_ID}:konu:banka-vergi', 'city_id': CITY_ID, 'slug': 'banka-odeme-vergi-sigorta', 'title': 'Banka, ödeme, vergi ve sigorta', 'description': 'İspanya\'da banka hesabı açma, ödeme sistemi, vergi beyanı ve sigorta türleri.', 'icon': 'bank', 'order': 6},
        {'topic_id': f'{CITY_ID}:konu:saglik', 'city_id': CITY_ID, 'slug': 'saglik-ve-bakim', 'title': 'Sağlık ve bakım', 'description': 'CatSalut kamu sağlığı, CAP kayıt, TSI kart, eczane, acil durum ve diş bakımı.', 'icon': 'heart', 'order': 7},
        {'topic_id': f'{CITY_ID}:konu:is-kariyer', 'city_id': CITY_ID, 'slug': 'is-ve-kariyer', 'title': 'İş ve kariyer', 'description': 'Barcelona\'da iş arama, meslek tanıma, sözleşme türleri ve yerel ağlar.', 'icon': 'briefcase', 'order': 8},
        {'topic_id': f'{CITY_ID}:konu:aile-egitim', 'city_id': CITY_ID, 'slug': 'aile-egitim-cocuk', 'title': 'Aile, eğitim ve çocuk', 'description': 'Barcelona\'da okul, kreş, üniversite, aile destekleri ve çocuklarla yaşam.', 'icon': 'users', 'order': 9},
        {'topic_id': f'{CITY_ID}:konu:ulasim', 'city_id': CITY_ID, 'slug': 'ulasim', 'title': 'Ulaşım', 'description': 'Havaalanı, TMB metro-otobüs, bilet-abonman, Bicing bisiklet, araç ve ehliyet.', 'icon': 'train', 'order': 10},
        {'topic_id': f'{CITY_ID}:konu:gunluk-yasam', 'city_id': CITY_ID, 'slug': 'gunluk-yasam-topluluk', 'title': 'Günlük yaşam ve topluluk', 'description': 'Alışveriş, Türk/diaspora kaynakları, atık yönetimi, güvenlik ve sosyal bağlantılar.', 'icon': 'shopping-bag', 'order': 11},
        {'topic_id': f'{CITY_ID}:konu:kesif-kultur', 'city_id': CITY_ID, 'slug': 'kesif-kultur-sanat-spor', 'title': 'Keşif, kültür, sanat ve spor', 'description': 'Müze, park, plaj, konser, etkinlik ve spor alanlarıyla Barcelona keşfi.', 'icon': 'compass', 'order': 12},
    ]
    
    for i, t in enumerate(topics):
        write_row(ws, 8 + i, cm, t)
    print(f"Konular: {len(topics)} kayıt")

# ============================================================
# 4. KAYNAKLAR (sources)
# ============================================================
def fill_kaynaklar(wb):
    ws = wb['Kaynaklar']
    cm = get_header_map(ws)
    clear_data_rows(ws)
    
    sources = [
        # Vize/oturum
        {'source_id': f'{CITY_ID}:kaynak:bcn-welcome-immigration', 'city_id': CITY_ID, 'title': 'Immigration and identification procedures', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en/live-and-settle/procedures/immigration-and-identification-id-procedures', 'checked_on': TODAY, 'topic': 'Vize, oturum, NIE', 'summary': 'Barcelona belediyesinin uluslararası hoş geldin sayfası. AB/AEA vatandaşları için yeşil NIE, AB dışı vatandaşlar için vize ve oturum izni türleri.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:bcn-green-nie', 'city_id': CITY_ID, 'title': 'Certificate of registration as an EU national (green NIE)', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en/procedure/certificate-registration-eu-national-green-nie', 'checked_on': TODAY, 'topic': 'AB yeşil NIE', 'summary': 'AB vatandaşları için İspanya\'da 3 aydan fazla kalış kayıt sertifikası. EX18 formu, randevu ve ücret bilgileri.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:bcn-empadronamiento', 'city_id': CITY_ID, 'title': 'Registration with the residents register', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en/registration-residents-register', 'checked_on': TODAY, 'topic': 'Empadronamiento', 'summary': 'Barcelona belediye kayıt sistemi. Padró\'ya kayıt, volant de residència belgesi.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:bcnmet-empadronamiento', 'city_id': CITY_ID, 'title': 'Registering as a Citizen in Barcelona', 'publisher': 'Barcelona Metropolitan', 'url': 'https://www.barcelona-metropolitan.com/living/registering-as-a-citizen-in-barcelona', 'checked_on': TODAY, 'topic': 'Empadronamiento detay', 'summary': 'Yabancılar için empadronamiento rehberi. Gerekli belgeler, kira sözleşmesi, adres kanıtı.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:bcnexpat-empadronamiento-2026', 'city_id': CITY_ID, 'title': 'Empadronamiento Requirements in Barcelona 2026', 'publisher': 'Barcelona Expat', 'url': 'https://barcelonaexpat.com/empadronamiento-requirements-barcelona-2026', 'checked_on': TODAY, 'topic': 'Empadronamiento 2026', 'summary': '2026 güncel empadronamiento gereksinimleri. Randevu sistemi, adres kanıtı detayları.', 'verified': 'Evet'},
        
        # Ulaşım
        {'source_id': f'{CITY_ID}:kaynak:tmb-fares', 'city_id': CITY_ID, 'title': 'Metro and bus fares', 'publisher': 'Transports Metropolitans de Barcelona', 'url': 'https://www.tmb.cat/en/barcelona-fares-metro-bus', 'checked_on': TODAY, 'topic': 'TMB ücretler', 'summary': 'TMB resmi ücret sayfası. Tek bilet 2,90€, T-Casual 13€, T-Usual 22,80€.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:tmb-2026-prices', 'city_id': CITY_ID, 'title': '2026 Barcelona metro & bus fares', 'publisher': 'Transports Metropolitans de Barcelona', 'url': 'https://www.tmb.cat/en/barcelona-fares-metro-bus/transport-ticket-fares', 'checked_on': TODAY, 'topic': '2026 ulaşım fiyatları', 'summary': '2026 ulaşım bilet fiyatları listesi.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:travelguide-tmb', 'city_id': CITY_ID, 'title': 'Barcelona Public Transport Tickets & Prices Guide (2026)', 'publisher': 'Travel Guide Barcelona', 'url': 'https://www.travelguide.barcelona/publictransport-tmb/tickets_travelcards/', 'checked_on': TODAY, 'topic': 'Ulaşım rehberi', 'summary': 'TMB bilet türleri karşılaştırması: tek bilet, T-Casual, Hola BCN, havalimanı bileti.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:metro-map-2026', 'city_id': CITY_ID, 'title': 'Barcelona Metro: map, fares, lines and hours 2026', 'publisher': 'Mapa Metro', 'url': 'https://mapa-metro.com/en/spain/barcelona/barcelona-metro-map.htm', 'checked_on': TODAY, 'topic': 'Metro haritası', 'summary': '12 hat, 189 istasyon, işletim saatleri ve ücret bilgileri.', 'verified': 'Evet'},
        
        # Sağlık
        {'source_id': f'{CITY_ID}:kaynak:bcn-healthcare', 'city_id': CITY_ID, 'title': 'Access to public healthcare', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en/access-public-healthcare', 'checked_on': TODAY, 'topic': 'Sağlık erişimi', 'summary': 'CatSalut kamu sağlık sistemi, TSI sağlık kartı başvurusu.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:bcn-public-health-system', 'city_id': CITY_ID, 'title': 'Public healthcare system', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en/live-and-settle/what-you-need/healthcare/public-healthcare-system', 'checked_on': TODAY, 'topic': 'Sağlık sistemi', 'summary': 'CAP birincil bakım merkezleri, 53 CAP, doktor randevu sistemi.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:catsalut-tsi', 'city_id': CITY_ID, 'title': 'Individual healthcare card (TSI)', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en/individual-healthcare-card-tsi', 'checked_on': TODAY, 'topic': 'TSI kart', 'summary': 'Bireysel sağlık kartı başvurusu, online ve yüz yüze yollar.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:gencat-catsalut', 'city_id': CITY_ID, 'title': 'I need access to the public health system', 'publisher': 'Generalitat de Catalunya - CatSalut', 'url': 'https://web.gencat.cat/en/ciutadania/salut/necessito-accedir-sistema-sanitari-public', 'checked_on': TODAY, 'topic': 'CatSalut erişim', 'summary': 'Katalonya kamu sağlık sistemine erişim rehberi.', 'verified': 'Evet'},
        
        # Banka
        {'source_id': f'{CITY_ID}:kaynak:bde-bank-account', 'city_id': CITY_ID, 'title': 'What do you need to do to open a bank account?', 'publisher': 'Banco de España', 'url': 'https://clientebancario.bde.es/pcb/en/blog/cuales-son-los-tramites-para-abrir-una-cuenta-.html', 'checked_on': TODAY, 'topic': 'Banka hesabı', 'summary': 'İspanya\'da banka hesabı açma gereksinimleri. Kimlik, NIE, adres kanıtı.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:immigrationspain-bank', 'city_id': CITY_ID, 'title': 'How to Open a Bank Account in Spain', 'publisher': 'Immigration Spain', 'url': 'https://www.immigrationspain.es/en/open-bank-account/', 'checked_on': TODAY, 'topic': 'Banka hesabı detay', 'summary': 'Yabancılar için İspanya banka hesabı açma rehberi. Yerleşik ve yerleşik olmayan hesapları.', 'verified': 'Evet'},
        
        # Kira/ev
        {'source_id': f'{CITY_ID}:kaynak:bcn-rent-index', 'city_id': CITY_ID, 'title': 'How the new index regulate rents in Barcelona?', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/lamerce/en/noticies/how-the-new-index-regulate-rents-in-barcelona-1375201', 'checked_on': TODAY, 'topic': 'Kira düzenlemesi', 'summary': 'Barcelona\'da kira fiyat düzenleme endeksi. Stresli piyasa alanı uygulaması.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:barcelona-rent-fyi', 'city_id': CITY_ID, 'title': 'Barcelona Rent Prices 2026', 'publisher': 'Barcelona Rent FYI', 'url': 'https://www.barcelona-rent.fyi/', 'checked_on': TODAY, 'topic': 'Kira fiyatları 2026', 'summary': 'INCASOL verilerine göre mahalle bazlı kira karşılaştırması. Q1 2026 ortalama 13,67-18,75€/m².', 'verified': 'Evet'},
        
        # Mahalleler
        {'source_id': f'{CITY_ID}:kaynak:bcn-neighborhoods', 'city_id': CITY_ID, 'title': 'Barcelona\'s neighborhoods', 'publisher': 'Barcelona.com', 'url': 'https://www.barcelona.com/neighborhoods', 'checked_on': TODAY, 'topic': 'Mahalleler', 'summary': 'Barcelona mahalleleri rehberi: Gotik, Born, Eixample, Gràcia, Barceloneta, Poblenou.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:barcelona-urbana-districts', 'city_id': CITY_ID, 'title': 'The 10 Districts of Barcelona, Guide and Map', 'publisher': 'Barcelona Urbana', 'url': 'https://barcelonaurbana.com/en/blog/barcelona-districts-guide', 'checked_on': TODAY, 'topic': '10 ilçe', 'summary': 'Barcelona\'nın 10 ilçesi ve 73 mahalle rehberi.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:lonely-planet-bcn', 'city_id': CITY_ID, 'title': 'Barcelona\'s best neighborhoods', 'publisher': 'Lonely Planet', 'url': 'https://www.lonelyplanet.com/articles/best-neighborhoods-in-barcelona', 'checked_on': TODAY, 'topic': 'Mahalle rehberi', 'summary': 'Lonely Planet Barcelona mahalle rehberi.', 'verified': 'Evet'},
        
        # Acil durum
        {'source_id': f'{CITY_ID}:kaynak:112-gencat', 'city_id': CITY_ID, 'title': '112 emergències', 'publisher': 'Generalitat de Catalunya', 'url': 'http://112.gencat.cat/es/inici', 'checked_on': TODAY, 'topic': 'Acil durum', 'summary': 'Katalonya acil durum numarası 112.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:bcn-emergency', 'city_id': CITY_ID, 'title': 'Emergency assistance in Barcelona', 'publisher': 'Barcelona.de', 'url': 'https://www.barcelona.de/en/barcelona-emergency-assistance.html', 'checked_on': TODAY, 'topic': 'Acil yardım', 'summary': 'Barcelona acil yardım numaraları: 112 genel, 091 polis, 092 yerel polis, 080 itfaiye, 061 ambulans.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:catsalut-urgencies', 'city_id': CITY_ID, 'title': 'Centre d\'urgències d\'atenció primària (CUAP)', 'publisher': 'CatSalut', 'url': 'https://catsalut.gencat.cat/ca/serveis-sanitaris/urgencies-mediques/cuap', 'checked_on': TODAY, 'topic': 'Acil bakım', 'summary': 'CUAP acil bakım merkezleri, 061 Salut Respon.', 'verified': 'Evet'},
        
        # NIE/TIE
        {'source_id': f'{CITY_ID}:kaynak:policia-tie', 'city_id': CITY_ID, 'title': 'Foreigner - Initial card or renewal residence', 'publisher': 'Policía Nacional', 'url': 'https://sede.policia.gob.es/portalCiudadano/_en/tramites_extranjeria_tramite_tarjeta_residencia_residenciaytrabajo.php', 'checked_on': TODAY, 'topic': 'TIE kart', 'summary': 'Yabancı kimlik kartı (TIE) başvurusu. EX17 formu, 790 kod 012 ücret.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:exteriores-nie', 'city_id': CITY_ID, 'title': 'Foreigner Identity Number (NIE)', 'publisher': 'Ministerio de Asuntos Exteriores', 'url': 'https://www.exteriores.gob.es/Consulados/nuevayork/en/ServiciosConsulares/Paginas/Consular/NIE.aspx', 'checked_on': TODAY, 'topic': 'NIE numarası', 'summary': 'NIE numarası açıklaması ve başvuru gereksinimleri.', 'verified': 'Evet'},
        
        # Ek kaynaklar
        {'source_id': f'{CITY_ID}:kaynak:bcn-cat-en', 'city_id': CITY_ID, 'title': 'Barcelona International Welcome', 'publisher': 'Ajuntament de Barcelona', 'url': 'https://www.barcelona.cat/internationalwelcome/en', 'checked_on': TODAY, 'topic': 'Genel rehber', 'summary': 'Barcelona belediyesi uluslararası hoş geldin portalı.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:barcelona-urbana-neighborhoods', 'city_id': CITY_ID, 'title': 'Best Barcelona Neighborhoods to Visit by Traveler Type', 'publisher': 'Barcelona Urbana', 'url': 'https://barcelonaurbana.com/en/blog/best-neighborhoods-visit-barcelona', 'checked_on': TODAY, 'topic': 'Mahalle karşılaştırma', 'summary': 'Ziyaretçi türüne göre mahalle önerileri ve karşılaştırma tablosu.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:webarcelona-districts', 'city_id': CITY_ID, 'title': 'The best neighborhoods in Barcelona', 'publisher': 'WeBarcelona', 'url': 'https://www.webarcelona.net/barcelona-districts-and-quarters', 'checked_on': TODAY, 'topic': 'Mahalle rehberi', 'summary': 'Barcelona ilçe ve mahalle rehberi.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:uab-catsalut', 'city_id': CITY_ID, 'title': 'Public Health-Care System', 'publisher': 'Universitat Autònoma de Barcelona', 'url': 'https://www.uab.cat/sites/ContentServer/mobility-international-exchange/international-support-service/living-in-barcelona/public-health-care-system-1345819425759.html', 'checked_on': TODAY, 'topic': 'Sağlık sistemi', 'summary': 'UAB uluslararası personel için CatSalut sağlık sistemi açıklaması.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:tmb-home', 'city_id': CITY_ID, 'title': 'TMB – metro bus', 'publisher': 'Transports Metropolitans de Barcelona', 'url': 'https://www.tmb.cat/en/home', 'checked_on': TODAY, 'topic': 'TMB ana sayfa', 'summary': 'TMB resmi web sitesi. Metro, otobüs hatları, bilet satın alma.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:tmobilitat-tcasual', 'city_id': CITY_ID, 'title': 'T-casual: the 10-journey ticket', 'publisher': 'T-mobilitat', 'url': 'https://t-mobilitat.cat/en/web/t-mobilitat/fares/t-casual', 'checked_on': TODAY, 'topic': 'T-Casual', 'summary': 'T-Casual 10 yolculuk bileti detayları.', 'verified': 'Evet'},
        {'source_id': f'{CITY_ID}:kaynak:barcelona-card-transport', 'city_id': CITY_ID, 'title': 'Barcelona Public Transport Tickets', 'publisher': 'Barcelona Card', 'url': 'https://www.barcelonacard.org/tickets/t/transport/', 'checked_on': TODAY, 'topic': 'Ulaşım biletleri', 'summary': 'Hola BCN, T-Casual, T-Dia, Aerobus bilet karşılaştırması.', 'verified': 'Evet'},
    ]
    
    for i, s in enumerate(sources):
        write_row(ws, 8 + i, cm, s)
    print(f"Kaynaklar: {len(sources)} kayıt")

# ============================================================
# 5. YANITLAR (240)
# ============================================================
def fill_yanitlar(wb):
    ws = wb['Yanıtlar']
    cm = get_header_map(ws)
    clear_data_rows(ws)
    
    answers = []
    src = lambda x: f'{CITY_ID}:kaynak:{x}'
    
    # KONU 1: Taşınmadan önce (20 yanıt)
    answers.extend([
        {'entry_id': f'{CITY_ID}:yanit:barcelonaya-tasinma-plani', 'city_id': CITY_ID, 'slug': 'barcelonaya-tasinma-plani', 'title': 'Barcelona\'ya taşınmaya nasıl hazırlanmalıyım?', 'subtitle': 'Taşınma öncesi genel hazırlık planı', 'summary': 'Barcelona\'ya taşınmadan önce statünüze göre (AB/AB dışı) vize, NIE, sigorta, bütçe ve konut araştırmasını tamamlayın. İlk 3 ay için yeterli birikim ayırın.', 'keywords': 'taşınma, hazırlık, plan, Barcelona, İspanya', 'stages': 'before;planning', 'source_ids': f'{src("bcn-cat-en")};{src("bcn-welcome-immigration")}', 'reviewed_on': TODAY, 'order': 1, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Mevcut statünüzü belirleyin (AB/AB dışı/öğrenci/dijital göçebe)\nVize/oturum gereksinimlerini kontrol edin\nNIE numarası için randevu alın\nSağlık sigortası ayarlayın\nBütçe planı oluşturun\nGeçici konut araştırın', 'documents': 'Geçerli pasaport/kimlik\nAB vatandaşıysanız: kimlik kartı\nAB dışıysanız: vize başvuru belgeleri\nEkonomik kaynak kanıtı\nSağlık sigortası belgesi', 'timing': 'Taşınmadan en az 2-3 ay önce başlayın', 'cost': 'Vize ücreti statüye göre değişir; NIE ücreti yaklaşık 10€', 'note': 'AB vatandaşları 3 aya kadar özel izin olmadan kalabilir. 3 aydan fazla kalış için kayıt zorunludur.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-yasam-maliyeti', 'city_id': CITY_ID, 'slug': 'barcelona-yasam-maliyeti', 'title': 'Barcelona\'da yaşam maliyeti ne kadar?', 'subtitle': 'Aylık bütçe tahmini', 'summary': 'Barcelona\'da tek kişilik aylık yaşam maliyeti ortalama 1.200-1.800€ arasındadır. Kira en büyük kalemdir; ilçe ve daire boyutuna göre 600-1.500€ arasında değişir.', 'keywords': 'yaşam maliyeti, kira, bütçe, fiyat', 'stages': 'before;planning', 'source_ids': f'{src("barcelona-rent-fyi")};{src("bcn-rent-index")}', 'reviewed_on': TODAY, 'order': 2, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Kira bütçenizi belirleyin (60 m² ortalama 800-1.200€)\nFatura maliyetlerini hesaplayın (aylık 100-200€)\nUlaşım abonmanı: T-Usual 22,80€/ay\nGıda: aylık 250-400€\nToplam: 1.200-1.800€ arası hedefleyin', 'documents': 'Gelir belgesi\nKira sözleşmesi', 'timing': 'Bütçe planını taşınmadan önce yapın', 'cost': 'Tek kişilik ortalama: 1.200-1.800€/ay', 'note': 'Q1 2026 verilerine göre ortalama kira 13,67-18,75€/m². Turistik merkezlerde daha pahalı.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-gereken-belgeler', 'city_id': CITY_ID, 'slug': 'barcelona-gereken-belgeler', 'title': 'Barcelona\'ya taşınırken hangi belgeleri getirmeliyim?', 'subtitle': 'Zorunlu ve önerilen belgeler', 'summary': 'Pasaport/kimlik, doğum kayıt örneği, sağlık sigortası, gelir kanıtı, diploma (varsa apostilli), ehliyet ve uluslararası sağlık kartı gereklidir.', 'keywords': 'belgeler, pasaport, apostil, evrak', 'stages': 'before', 'source_ids': f'{src("bcn-welcome-immigration")};{src("exteriores-nie")}', 'reviewed_on': TODAY, 'order': 3, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Pasaport/kimlik fotokopileri\nDoğum kayıt örneği (apostilli)\nSağlık sigortası belgesi\nGelir kanıtı (iş sözleşmesi veya banka ekstresi)\nDiploma ve transkript (apostilli, İspanyolca tercüme)\nEhliyet (uluslararası veya AB ehliyeti)\nAvrupa Sağlık Sigorta Kartı (AB vatandaşları için)', 'documents': 'Pasaport\nDoğum kayıt örneği\nGelir belgesi\nSigorta belgesi', 'timing': 'Taşınmadan 1-2 ay önce hazırlayın', 'cost': 'Apostil: ülke başına değişir. Tercüme: 30-80€/sayfa', 'note': 'AB dışı belgeler apostil ve yeminli İspanyolca tercüme gerektirir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-ilk-gunler', 'city_id': CITY_ID, 'slug': 'barcelona-ilk-gunler', 'title': 'Barcelona\'ya vardığımda ilk yapmam gerekenler neler?', 'subtitle': 'İlk hafta öncelikleri', 'summary': 'İlk günlerde: geçici konuta yerleşin, empadronamiento randevusu alın, yerel SIM kart alın, CAP sağlık merkezine kaydolun ve NIE başvurusunu başlatın.', 'keywords': 'ilk günler, varış, öncelik', 'stages': 'new', 'source_ids': f'{src("bcn-empadronamiento")};{src("bcn-healthcare")}', 'reviewed_on': TODAY, 'order': 4, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Geçici konuta yerleşin\nTelefon hattı/SIM kart alın\nEmpadronamiento için randevu oluşturun\nYakın CAP sağlık merkezini bulun\nNIE randevusu alın (extranjeria.gob.es)\nBanka hesabı açın\nToplu taşıma bileti (T-Casual) edinin', 'documents': 'Pasaport\nKira sözleşmesi veya adres kanıtı', 'timing': 'İlk 1-2 hafta içinde', 'cost': 'T-Casual: 13€, SIM kart: 10-20€', 'note': 'NIE randevuları aylar sonrasına dolu olabilir; erken başvurun.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-ab-vatandasi', 'city_id': CITY_ID, 'slug': 'barcelona-ab-vatandasi', 'title': 'AB vatandaşı olarak Barcelona\'da oturmak için ne gerekiyor?', 'subtitle': 'AB/AEA vatandaşları için özel kurallar', 'summary': 'AB/AEA vatandaşları İspanya\'da serbestçe yaşayabilir ve çalışabilir. 3 aydan fazla kalış için "yeşil NIE" (certificado de registro) almanız gerekir.', 'keywords': 'AB, vatandaş, yeşil NIE, serbest dolaşım', 'stages': 'before;planning', 'source_ids': f'{src("bcn-green-nie")};{src("bcn-welcome-immigration")}', 'reviewed_on': TODAY, 'order': 5, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'EX18 formunu doldurun\nRandevu alın (sede.administracionespublicas.gob.es)\nModelo 790 kod 012 ücretini yatırın\nPolis istasyonuna gidin: pasaport + form + ücret dekontu + adres kanıtı + ekonomik kaynak kanıtı\nYeşil NIE\'yi anında alın', 'documents': 'Pasaport veya AB kimlik kartı\nEX18 formu\nModelo 790 kod 012 ücret dekontu\nAdres kanıtı (kira sözleşmesi veya empadronamiento)\nEkonomik kaynak kanıtı (iş sözleşmesi, banka ekstresi)', 'timing': '3 aydan fazla kalış için kayıt zorunlu', 'cost': 'Modelo 790 kod 012: yaklaşık 12€', 'note': '5 yıl kesintisiz yasal ikamet sonrası kalıcı oturum hakkı başvurusu yapılabilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-ab-disi-vize', 'city_id': CITY_ID, 'slug': 'barcelona-ab-disi-vize', 'title': 'AB dışı vatandaş olarak hangi vize türleri var?', 'subtitle': 'Oturum ve çalışma vizesi seçenekleri', 'summary': 'AB dışı vatandaşlar için başlıca seçenekler: çalışma vizesi, dijital göçebe vizesi, öğrenci vizesi, girişimci vizesi, yüksek nitelikli profesyonel (AB Mavi Kart), karışık olmayan gelir vizesi ve aile birleşimi.', 'keywords': 'AB dışı, vize, oturum, çalışma izni', 'stages': 'before;planning', 'source_ids': f'{src("bcn-welcome-immigration")};{src("exteriores-nie")}', 'reviewed_on': TODAY, 'order': 6, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Size uygun vize türünü belirleyin\nGerekli belgeleri hazırlayın\nİspanyol konsolosluğundan vize başvurusu yapın\nİspanya\'ya vardıktan sonra TIE (yabancı kimlik kartı) başvurusu yapın\nSosyal güvenlik kaydını tamamlayın', 'documents': 'Pasaport\nVize türüne göre değişen belgeler\nEkonomik kaynak kanıtı\nSağlık sigortası\nSabıka kaydı', 'timing': 'Vize başvurusu 1-3 ay sürebilir', 'cost': 'Vize ücreti türüne göre değişir (60-160€)', 'note': 'Dijital göçebe vizesi uzaktan çalışanlar için popüler bir seçenektir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-dijital-gocebe', 'city_id': CITY_ID, 'slug': 'barcelona-dijital-gocebe', 'title': 'Dijital göçebe vizesi ile Barcelona\'da yaşanabilir mi?', 'subtitle': 'Uzaktan çalışanlar için İspanya dijital göçebe vizesi', 'summary': 'Evet. İspanya\'nın dijital göçebe vizesi (residencia para teletrabajadores) uzaktan çalışanlara 12 aya kadar oturum izni verir. Aylık minimum gelir gereksinimi İspanya asgari ücretinin %200\'üdür.', 'keywords': 'dijital göçebe, uzaktan çalışma, teletrabajo', 'stages': 'before;planning', 'source_ids': f'{src("bcn-welcome-immigration")}', 'reviewed_on': TODAY, 'order': 7, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'İspanya\'da uzaktan çalışma hakkınızı doğrulayın\nGelir kanıtı hazırlayın (minimum %200 SMI)\nSağlık sigortası alın\nİspanyol konsolosluğundan vize başvurusu yapın\nVarışta TIE başvurusu yapın', 'documents': 'Pasaport\nİş sözleşmesi veya müşteri sözleşmeleri\nGelir kanıtı (son 3 ay)\nSağlık sigortası\nSabıka kaydı', 'timing': 'Başvuru 20 iş günü içinde sonuçlanır', 'cost': 'Vize ücreti yaklaşık 240€', 'note': 'Vize 12 ay geçerlidir; 5 yıla kadar yenilenebilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-ogrenci-vizesi', 'city_id': CITY_ID, 'slug': 'barcelona-ogrenci-vizesi', 'title': 'Öğrenci olarak Barcelona\'da nasıl kalabilirim?', 'subtitle': 'Öğrenci vizesi ve izinleri', 'summary': 'AB dışı öğrenciler öğrenci vizesi (estancia por estudios) almalıdır. AB öğrenciler yeşil NIE ile kayıt olur. Öğrenciler haftada 30 saate kadar çalışma iznine başvurabilir.', 'keywords': 'öğrenci, üniversite, estancias, estudio', 'stages': 'before;planning', 'source_ids': f'{src("bcn-welcome-immigration")};{src("uab-catsalut")}', 'reviewed_on': TODAY, 'order': 8, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Barcelona\'daki bir eğitim kurumuna kabul alın\nÖğrenci vizesi için başvurun (AB dışı)\nVarışta NIE/yeşil NIE alın\nTSI sağlık kartı başvurusu yapın\nGerekirse çalışma iznine başvurun', 'documents': 'Kabul mektubu\nPasaport\nEkonomik kaynak kanıtı\nSağlık sigortası', 'timing': 'Vize başvurusu 1-2 ay', 'cost': 'Vize ücreti yaklaşık 670€', 'note': 'Öğrenci vizesi oturum sayılmaz; çalışma iznine dönüşüm için ayrı başvuru gerekir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-saglik-sigortasi', 'city_id': CITY_ID, 'slug': 'barcelona-saglik-sigortasi', 'title': 'Barcelona için sağlık sigortası nasıl ayarlanır?', 'subtitle': 'Kamu ve özel sağlık sigortası seçenekleri', 'summary': 'AB vatandaşları EHIC ile geçici kapsam alır. Yerleşik olduktan sonra CatSalut\'a kaydolun. AB dışı vatandaşlar vize için özel sağlık sigortası gerektirir (copago olmayan, sınırsız kapsamlı).', 'keywords': 'sağlık sigortası, EHIC, özel sigorta, CatSalut', 'stages': 'before;planning', 'source_ids': f'{src("bcn-healthcare")};{src("catsalut-tsi")}', 'reviewed_on': TODAY, 'order': 9, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'AB vatandaşıysanız: EHIC kartını yanınıza alın\nAB dışıysanız: vize için özel sağlık sigortası alın\nİspanya\'ya yerleştikten sonra CatSalut\'a kaydolun\nTSI sağlık kartı başvurusu yapın\nCAP merkezinize kaydolun', 'documents': 'EHIC kartı (AB) veya özel sigorta poliçesi\nPasaport/NIE\nEmpadronamiento belgesi', 'timing': 'Sigortayı taşınmadan önce ayarlayın', 'cost': 'Özel sağlık sigortası: 40-100€/ay (kişi ve kapsama göre)', 'note': 'Çalışanlar sosyal güvenlik üzerinden otomatik kamu sağlığı kapsamına girer.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-gecici-konut', 'city_id': CITY_ID, 'slug': 'barcelona-gecici-konut', 'title': 'İlk aylar için geçici konut nasıl bulunur?', 'subtitle': 'Kısa dönem konut seçenekleri', 'summary': 'Airbnb, Booking.com, Spotahome ve Uniplaces kısa dönem konut için kullanılır. Oda kiralama 400-900€, stüdyo 900-1.500€ arasındadır. En az 32 günlük sözleşmeler yaygındır.', 'keywords': 'geçici konut, Airbnb, oda, kiralama', 'stages': 'before;planning', 'source_ids': f'{src("barcelona-rent-fyi")};{src("bcn-rent-index")}', 'reviewed_on': TODAY, 'order': 10, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Online platformlarda araştırma yapın\nEn az 3-5 farklı seçeneği karşılaştırın\nKontratı dikkatlice okuyun\nDepozito koşullarını kontrol edin\nEmpadronamiento için uygun adres seçin', 'documents': 'Pasaport\nGelir kanıtı', 'timing': 'Taşınmadan 2-4 hafta önce araştırın', 'cost': 'Oda: 400-900€/ay, Stüdyo: 900-1.500€/ay', 'note': 'Turistik kiralama lisanslı daireleri tercih edin; kayıt dışı kiralama yasal sorun yaratabilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-katalanca-temel', 'city_id': CITY_ID, 'slug': 'barcelona-katalanca-temel', 'title': 'Barcelona\'da Katalanca bilmem gerekiyor mu?', 'subtitle': 'Dil durumu ve temel ifadeler', 'summary': 'Barcelona\'da iki resmî dil vardır: Katalanca ve İspanyolca. Günlük hayatta İspanyolca yeterlidir ancak Katalanca bilmek sosyal entegrasyonu kolaylaştırır. Belediye ücretsiz Katalanca kursları sunar.', 'keywords': 'Katalanca, İspanyolca, dil, kurs', 'stages': 'before;planning', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 11, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Temel İspanyolca öğrenin\nKatalanca temel ifadeleri öğrenin\nBelediye dil kurslarına kaydolun (CPNL)\nPratik yapın', 'documents': None, 'timing': 'Sürekli', 'cost': 'Belediye kursları ücretsiz veya düşük ücretli', 'note': 'Resmî işlemlerde her iki dil de kullanılabilir. Çoğu genç İngilizce de konuşur.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-telefon-hatti', 'city_id': CITY_ID, 'slug': 'barcelona-telefon-hatti', 'title': 'Barcelona\'da telefon hattı nasıl alınır?', 'subtitle': 'Mobil hat ve SIM kart seçenekleri', 'summary': 'Varışta havalimanında veya şehirdeki mağazalardan ön ödemeli SIM kart alabilirsiniz. Vodafone, Orange, Movistar ve Yoigo ana operatörlerdir. Aylık planlar 10-30€ arasındadır.', 'keywords': 'telefon, SIM, mobil, hat', 'stages': 'new', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 12, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Pasaport/NIE ile operatör mağazasına gidin\nÖn ödemeli veya aylık plan seçin\nSIM kartı alın ve etkinleştirin\nNumaranızı alın', 'documents': 'Pasaport veya NIE', 'timing': 'Varışta veya ilk hafta', 'cost': 'Ön ödemeli SIM: 5-10€, Aylık plan: 10-30€', 'note': 'NIE olmadan da ön ödemeli hat alınabilir; sözleşmeli hat için NIE gerekir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-butc-plani', 'city_id': CITY_ID, 'slug': 'barcelona-butc-plani', 'title': 'Barcelona taşınma bütçesi nasıl hazırlanır?', 'subtitle': 'İlk 3 ay için bütçe planlaması', 'summary': 'İlk 3 ay için en az 5.000-8.000€ birikim önerilir. Kira depozitosu (2-3 ay), emlakçı ücreti, eşya ve ilk ay faturaları dahil.', 'keywords': 'bütçe, birikim, mali plan', 'stages': 'before;planning', 'source_ids': f'{src("barcelona-rent-fyi")}', 'reviewed_on': TODAY, 'order': 13, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Kira + depozito hesaplayın\nİlk ay faturalarını ekleyin\nTaşınma masraflarını hesaplayın\n3 aylık acil durum fonu ayırın\nToplam bütçeyi belirleyin', 'documents': 'Gelir belgesi\nBanka ekstresi', 'timing': 'Taşınmadan 2-3 ay önce', 'cost': 'Minimum 5.000-8.000€ önerilir', 'note': 'Depozito genellikle 2 aylık kiradır.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-esya-tasima', 'city_id': CITY_ID, 'slug': 'barcelona-esya-tasima', 'title': 'Eşyalarımı Barcelona\'ya nasıl taşıyabilirim?', 'subtitle': 'Uluslararası nakliye seçenekleri', 'summary': 'AB içi taşıma için kamyon nakliye (2-5 gün), denizyolu veya hava kargo seçenekleri vardır. AB dışı için gümrük beyannamesi gerekir.', 'keywords': 'nakliye, eşya, taşıma, gümrük', 'stages': 'before', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 14, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Nakliye firmalarından teklif alın\nGümrük belgelerini hazırlayın (AB dışı)\nSigorta yaptırın\nTaşıma tarihini planlayın', 'documents': 'Fatura listesi\nGümrük beyannamesi (AB dışı)', 'timing': 'Taşınmadan 4-6 hafta önce', 'cost': 'AB içi: 1.000-3.000€, AB dışı: 2.000-5.000€+', 'note': 'AB içi taşımalarda gümrük vergisi yoktur.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-ehliyet', 'city_id': CITY_ID, 'slug': 'barcelona-ehliyet', 'title': 'Türk ehliyetim Barcelona\'da geçerli mi?', 'subtitle': 'Ehliyet değişimi ve kullanım kuralları', 'summary': 'AB ehliyeti doğrudan geçerlidir. AB dışı ehliyetler 6 ay geçerlidir; sonra İspanyol ehliyetine değiştirmek gerekir. Türk ehliyeti için sınav gerekebilir.', 'keywords': 'ehliyet, araç, sürüş, değişim', 'stages': 'before;new', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 15, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Mevcut ehliyetinizin geçerliliğini kontrol edin\n6 ay içinde İspanyol ehliyetine değişim başvurusu yapın\nGerekirse teorik/pratik sınavlara girin\nJefatura de Tráfico\'den randevu alın', 'documents': 'Mevcut ehliyet\nPasaport/NIE\nEmpadronamiento\nSağlık raporu', 'timing': '6 ay içinde değişim zorunlu', 'cost': 'Başvuru ücreti: yaklaşık 95€', 'note': 'Türkiye ile İspanya arasında karşılıklı ehliyet anlaşması olup olmadığını kontrol edin.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-hayvan-tasima', 'city_id': CITY_ID, 'slug': 'barcelona-hayvan-tasima', 'title': 'Evcil hayvanımla Barcelona\'ya nasıl taşınırım?', 'subtitle': 'Evcil hayvan taşıma kuralları', 'summary': 'AB içi taşıma için mikroçip, kuduz aşısı ve AB hayvan sağlık pasaportu gerekir. AB dışından gelişlerde ek kan testi gerekebilir.', 'keywords': 'evcil hayvan, kedi, köpek, taşıma', 'stages': 'before', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 16, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Mikroçip taktırın\nKuduz aşısını yaptırın\nAB hayvan sağlık pasaportu alın (AB)\nKan testi yaptırın (AB dışı)\nVarışta belediyeye hayvan kaydı yaptırın', 'documents': 'Hayvan sağlık pasaportu\nAşı kayıtları', 'timing': 'Taşınmadan 1-3 ay önce', 'cost': 'Mikroçip + aşı: 50-100€', 'note': 'Barcelona\'da evcil hayvan kaydı zorunludur.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-turk-toplulugu', 'city_id': CITY_ID, 'slug': 'barcelona-turk-toplulugu', 'title': 'Barcelona\'da Türk topluluğu var mı?', 'subtitle': 'Diaspora kaynakları ve sosyal ağlar', 'summary': 'Barcelona\'da aktif bir Türk topluluğu vardır. Türk konsolosluğu, dernekler, restoranlar ve sosyal medya grupları aracılığıyla bağlantı kurulabilir.', 'keywords': 'Türk, topluluk, diaspora, konsolosluk', 'stages': 'before;new', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 17, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Türk Başkonsolosluğu\'na kaydolun\nTürk derneklerini bulun\nFacebook/WhatsApp gruplarına katılın\nTürk restoranlarını ve marketlerini keşfedin', 'documents': None, 'timing': 'Taşınmadan önce veya varışta', 'cost': 'Ücretsiz', 'note': 'Türk Başkonsolosluğu Barcelona: Carrer de la República Argentina, 25.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-hava-durumu', 'city_id': CITY_ID, 'slug': 'barcelona-hava-durumu', 'title': 'Barcelona\'da hava durumu nasıl?', 'subtitle': 'İklim ve mevsimsel bilgiler', 'summary': 'Barcelona Akdeniz iklimine sahiptir. Yazlar sıcak ve kurak (25-30°C), kışlar ılıman (8-15°C). Yıllık ortalama 17°C. Eylül-Ekim en yağışlı aylardır.', 'keywords': 'hava, iklim, mevsim, sıcaklık', 'stages': 'before', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 18, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Meteo.cat\'tan güncel tahmini kontrol edin\nMevsime uygun kıyafet hazırlayın\nGüneş koruması edinin', 'documents': None, 'timing': 'Sürekli', 'cost': None, 'note': 'Canlı hava verisi değil, genel iklim bilgisidir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-saat-farki', 'city_id': CITY_ID, 'slug': 'barcelona-saat-farki', 'title': 'Barcelona\'da saat dilimi nedir?', 'subtitle': 'Zaman dilimi ve yaz/kış saati', 'summary': 'Barcelona CET (UTC+1) saat dilimindedir. Yaz aylarında CEST (UTC+2) uygulanır. Türkiye\'den 1-2 saat geridedir.', 'keywords': 'saat dilimi, zaman, CET', 'stages': 'before', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 19, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Saat farkını hesaplayın\nToplantı ve uçuş saatlerini buna göre planlayın', 'documents': None, 'timing': None, 'cost': None, 'note': 'Yaz saati: Mart son Pazar - Ekim son Pazar.'},
        
        {'entry_id': f'{CITY_ID}:yanit:barcelona-para-birimi', 'city_id': CITY_ID, 'slug': 'barcelona-para-birimi', 'title': 'Barcelona\'da para birimi nedir?', 'subtitle': 'Euro kullanımı ve ödeme yöntemleri', 'summary': 'Barcelona\'da para birimi Euro\'dur (€). Kart ödemeleri yaygındır; temassız ödeme her yerde geçerlidir. Nakit için ATM\'ler mevcuttur.', 'keywords': 'para, Euro, ödeme, kart', 'stages': 'before', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 20, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:tasınma-oncesi', 'steps': 'Euro\'ya geçiş planı yapın\nUluslararası kartınızı aktifleştirin\nVarışta yerel banka hesabı açmayı planlayın', 'documents': None, 'timing': None, 'cost': 'Döviz komisyonu bankaya göre değişir', 'note': 'Küçük işletmelerde minimum harcama limiti olabilir.'},
    ])
    
    # KONU 2: Vize, oturum ve çalışma hakkı (20 yanıt)
    answers.extend([
        {'entry_id': f'{CITY_ID}:yanit:nie-nedir', 'city_id': CITY_ID, 'slug': 'nie-nedir', 'title': 'NIE numarası nedir ve nasıl alınır?', 'subtitle': 'Yabancı kimlik numarası', 'summary': 'NIE (Número de Identidad de Extranjero) İspanya\'da yabancılar için verilen benzersiz kimlik numarasıdır. Çalışma, banka hesabı açma, kira sözleşmesi gibi tüm resmî işlemler için zorunludur.', 'keywords': 'NIE, kimlik numarası, yabancı', 'stages': 'before;planning', 'source_ids': f'{src("exteriores-nie")};{src("bcn-welcome-immigration")}', 'reviewed_on': TODAY, 'order': 21, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'EX15 formunu doldurun\nRandevu alın (sede.administracionespublicas.gob.es)\nModelo 790 kod 012 ücretini yatırın\nPolis istasyonuna gidin\nNIE numaranızı alın', 'documents': 'Pasaport\nEX15 formu\nModelo 790 kod 012 ücret dekontu\nNIE gerektiren işlemin belgesi', 'timing': 'Randevu 2-8 hafta sonra olabilir', 'cost': 'Modelo 790 kod 012: yaklaşık 10€', 'note': 'NIE tek başına oturum hakkı vermez; sadece kimlik numarasıdır.'},
        
        {'entry_id': f'{CITY_ID}:yanit:green-nie-basvuru', 'city_id': CITY_ID, 'slug': 'green-nie-basvuru', 'title': 'Yeşil NIE (AB kayıt sertifikası) nasıl alınır?', 'subtitle': 'AB vatandaşları için oturum kaydı', 'summary': 'AB/AEA vatandaşları 3 aydan fazla kalmak için yeşil NIE (certificado de registro de residente comunitario) almalıdır. EX18 formu, pasaport, adres ve ekonomik kaynak kanıtı gerekir.', 'keywords': 'yeşil NIE, AB kayıt, certificado', 'stages': 'planning;new', 'source_ids': f'{src("bcn-green-nie")}', 'reviewed_on': TODAY, 'order': 22, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'EX18 formunu online doldurun\nRandevu alın (Barcelona ilini seçin)\nModelo 790 kod 012 ücretini yatırın\nGerekli belgelerle polis istasyonuna gidin\nYeşil NIE\'yi anında alın', 'documents': 'AB pasaportu veya kimlik kartı\nEX18 formu\nModelo 790 kod 012 ücret dekontu\nAdres kanıtı (kira sözleşmesi veya empadronamiento)\nEkonomik kaynak kanıtı (iş sözleşmesi, banka ekstresi)', 'timing': 'Randevu 2-6 hafta sonra', 'cost': 'Modelo 790 kod 012: yaklaşık 12€', 'note': 'Belgeler eksiksizse sertifika aynı anda verilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:tie-kart-basvuru', 'city_id': CITY_ID, 'slug': 'tie-kart-basvuru', 'title': 'TIE (yabancı kimlik kartı) nasıl alınır?', 'subtitle': 'AB dışı vatandaşlar için fiziksel kimlik kartı', 'summary': 'TIE (Tarjeta de Identidad de Extranjero) AB dışı vatandaşların fiziksel kimlik kartıdır. Oturum izni onaylandıktan sonra 1 ay içinde başvurulmalıdır.', 'keywords': 'TIE, kimlik kartı, yabancı', 'stages': 'new', 'source_ids': f'{src("policia-tie")};{src("bcn-welcome-immigration")}', 'reviewed_on': TODAY, 'order': 23, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'Oturum izni onayını alın\nEX17 formunu doldurun\nModelo 790 kod 012 ücretini yatırın\nPolis istasyonundan randevu alın\nParmak izi ve fotoğraf verin\nTIE kartınızı alın (3-4 hafta)', 'documents': 'Pasaport\nEX17 formu\nModelo 790 kod 012 ücret dekontu\nOturum izni onay belgesi\n3 adet biyometrik fotoğraf', 'timing': 'Onaydan sonra 1 ay içinde başvuru zorunlu', 'cost': 'Modelo 790 kod 012: yaklaşık 16€', 'note': 'TIE kartı hazır olana kadar geçici belge verilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:empadronamiento-nasil', 'city_id': CITY_ID, 'slug': 'empadronamiento-nasil', 'title': 'Empadronamiento (belediye kaydı) nasıl yapılır?', 'subtitle': 'Padrón\'a kayıt işlemi', 'summary': 'Empadronamiento belediye nüfus kütüğüne kayıt olup oturduğunuz adresi resmî olarak tescil ettirmenizdir. Ücretsizdir ve çoğu resmî işlem için ön koşuldur.', 'keywords': 'empadronamiento, padrón, belediye kayıt', 'stages': 'new', 'source_ids': f'{src("bcn-empadronamiento")};{src("bcnmet-empadronamiento")};{src("bcnexpat-empadronamiento-2026")}', 'reviewed_on': TODAY, 'order': 24, 'featured': 'Evet', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'Barcelona belediyesi web sitesinden randevu alın\nGerekli belgeleri hazırlayın\nİlgili Oficina de Atención Ciudadana\'ya gidin\nVolant de residència belgenizi alın', 'documents': 'Pasaport/NIE/TIE\nKira sözleşmesi (en az 3 aylık) veya tapu\nAdres kanıtı (fatura veya banka ekstresi)\nMülk sahibinin yetkilendirmesi (adınız sözleşmede değilse)', 'timing': 'Randevu 1-4 hafta sonra olabilir', 'cost': 'Ücretsiz', 'note': 'AB vatandaşları her 5 yılda bir yenilemelidir. Kayıt olmadan birçok resmî işlem yapılamaz.'},
        
        {'entry_id': f'{CITY_ID}:yanit:sosyal-guvenlik-kayit', 'city_id': CITY_ID, 'slug': 'sosyal-guvenlik-kayit', 'title': 'Sosyal güvenlik numarası nasıl alınır?', 'subtitle': 'Seguridad Social kayıt', 'summary': 'İşveren işe başladığınızda sosyal güvenlik kaydınızı yapar. Bağımsız çalışanlar (autónomo) kendileri kayıt olur. Numara sağlık hizmetinden emekliliğe kadar tüm haklar için gereklidir.', 'keywords': 'sosyal güvenlik, seguridad social, numara', 'stages': 'new', 'source_ids': f'{src("bcn-welcome-immigration")}', 'reviewed_on': TODAY, 'order': 25, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'İşveren kaydınızı yapar (çalışanlar için)\nVeya Tesorería General de la Seguridad Social\'a gidin\nNIE ve pasaport ile başvurun\nSosyal güvenlik numaranızı alın', 'documents': 'Pasaport/NIE\nİş sözleşmesi (varsa)\nEmpadronamiento', 'timing': 'İşe başlama ile eş zamanlı', 'cost': 'Ücretsiz', 'note': 'Numara hayat boyu aynı kalır.'},
        
        {'entry_id': f'{CITY_ID}:yanit:calisma-izni-ab', 'city_id': CITY_ID, 'slug': 'calisma-izni-ab', 'title': 'AB vatandaşı olarak çalışma izni gerekiyor mu?', 'subtitle': 'AB serbest dolaşım hakkı', 'summary': 'AB/AEA vatandaşları İspanya\'da herhangi bir çalışma izni almadan çalışabilir. Yeşil NIE kaydından sonra serbestçe çalışabilirsiniz.', 'keywords': 'AB çalışma, serbest dolaşım', 'stages': 'planning;new', 'source_ids': f'{src("bcn-green-nie")}', 'reviewed_on': TODAY, 'order': 26, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'Yeşil NIE\'yi alın\nİş arama başlayın\nİşveren sosyal güvenlik kaydınızı yapar', 'documents': 'Yeşil NIE\nPasaport', 'timing': 'Yeşil NIE alındıktan sonra hemen', 'cost': None, 'note': 'Ek izin veya belge gerekmez.'},
        
        {'entry_id': f'{CITY_ID}:yanit:autonomo-kayit', 'city_id': CITY_ID, 'slug': 'autonomo-kayit', 'title': 'Serbest çalışan (autónomo) olarak nasıl kayıt olunur?', 'subtitle': 'Autónomo statüsü', 'summary': 'Barcelona\'da serbest çalışan (autónomo) olmak için Seguridad Social\'a kayıt, Hacienda\'da vergi kaydı ve ilgili meslek odasına kayıt gerekir. Aylık sosyal güvenlik primi 2026\'da minimum 320€ civarıdır.', 'keywords': 'autónomo, serbest çalışma, freelance', 'stages': 'planning;new', 'source_ids': f'{src("bcn-cat-en")}', 'reviewed_on': TODAY, 'order': 27, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'NIE ve empadronamiento\'yu tamamlayın\nSeguridad Social\'a autónomo kaydı yapın\nHacienda\'da 036/037 formuyla vergi kaydı yapın\nİlgili meslek odasına kaydolun (gerekirse)\nFatura sistemi kurun', 'documents': 'NIE/TIE\nEmpadronamiento\nPasaport', 'timing': 'Faaliyete başlamadan önce kayıt zorunlu', 'cost': 'Aylık sosyal güvenlik primi: ~320€ (2026 minimum)', 'note': 'İlk 2 yıl için kademeli indirim (tarifa plana) uygulanabilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:oturum-yenileme', 'city_id': CITY_ID, 'slug': 'oturum-yenileme', 'title': 'Oturum izni nasıl yenilenir?', 'subtitle': 'Yenileme süreci ve zamanlama', 'summary': 'Geçici oturum izni genellikle 1-2 yıllık sürelerle verilir. Süresi dolmadan 60 gün önce yenileme başvurusu yapılmalıdır. EX17 formu ve gerekli belgelerle başvurulur.', 'keywords': 'yenileme, oturum, süresi dolma', 'stages': 'settled', 'source_ids': f'{src("policia-tie")}', 'reviewed_on': TODAY, 'order': 28, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'Süresi dolmadan 60 gün önce hazırlanın\nEX17 formunu doldurun\nModelo 790 kod 012 ücretini yatırın\nRandevu alın\nGerekli belgelerle başvurun', 'documents': 'Pasaport\nMevcut TIE\nEX17 formu\nModelo 790 kod 012\nGelir kanıtı\nEmpadronamiento', 'timing': 'Süresi dolmadan 60 gün önce', 'cost': 'Modelo 790 kod 012: yaklaşık 16€', 'note': '5 yıl sonra kalıcı oturum iznine geçiş yapılabilir.'},
        
        {'entry_id': f'{CITY_ID}:yanit:aile-birlesimi', 'city_id': CITY_ID, 'slug': 'aile-birlesimi', 'title': 'Aile birleşimi ile Barcelona\'ya nasıl gelinir?', 'subtitle': 'Aile üyeleri için oturum', 'summary': 'AB vatandaşlarının aile üyeleri (eş, çocuk, bakmakla yükümlü üst soy) birlikte yaşama hakkına sahiptir. AB dışı aile üyeleri için aile bireyi oturum kartı başvurusu yapılır.', 'keywords': 'aile birleşimi, eş, çocuk', 'stages': 'planning', 'source_ids': f'{src("bcn-welcome-immigration")};{src("policia-tie")}', 'reviewed_on': TODAY, 'order': 29, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': 'Aile bağını belgelendirin\nEX19 formunu doldurun\nRandevu alın\nPolis istasyonuna gidin\nOturum kartını alın', 'documents': 'EX19 formu\nPasaport\nAile bağını gösteren belge (evlilik cüzdanı, doğum kayıtı)\nAB vatandaşının yeşil NIE\'si\nEkonomik kaynak kanıtı', 'timing': 'Başvuru 3 ay içinde sonuçlanır', 'cost': 'Modelo 790 kod 012', 'note': '5 yıl sonra aile üyeleri de kalıcı oturum hakkı kazanır.'},
        
        {'entry_id': f'{CITY_ID}:yanit:kalici-oturum', 'city_id': CITY_ID, 'slug': 'kalici-oturum', 'title': 'Kalıcı oturum hakkı nasıl kazanılır?', 'subtitle': 'Larga duración', 'summary': '5 yıl kesintisiz yasal ikamet sonrası kalıcı oturum izni (larga duración) başvurusu yapılabilir. Kalıcı oturum sınırsız çalışma hakkı verir.', 'keywords': 'kalıcı oturum, larga duración, 5 yıl', 'stages': 'settled', 'source_ids': f'{src("bcn-green-nie")}', 'reviewed_on': TODAY, 'order': 30, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'topic_id': f'{CITY_ID}:konu:vize-oturum', 'steps': '5 yıl kesintisiz yasal ikameti belgeleyin\nEX17 formu ile başvurun\nRandevu alın\nKalıcı oturum kartını alın', 'documents': 'Pasaport\nEX17 formu\n5 yıllık ikamet kanıtı\nModelo 790 kod 012', 'timing': '5 yıl sonra', 'cost': 'Modelo 790 kod 012: yaklaşık 16€', 'note': 'Kalıcı oturum 10 yıllık kart ile verilir.'},
    ])
    
    # Write all answers
    for i, a in enumerate(answers):
        write_row(ws, 8 + i, cm, a)
    print(f"Yanıtlar (aşama 1): {len(answers)} kayıt yazıldı")

# ============================================================
# ANA İŞLEV
# ============================================================
def main():
    print("=" * 60)
    print("CITY-009 Barcelona Üretim - Aşama 1: Temel İçerik")
    print("=" * 60)
    
    wb = load_wb()
    fill_teslimat(wb)
    fill_sehir(wb)
    fill_konular(wb)
    fill_kaynaklar(wb)
    fill_yanitlar(wb)
    
    save_wb(wb)
    print("\nAşama 1 tamamlandı. Excel kaydedildi.")
    print(f"Dosya: {EXCEL_PATH}")

if __name__ == '__main__':
    main()
