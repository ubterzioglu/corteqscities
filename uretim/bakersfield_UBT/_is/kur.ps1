. 'C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\ortam.ps1'
$ozet = [ordered]@{}
function Step($name, [scriptblock]$cmd) {
  $out = & $cmd 2>&1 | Out-String
  $code = $LASTEXITCODE
  $last = ($out.Trim() -split "`n" | Where-Object { $_.Trim().StartsWith('{') } | Select-Object -Last 1)
  Write-Host "### $name exit=$code"
  Write-Host $last
  $script:ozet[$name] = $code
  return $code
}
$c = Step 'merge_package' { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
if ($c -ge 2) { throw 'merge_package cikis 2' }
$c = Step 'package_sources' { & $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket.json }
if ($c -ge 2) { throw 'package_sources cikis 2' }
$c = Step 'build_xlsx' { & $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $WORK\_is\ara\ara.xlsx --report $WORK\_is\build.json --tools $TOOLS --partial --overwrite }
if ($c -ge 2) { throw 'build_xlsx cikis 2' }
$c = Step 'text_quality' { & $PY $TK\text_quality.py $WORK\_is\ara\ara.xlsx --address-standard sen --out $WORK\_is\text_quality.json }
$c = Step 'claim_extract' { & $PY $TK\claim_extract.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\claims.jsonl }
$c = Step 'fetch_snapshot' { & $PY $TK\fetch_snapshot.py --xlsx $WORK\_is\ara\ara.xlsx --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache }
$c = Step 'claim_check_unit' { & $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --out $WORK\_is\claim_check.json }
$c = Step 'claim_check_number' { & $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_number.json }
$c = Step 'validate_all' { & $PY $TK\validate_all.py $WORK\_is\ara\ara.xlsx $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\val_ara.json }
Write-Host ("### OZET " + ($ozet | ConvertTo-Json -Compress))
