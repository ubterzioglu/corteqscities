import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from addlib import add

add('gunluk', [
 {"url": "https://recht.nrw.de/lrgv/gesetz/01012000-bekanntmachung-der-neufassung-des-gesetzes-ueber-die-sonn-und-feiertage/",
  "must_contain": ["der Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis)", "der Allerheiligentag (1. November)", "der 2. Weihnachtstag"],
  "title": "Gesetz über die Sonn- und Feiertage (Feiertagsgesetz NW)", "publisher": "Land NRW, recht.nrw.de (Ministerium des Innern)", "lang": "de",
  "why": "Kart 1: NRW'de yasal tatil listesi (md. 2 Abs. 1, Fronleichnam ve Allerheiligen dahil); tarih sayfa degil kural, yillik tarihler hesaplanir. Sayfa tek (2000 tarihli) surum.", "cards": [1]},
 {"url": "https://recht.nrw.de/lrgv/gesetz/30032018-gesetz-zur-regelung-der-ladenoeffnungszeiten-ladenoeffnungsgesetz-loeg-nrw/",
  "must_contain": ["an Werktagen ohne zeitliche Begrenzung geöffnet sein (allgemeine Ladenöffnungszeit)", "An jährlich höchstens acht, nicht unmittelbar aufeinanderfolgenden Sonn- oder Feiertagen dürfen Verkaufsstellen im öffentlichen Interesse ab 13 Uhr bis zur Dauer von fünf Stunden geöffnet sein", "Innerhalb einer Gemeinde dürfen nach Absatz 1 insgesamt nicht mehr als 16 Sonn- und Feiertage je Kalenderjahr freigegeben werden"],
  "title": "Gesetz zur Regelung der Ladenöffnungszeiten (Ladenöffnungsgesetz - LÖG NRW)", "publisher": "Land NRW, recht.nrw.de (Ministerium des Innern)", "lang": "de",
  "why": "Kart 2 (+1): Werktags ohne Zeitgrenze (§ 4), Sonn-/Feiertag-Ausnahmen (§ 5), verkaufsoffene Sonntage max. 8/Jahr, 13 Uhr, 5 Std., Gemeinde max. 16 (§ 6). Fassung vom 30.03.2018 (aktuell lt. Seite).", "cards": [2, 1]},
])

add('aile', [
 {"url": "https://bass.schule.nrw/191.htm",
  "must_contain": ["Die Ferien für die Schuljahre 2026/27 bis 2029/30 werden für die Schulen wie folgt festgelegt", "Montag, 20. Juli 2026", "Samstag, 17. Oktober 2026", "Montag, 10. April 2028"],
  "title": "12-65 Nr. 1 Ordnung der Ferien und Termine für die Aushändigung der Halbjahreszeugnisse", "publisher": "Ministerium für Schule und Bildung NRW (BASS)", "lang": "de",
  "why": "Kart 1: Ferien 2026/27 bis 2029/30 (Sommer, Herbst, Weihnachten, Ostern, Pfingsten) ve beweglicher Ferientage; RdErl. 19.05.2022, Tabellen 2026/27-2029/30.", "cards": [1]},
])
