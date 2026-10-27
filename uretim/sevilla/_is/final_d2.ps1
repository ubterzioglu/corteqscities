. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
function S($ad) { "### $ad exit=$LASTEXITCODE $(Get-Date -Format HH:mm:ss)" }
& $PY $TK\acik_mi.py $WORK\_is\acik_mi --mekanlar $WORK\_is\data\parcalar --kaynaklar $WORK\_is\kaynak_dizini.jsonl --out $WORK\_is\acik_mi_rapor.json | Select-Object -Last 1 | ForEach-Object { $_.Substring(0, [Math]::Min(1500, $_.Length)) }; S acik_mi
& $PY $TK\phase_usage.py mark places end --log $WORK\_is\phase_log.jsonl
& $PY $TK\phase_usage.py mark photos start --log $WORK\_is\phase_log.jsonl
& $WORK\_is\foto\foto_d2.ps1
& $PY $TK\phase_usage.py mark photos end --log $WORK\_is\phase_log.jsonl
& $PY -X utf8 -c "import json,pathlib; W=pathlib.Path(r'$WORK'); m=json.loads((W/'manifest.json').read_text(encoding='utf-8')); m['sources_researched']=sum(1 for l in (W/'_is'/'kaynak_dizini.jsonl').read_text(encoding='utf-8-sig').splitlines() if l.strip()); m['photos_downloaded']=len(json.loads((W/'_is'/'foto'/'indirme_plani.json').read_text(encoding='utf-8'))); (W/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8'); lines=['# Açık konular — Sevilla (CITY-107)','']+[f\"- [{o.get('priority','P2')}] {o['id']} ({o.get('owner','insan')}): {o['text']}\" for o in m['open_items']]; (W/'_is'/'notlar.md').write_text(chr(10).join(lines)+chr(10),encoding='utf-8'); print('manifest', m['sources_researched'], m['photos_downloaded'])"
& $WORK\_is\teslim_d2.ps1
'FINAL_D2_BITTI'
