# Eindhoven teslim zinciri (foto turları bittikten sonra tek seferde çalıştırılır).
# Sıra kuralları: birlestir -> kaynak_paketle (Kaynaklar'ı her seferinde yeniden yazar) -> build;
# download_media her zaman -X utf8 ile (aksi hâlde Windows'ta "FotoÄŸraflar" klasörü oluşur);
# .download-cache teslimden önce silinir (envanterde sahte ext_mismatch/dup_sha üretir).
$ErrorActionPreference = 'Continue'
$ROOT = 'C:\temp_private\corteqs\0000_newera'
$PY   = "$ROOT\.venv\Scripts\python.exe"
$TK   = "$ROOT\corteqs-skills\toolkit\scripts"
$TOOLS= "$ROOT\araclar\arac"
$W    = "$ROOT\uretim\eindhoven\_is"
$PKG  = "$ROOT\uretim\eindhoven\paket"
$XLSX = "$PKG\CITY-039_eindhoven_v001.xlsx"
$env:PYTHONDONTWRITEBYTECODE = 1

function Adim($ad) { "`n===== $ad =====" }

Adim 'birlestir (on) - yeni mekanlarin slug''lari foto planindan once data/da olsun'
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

Adim 'kullanilmayan foto dosyalari (plan disi) temizligi'
& $PY -X utf8 -c "import json,os,sys; pkg,w=sys.argv[1],sys.argv[2]; keep={os.path.basename(r['original_file']) for r in json.load(open(os.path.join(w,'foto','indirme_plani.json'),encoding='utf-8'))}; d=os.path.join(pkg,'Fotoğraflar'); rm=[f for f in os.listdir(d) if f not in keep]; [os.remove(os.path.join(d,f)) for f in rm]; print('silinen',len(rm),'kalan',len(os.listdir(d)))" $PKG $W

Adim 'birlestir'
& $PY "$W\birlestir.py" $W
Adim 'kaynak kopyalari'
& $PY "$W\kaynak_paketle.py" $W $PKG

Adim 'Excel (TAM; --partial yok)'
& $PY $TK\build_xlsx.py --template "$W\sablon.xlsx" --data-dir "$W\data" --out $XLSX --report "$W\build_final.json" --tools $TOOLS --overwrite

Adim 'kalite kapilari'
& $PY $TK\validate_all.py $XLSX $PKG --tools $TOOLS --mode audit --new-content --out "$W\validation.json"
& $PY $TK\text_quality.py $XLSX --out "$W\text_quality_final.json"
& $PY $TK\claim_extract.py $XLSX --out "$W\claims_final.jsonl"
& $PY $TK\claim_check.py --claims "$W\claims_final.jsonl" --snapshots "$W\snap" --out "$W\claim_check_final.json" --mode number
& $PY $TK\url_check.py $XLSX --cache-dir "$W\cache" --out "$W\url_check_final.json" --retry-transient

Adim 'indirme onbellegi silinir (paket ici artik)'
& $PY -X utf8 -c "import shutil,os,sys; p=os.path.join(sys.argv[1],'Teslimler','.download-cache'); shutil.rmtree(p,ignore_errors=True); print('silindi' if not os.path.exists(p) else 'SILINEMEDI')" $PKG

Adim 'resmi teslim ciktilari (emit) + ozet + envanter (sira: once tum dosyalar, sonra sayim; L0 ISS-005)'
& $PY $TK\validate_all.py $XLSX $PKG --tools $TOOLS --mode emit --new-content --out "$W\validation_emit.json"
# Sira (L0b ISS-005): envanter -> ozet (BIR kez; render_summary ILERLEME_KAYDI'na her calismada girdi EKLER) -> envanter (EN SON) -> kopya.
# Son envanterden sonra pakete hicbir sey yazilmaz; yoksa envanterdeki SHA dosyayla tutmaz.
& $PY -X utf8 $TK\inventory.py $PKG --xlsx $XLSX --out "$W\dosya-envanteri.json"
& $PY -X utf8 $TK\render_summary.py --xlsx $XLSX --out-dir "$PKG\Teslimler" --inventory "$W\dosya-envanteri.json" --validation "$W\validation_emit.json" --notes "$W\notlar.md" --manifest "$ROOT\uretim\eindhoven\manifest.json"
& $PY -X utf8 $TK\inventory.py $PKG --xlsx $XLSX --out "$W\dosya-envanteri.json"
Copy-Item "$W\dosya-envanteri.json" "$PKG\Teslimler\dosya-envanteri.json" -Force
"`nTESLIM ZINCIRI BITTI"
