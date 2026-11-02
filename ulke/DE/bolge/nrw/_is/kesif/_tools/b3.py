import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from addlib import add

add('saglik', [
 {"url": "https://www.lzg.nrw.de/ges_foerd/kindergesundheit/zentrale-stelle/index.html",
  "must_contain": ["Die Kommune wird dann in eigener Zuständigkeit prüfen und entscheiden, ob sie mit den Eltern/Sorgeberechtigten Kontakt aufnimmt",
                   "In der Bestätigung wird kein Untersuchungsergebnis mitgeteilt"],
  "title": "Zentrale Stelle Gesunde Kindheit", "publisher": "Landesamt für Gesundheit und Arbeitsschutz NRW (LfGA NRW)", "lang": "de",
  "why": "Kart 1: Eltern-Sicht des U5-U9-Meldeverfahrens: Arzt bestaetigt Teilnahme, Erinnerungsschreiben, nach 6 Wochen Info an Kommune; Toleranzgrenzen-Tabelle. Sayfa tarihsiz (LfGA-Name = Nachfolger LZG).", "cards": [1]},
])
