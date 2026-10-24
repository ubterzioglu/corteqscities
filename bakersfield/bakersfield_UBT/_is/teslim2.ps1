. 'C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\ortam.ps1'
Remove-Item -LiteralPath "$PKG\Teslimler\.download-cache" -Recurse -Force -ErrorAction SilentlyContinue
& $PY $TK\validate_all.py $EXCEL $PKG --tools $TOOLS --mode emit --new-content --out $WORK\_is\validation_emit.json | Select-Object -Last 1 | ForEach-Object { Write-Host ("### emit " + $_.Substring(0,[Math]::Min(300,$_.Length))) }
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Out-Null
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Out-Null
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Out-Null
& $PY $TK\render_summary.py --xlsx $EXCEL --out-dir $PKG\Teslimler --inventory $WORK\_is\dosya-envanteri.json --validation $WORK\_is\validation_emit.json --notes $WORK\_is\notlar.md --manifest $WORK\manifest.json | Out-Null
& $PY $TK\inventory.py $PKG --xlsx $EXCEL --out $WORK\_is\dosya-envanteri.json | Select-Object -Last 1 | ForEach-Object { Write-Host ("### envanter " + $_.Substring(0,[Math]::Min(500,$_.Length))) }
Copy-Item $WORK\_is\dosya-envanteri.json $PKG\Teslimler\dosya-envanteri.json -Force
Write-Host "### BITTI"
