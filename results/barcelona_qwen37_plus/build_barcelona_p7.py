# -*- coding: utf-8 -*-
"""
CITY-009 Barcelona - Aşama 7: Kalan 30 mekân + Rotalar (12) + Sözlük (60)
"""

import openpyxl
import json

EXCEL_PATH = r"C:\temp_private\corteqs\0000_newera\results\barcelona_qwen37_plus\2_excel\CITY-009_barcelona_v001.xlsx"
CITY_ID = "barcelona"
TODAY = "2026-10-20"

def load_wb():
    return openpyxl.load_workbook(EXCEL_PATH)

def save_wb(wb):
    wb.save(EXCEL_PATH)

def get_header_map(ws, key_row=7):
    m = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=key_row, column=c).value
        if v:
            m[v.strip()] = c
    return m

def write_row(ws, row_num, col_map, data_dict):
    for key, val in data_dict.items():
        if key in col_map:
            ws.cell(row=row_num, column=col_map[key], value=val)

def src(x):
    return f'{CITY_ID}:kaynak:{x}'

def main():
    wb = load_wb()
    s = lambda x: f'{CITY_ID}:kaynak:{x}'
    
    # ============================================================
    # KALAN 30 MEKÂN (satır 98'den devam)
    # ============================================================
    ws = wb['Mekânlar']
    cm = get_header_map(ws)
    
    last_place_row = 98
    for r in range(8, ws.max_row + 1):
        if ws.cell(row=r, column=1).value:
            last_place_row = r + 1
        else:
            break
    
    places = []
    
    # YEME-İÇME devam (10)
    places.extend([
        {'entry_id': f'{CITY_ID}:yer:sant-antonio-pazar', 'city_id': CITY_ID, 'slug': 'encants-mercat-fira', 'title': 'Els Encants Bit Pazarı', 'subtitle': 'Mercat Fira de Bellcaire', 'summary': 'Avrupa\'nın en eski açık hava bit pazarlarından. Pazartesi-Çarşamba-Cuma. Uygun fiyatlı ikinci el.', 'keywords': 'Encants, bit pazarı, ikinci el', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 91, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Sant Martí', 'setting': 'Açık hava', 'location': 'Av. Meridiana, 69, 08018 Barcelona', 'latitude': 41.4150, 'longitude': 2.1970, 'visit_status': 'Açık', 'note': 'Pzt-Çar-Cum 09:00-17:00. L1 Glòries.', 'collection': 'Hayır', 'media_key': 'encants'},
        
        {'entry_id': f'{CITY_ID}:yer:vincon', 'city_id': CITY_ID, 'slug': 'bar-vincon', 'title': 'Vincon Tasarım Bar', 'subtitle': 'Tasarım ve kahve', 'summary': 'Eixample\'da tasarım mağazası ve kafe. Modernist atmosfer, İtalyan kahvesi.', 'keywords': 'Vincon, tasarım, kafe', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 92, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Passeig de Gràcia, 96, 08008 Barcelona', 'latitude': 41.3940, 'longitude': 2.1640, 'visit_status': 'Açık', 'note': 'L2/L3/L4 Passeig de Gràcia.', 'collection': 'Hayır', 'media_key': 'vincon'},
        
        {'entry_id': f'{CITY_ID}:yer:7-portes', 'city_id': CITY_ID, 'slug': 'restaurant-7-portes', 'title': '7 Portes', 'subtitle': 'Tarihi deniz ürünleri restoranı', 'summary': '1836\'dan beri Barcelona\'nın en eski restoranlarından. Paella ve deniz ürünleri. Eixample\'da.', 'keywords': '7 Portes, paella, tarihi, deniz', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 93, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Passeig d\'Isabel II, 14, 08003 Barcelona', 'latitude': 41.3810, 'longitude': 2.1830, 'visit_status': 'Açık', 'note': 'Rezervasyon önerilir. L4 Barceloneta.', 'collection': 'Hayır', 'media_key': '7-portes'},
        
        {'entry_id': f'{CITY_ID}:yer:can-culleretes', 'city_id': CITY_ID, 'slug': 'can-culleretes', 'title': 'Can Culleretes', 'subtitle': 'Barcelona\'nın en eski restoranı', 'summary': '1786\'dan beri. Katalan mutfağı. Gotik Mahalle\'de. Tarihi atmosfer.', 'keywords': 'Can Culleretes, en eski, Katalan', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 94, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Ciutat Vella', 'setting': 'Kapalı alan', 'location': 'Carrer de Quintana, 5, 08002 Barcelona', 'latitude': 41.3830, 'longitude': 2.1750, 'visit_status': 'Açık', 'note': 'L4 Jaume I.', 'collection': 'Hayır', 'media_key': 'can-culleretes'},
        
        {'entry_id': f'{CITY_ID}:yer:cal-xim', 'city_id': CITY_ID, 'slug': 'bar-cal-xim', 'title': 'Cal Xim', 'subtitle': 'Gràcia tapas barı', 'summary': 'Gràcia\'da yerel tapas barı. Patatas bravas, kroket, vermouth. Samimi atmosfer.', 'keywords': 'Cal Xim, tapas, Gràcia, vermouth', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 95, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Gràcia', 'setting': 'Kapalı alan', 'location': 'Carrer de Sant Lluís, 6, 08012 Barcelona', 'latitude': 41.4070, 'longitude': 2.1560, 'visit_status': 'Açık', 'note': 'L3 Fontana.', 'collection': 'Hayır', 'media_key': 'cal-xim'},
        
        {'entry_id': f'{CITY_ID}:yer:la-cova-fosca', 'city_id': CITY_ID, 'slug': 'la-cova-fosca', 'title': 'La Cova Fosca', 'subtitle': 'Vegan restoran', 'summary': 'El Raval\'da vegan restoran. Yaratıcı bitkisel yemekler. Uygun fiyatlı.', 'keywords': 'vegan, Raval, bitkisel', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 96, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Ciutat Vella', 'setting': 'Kapalı alan', 'location': 'Carrer de l\'Àngel, 12, 08001 Barcelona', 'latitude': 41.3830, 'longitude': 2.1700, 'visit_status': 'Açık', 'note': 'L3 Liceu.', 'collection': 'Hayır', 'media_key': 'cova-fosca'},
        
        {'entry_id': f'{CITY_ID}:yer:turk-restaurant', 'city_id': CITY_ID, 'slug': 'istanbul-restaurant-bcn', 'title': 'İstanbul Restoran', 'subtitle': 'Türk mutfağı', 'summary': 'Raval\'da Türk restoranı. Kebap, pide, baklava. Türk topluluğu buluşma noktası.', 'keywords': 'Türk, kebap, Raval, İstanbul', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 97, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Ciutat Vella', 'setting': 'Kapalı alan', 'location': 'El Raval, Barcelona', 'visit_status': 'Açık', 'note': 'L3 Liceu.', 'collection': 'Hayır', 'media_key': 'istanbul'},
        
        {'entry_id': f'{CITY_ID}:yer:la-boqueria-bar', 'city_id': CITY_ID, 'slug': 'bar-boqueria-market', 'title': 'La Boqueria Tapas Barları', 'subtitle': 'Pazar içi tapas', 'summary': 'La Boqueria pazarında taze deniz ürünleri ve tapas barları. Ayakta yemek.', 'keywords': 'Boqueria, tapas, deniz ürünleri', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 98, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Ciutat Vella', 'setting': 'Kapalı alan', 'location': 'La Rambla, 91, 08002 Barcelona', 'latitude': 41.3815, 'longitude': 2.1715, 'visit_status': 'Açık', 'note': 'L3 Liceu.', 'collection': 'Hayır', 'media_key': 'boqueria-bar'},
        
        {'entry_id': f'{CITY_ID}:yer:el-xampanyet', 'city_id': CITY_ID, 'slug': 'bar-el-xampanyet', 'title': 'El Xampanyet', 'subtitle': 'Cava barı', 'summary': 'El Born\'da 1929\'dan beri cava barı. Anchovies, peynir, deniz ürünleri. Otantik.', 'keywords': 'Xampanyet, cava, Born, anchovies', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 99, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Ciutat Vella', 'setting': 'Kapalı alan', 'location': 'Carrer de Montcada, 22, 08003 Barcelona', 'latitude': 41.3850, 'longitude': 2.1820, 'visit_status': 'Açık', 'note': 'L4 Jaume I.', 'collection': 'Hayır', 'media_key': 'xampanyet'},
        
        {'entry_id': f'{CITY_ID}:yer:bar-celta-pub', 'city_id': CITY_ID, 'slug': 'celta-pub-barcelona', 'title': 'Celta Pub', 'subtitle': 'İrlanda pub', 'summary': 'Eixample\'da İrlanda pub. Bira, futbol, canlı müzik. Expats buluşma noktası.', 'keywords': 'İrlanda, pub, bira, futbol', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 100, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Yeme ve içme', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Carrer de Consell de Cent, 315, 08007 Barcelona', 'latitude': 41.3900, 'longitude': 2.1630, 'visit_status': 'Açık', 'note': 'L2/L3/L4 Passeig de Gràcia.', 'collection': 'Hayır', 'media_key': 'celta'},
    ])
    
    # TARİH VE MİMARİ devam (10)
    places.extend([
        {'entry_id': f'{CITY_ID}:yer:casa-mila', 'city_id': CITY_ID, 'slug': 'casa-mila-la-pedrera', 'title': 'Casa Milà (La Pedrera)', 'subtitle': 'Gaudí - Casa Milà', 'summary': 'Gaudí\'nin dalgalı taş cephesi. Çatı terası, iç avlu. UNESCO Dünya Mirası. Passeig de Gràcia\'da.', 'keywords': 'Casa Milà, La Pedrera, Gaudí, UNESCO', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 101, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Passeig de Gràcia, 92, 08008 Barcelona', 'latitude': 41.3950, 'longitude': 2.1630, 'visit_status': 'Açık', 'note': 'Bilet: 25€. L3 Diagonal.', 'collection': 'Evet', 'media_key': 'casa-mila'},
        
        {'entry_id': f'{CITY_ID}:yer:casa-batllo', 'city_id': CITY_ID, 'slug': 'casa-batllo', 'title': 'Casa Batlló', 'subtitle': 'Gaudí - Casa Batlló', 'summary': 'Gaudí\'nin renkli ejderha çatılı binası. Passeig de Gràcia\'da. UNESCO Dünya Mirası.', 'keywords': 'Casa Batlló, Gaudí, ejderha, UNESCO', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 102, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Passeig de Gràcia, 43, 08007 Barcelona', 'latitude': 41.3915, 'longitude': 2.1650, 'visit_status': 'Açık', 'note': 'Bilet: 35€. L2/L3/L4 Passeig de Gràcia.', 'collection': 'Evet', 'media_key': 'casa-batllo'},
        
        {'entry_id': f'{CITY_ID}:yer:casa-amatller', 'city_id': CITY_ID, 'slug': 'casa-amatller', 'title': 'Casa Amatller', 'subtitle': 'Modernist konut', 'summary': 'Passeig de Gràcia\'da Modernist bina. Çikolata müzesi. Casa Batlló yanında.', 'keywords': 'Casa Amatller, Modernisme, çikolata', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 103, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Passeig de Gràcia, 41, 08007 Barcelona', 'latitude': 41.3915, 'longitude': 2.1650, 'visit_status': 'Açık', 'note': 'L2/L3/L4 Passeig de Gràcia.', 'collection': 'Evet', 'media_key': 'casa-amatller'},
        
        {'entry_id': f'{CITY_ID}:yer:casa-lleo-morera', 'city_id': CITY_ID, 'slug': 'casa-lleo-morera', 'title': 'Casa Lleó Morera', 'subtitle': 'Modernist konut', 'summary': 'Passeig de Gràcia\'da Modernist bina. Starbucks binası. Casa Batlló ve Amatller yanında.', 'keywords': 'Casa Lleó Morera, Modernisme', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 104, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Eixample', 'setting': 'Kapalı alan', 'location': 'Passeig de Gràcia, 35, 08007 Barcelona', 'latitude': 41.3910, 'longitude': 2.1655, 'visit_status': 'Açık', 'note': 'Dışarıdan görülebilir. L2/L3/L4 Passeig de Gràcia.', 'collection': 'Evet', 'media_key': 'casa-lleo'},
        
        {'entry_id': f'{CITY_ID}:yer:hospital-sant-pau', 'city_id': CITY_ID, 'slug': 'hospital-sant-pau-modernist', 'title': 'Eski Sant Pau Hastanesi', 'subtitle': 'Recinte Modernista de Sant Pau', 'summary': 'Modernist hastane kompleksi. UNESCO Dünya Mirası. Şimdi kültür merkezi.', 'keywords': 'Sant Pau, hastane, Modernisme, UNESCO', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 105, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Sant Martí', 'setting': 'Karma', 'location': 'Carrer de Sant Antoni Maria Claret, 167, 08025 Barcelona', 'latitude': 41.4240, 'longitude': 2.1830, 'visit_status': 'Açık', 'note': 'L5 Sant Pau | Dos de Maig.', 'collection': 'Evet', 'media_key': 'hospital-sant-pau'},
        
        {'entry_id': f'{CITY_ID}:yer:palau-guell-gaudi', 'city_id': CITY_ID, 'slug': 'palau-guell-gaudi', 'title': 'Palau Güell', 'subtitle': 'Gaudí - Palau Güell', 'summary': 'Gaudí\'nin ilk büyük eseri. Raval\'da. Gotik-Viktoryen karışımı. UNESCO Dünya Mirası.', 'keywords': 'Palau Güell, Gaudí, UNESCO, Raval', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 106, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Ciutat Vella', 'setting': 'Kapalı alan', 'location': 'Carrer Nou de la Rambla, 3-5, 08001 Barcelona', 'latitude': 41.3775, 'longitude': 2.1700, 'visit_status': 'Açık', 'note': 'L3 Drassanes veya Liceu.', 'collection': 'Evet', 'media_key': 'palau-guell-gaudi'},
        
        {'entry_id': f'{CITY_ID}:yer:torre-bellesguard', 'city_id': CITY_ID, 'slug': 'torre-bellesguard', 'title': 'Torre Bellesguard', 'subtitle': 'Gaudí - Torre Bellesguard', 'summary': 'Gaudí\'nin az bilinen eseri. Gotik-Modernist karışımı. Sarrià\'da. Sınırlı ziyaret.', 'keywords': 'Bellesguard, Gaudí, Gotik', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 107, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Sarrià-Sant Gervasi', 'setting': 'Karma', 'location': 'Carrer de Bellesguard, 16-20, 08022 Barcelona', 'latitude': 41.4280, 'longitude': 2.1250, 'visit_status': 'Randevu ile', 'note': 'Önceden randevu alın.', 'collection': 'Evet', 'media_key': 'bellesguard'},
        
        {'entry_id': f'{CITY_ID}:yer:pavellons-guell', 'city_id': CITY_ID, 'slug': 'pavellons-guell', 'title': 'Güell Köşkleri', 'subtitle': 'Pavellons Güell', 'summary': 'Gaudí\'nin erken eseri. Pedralbes\'te. Çiftlik kapısı ve ahırlar. Sınırlı ziyaret.', 'keywords': 'Pavellons Güell, Gaudí, Pedralbes', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 108, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Les Corts', 'setting': 'Açık hava', 'location': 'Av. de Pedralbes, s/n, 08034 Barcelona', 'latitude': 41.4000, 'longitude': 2.1100, 'visit_status': 'Sınırlı erişim', 'note': 'Üniversite kampüsü içinde.', 'collection': 'Evet', 'media_key': 'pavellons-guell'},
        
        {'entry_id': f'{CITY_ID}:yer:monument-rambla', 'city_id': CITY_ID, 'slug': 'monument-colom', 'title': 'Kolomb Anıtı', 'subtitle': 'Monument a Colom', 'summary': 'La Rambla sonunda Kolomb anıtı. Asansör ile tepeye çıkış. Şehir manzarası.', 'keywords': 'Kolomb, anıt, La Rambla, manzara', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 109, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Ciutat Vella', 'setting': 'Karma', 'location': 'Plaça del Portal de la Pau, s/n, 08002 Barcelona', 'latitude': 41.3760, 'longitude': 2.1770, 'visit_status': 'Açık', 'note': 'Bilet: 7€. L3 Drassanes.', 'collection': 'Evet', 'media_key': 'colom'},
        
        {'entry_id': f'{CITY_ID}:yer:arc-triomf', 'city_id': CITY_ID, 'slug': 'arc-de-triomf', 'title': 'Zafer Takı', 'subtitle': 'Arc de Triomf', 'summary': '1888 Dünya Fuarı için yapıldı. Ciutadella Parkı girişi. Kırmızı tuğla, Modernist.', 'keywords': 'Zafer Takı, Arc de Triomf, 1888', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 110, 'featured': 'Evet', 'editorial_status': 'Taslak', 'group': 'Tarih ve mimari', 'district': 'Ciutat Vella', 'setting': 'Açık hava', 'location': 'Passeig Lluís Companys, s/n, 08010 Barcelona', 'latitude': 41.3900, 'longitude': 2.1840, 'visit_status': 'Açık', 'note': 'Ücretsiz. L4 Arc de Triomf.', 'collection': 'Hayır', 'media_key': 'arc-triomf'},
    ])
    
    # SPOR devam (10)
    places.extend([
        {'entry_id': f'{CITY_ID}:yer:forum-parc', 'city_id': CITY_ID, 'slug': 'parc-del-forum', 'title': 'Fòrum Parkı', 'subtitle': 'Àrea del Fòrum', 'summary': '2004 Fòrum Universal için yapıldı. Modern mimari, etkinlik alanı, plaj. Diagonal Mar yanında.', 'keywords': 'Fòrum, park, modern, etkinlik', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 111, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Sant Martí', 'setting': 'Açık hava', 'location': 'Plaça del Fòrum, 08019 Barcelona', 'latitude': 41.4100, 'longitude': 2.2200, 'visit_status': 'Açık', 'note': 'L4 El Maresme | Fòrum.', 'collection': 'Hayır', 'media_key': 'forum-parc'},
        
        {'entry_id': f'{CITY_ID}:yer:ccib', 'city_id': CITY_ID, 'slug': 'centre-convencions-internacional', 'title': 'Uluslararası Kongre Merkezi', 'subtitle': 'Centre de Convencions Internacional de Barcelona (CCIB)', 'summary': 'Büyük kongre ve fuar merkezi. Diagonal Mar\'da. İş etkinlikleri.', 'keywords': 'kongre, fuar, CCIB, iş', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 112, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Sant Martí', 'setting': 'Kapalı alan', 'location': 'Carrer de la Selva de Mar, 13, 08019 Barcelona', 'latitude': 41.4080, 'longitude': 2.2180, 'visit_status': 'Etkinlik bazlı', 'note': 'L4 El Maresme | Fòrum.', 'collection': 'Hayır', 'media_key': 'ccib'},
        
        {'entry_id': f'{CITY_ID}:yer:fira-barcelona', 'city_id': CITY_ID, 'slug': 'fira-de-barcelona', 'title': 'Fira Barcelona', 'subtitle': 'Fuar ve kongre merkezi', 'summary': 'Mobile World Congress dahil büyük fuarlar. Montjuïc ve Gran Via\'da iki alan.', 'keywords': 'Fira, fuar, MWC, kongre', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 113, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Sants-Montjuïc', 'setting': 'Kapalı alan', 'location': 'Plaça d\'Espanya, 08015 Barcelona', 'latitude': 41.3730, 'longitude': 2.1530, 'visit_status': 'Etkinlik bazlı', 'note': 'L1/L3 Espanya.', 'collection': 'Hayır', 'media_key': 'fira'},
        
        {'entry_id': f'{CITY_ID}:yer:palau-sant-jordi', 'city_id': CITY_ID, 'slug': 'palau-sant-jordi', 'title': 'Palau Sant Jordi', 'subtitle': 'Kapalı spor salonu', 'summary': '1992 Olimpiyatları için Arata Isozaki tasarımı. Konserler ve spor etkinlikleri. Montjuïc\'te.', 'keywords': 'Palau Sant Jordi, Isozaki, konser, spor', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 114, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Sants-Montjuïc', 'setting': 'Kapalı alan', 'location': 'Passeig Olímpic, 5-7, 08038 Barcelona', 'latitude': 41.3640, 'longitude': 2.1560, 'visit_status': 'Etkinlik bazlı', 'note': 'L1 Espanya.', 'collection': 'Hayır', 'media_key': 'sant-jordi'},
        
        {'entry_id': f'{CITY_ID}:yer:piscina-municipal-montjuic', 'city_id': CITY_ID, 'slug': 'piscina-municipal-montjuic', 'title': 'Montjuïc Olimpik Havuzu', 'subtitle': 'Piscines Bernat Picornell', 'summary': '1992 Olimpiyat yüzme havuzları. Montjuïc\'te. Halka açık seanslar.', 'keywords': 'havuz, olimpiyat, Montjuïc', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 115, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Sants-Montjuïc', 'setting': 'Karma', 'location': 'Av. de l\'Estadi, 60-64, 08038 Barcelona', 'latitude': 41.3630, 'longitude': 2.1550, 'visit_status': 'Açık', 'note': 'Seans saatleri değişken.', 'collection': 'Hayır', 'media_key': 'piscina-montjuic'},
        
        {'entry_id': f'{CITY_ID}:yer:club-nautic', 'city_id': CITY_ID, 'slug': 'club-nautic-barcelona', 'title': 'Barcelona Deniz Kulübü', 'subtitle': 'Club Nàutic Barcelona', 'summary': 'Port Olímpic\'te yelken ve deniz sporları kulübü. Üyelik ve dersler.', 'keywords': 'deniz, yelken, kulüp, Port Olímpic', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 116, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Ciutat Vella', 'setting': 'Açık hava', 'location': 'Port Olímpic, 08005 Barcelona', 'latitude': 41.3860, 'longitude': 2.1970, 'visit_status': 'Açık', 'note': 'L4 Ciutadella | Vila Olímpica.', 'collection': 'Hayır', 'media_key': 'club-nautic'},
        
        {'entry_id': f'{CITY_ID}:yer:real-club-tenis', 'city_id': CITY_ID, 'slug': 'real-club-tenis-barcelona', 'title': 'Real Club de Tenis Barcelona', 'subtitle': 'Tenis kulübü', 'summary': '1899\'dan beri tenis kulübü. Barcelona Open turnuvası evi. Üyelik bazlı.', 'keywords': 'tenis, kulüp, Barcelona Open', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 117, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Les Corts', 'setting': 'Açık hava', 'location': 'Carrer d\'Arístides Maillol, s/n, 08028 Barcelona', 'latitude': 41.3790, 'longitude': 2.1180, 'visit_status': 'Açık', 'note': 'Üyelik gerekli.', 'collection': 'Hayır', 'media_key': 'tenis-club'},
        
        {'entry_id': f'{CITY_ID}:yer:club-futbol-barcelona', 'city_id': CITY_ID, 'slug': 'club-barca-training', 'title': 'FC Barcelona Antrenman Tesisleri', 'subtitle': 'Ciutat Esportiva Joan Gamper', 'summary': 'Barça\'nın modern antrenman tesisleri. Sant Joan Despí\'de. Tur yok.', 'keywords': 'Barça, antrenman, tesis', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 118, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Les Corts', 'setting': 'Kapalı alan', 'location': 'Sant Joan Despí (Barcelona dışı)', 'visit_status': 'Kapalı', 'note': 'Halka açık değil.', 'collection': 'Hayır', 'media_key': 'barca-training'},
        
        {'entry_id': f'{CITY_ID}:yer:padel-club', 'city_id': CITY_ID, 'slug': 'padel-club-barcelona', 'title': 'Padel Kulüpleri', 'subtitle': 'Pàdel a Barcelona', 'summary': 'Barcelona\'da birçok padel kulübü. Rezervasyon ile oynanır. Popüler spor.', 'keywords': 'padel, kulüp, spor', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 119, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Eixample', 'setting': 'Açık hava', 'location': 'Çeşitli lokasyonlar', 'visit_status': 'Açık', 'note': 'Rezervasyon gerekli.', 'collection': 'Hayır', 'media_key': 'padel'},
        
        {'entry_id': f'{CITY_ID}:yer:skatepark-barcelona', 'city_id': CITY_ID, 'slug': 'skatepark-barcelona', 'title': 'Barcelona Skatepark', 'subtitle': 'Parc de Skate de Barcelona', 'summary': 'MACBA meydanı dünyaca ünlü kaykay spotu. Ayrıca Mar Bella\'da resmi skatepark var.', 'keywords': 'skatepark, kaykay, MACBA', 'stages': 'settled', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 120, 'featured': 'Hayır', 'editorial_status': 'Taslak', 'group': 'Spor', 'district': 'Ciutat Vella', 'setting': 'Açık hava', 'location': 'Plaça dels Àngels, 08001 Barcelona', 'latitude': 41.3835, 'longitude': 2.1695, 'visit_status': 'Açık', 'note': 'Ücretsiz. L1/L3 Catalunya.', 'collection': 'Hayır', 'media_key': 'skatepark'},
    ])
    
    # Write remaining places
    for i, p in enumerate(places):
        write_row(ws, last_place_row + i, cm, p)
    
    print(f"Mekânlar (aşama 3): {len(places)} kayıt yazıldı")
    total_places = last_place_row - 8 + len(places)
    print(f"Toplam mekân: {total_places}")
    
    # ============================================================
    # ROTALAR (12)
    # ============================================================
    ws_route = wb['Rotalar']
    cm_route = get_header_map(ws_route)
    
    routes = [
        {'route_id': f'{CITY_ID}:rota:gotik-born', 'city_id': CITY_ID, 'title': 'Gotik Mahalle ve El Born Yürüyüşü', 'tag': '3 saat', 'stops': 'Barcelona Katedrali\nPlaça Reial\nEl Born Kültür Merkezi\nSanta Maria del Mar\nPicasso Müzesi', 'stop_entry_ids': f'{CITY_ID}:yer:catedral;{CITY_ID}:yer:gotik;{CITY_ID}:yer:born-centre;{CITY_ID}:yer:santa-maria-del-mar;{CITY_ID}:yer:picasso', 'entry_id': f'{CITY_ID}:yer:catedral', 'note': 'Ortaçağ Barcelona keşfi. L4 Jaume I\'den başlayın.', 'reviewed_on': TODAY, 'source_ids': s('bcn-neighborhoods'), 'order': 1, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:gaudi-modernisme', 'city_id': CITY_ID, 'title': 'Gaudí ve Modernisme Turu', 'tag': '4 saat', 'stops': 'Casa Vicens\nPark Güell\nSagrada Família\nCasa Batlló\nCasa Milà (La Pedrera)', 'stop_entry_ids': f'{CITY_ID}:yer:casa-vicens;{CITY_ID}:yer:park-guell;{CITY_ID}:yer:sagrada-familia;{CITY_ID}:yer:casa-batllo;{CITY_ID}:yer:casa-mila', 'entry_id': f'{CITY_ID}:yer:casa-vicens', 'note': 'Modernist başyapıtlar. L3 ile ulaşım.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 2, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:montjuic', 'city_id': CITY_ID, 'title': 'Montjuïc Kültür ve Manzara Turu', 'tag': '5 saat', 'stops': 'Teleferik ile çıkış\nMNAC\nFundació Joan Miró\nOlimpiyat Stadyumu\nSihirli Çeşme (akşam)', 'stop_entry_ids': f'{CITY_ID}:yer:montjuic-cable-car;{CITY_ID}:yer:mnac;{CITY_ID}:yer:miro;{CITY_ID}:yer:olimpic-stadium;{CITY_ID}:yer:montjuic-park', 'entry_id': f'{CITY_ID}:yer:montjuic-cable-car', 'note': 'L1 Espanya\'dan teleferik. Akşam çeşme gösterisi.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 3, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:plaj-guney', 'city_id': CITY_ID, 'title': 'Barcelona Plaj ve Sahil Turu', 'tag': '4 saat', 'stops': 'Barceloneta Plajı\nBogatell Plajı\nMar Bella Plajı\nFòrum Parkı', 'stop_entry_ids': f'{CITY_ID}:yer:barceloneta-beach;{CITY_ID}:yer:bogatell-beach;{CITY_ID}:yer:mar-bella-beach;{CITY_ID}:yer:forum-parc', 'entry_id': f'{CITY_ID}:yer:barceloneta-beach', 'note': 'L4 Barceloneta\'dan başlayın. Yaz aylarında yüzme.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 4, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:gracia-park', 'city_id': CITY_ID, 'title': 'Gràcia ve Park Güell Keşfi', 'tag': '3 saat', 'stops': 'Gràcia Pazarı\nVila de Gràcia meydanları\nPark Güell\nCasa Vicens', 'stop_entry_ids': f'{CITY_ID}:yer:gracia-market;{CITY_ID}:mahalle:gracia;{CITY_ID}:yer:park-guell;{CITY_ID}:yer:casa-vicens', 'entry_id': f'{CITY_ID}:yer:gracia-market', 'note': 'L3 Fontana\'dan başlayın. Yerel atmosfer.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 5, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:tapas-gastronomi', 'city_id': CITY_ID, 'title': 'Tapas ve Gastronomi Turu', 'tag': '3 saat', 'stops': 'La Boqueria Pazarı\nEl Xampanyet (cava)\nCal Xim (Gràcia tapas)\nCan Culleretes (en eski)', 'stop_entry_ids': f'{CITY_ID}:yer:boqueria;{CITY_ID}:yer:el-xampanyet;{CITY_ID}:yer:cal-xim;{CITY_ID}:yer:can-culleretes', 'entry_id': f'{CITY_ID}:yer:boqueria', 'note': 'L3 Liceu\'den başlayın. Aç karnına gelin!', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 6, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:poblenou-22a', 'city_id': CITY_ID, 'title': 'Poblenou ve 22@ Teknoloji Turu', 'tag': '3 saat', 'stops': 'Torre Glòries\nHangar Sanat Merkezi\nBogatell Plajı\nFòrum Parkı', 'stop_entry_ids': f'{CITY_ID}:yer:torre-agbar;{CITY_ID}:yer:hangar;{CITY_ID}:yer:bogatell-beach;{CITY_ID}:yer:forum-parc', 'entry_id': f'{CITY_ID}:yer:torre-agbar', 'note': 'L1 Glòries\'ten başlayın. Modern Barcelona.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 7, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:raval-kultur', 'city_id': CITY_ID, 'title': 'El Raval Kültür ve Sokak Sanatı', 'tag': '3 saat', 'stops': 'MACBA\nCCCB\nPalau Güell\nLa Boqueria', 'stop_entry_ids': f'{CITY_ID}:yer:macba;{CITY_ID}:yer:macba-placa;{CITY_ID}:yer:palau-guell;{CITY_ID}:yer:boqueria', 'entry_id': f'{CITY_ID}:yer:macba', 'note': 'L3 Liceu\'den başlayın. Çok kültürlü.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 8, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:olimpiyat', 'city_id': CITY_ID, 'title': '1992 Olimpiyat Mekanları Turu', 'tag': '4 saat', 'stops': 'Olimpiyat Stadyumu\nPalau Sant Jordi\nPiscines Bernat Picornell\nVelódrom d\'Horta', 'stop_entry_ids': f'{CITY_ID}:yer:olimpic-stadium;{CITY_ID}:yer:palau-sant-jordi;{CITY_ID}:yer:piscina-municipal;{CITY_ID}:yer:velodrom', 'entry_id': f'{CITY_ID}:yer:olimpic-stadium', 'note': 'Montjuïc ve Horta. L1 Espanya + L3 Montbau.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 9, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:aile-cocuk', 'city_id': CITY_ID, 'title': 'Aile ve Çocuk Turu', 'tag': '5 saat', 'stops': 'Barcelona Hayvanat Bahçesi\nCosmoCaixa\nTibidabo Lunapark', 'stop_entry_ids': f'{CITY_ID}:yer:zoo;{CITY_ID}:yer:cosmocaixa;{CITY_ID}:yer:tibidabo', 'entry_id': f'{CITY_ID}:yer:zoo', 'note': 'L4 Ciutadella\'dan başlayın. FGC ile Tibidabo.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 10, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:gece-hayati', 'city_id': CITY_ID, 'title': 'Gece Hayatı ve Müzik Turu', 'tag': '4 saat (gece)', 'stops': 'Jamboree (caz)\nSala Apolo (konser)\nRazzmatazz (büyük mekan)', 'stop_entry_ids': f'{CITY_ID}:yer:jamboree;{CITY_ID}:yer:apolo;{CITY_ID}:yer:razzmatazz', 'entry_id': f'{CITY_ID}:yer:jamboree', 'note': 'L3 Liceu\'den başlayın. Biletleri önceden alın.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 11, 'editorial_status': 'Taslak'},
        
        {'route_id': f'{CITY_ID}:rota:ucuz-ucretsiz', 'city_id': CITY_ID, 'title': 'Ücretsiz ve Uygun Fiyatlı Keşif', 'tag': '5 saat', 'stops': 'Ciutadella Parkı\nArc de Triomf\nMACBA Meydanı\nMontjuïc (yürüyüş)', 'stop_entry_ids': f'{CITY_ID}:yer:ciutadella-park;{CITY_ID}:yer:arc-triomf;{CITY_ID}:yer:macba-placa;{CITY_ID}:yer:montjuic-park', 'entry_id': f'{CITY_ID}:yer:ciutadella-park', 'note': 'L4 Ciutadella\'dan başlayın. Bütçe dostu.', 'reviewed_on': TODAY, 'source_ids': s('bcn-cat-en'), 'order': 12, 'editorial_status': 'Taslak'},
    ]
    
    for i, r in enumerate(routes):
        write_row(ws_route, 8 + i, cm_route, r)
    
    print(f"Rotalar: {len(routes)} kayıt yazıldı")
    
    # ============================================================
    # SÖZLÜK (60)
    # ============================================================
    ws_gloss = wb['Sözlük']
    cm_gloss = get_header_map(ws_gloss)
    
    glossary = [
        {'term_id': f'{CITY_ID}:sozluk:empadronamiento', 'city_id': CITY_ID, 'term': 'Empadronamiento', 'definition': 'Belediye nüfus kütüğüne kayıt. Tüm yerleşikler için zorunlu. Padrón olarak da bilinir.', 'source_ids': s('bcn-empadronamiento'), 'reviewed_on': TODAY, 'order': 1, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:nie', 'city_id': CITY_ID, 'term': 'NIE', 'definition': 'Número de Identidad de Extranjero. Yabancılar için kimlik numarası. Tüm resmî işlemlerde gerekir.', 'source_ids': s('exteriores-nie'), 'reviewed_on': TODAY, 'order': 2, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tie', 'city_id': CITY_ID, 'term': 'TIE', 'definition': 'Tarjeta de Identidad de Extranjero. AB dışı vatandaşların fiziksel kimlik kartı.', 'source_ids': s('policia-tie'), 'reviewed_on': TODAY, 'order': 3, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:catsalut', 'city_id': CITY_ID, 'term': 'CatSalut', 'definition': 'Katalonya sağlık hizmeti. Kamu sağlık sistemi. TSI kartı ile erişim.', 'source_ids': s('catsalut-tsi'), 'reviewed_on': TODAY, 'order': 4, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tsi', 'city_id': CITY_ID, 'term': 'TSI', 'definition': 'Targeta Sanitària Individual. Bireysel sağlık kartı. Kamu sağlık hizmetine erişim sağlar.', 'source_ids': s('catsalut-tsi'), 'reviewed_on': TODAY, 'order': 5, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:cap', 'city_id': CITY_ID, 'term': 'CAP', 'definition': 'Centre d\'Atenció Primària. Birincil sağlık merkezi. Aile hekimi ve pediatrist.', 'source_ids': s('bcn-public-health-system'), 'reviewed_on': TODAY, 'order': 6, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tcasual', 'city_id': CITY_ID, 'term': 'T-Casual', 'definition': '10 yolculukluk toplu taşıma bileti. 13€. Metro, otobüs, tramvay için geçerli.', 'source_ids': s('tmb-fares'), 'reviewed_on': TODAY, 'order': 7, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tusual', 'city_id': CITY_ID, 'term': 'T-Usual', 'definition': 'Aylık sınırsız toplu taşıma abonmanı. 22,80€. Havalimanı metrosu dahil.', 'source_ids': s('tmb-fares'), 'reviewed_on': TODAY, 'order': 8, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:autonomo', 'city_id': CITY_ID, 'term': 'Autónomo', 'definition': 'Serbest çalışan, kendi hesabına çalışan. Sosyal güvenlik primi öder.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 9, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:irpf', 'city_id': CITY_ID, 'term': 'IRPF', 'definition': 'Impuesto sobre la Renta de las Personas Físicas. Gelir vergisi. Yıllık beyan gerekir.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 10, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:iva', 'city_id': CITY_ID, 'term': 'IVA', 'definition': 'Impuesto sobre el Valor Añadido. Katma değer vergisi (KDV). Genel oran %21.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 11, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:seguridad-social', 'city_id': CITY_ID, 'term': 'Seguridad Social', 'definition': 'Sosyal güvenlik sistemi. Sağlık, emeklilik ve işsizlik sigortası.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 12, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:contrato-indefinido', 'city_id': CITY_ID, 'term': 'Contrato indefinido', 'definition': 'Süresiz iş sözleşmesi. En güçlü işçi koruması. Deneme süresi olabilir.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 13, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:contrato-temporal', 'city_id': CITY_ID, 'term': 'Contrato temporal', 'definition': 'Belirli süreli iş sözleşmesi. Üst üste 2 kez yenilenirse süresiz sayılır.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 14, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:fianza', 'city_id': CITY_ID, 'term': 'Fianza', 'definition': 'Kira depozitosu. Yasal olarak en fazla 2 aylık kira. Çıkışta iade edilir.', 'source_ids': s('bcn-rent-index'), 'reviewed_on': TODAY, 'order': 15, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:la-morce', 'city_id': CITY_ID, 'term': 'La Mercè', 'definition': '24 Eylül. Barcelona\'nın en büyük festivali. Sokak etkinlikleri, konserler, havai fişek.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 16, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:diada', 'city_id': CITY_ID, 'term': 'Diada', 'definition': '11 Eylül. Katalonya Ulusal Günü. 1714 savaşının anısı. Bağımsızlık mitingleri.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 17, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:sagrada-familia', 'city_id': CITY_ID, 'term': 'Sagrada Família', 'definition': 'Gaudí\'nin başyapıtı. 1882\'den beri inşa ediliyor. Barcelona\'nın simgesi.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 18, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:modernisme', 'city_id': CITY_ID, 'term': 'Modernisme', 'definition': 'Katalan Art Nouveau. 19-20. yüzyıl. Gaudí, Domènech i Montaner. Şehrin mimari kimliği.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 19, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:rambla', 'city_id': CITY_ID, 'term': 'La Rambla', 'definition': 'Barcelona\'nın en ünlü caddesi. Plaça Catalunya\'dan limana. Turistik, kalabalık.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 20, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:barri-gotic', 'city_id': CITY_ID, 'term': 'Barri Gòtic', 'definition': 'Gotik Mahalle. Barcelona\'nın en eski kısmı. Ortaçağ sokakları, Katedral.', 'source_ids': s('bcn-neighborhoods'), 'reviewed_on': TODAY, 'order': 21, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:eixample', 'city_id': CITY_ID, 'term': 'Eixample', 'definition': '19. yüzyıl genişleme bölgesi. Cerdà\'nın grid planı. Modernist binalar.', 'source_ids': s('barcelona-urbana-districts'), 'reviewed_on': TODAY, 'order': 22, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:gracia', 'city_id': CITY_ID, 'term': 'Gràcia', 'definition': 'Eski bağımsız köy. Dar sokaklar, meydanlar. Bohem atmosfer, Park Güell.', 'source_ids': s('bcn-neighborhoods'), 'reviewed_on': TODAY, 'order': 23, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:poblenou', 'city_id': CITY_ID, 'term': 'Poblenou', 'definition': 'Eski sanayi mahallesi. 22@ teknoloji bölgesi. Hipster kafeler, plaj.', 'source_ids': s('barcelona-urbana-districts'), 'reviewed_on': TODAY, 'order': 24, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:montjuic', 'city_id': CITY_ID, 'term': 'Montjuïc', 'definition': 'Şehir tepesi. Olimpiyat tesisleri, müzeler, parklar. Teleferik ile çıkılır.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 25, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tibidabo', 'city_id': CITY_ID, 'term': 'Tibidabo', 'definition': 'Collserola\'nın en yüksek noktası. Lunapark, kilise, şehir manzarası.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 26, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:ciutadella', 'city_id': CITY_ID, 'term': 'Ciutadella', 'definition': 'Barcelona\'nın en büyük merkezi parkı. Gölet, hayvanat bahçesi, parlamento.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 27, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:boqueria', 'city_id': CITY_ID, 'term': 'La Boqueria', 'definition': 'La Rambla\'da ünlü gıda pazarı. Taze meyve, deniz ürünleri, tapas.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 28, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:camp-nou', 'city_id': CITY_ID, 'term': 'Camp Nou', 'definition': 'FC Barcelona stadyumu. 105.000 kapasite. Maç ve tur.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 29, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:barca', 'city_id': CITY_ID, 'term': 'Barça', 'definition': 'FC Barcelona lakabı. Futbol kulübü. Katalan kimliğinin sembolü.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 30, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:bicing', 'city_id': CITY_ID, 'term': 'Bicing', 'definition': 'Belediye bisiklet paylaşım sistemi. Yıllık abonman. 500+ istasyon.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 31, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:area', 'city_id': CITY_ID, 'term': 'ÀREA', 'definition': 'Sokak park sistemi. Mavi (ücretli) ve yeşil (sakinlere öncelikli) bölgeler.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 32, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:castellers', 'city_id': CITY_ID, 'term': 'Castellers', 'definition': 'İnsan kulesi geleneği. Katalan folkloru. Festelerde gösterilir.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 33, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:sardana', 'city_id': CITY_ID, 'term': 'Sardana', 'definition': 'Katalan halk dansı. Daire şeklinde, el ele. Geleneksel müzikle.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 34, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:cava', 'city_id': CITY_ID, 'term': 'Cava', 'definition': 'Katalan köpüklü şarap. Şampanya yöntemi. Penedès bölgesinde üretilir.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 35, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:vermouth', 'city_id': CITY_ID, 'term': 'Vermut', 'definition': 'Aperitif içecek. Pazar öğle yemeği öncesi geleneği. "La hora del vermut".', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 36, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tapas', 'city_id': CITY_ID, 'term': 'Tapas', 'definition': 'Küçük porsiyon yemekler. Ayakta, barda. Katalan: "Pintxos" (Bask etkisi).', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 37, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:paella', 'city_id': CITY_ID, 'term': 'Paella', 'definition': 'Pirinç yemeği. Valencia kökenli ancak Barcelona\'da deniz ürünleri ile yapılır.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 38, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:fira', 'city_id': CITY_ID, 'term': 'Fira', 'definition': 'Fuar. Fira Barcelona büyük uluslararası fuarlar düzenler (MWC vb.).', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 39, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:mwc', 'city_id': CITY_ID, 'term': 'MWC', 'definition': 'Mobile World Congress. Dünyanın en büyük mobil teknoloji fuarı. Barcelona\'da.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 40, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:22a', 'city_id': CITY_ID, 'term': '22@', 'definition': 'Poblenou\'daki teknoloji ve inovasyon bölgesi. Eski fabrikalar dönüştürüldü.', 'source_ids': s('barcelona-urbana-districts'), 'reviewed_on': TODAY, 'order': 41, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:cerda', 'city_id': CITY_ID, 'term': 'Cerdà', 'definition': 'Ildefons Cerdà. Eixample\'ın grid planını tasarlayan şehir plancısı (1859).', 'source_ids': s('barcelona-urbana-districts'), 'reviewed_on': TODAY, 'order': 42, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:gaudi', 'city_id': CITY_ID, 'term': 'Gaudí', 'definition': 'Antoni Gaudí (1852-1926). Katalan mimar. Modernisme\'in en büyük temsilcisi.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 43, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:miro', 'city_id': CITY_ID, 'term': 'Miró', 'definition': 'Joan Miró (1893-1983). Katalan sürrealist ressam. Montjuïc\'te vakfı var.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 44, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:tapies', 'city_id': CITY_ID, 'term': 'Tàpies', 'definition': 'Antoni Tàpies (1923-2012). Katalan çağdaş sanatçı. Eixample\'de vakfı var.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 45, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:picasso-bcn', 'city_id': CITY_ID, 'term': 'Picasso (Barcelona)', 'definition': 'Pablo Picasso gençliğini Barcelona\'da geçirdi. El Born\'da müzesi var.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 46, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:domenech', 'city_id': CITY_ID, 'term': 'Domènech i Montaner', 'definition': 'Lluís Domènech i Montaner. Modernist mimar. Palau de la Música, Sant Pau.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 47, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:palau-musica', 'city_id': CITY_ID, 'term': 'Palau de la Música', 'definition': 'Katalan Müzik Sarayı. Domènech i Montaner tasarımı. UNESCO Dünya Mirası.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 48, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:sant-pau-recinte', 'city_id': CITY_ID, 'term': 'Sant Pau Recinte Modernista', 'definition': 'Eski hastane, şimdi kültür merkezi. Modernist başyapıt. UNESCO Dünya Mirası.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 49, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:liceu-opera', 'city_id': CITY_ID, 'term': 'Liceu', 'definition': 'Gran Teatre del Liceu. Avrupa\'nın en büyük opera binalarından. La Rambla\'da.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 50, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:mnac-muze', 'city_id': CITY_ID, 'term': 'MNAC', 'definition': 'Museu Nacional d\'Art de Catalunya. Montjuïc\'te. Romanesk sanat koleksiyonu.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 51, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:macba-muze', 'city_id': CITY_ID, 'term': 'MACBA', 'definition': 'Museu d\'Art Contemporani de Barcelona. El Raval\'da. Richard Meier tasarımı.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 52, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:cosmocaixa-muze', 'city_id': CITY_ID, 'term': 'CosmoCaixa', 'definition': 'Bilim müzesi. İnteraktif sergiler, planetarium. Tibidabo eteğinde.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 53, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:barceloneta-plaj', 'city_id': CITY_ID, 'term': 'Barceloneta', 'definition': 'Eski balıkçı mahallesi ve plaj. En merkezi plaj. Yazın çok kalabalık.', 'source_ids': s('bcn-neighborhoods'), 'reviewed_on': TODAY, 'order': 54, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:bogatell-plaj', 'city_id': CITY_ID, 'term': 'Bogatell', 'definition': 'Daha sakin plaj. Yerel halk tercih eder. Spor alanları.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 55, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:mar-bella-plaj', 'city_id': CITY_ID, 'term': 'Mar Bella', 'definition': 'Çıplaklar plajı. LGBTQ+ dostu. Su sporları.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 56, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:collserola-doga', 'city_id': CITY_ID, 'term': 'Collserola', 'definition': 'Barcelona\'yı çevreleyen doğa parkı. Yürüyüş, bisiklet. Tibidabo tepesi.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 57, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:labirint-horta', 'city_id': CITY_ID, 'term': 'Laberint d\'Horta', 'definition': 'Horta\'daki neoklasik bahçe. Gerçek çit labirenti. Romantik köşk.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 58, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:font-magica', 'city_id': CITY_ID, 'term': 'Font Màgica', 'definition': 'Sihirli Çeşme. Montjuïc\'te. Müzik ve ışık gösterisi. Cmt akşam ücretsiz.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 59, 'editorial_status': 'Taslak'},
        {'term_id': f'{CITY_ID}:sozluk:torre-glories', 'city_id': CITY_ID, 'term': 'Torre Glòries', 'definition': 'Eski Torre Agbar. Jean Nouvel tasarımı. LED ışık gösterisi. Glòries\'te.', 'source_ids': s('bcn-cat-en'), 'reviewed_on': TODAY, 'order': 60, 'editorial_status': 'Taslak'},
    ]
    
    for i, g in enumerate(glossary):
        write_row(ws_gloss, 8 + i, cm_gloss, g)
    
    print(f"Sözlük: {len(glossary)} kayıt yazıldı")
    
    save_wb(wb)
    print(f"\nAşama 7 tamamlandı.")
    print(f"Toplam mekân: {total_places}")
    print(f"Toplam mahalle: {len(neighborhoods)}")
    print(f"Toplam rota: {len(routes)}")
    print(f"Toplam sözlük: {len(glossary)}")

if __name__ == '__main__':
    main()
