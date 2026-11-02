#!/bin/bash
# KUR bloğu (SKILL.md): birleştir → kur → kapılar
. /home/user/corteqscities/uretim/marbella/_is/ortam.sh
cd $WORK/_is
s(){ echo "== $1"; }
s merge;   $PY $TK/merge_package.py $WORK/_is --city-id $CITY --bbox=$BBOX | tail -c 1500; echo
s pkgsrc;  $PY $TK/package_sources.py $WORK/_is $PKG --out $WORK/_is/kaynak_paket.json | tail -c 400; echo
s build;   $PY $TK/build_xlsx.py --template $WORK/_is/sablon.xlsx --data-dir $WORK/_is/data --out $WORK/_is/ara/ara.xlsx --report $WORK/_is/build.json --tools $TOOLS --partial --overwrite | tail -c 600; echo
s textq;   $PY $TK/text_quality.py $WORK/_is/ara/ara.xlsx --address-standard sen --out $WORK/_is/text_quality.json | tail -c 800; echo
s warn;    $PY $TK/preview_checks.py warning-scan --xlsx $WORK/_is/ara/ara.xlsx --out $WORK/_is/uyari_tarama.json | tail -c 400; echo
s tutar;   $PY $TK/kart_tutarlilik.py $WORK/_is/ara/ara.xlsx --out $WORK/_is/tutarlilik.json | tail -c 300; echo
s extract; $PY $TK/claim_extract.py $WORK/_is/ara/ara.xlsx --out $WORK/_is/claims.jsonl | tail -c 300; echo
s snap;    $PY $TK/fetch_snapshot.py --xlsx $WORK/_is/ara/ara.xlsx --out-dir $WORK/_is/snap --cache-dir $WORK/_is/cache | tail -c 400; echo
s ccheck;  $PY $TK/claim_check.py --claims $WORK/_is/claims.jsonl --snapshots $WORK/_is/snap --out $WORK/_is/claim_check.json | tail -c 400; echo
s ccheckn; $PY $TK/claim_check.py --claims $WORK/_is/claims.jsonl --snapshots $WORK/_is/snap --mode number --out $WORK/_is/claim_check_number.json | tail -c 400; echo
s valid;   $PY $TK/validate_all.py $WORK/_is/ara/ara.xlsx $PKG --tools $TOOLS --mode audit --new-content --out $WORK/_is/val_ara.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'structure':d['structure'],'media':d['media'],'classes':[(c['class'],c['count']) for c in d['error_classes']][:20]},ensure_ascii=False))"
