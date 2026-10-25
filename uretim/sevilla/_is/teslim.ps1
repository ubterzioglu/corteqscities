. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
function S($ad) { "### $ad exit=$LASTEXITCODE" }
& $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX | Select-Object -Last 1; S merge
& $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket_final.json | Select-Object -Last 1; S package_sources
& $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $EXCEL --report $WORK\_is\build_final.json --tools $TOOLS --overwrite | Select-Object -Last 1; S build
& $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\validation.json | Out-Null; S validate
& $PY $TK\text_quality.py $EXCEL --address-standard sen --out $WORK\_is\text_quality_final.json | Select-Object -Last 1; S text_quality
& $PY $TK\claim_extract.py $EXCEL --out $WORK\_is\claims_final.jsonl | Select-Object -Last 1; S claim_extract
& $PY $TK\fetch_snapshot.py --xlsx $EXCEL --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache | Select-Object -Last 1; S fetch
& $PY $TK\claim_check.py --claims $WORK\_is\claims_final.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_final.json | Select-Object -Last 1; S claim_number
& $PY $TK\url_check.py $EXCEL --cache-dir $WORK\_is\cache --out $WORK\_is\url_check_final.json --retry-transient | Select-Object -Last 1; S url_check
