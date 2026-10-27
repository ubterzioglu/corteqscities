. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$ErrorActionPreference = 'Continue'
function S($ad) { "### $ad exit=$LASTEXITCODE $(Get-Date -Format HH:mm:ss)" }
# d14 sonrası ara kurulum (PKG'ye yazmaz): birleştir -> ara Excel -> metin/bant/doğrulayıcı
& $PY $TK\merge_package.py $WORK\_is --city-id $CITY --bbox=$BBOX | Select-Object -Last 1; S merge
& $PY $TK\build_xlsx.py --template $WORK\_is\sablon.xlsx --data-dir $WORK\_is\data --out $WORK\_is\ara\ara.xlsx --report $WORK\_is\build.json --tools $TOOLS --partial --overwrite | Select-Object -Last 1; S build
& $PY $TK\text_quality.py $WORK\_is\ara\ara.xlsx --address-standard sen --out $WORK\_is\text_quality.json | Select-Object -Last 1; S text_quality
& $PY $TK\preview_checks.py warning-scan --xlsx $WORK\_is\ara\ara.xlsx --out $WORK\_is\uyari_tarama.json | Select-Object -Last 1; S warning_scan
& $PY $TK\kart_tutarlilik.py $WORK\_is\ara\ara.xlsx --out $WORK\_is\tutarlilik.json | Select-Object -Last 1; S tutarlilik
& $PY $TK\validate_all.py $WORK\_is\ara\ara.xlsx $PKG --tools $TOOLS --mode audit --new-content --out $WORK\_is\val_ara.json | Select-Object -Last 1; S validate
'KUR_d14_BITTI'

