. C:\temp_private\corteqs\0000_newera\uretim\marbella\_is\ortam.ps1
Set-Location $WORK\_is
$log = "$WORK\_is\foto\ikinci_kaynak_log.txt"
"basla $(Get-Date -Format s)" | Out-File $log -Encoding utf8
for ($i = 1; $i -le 30; $i++) {
  $out = & $PY $TK\photo_sources.py --plan $WORK\_is\foto\venues.jsonl --search $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache_alt --min-per-venue 3 --max-requests 400 --sources openverse,smithsonian,europeana 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $out | Out-File $WORK\_is\foto\photo_sources_out.json -Encoding utf8
  $son = $out.Trim()
  "tur $i rc=$rc $(Get-Date -Format s) $($son.Substring(0, [Math]::Min(400, $son.Length)))" | Out-File $log -Append -Encoding utf8
  if ($rc -ge 2) { break }
  if ($out -notmatch '"status":\s*"stopped"') { break }
  Start-Sleep -Seconds 1800
}
$out = & $PY $TK\photo_candidates.py from-search $WORK\_is\foto\search.jsonl --out $WORK\_is\foto\candidates.jsonl 2>&1 | Out-String
"candidates rc=$LASTEXITCODE $(Get-Date -Format s) $($out.Trim())" | Out-File $log -Append -Encoding utf8
