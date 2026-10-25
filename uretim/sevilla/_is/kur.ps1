. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$ErrorActionPreference = 'Continue'
function S($ad) { "### $ad exit=$LASTEXITCODE" }
& $PY $DU\country_apply.py audit-scope $WORK\_is --pack $WORK\_is\ulke_paketi --out $WORK\_is\ulke_denetim_kapsami.json; S audit-scope
& $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX; S merge
& $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket.json | Out-Null; S package_sources
& $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $WORK\_is\ara\ara.xlsx --report $WORK\_is\build.json --tools $TOOLS --partial --overwrite | Select-Object -Last 1; S build
& $PY $TK\text_quality.py $WORK\_is\ara\ara.xlsx --address-standard sen --out $WORK\_is\text_quality.json | Select-Object -Last 1; S text_quality
& $PY $TK\claim_extract.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\claims.jsonl | Select-Object -Last 1; S claim_extract
& $PY $TK\fetch_snapshot.py --xlsx $WORK\_is\ara\ara.xlsx --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache | Select-Object -Last 1; S fetch
& $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --out $WORK\_is\claim_check.json | Select-Object -Last 1; S claim_unit
& $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_number.json | Select-Object -Last 1; S claim_number
& $PY $TK\validate_all.py $WORK\_is\ara\ara.xlsx $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\val_ara.json | Out-Null; S validate
