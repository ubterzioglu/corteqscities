. C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\ortam.ps1
function Adim($ad, [scriptblock]$komut) {
  $cikti = & $komut 2>&1 | Out-String
  $kod = $LASTEXITCODE
  $son = ($cikti -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
  if ($son -and $son.Length -gt 600) { $son = $son.Substring(0, 600) + '…' }
  "[{0}] cikis={1} | {2}" -f $ad, $kod, "$son".Trim()
}

# Faz 5 adım 6–7: birleştir, seçim, plan, indirme, satırlar
Adim merge { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
Adim foto_secim { & $PY -X utf8 $WORK\_is\araclar\foto_secim_birlestir.py $WORK\_is }
Adim photo_rows_plan { & $PY $TK\photo_rows.py plan $WORK\_is --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\plan_rapor.json }
if ($LASTEXITCODE -ge 2) { throw 'photo_rows plan cikis 2' }
# İndirme kuyruğu izlenmeyen bir kökte çalışır (önbellek orada kalır, paket dışında): paket\Teslimler'de
# ilerleme dosyasının saniyede onlarca kez yeniden adlandırılması dosya izleyicisiyle çakışıp WinError 5 veriyordu.
# Kayıt, paketteki dosyalarla SHA karşılaştırıldıktan sonra pakete alınır.
$indirKok = "$WORK\_is\cache\indir_kok"
Push-Location $TOOLS
for ($i = 1; $i -le 15; $i++) {
  Adim "indir$i" { & $PY -X utf8 -B download_media.py $WORK\_is\foto\indirme_plani.json $indirKok --allow-host upload.wikimedia.org --allow-host thumb.wikimedia.org --workers 2 }
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 3
}
$indirKod = $LASTEXITCODE
Pop-Location
if ($indirKod -ne 0) { throw 'download_media tamamlanmadi (429/kilit); bekleyip zinciri baştan çalıştır' }
Adim progress_al { & $PY -X utf8 $WORK\_is\araclar\progress_al.py $indirKok $PKG }
if ($LASTEXITCODE -ne 0) { throw 'indirme kaydi paketteki dosyalarla uyusmuyor (yeni kare varsa indir_kok\Fotoğraflar''dan pakete kopyala)' }
Adim photo_rows_rows { & $PY $TK\photo_rows.py rows $WORK\_is --package $PKG --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\rows_rapor.json }
if ($LASTEXITCODE -ge 2) { throw 'photo_rows rows cikis 2' }
$kontrol = "import json,sys,pathlib; d=pathlib.Path(sys.argv[1]); fs=sorted(d.glob('*.foto.jsonl')); alan=[(p.name,k,str(v)) for p in fs for l in p.read_text(encoding='utf-8-sig').split(chr(10)) if l.strip() for k,v in json.loads(l).items() if k=='file' or k.endswith('_file')]; bad=[a for a in alan if chr(92) in a[2]]; print(json.dumps({'dosya':len(fs),'alan':len(alan),'ters_bolu':len(bad),'ornek':bad[:3]},ensure_ascii=False)); sys.exit(2 if not fs else 1 if bad else 0)"
Adim yol_kontrol { & $PY -X utf8 -c $kontrol "$WORK\_is\data\parcalar" }
if ($LASTEXITCODE -ne 0) { throw 'foto yol kontrolu temiz degil' }
$keep = @((Get-Content $WORK\_is\foto\indirme_plani.json -Raw -Encoding utf8 | ConvertFrom-Json) | ForEach-Object { Split-Path $_.original_file -Leaf })
if ($keep.Count -gt 0) { Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File | Where-Object { $keep -notcontains $_.Name } | Remove-Item }
"foto dosya sayisi: " + @(Get-ChildItem -LiteralPath "$PKG\Fotoğraflar" -File).Count

# Faz 6
Adim merge2 { & $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX }
Adim package_sources { & $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket_final.json }
Adim build_xlsx { & $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $EXCEL --report $WORK\_is\build_final.json --tools $TOOLS --overwrite }
Adim validate_audit { & $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\validation.json }
Adim text_quality { & $PY $TK\text_quality.py $EXCEL --address-standard sen --out $WORK\_is\text_quality_final.json }
Adim warning_scan { & $PY $TK\preview_checks.py warning-scan --xlsx $EXCEL --out $WORK\_is\uyari_tarama_final.json }
Adim claim_extract { & $PY $TK\claim_extract.py $EXCEL --out $WORK\_is\claims_final.jsonl }
Adim fetch_snapshot { & $PY $TK\fetch_snapshot.py --xlsx $EXCEL --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache }
Adim claim_check { & $PY $TK\claim_check.py --claims $WORK\_is\claims_final.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_final.json }
Adim url_check { & $PY $TK\url_check.py $EXCEL --cache-dir $WORK\_is\cache --out $WORK\_is\url_check_final.json --retry-transient }

# Faz 7
Remove-Item -LiteralPath "$PKG\Teslimler\.download-cache" -Recurse -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath "$PKG\Teslimler\.download-cache") { throw 'download-cache silinemedi' }
Adim validate_emit { & $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode emit --new-content --out $WORK\_is\validation_emit.json }
Adim iddia_defteri { & $PY $TK\iddia_defteri.py --xlsx $EXCEL --claims-dir $WORK\_is\claims --audit-dir $ROOT\ulke\ES\_is\denetim --audit-dir $WORK\_is\denetim --out-dir $PKG\Teslimler }
Adim gorsel_kalite { & $PY $TK\gorsel_kalite.py --xlsx $EXCEL --pkg $PKG --out-dir $WORK\_is\gorsel_kalite }
Adim kanit_teslim { & $PY $TK\kanit_teslim.py --xlsx $EXCEL --work $WORK\_is --pkg $PKG --quality $WORK\_is\gorsel_kalite\gorsel-kalite-v7.json }
Adim inventory1 { & $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json }
Adim summary1 { & $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json }
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
Adim inventory2 { & $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json }
Adim summary2 { & $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json }
Adim inventory3 { & $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json }
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
Adim kanit_kapsami { & $PY $TK\kanit_kapsami.py --xlsx $EXCEL --pkg $PKG --out $WORK\_is\kanit_kapsami.json }
"### teslim zinciri bitti"
