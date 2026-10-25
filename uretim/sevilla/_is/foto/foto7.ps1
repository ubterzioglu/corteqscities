. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
& $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX | Select-Object -Last 1
& $PY $TK\photo_rows.py plan $WORK\_is --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\plan_rapor.json
if ($LASTEXITCODE -ge 2) { throw 'photo_rows plan cikis 2' }
Push-Location $TOOLS
for ($i = 1; $i -le 8; $i++) {
  & $PY -X utf8 -B download_media.py $WORK\_is\foto\indirme_plani.json $PKG --allow-host upload.wikimedia.org --allow-host thumb.wikimedia.org --workers 2 2>&1 | Select-Object -Last 2
  "download try $i exit $LASTEXITCODE"
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 20
}
Pop-Location
& $PY $TK\photo_rows.py rows $WORK\_is --package $PKG --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\rows_rapor.json
if ($LASTEXITCODE -ge 2) { throw 'photo_rows rows cikis 2' }
& $PY -X utf8 -c "import json,sys,pathlib; d=pathlib.Path(sys.argv[1]); fs=sorted(d.glob('*.foto.jsonl')); alan=[(p.name,k,str(v)) for p in fs for l in p.read_text(encoding='utf-8-sig').split(chr(10)) if l.strip() for k,v in json.loads(l).items() if k=='file' or k.endswith('_file')]; bad=[a for a in alan if chr(92) in a[2]]; print(json.dumps({'dosya':len(fs),'alan':len(alan),'ters_bolu':len(bad),'ornek':bad[:3]},ensure_ascii=False)); sys.exit(2 if not fs else 1 if bad else 0)" "$WORK\_is\data\parcalar"
if ($LASTEXITCODE -ne 0) { throw 'foto yol kontrolu temiz degil' }
$keep = @((Get-Content $WORK\_is\foto\indirme_plani.json -Raw -Encoding utf8 | ConvertFrom-Json) | ForEach-Object { Split-Path $_.original_file -Leaf })
if ($keep.Count -gt 0) { Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File | Where-Object { $keep -notcontains $_.Name } | Remove-Item }
"fotograf dosyasi: $((Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File).Count)"
