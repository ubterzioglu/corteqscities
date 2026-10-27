$env:PYTHONDONTWRITEBYTECODE=1; $env:PYTHONUTF8=1
$ROOT='C:\temp_private\corteqs\0000_newera'; $PY="$ROOT\.venv\Scripts\python.exe"; $TK="$ROOT\corteqs-skills\toolkit\scripts"
$OUT="$ROOT\denetim\sevilla_2026-10-26_L1"
"== 1. kapi (kayit kusurlari)"
& $PY $TK\acik_mi.py $OUT\_acikmi --mekanlar $OUT\acik-mi-orneklem.jsonl --out $OUT\acik-mi-denetim.json | Out-String -Width 300 | % { $_.Substring(0,[Math]::Min(1500,$_.Length)) }
"kapi1 cikis=$LASTEXITCODE"
"== kanit"
& $PY $TK\acik_mi_denetim.py kanit $OUT; "kanit cikis=$LASTEXITCODE"
if ($LASTEXITCODE -eq 2) { throw 'acik-mi kanit listesi kurulamadi' }
"== 2. kapi (acik kaniti)"
& $PY $TK\acik_mi.py $OUT\_acikmi_acik --mekanlar $OUT\acik-mi-acik-liste.jsonl --out $OUT\acik-mi-acik.json | Out-String -Width 300 | % { $_.Substring(0,[Math]::Min(1500,$_.Length)) }
"kapi2 cikis=$LASTEXITCODE"
"== kanit kopyasi"
& $PY $TK\fetch_snapshot.py --urls $OUT\kanitlar\acikmi\urls.txt --must-contain $OUT\kanitlar\acikmi\kanit.jsonl --out-dir $OUT\kanitlar\acikmi --cache-dir $OUT\_cache --retry-transient
"snap cikis=$LASTEXITCODE"
"== sayim"
& $PY $TK\acik_mi_denetim.py sayim $OUT; "sayim cikis=$LASTEXITCODE"
