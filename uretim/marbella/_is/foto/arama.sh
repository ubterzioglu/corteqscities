#!/bin/bash
. /home/user/corteqscities/uretim/marbella/_is/ortam.sh
cd $WORK/_is
for i in 1 2 3 4; do
  $PY $TK/commons_search.py --plan $WORK/_is/foto/venues.jsonl --out $WORK/_is/foto/search.jsonl --cache-dir $WORK/_is/foto/cache --max-requests 1500 --limit 25 --geo-max 5 > foto/commons_search_out.json 2>foto/commons_search_err.txt
  rc=$?; echo "commons_search rc=$rc"; tail -c 600 foto/commons_search_out.json; echo
  grep -q resume_later foto/commons_search_out.json || break
  sleep 60
done
$PY $TK/photo_sources.py --plan $WORK/_is/foto/venues.jsonl --search $WORK/_is/foto/search.jsonl --cache-dir $WORK/_is/foto/cache_alt --min-per-venue 3 --max-requests 400 --sources openverse,smithsonian,europeana > foto/photo_sources_out.json 2>&1; echo "photo_sources rc=$?"; tail -c 800 foto/photo_sources_out.json; echo
$PY $TK/photo_candidates.py from-search $WORK/_is/foto/search.jsonl --out $WORK/_is/foto/candidates.jsonl | tail -c 400
