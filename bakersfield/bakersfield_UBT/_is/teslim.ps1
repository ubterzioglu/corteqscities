. 'C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\ortam.ps1'
function Step($name, [scriptblock]$cmd) { $out = & $cmd 2>&1 | Out-String; $code = $LASTEXITCODE; $last = ($out.Trim() -split "`n" | Where-Object { $_.Trim().StartsWith('{') } | Select-Object -Last 1); Write-Host "### $name exit=$code"; Write-Host $last; return $code }
$null = Step 'merge' { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
$null = Step 'package_sources' { & $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket_final.json }
$null = Step 'build_xlsx' { & $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $EXCEL --report $WORK\_is\build_final.json --tools $TOOLS --overwrite }
$null = Step 'validate_all' { & $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\validation.json }
$null = Step 'text_quality' { & $PY $TK\text_quality.py $EXCEL --address-standard sen --out $WORK\_is\text_quality_final.json }
$null = Step 'claim_extract' { & $PY $TK\claim_extract.py $EXCEL --out $WORK\_is\claims_final.jsonl }
$null = Step 'fetch_snapshot' { & $PY $TK\fetch_snapshot.py --xlsx $EXCEL --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache }
$null = Step 'claim_check_number' { & $PY $TK\claim_check.py --claims $WORK\_is\claims_final.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_final.json }
$null = Step 'url_check' { & $PY $TK\url_check.py $EXCEL --cache-dir $WORK\_is\cache --out $WORK\_is\url_check_final.json --retry-transient }
Write-Host "### BITTI"
