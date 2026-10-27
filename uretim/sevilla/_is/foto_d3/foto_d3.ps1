. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
function S($ad) { "### $ad exit=$LASTEXITCODE $(Get-Date -Format HH:mm:ss)" }
& $PY $TK\photo_rows.py plan $WORK\_is --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\plan_rapor.json | Select-Object -Last 1 | ForEach-Object { $_.Substring(0, [Math]::Min(1500, $_.Length)) }; S plan
if ($LASTEXITCODE -ge 2) { throw 'photo_rows plan cikis 2' }
$TMPPKG = 'C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\e1640e62-11af-476a-83cc-e29539d8a592\scratchpad\d3_foto2_w\pkg_tmp'
Remove-Item -LiteralPath $TMPPKG -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$TMPPKG\Fotoğraflar" | Out-Null
New-Item -ItemType Directory -Force "$TMPPKG\Teslimler" | Out-Null
if (Test-Path -LiteralPath "$PKG\Teslimler\.download-cache") { Copy-Item -LiteralPath "$PKG\Teslimler\.download-cache" -Destination "$TMPPKG\Teslimler\.download-cache" -Recurse -Force; 'cache kopyalandi' }
# paket fotograflari gecici pakete kopyalanmaz: ayni ada farkli icerik (yeniden numaralanan kare) aracta 'Existing destination differs' verir
Push-Location $TOOLS
$ok = $false
for ($i = 1; $i -le 40; $i++) {
  & $PY -X utf8 -B download_media.py $WORK\_is\foto\indirme_plani.json $TMPPKG --allow-host upload.wikimedia.org --allow-host thumb.wikimedia.org --workers 2 2>&1 | Select-Object -Last 1 | ForEach-Object { "$_".Substring(0, [Math]::Min(300, "$_".Length)) }
  $code = $LASTEXITCODE
  "download try $i exit $code $(Get-Date -Format HH:mm:ss)"
  if ($code -eq 0) { $ok = $true; break }
  Remove-Item -LiteralPath "$TMPPKG\Teslimler\download-progress-v7.part" -Force -ErrorAction SilentlyContinue
  Start-Sleep -Seconds 10
}
Pop-Location
if (-not $ok) { throw 'indirme tamamlanamadi' }
$plan = Get-Content $WORK\_is\foto\indirme_plani.json -Raw -Encoding utf8 | ConvertFrom-Json
$keep = @($plan | ForEach-Object { Split-Path $_.original_file -Leaf })
"plan dosya: $($keep.Count); gecici pakette: $((Get-ChildItem -LiteralPath "$TMPPKG\Fotoğraflar" -File).Count)"
$silinen = @(Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File | Where-Object { $keep -notcontains $_.Name } | ForEach-Object { $_.Name })
"plan disi silinen: $($silinen.Count) $($silinen -join ', ')"
Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File | Where-Object { $keep -notcontains $_.Name } | Remove-Item -Force
Get-ChildItem -LiteralPath "$TMPPKG\Fotoğraflar" -File | Where-Object { $keep -contains $_.Name } | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination "$PKG\Fotoğraflar\$($_.Name)" -Force }
Copy-Item -LiteralPath "$TMPPKG\Teslimler\download-progress-v7.json" -Destination "$PKG\Teslimler\download-progress-v7.json" -Force
"paket fotograf: $((Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File).Count)"
& $PY $TK\photo_rows.py rows $WORK\_is --package $PKG --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\rows_rapor.json | Select-Object -Last 1 | ForEach-Object { $_.Substring(0, [Math]::Min(1200, $_.Length)) }; S rows
if ($LASTEXITCODE -ge 2) { throw 'photo_rows rows cikis 2' }
& $PY -X utf8 -c "import json,sys,pathlib; d=pathlib.Path(sys.argv[1]); fs=sorted(d.glob('*.foto.jsonl')); alan=[(p.name,k,str(v)) for p in fs for l in p.read_text(encoding='utf-8-sig').split(chr(10)) if l.strip() for k,v in json.loads(l).items() if k=='file' or k.endswith('_file')]; bad=[a for a in alan if chr(92) in a[2]]; print(json.dumps({'dosya':len(fs),'alan':len(alan),'ters_bolu':len(bad),'ornek':bad[:3]},ensure_ascii=False)); sys.exit(2 if not fs else 1 if bad else 0)" "$WORK\_is\data\parcalar"
if ($LASTEXITCODE -ne 0) { throw 'foto yol kontrolu temiz degil' }
'FOTO_D3_BITTI'
