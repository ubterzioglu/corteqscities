. C:\temp_private\corteqs\0000_newera\uretim\marbella\_is\ortam.ps1
Set-Location $WORK\_is
$log = "$WORK\_is\kur_d5_log.txt"
"basla $(Get-Date -Format s)" | Out-File $log -Encoding utf8
function Adim($ad, [scriptblock]$komut) {
  $out = & $komut 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $son = ($out.Trim() -split "`n" | Select-Object -Last 1)
  "$ad rc=$rc $($son.Substring(0, [Math]::Min(700, $son.Length)))" | Out-File $log -Append -Encoding utf8
}
Adim 'merge' { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
Adim 'package_sources' { & $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket.json }
Adim 'build' { & $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $WORK\_is\ara\ara.xlsx --report $WORK\_is\build.json --tools $TOOLS --partial --overwrite }
Adim 'text_quality' { & $PY $TK\text_quality.py $WORK\_is\ara\ara.xlsx --address-standard sen --out $WORK\_is\text_quality.json }
Adim 'warning_scan' { & $PY $TK\preview_checks.py warning-scan --xlsx $WORK\_is\ara\ara.xlsx --out $WORK\_is\uyari_tarama.json }
Adim 'tutarlilik' { & $PY $TK\kart_tutarlilik.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\tutarlilik.json }
Adim 'claim_extract' { & $PY $TK\claim_extract.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\claims.jsonl }
Adim 'fetch_snapshot' { & $PY $TK\fetch_snapshot.py --xlsx $WORK\_is\ara\ara.xlsx --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache }
Adim 'claim_check' { & $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --out $WORK\_is\claim_check.json }
Adim 'claim_check_number' { & $PY $TK\claim_check.py --claims $WORK\_is\claims.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_number.json }
Adim 'validate' { & $PY $TK\validate_all.py $WORK\_is\ara\ara.xlsx $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\val_ara.json }
Adim 'acik_mi' { & $PY $TK\acik_mi.py $WORK\_is\acik_mi --mekanlar $WORK\_is\data\parcalar --kaynaklar $WORK\_is\kaynak_dizini.jsonl --out $WORK\_is\acik_mi_rapor.json }
Adim 'rota_mesafe' { & $PY $TK\rota_mesafe.py --xlsx $WORK\_is\ara\ara.xlsx --out $WORK\_is\rota_mesafe.jsonl --cache-dir $WORK\_is\cache_rota }
"bitti $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
