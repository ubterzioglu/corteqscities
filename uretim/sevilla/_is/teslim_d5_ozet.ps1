. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$ErrorActionPreference = 'Continue'
function S($ad) { "### $ad exit=$LASTEXITCODE $(Get-Date -Format HH:mm:ss)" }
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv1
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Select-Object -Last 1; S sum1
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv2
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Select-Object -Last 1; S sum2
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1; S inv3
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
& $PY $TK\kanit_kapsami.py --xlsx $EXCEL --pkg $PKG --out $WORK\_is\kanit_kapsami.json | Select-Object -Last 1; S kanit_kapsami
'KUYRUK_BITTI'
