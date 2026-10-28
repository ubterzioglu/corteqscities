. C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\ortam.ps1
function Adim($ad, [scriptblock]$komut) {
  $cikti = & $komut 2>&1 | Out-String
  $kod = $LASTEXITCODE
  $son = ($cikti -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
  if ($son.Length -gt 500) { $son = $son.Substring(0, 500) + '…' }
  "[{0}] cikis={1} | {2}" -f $ad, $kod, $son.Trim()
}
Adim merge { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
Adim package_sources { & $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket.json }
Adim build_xlsx { & $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $WORK\_is\ara\ara.xlsx --report $WORK\_is\build.json --tools $TOOLS --partial --overwrite }
Adim text_quality { & $PY $TK\text_quality.py $WORK\_is\ara\ara.xlsx --address-standard sen --out $WORK\_is\text_quality.json }
Adim warning_scan { & $PY $TK\preview_checks.py warning-scan --xlsx $WORK\_is\ara\ara.xlsx --out $WORK\_is\uyari_tarama.json }
