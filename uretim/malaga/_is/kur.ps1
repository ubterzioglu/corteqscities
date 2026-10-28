. C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\ortam.ps1
$ErrorActionPreference = 'Continue'
function Adim($ad, [scriptblock]$komut) {
  $t0 = Get-Date
  $cikti = & $komut 2>&1 | Out-String
  $kod = $LASTEXITCODE
  $son = ($cikti -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
  if ($son.Length -gt 600) { $son = $son.Substring(0, 600) + '…' }
  "[{0}] cikis={1} sure={2:n0}s | {3}" -f $ad, $kod, ((Get-Date) - $t0).TotalSeconds, $son.Trim()
}
Adim merge { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
Adim package_sources { & $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket.json }
Adim build_xlsx { & $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $WORK\_is\ara\ara.xlsx --report $WORK\_is\build.json --tools $TOOLS --partial --overwrite }
Adim text_quality { & $PY $TK\text_quality.py $WORK\_is\ara\ara.xlsx --address-standard sen --out $WORK\_is\text_quality.json }
Adim warning_scan { & $PY $TK\preview_checks.py warning-scan --xlsx $WORK\_is\ara\ara.xlsx --out $WORK\_is\uyari_tarama.json }
Adim tutarlilik { & $PY $TK\kart_tutarlilik.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\tutarlilik.json }
Adim claim_extract { & $PY $TK\claim_extract.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\claims.jsonl }
Adim fetch_snapshot { & $PY $TK\fetch_snapshot.py --xlsx $WORK\_is\ara\ara.xlsx --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache }
Adim claim_check { & $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --out $WORK\_is\claim_check.json }
Adim claim_check_number { & $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_number.json }
Adim validate_all { & $PY $TK\validate_all.py $WORK\_is\ara\ara.xlsx $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\val_ara.json }
