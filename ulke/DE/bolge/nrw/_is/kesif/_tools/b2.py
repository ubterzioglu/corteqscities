import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from addlib import add

KIBIZ = "https://recht.nrw.de/lrgv/gesetz/01082026-gesetz-zur-fruehen-bildung-und-foerderung-von-kindern-kinderbildungsgesetz/"
SCHULG = "https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/"

add('aile', [
 {"url": KIBIZ,
  "must_contain": ["können Teilnahme- oder Kostenbeiträge (Elternbeiträge) nach § 90 Absatz 1 des Achten Buches Sozialgesetzbuch ausschließlich vom Jugendamt festgesetzt werden",
                   "ist ab Beginn des im selben Kalenderjahr beginnenden Kindergartenjahres bis zur Einschulung beitragsfrei",
                   "hat es eine soziale Staffelung vorzusehen und die wirtschaftliche Leistungsfähigkeit der Eltern sowie die Betreuungszeit zu berücksichtigen"],
  "title": "Gesetz zur frühen Bildung und Förderung von Kindern (Kinderbildungsgesetz - KiBiz)", "publisher": "Land NRW, recht.nrw.de (Ministerium des Innern)", "lang": "de",
  "why": "Kart 2: § 50 (beitragsfrei ab Kindergartenjahr bis Einschulung fuer Kinder, die bis 30.09. 4 Jahre alt werden) und § 51 (Elternbeitrag nur vom Jugendamt, soziale Staffelung). Fassung gueltig ab 01.08.2026; Seite nennt auch 01.08.2027-Fassung (spaeter).", "cards": [2]},
 {"url": SCHULG,
  "must_contain": ["Die Schulpflicht beginnt für Kinder, die bis zum Beginn des 30. September das sechste Lebensjahr vollendet haben, am 1. August desselben Kalenderjahres",
                   "Die Grundschule umfasst die Klassen 1 bis 4",
                   "Die Sekundarstufe I umfasst die Hauptschule, die Realschule, die Sekundarschule sowie die Gesamtschule und das Gymnasium bis Klasse 10",
                   "Schulpflichtig ist, wer in Nordrhein-Westfalen seinen Wohnsitz oder seinen gewöhnlichen Aufenthalt"],
  "title": "Schulgesetz für das Land Nordrhein-Westfalen (Schulgesetz NRW - SchulG)", "publisher": "Land NRW, recht.nrw.de (Ministerium des Innern)", "lang": "de",
  "why": "Kart 3 (+saglik 1): § 34 Schulpflicht (Wohnsitz/gewoehnlicher Aufenthalt), § 35 Beginn 30.09./1.8., § 10-11 Grundschule Kl. 1-4 und Schulformen Sek I; § 54 Schulgesundheitspflege. Fassung 01.08.2026.", "cards": [3]},
 {"url": "https://bass.schule.nrw/18425.htm",
  "must_contain": ["Neu zugewanderte Schülerinnen und Schüler werden nach ihrer Aufnahme an einer Schule entweder in innerer Differenzierung, in teilweise oder in vollständig äußerer Differenzierung",
                   "Die Aufnahme der neu zugewanderten Schülerinnen und Schüler an eine Schule erfolgt gemäß § 46 SchulG"],
  "title": "13-63 Nr. 3 Integration und Deutschförderung neu zugewanderter Schülerinnen und Schüler", "publisher": "Ministerium für Schule und Bildung NRW (BASS)", "lang": "de",
  "why": "Kart 3: Aufnahme neu zugewanderter Kinder, Differenzierungsformen, Zuordnung zum Bildungsgang meist innerhalb von 2 Jahren (B1). BASS-Stand 2026/2027.", "cards": [3]},
 {"url": "https://bass.schule.nrw/16253.htm",
  "must_contain": ["Herkunftssprachlicher Unterricht wird in der Primarstufe angeboten, wenn eine mindestens 15 Schülerinnen und Schüler umfassende Lerngruppe dauerhaft ermöglicht werden kann",
                   "Die Anmeldung verpflichtet zur regelmäßigen Teilnahme. Eine Abmeldung ist nur zum Schuljahresende für das kommende Schuljahr möglich",
                   "Die Leistung aus dem Herkunftssprachlichen Unterricht ist nicht versetzungsrelevant"],
  "title": "13-61 Nr. 2 Herkunftssprachlicher Unterricht", "publisher": "Ministerium für Schule und Bildung NRW (BASS)", "lang": "de",
  "why": "Kart 4: HSU Teilnahme (min. 15 Primarstufe / 18 Sek I), Anmeldung verbindlich, Zeugnisvermerk/Note, Sprachpruefung. RdErl. 20.09.2021; Seite nennt keine einzelne Sprache.", "cards": [4]},
 {"url": "https://www.schulministerium.nrw/tuerkisch-schulen-nordrhein-westfalen",
  "must_contain": ["Der herkunftssprachliche Türkischunterricht wird in NRW von der Primarstufe bis zum Ende der Sekundarstufe I angeboten"],
  "title": "Türkisch an Schulen in Nordrhein-Westfalen", "publisher": "Ministerium für Schule und Bildung NRW", "lang": "de",
  "why": "Kart 4: Tuerkisch als HSU in NRW ab Primarstufe bis Ende Sek I; Tuerkisch auch als Fremdsprache. Sayfa tarihsiz.", "cards": [4]},
])

add('saglik', [
 {"url": "https://recht.nrw.de/lrgv/rechtsverordnung/02072025-verordnung-zur-datenmeldung-der-teilnahme/",
  "must_contain": ["Mit dem Verfahren zur Feststellung der Teilnahme an Früherkennungsuntersuchungen bei Kindern (U5 bis U9) soll erreicht werden, dass alle Kinder in Nordrhein-Westfalen an den für sie angebotenen Früherkennungsuntersuchungen teilnehmen",
                   "erinnert die Zentrale Stelle die Personensorgeberechtigten des Kindes",
                   "Landesamt für Gesundheit und Arbeitsschutz Nordrhein-Westfalen"],
  "title": "Verordnung zur Datenmeldung der Teilnahme an Kinderfrüherkennungsuntersuchungen / U-Untersuchungen (UTeilnahmeDatVO)", "publisher": "Land NRW, recht.nrw.de (Ministerium des Innern)", "lang": "de",
  "why": "Kart 1: NRW-Meldeverfahren U5-U9: Aerzte melden an Zentrale Stelle, Erinnerung an Sorgeberechtigte, Jugendamt wird informiert (§ 4). Fassung 02.07.2025; Zentrale Stelle = LAGA NRW.", "cards": [1]},
 {"url": SCHULG,
  "must_contain": ["schulärztliche Untersuchungen, insbesondere Reihenuntersuchungen zur Einschulung, und zahnärztliche Untersuchungen",
                   "Schulgesundheitspflege nehmen die unteren Gesundheitsbehörden in Zusammenarbeit mit der Schule und den Eltern wahr"],
  "title": "Schulgesetz für das Land Nordrhein-Westfalen (Schulgesetz NRW - SchulG)", "publisher": "Land NRW, recht.nrw.de (Ministerium des Innern)", "lang": "de",
  "why": "Kart 1: § 54 Schulgesundheitspflege, Reihenuntersuchungen zur Einschulung durch untere Gesundheitsbehoerde; § 35 amtsaerztliches Gutachten. Fassung 01.08.2026.", "cards": [1]},
])
