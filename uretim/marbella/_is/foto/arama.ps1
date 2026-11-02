. C:\temp_private\corteqs\0000_newera\uretim\marbella\_is\ortam.ps1
Set-Location $WORK\_is
$log = "$WORK\_is\foto\arama_log.txt"
"basla $(Get-Date -Format s)" | Out-File $log -Encoding utf8
for ($i = 1; $i -le 120; $i++) {
  & $PY $TK\commons_search.py --plan $WORK\_is\foto\venues.jsonl --out $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache --max-requests 1500 --limit 25 --geo-max 5 > foto\commons_search_out.json 2> foto\commons_search_err.txt
  $rc = $LASTEXITCODE
  $out = Get-Content foto\commons_search_out.json -Raw -Encoding utf8
  "tur $i rc=$rc $(Get-Date -Format s) $($out.Substring(0, [Math]::Min(200, $out.Length)))" | Out-File $log -Append -Encoding utf8
  if ($out -notmatch 'resume_later') { break }
  Start-Sleep -Seconds 300
}
& $PY $TK\photo_sources.py --plan $WORK\_is\foto\venues.jsonl --search $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache_alt --min-per-venue 3 --max-requests 400 --sources openverse,smithsonian,europeana > foto\photo_sources_out.json 2>&1
"photo_sources rc=$LASTEXITCODE $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
& $PY $TK\photo_candidates.py from-search $WORK\_is\foto\search.jsonl --out $WORK\_is\foto\candidates.jsonl > foto\candidates_out.json 2>&1
"candidates rc=$LASTEXITCODE $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
Get-Content foto\candidates_out.json -Raw -Encoding utf8 | Out-File $log -Append -Encoding utf8
