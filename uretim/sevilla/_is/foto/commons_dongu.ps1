. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
for ($i = 1; $i -le 40; $i++) {
  $o = & $PY $TK\commons_search.py --plan $WORK\_is\foto\venues.jsonl --out $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache --max-requests 1500 --limit 25 --geo-max 5 2>&1 | Select-Object -Last 1
  $s = "$o"
  "$i $(Get-Date -Format HH:mm:ss) $($s.Substring(0, [Math]::Min(300, $s.Length)))"
  if ($s -notmatch 'resume_later') { break }
  Start-Sleep -Seconds 90
}
& $PY $TK\photo_candidates.py from-search $WORK\_is\foto\search.jsonl --out $WORK\_is\foto\candidates.jsonl
