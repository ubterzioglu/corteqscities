# teslim.ps1'in yalniz foto kismi (tekrar calistirilabilir): birlestir (slug'lar) -> secim birlestir -> plan -> indirme -> satirlar.
# Amac: uzun suren indirmeyi asil teslimden once yapmak; teslim.ps1 ayni adimlari yeniden calistirir, inmis dosyalari atlar.
$ErrorActionPreference = 'Continue'
$ROOT = 'C:\temp_private\corteqs\0000_newera'
$PY   = "$ROOT\.venv\Scripts\python.exe"
$TOOLS= "$ROOT\araclar\arac"
$W    = "$ROOT\uretim\eindhoven\_is"
$PKG  = "$ROOT\uretim\eindhoven\paket"
$env:PYTHONDONTWRITEBYTECODE = 1

function Adim($ad) { "`n===== $ad =====" }

Adim 'birlestir (slug)'
& $PY "$W\birlestir.py" $W
Adim 'foto secim birlestir'
& $PY "$W\foto_secim_birlestir.py" $W --max-per-entry 5
Adim 'indirme plani'
& $PY -X utf8 "$W\foto_satirlari.py" plan $W $PKG
Adim 'indirme (resmi kuyruk, UTF-8, yeniden deneme)'
Push-Location $TOOLS
for ($i = 1; $i -le 8; $i++) {
  $out = & $PY -X utf8 -B download_media.py "$W\foto\indirme_plani.json" $PKG --allow-host upload.wikimedia.org --allow-host thumb.wikimedia.org --workers 2 2>&1
  "deneme $i : $($out | Select-Object -Last 1)"
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 20
}
Pop-Location
Adim 'foto satirlari'
& $PY -X utf8 "$W\foto_satirlari.py" rows $W $PKG
"`nFOTO ON ADIMI BITTI"
