. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$ErrorActionPreference = 'Continue'
function S($ad) { "### $ad exit=$LASTEXITCODE $(Get-Date -Format HH:mm:ss)" }
# L2 düzeltme turu (d11/d12) sonrası: foto adım 6-7 -> artık kanıt temizliği -> assemble (tam kurulum) -> deliver (kanıtlar dahil)
& $PY $TK\acik_mi.py $WORK\_is\acik_mi --mekanlar $WORK\_is\data\parcalar --kaynaklar $WORK\_is\kaynak_dizini.jsonl --out $WORK\_is\acik_mi_rapor.json | Select-Object -Last 1; S acik_mi
if ($LASTEXITCODE -ne 0) { throw 'acik-mi kapisi temiz degil' }
& $PY $TK\phase_usage.py mark answers end --log $WORK\_is\phase_log.jsonl
& $PY $TK\phase_usage.py mark photos start --log $WORK\_is\phase_log.jsonl
& $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX | Select-Object -Last 1; S merge_foto
& $PY $TK\photo_rows.py plan $WORK\_is --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\plan_rapor.json | Select-Object -Last 1; S photo_plan
if ($LASTEXITCODE -ge 2) { throw 'photo_rows plan cikis 2' }
Push-Location $TOOLS
for ($i = 1; $i -le 8; $i++) {
  & $PY -X utf8 -B download_media.py $WORK\_is\foto\indirme_plani.json $PKG --allow-host upload.wikimedia.org --allow-host thumb.wikimedia.org --allow-host live.staticflickr.com --workers 2 | Select-Object -Last 1
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 20
}
Pop-Location; S download
& $PY $TK\photo_rows.py rows $WORK\_is --package $PKG --city-id $CITY --tools $TOOLS --out $WORK\_is\foto\rows_rapor.json | Select-Object -Last 1; S photo_rows
if ($LASTEXITCODE -ge 2) { throw 'photo_rows rows cikis 2' }
& $PY -I -X utf8 $WORK\_is\duzeltme_l2\foto_temizle.py $WORK\_is $PKG --uygula; S foto_temizle
if ($LASTEXITCODE -ne 0) { throw 'foto yol kontrolu ya da artik foto temizligi temiz degil' }
& $PY -I -X utf8 $WORK\_is\duzeltme_l2\artik_kanit_temizle.py $WORK\_is $PKG; S artik_kanit
& $PY $TK\phase_usage.py mark photos end --log $WORK\_is\phase_log.jsonl
& $PY $TK\phase_usage.py mark assemble start --log $WORK\_is\phase_log.jsonl
& $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX | Select-Object -Last 1; S merge
if ($LASTEXITCODE -ne 0) { throw 'merge temiz degil' }
& $PY $TK\package_sources.py $WORK\_is $PKG --out $WORK\_is\kaynak_paket_final.json | Select-Object -Last 1; S package_sources
& $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $EXCEL --report $WORK\_is\build_final.json --tools $TOOLS --overwrite | Select-Object -Last 1; S build
if ($LASTEXITCODE -ne 0) { throw 'build_xlsx temiz degil' }
& $PY $TK\rota_mesafe.py --xlsx $EXCEL --out $WORK\_is\rota_mesafe.jsonl --cache-dir $WORK\_is\cache_rota | Select-Object -Last 1; S rota_mesafe
& $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\validation.json | Select-Object -Last 1; S validate
& $PY $TK\text_quality.py $EXCEL --address-standard sen --out $WORK\_is\text_quality_final.json | Select-Object -Last 1; S text_quality
& $PY $TK\preview_checks.py warning-scan --xlsx $EXCEL --out $WORK\_is\uyari_tarama_final.json | Select-Object -Last 1; S warning_scan
& $PY $TK\claim_extract.py $EXCEL --out $WORK\_is\claims_final.jsonl | Select-Object -Last 1; S claim_extract
& $PY $TK\fetch_snapshot.py --xlsx $EXCEL --out-dir $WORK\_is\snap --cache-dir $WORK\_is\cache | Select-Object -Last 1; S fetch
& $PY $TK\claim_check.py --claims $WORK\_is\claims_final.jsonl --snapshots $WORK\_is\snap --mode number --out $WORK\_is\claim_check_final.json | Select-Object -Last 1; S claim_number
& $PY $TK\url_check.py $EXCEL --cache-dir $WORK\_is\cache --out $WORK\_is\url_check_final.json --retry-transient | Select-Object -Last 1; S url_check
& $PY $TK\phase_usage.py mark assemble end --log $WORK\_is\phase_log.jsonl
& $PY $TK\phase_usage.py mark deliver start --log $WORK\_is\phase_log.jsonl
Remove-Item -LiteralPath "$PKG\Teslimler\.download-cache" -Recurse -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath "$PKG\Teslimler\.download-cache") { throw 'download-cache silinemedi' }
& $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode emit --new-content --out $WORK\_is\validation_emit.json | Select-Object -Last 1; S emit
& $PY $TK\iddia_defteri.py --xlsx $EXCEL --claims-dir $WORK\_is\claims --audit-dir $ROOT\ulke\ES\_is\denetim --audit-dir $WORK\_is\denetim --out-dir $PKG\Teslimler | Select-Object -Last 1; S iddia_defteri
& $PY $TK\gorsel_kalite.py --xlsx $EXCEL --pkg $PKG --out-dir $WORK\_is\gorsel_kalite | Select-Object -Last 1; S gorsel_kalite
& $PY $TK\kanit_teslim.py --xlsx $EXCEL --work $WORK\_is --pkg $PKG --quality $WORK\_is\gorsel_kalite\gorsel-kalite-v7.json | Select-Object -Last 1; S kanit_teslim
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv1
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Select-Object -Last 1; S sum1
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv2
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Select-Object -Last 1; S sum2
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv3
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
& $PY $TK\kanit_kapsami.py --xlsx $EXCEL --pkg $PKG --out $WORK\_is\kanit_kapsami.json | Select-Object -Last 1; S kanit_kapsami
'TESLIM_D11_BITTI'
