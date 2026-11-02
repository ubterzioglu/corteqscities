# Almanya bölge (eyalet) paketleri — klasör eşlemesi

Şehir skill'i bölge paketini `ulke\DE\bolge\<bölge_slug>\pack.json` diye arar. Eyalet adı ile klasör adı aynı değil; bu tablo geçerlidir.

| Eyalet (Land) | Klasör | Durum | Şehirler (Drive kataloğu) |
|---|---|---|---|
| Nordrhein-Westfalen | `nrw` | v1, 02.11.2026, 14 kart | Aachen, Bielefeld, Bochum, Bonn, Dortmund, Duisburg, Düsseldorf, Essen, Köln |
| Baden-Württemberg | — (sırada; NRW'nin ilk şehrinden sonra) | yok | Freiburg, Heidelberg, Heilbronn, Karlsruhe, Mannheim, Stuttgart, Ulm |
| Diğerleri | — | yok | — |

Birleşik paket: `pack_merge.py --pack ROOT\ulke\DE --pack ROOT\ulke\DE\bolge\nrw --out $WORK\_is\ulke_paketi` (02.11.2026'da denendi: 127 kart, 0 çakışma).
