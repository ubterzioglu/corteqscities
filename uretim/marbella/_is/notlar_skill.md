# Skill/araç notları — Marbella (kural 14)
- 2026-10-28 | intake | Oturum Linux bulut kabuğunda (PowerShell yok; ROOT=/home/user/corteqscities, PY=/home/user/venv/bin/python). ortam.ps1 yerine _is/ortam.sh yazıldı; komutlar aynı, yollar POSIX. | SKILL.md'ye bulut/Linux karşılığı (ortam.sh, `--bbox=$BBOX`) eklenmeli.
- 2026-10-28 | intake | Wikidata wbsearchentities API'si bu ağdan 429 verdi; QID SPARQL ile bulundu (Q484799). | QID adımı için SPARQL sorgusu skill'e yazılabilir.
- 2026-10-28 | intake | Atınç şablonunda yine büyük harf delivery_id (3. şehir). | Atınç'a toplu bildirim.
- 2026-10-28 | sources | fetch_snapshot/add_sources hcs.es (Hospital Costa del Sol) sayfalarını gzip baytı olarak kaydediyor (Content-Encoding açılmıyor); metin bozuk, kanıt aranamıyor. | fetch_snapshot'a gzip/deflate çözme eklenmeli.
- 2026-11-02 | places | Bulut oturumunda Wikimedia (Commons API ve upload.wikimedia.org) 429 verdi, Openverse zaman aşımı; photos fazı buradan yapılamadı. | Foto adımları yerel makinede ya da başka çıkış adresinde; commons_search'ün >30 sn Retry-After'da durması uzun beklemede tekrarlanacak biçimde belgelenmeli.
