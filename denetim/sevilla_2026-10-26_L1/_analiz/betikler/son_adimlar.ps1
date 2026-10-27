$env:PYTHONDONTWRITEBYTECODE=1; $env:PYTHONUTF8=1
$ROOT='C:\temp_private\corteqs\0000_newera'; $PY="$ROOT\.venv\Scripts\python.exe"; $TK="$ROOT\corteqs-skills\toolkit\scripts"
$B="$ROOT\.claude\skills\city-audit\betikler"; $PKG="$ROOT\uretim\sevilla\paket"; $XLSX="$PKG\CITY-107_sevilla_v001.xlsx"
$OUT="$ROOT\denetim\sevilla_2026-10-26_L1"; $A="$OUT\_analiz\betikler"
"== birlestir_l2"; & $PY -I -X utf8 $A\birlestir_l2.py $OUT | % { $_.Substring(0,[Math]::Min(1500,$_.Length)) }; "cikis=$LASTEXITCODE"
"== son envanter + K04"; & $PY $TK\inventory.py $PKG --xlsx $XLSX --out $OUT\_dosya-envanteri-son.json | Out-Null
& $PY -I -X utf8 $B\k04.py $OUT $PKG; "k04 cikis=$LASTEXITCODE"
"== kayitlar_l2"; & $PY -I -X utf8 $A\kayitlar_l2.py $OUT $PKG; "cikis=$LASTEXITCODE"
"== editorial_score"; & $PY $TK\editorial_score.py --input $OUT\criteria.json --out $OUT\score.json --format md | Select-Object -First 3; "cikis=$LASTEXITCODE"
"== rapor_l2"; & $PY -I -X utf8 $A\rapor_l2.py $OUT; "cikis=$LASTEXITCODE"
