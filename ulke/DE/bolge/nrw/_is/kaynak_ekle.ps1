# NRW bolge paketi: kesif adaylarini kopyalar, must_contain ile dogrular, yazar kaynak listelerini uretir.
# Kullanim: & kaynak_ekle.ps1 gunluk,aile,saglik
param([string[]]$Konular)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'; $env:PYTHONDONTWRITEBYTECODE = '1'
$Py = 'C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe'
$Toolkit = 'C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts'
$Du = 'C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi'
$Work = 'C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is'
foreach ($k in $Konular) {
    $sel = "$Work\kesif\$k\selected.jsonl"
    if (-not (Test-Path $sel)) { Write-Output "$k : selected.jsonl yok, atlandi"; continue }
    & $Py -X utf8 "$Toolkit\add_sources.py" $Work --candidates $sel --subdir "snap_kesif_$k" --topic $k --city-id de-nw --cache-dir "$Work\cache" | Out-String | Write-Output
    & $Py -X utf8 "$Du\kaynak_listesi.py" $Work $k | Out-String | Write-Output
}
