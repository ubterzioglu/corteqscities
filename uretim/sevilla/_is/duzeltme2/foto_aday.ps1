. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$S='C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\56c9766a-06a1-495c-9d57-190d48973e42\scratchpad'
$o="$WORK\_is\foto_ek7"; New-Item -ItemType Directory -Force $o | Out-Null
$part=$args[0]; $harf=$args[1]
$live = Get-Content "$WORK\_is\data\parcalar\Mekânlar.$part.jsonl" -Encoding utf8 | ForEach-Object { ($_ | ConvertFrom-Json).entry_id }
Get-Content "$WORK\_is\mekan\secim_$harf.jsonl" -Encoding utf8 | ForEach-Object { $r = $_ | ConvertFrom-Json; if ($live -contains $r.entry_id -and $r.commons_category) { $slug=$r.slug; $n = (& $PY -X utf8 "$S\commons_kat_aday.py" ($r.commons_category -replace ' ','_') $r.entry_id "$o\cand_$slug`_candidates.jsonl" "$S\prev_$slug" 2>&1 | Measure-Object -Line).Lines; "$slug : $n"; Start-Sleep -Seconds 3 } }
'FOTO_ADAY_BITTI'
