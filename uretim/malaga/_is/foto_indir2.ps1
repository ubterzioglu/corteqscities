. C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\ortam.ps1
Push-Location $TOOLS
for ($i = 1; $i -le 10; $i++) {
  $o = (& $PY -X utf8 -B download_media.py $WORK\_is\foto\indirme_plani.json $PKG --allow-host upload.wikimedia.org --allow-host thumb.wikimedia.org --workers 2 2>&1 | Out-String)
  $k = $LASTEXITCODE
  $s = ($o -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
  "indir$($i): cikis=$k dosya=$(@(Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File -ErrorAction SilentlyContinue).Count) | $($s.Substring(0, [Math]::Min(250, $s.Length)))"
  if ($k -eq 0) { break }
  Start-Sleep -Seconds 300
}
Pop-Location
& $PY -X utf8 $TK\photo_rows.py rows $WORK\_is --package $PKG --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\rows_rapor.json 2>&1 | Out-String | ForEach-Object { "rows: " + $_.Substring(0, [Math]::Min(600, $_.Length)) }
$kontrol = "import json,sys,pathlib; d=pathlib.Path(sys.argv[1]); fs=sorted(d.glob('*.foto.jsonl')); alan=[(p.name,k,str(v)) for p in fs for l in p.read_text(encoding='utf-8-sig').split(chr(10)) if l.strip() for k,v in json.loads(l).items() if k=='file' or k.endswith('_file')]; bad=[a for a in alan if chr(92) in a[2]]; print(json.dumps({'dosya':len(fs),'alan':len(alan),'ters_bolu':len(bad)},ensure_ascii=False)); sys.exit(2 if not fs else 1 if bad else 0)"
& $PY -X utf8 -c $kontrol "$WORK\_is\data\parcalar"
"foto dosya sayisi: " + @(Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File).Count
