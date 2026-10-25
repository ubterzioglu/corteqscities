. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
function S($ad) { "### $ad exit=$LASTEXITCODE" }
Remove-Item -LiteralPath "$PKG\Teslimler\.download-cache" -Recurse -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath "$PKG\Teslimler\.download-cache") { throw 'download-cache silinemedi' }
& $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode emit --new-content --out $WORK\_is\validation_emit.json | Out-Null; S emit
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv1
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Select-Object -Last 1; S sum1
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv2
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Select-Object -Last 1; S sum2
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv3
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
