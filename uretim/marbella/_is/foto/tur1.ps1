. C:\temp_private\corteqs\0000_newera\uretim\marbella\_is\ortam.ps1
$log = "$WORK\_is\foto\tur1\tur1_log.txt"
"basla $(Get-Date -Format s)" | Out-File $log -Encoding utf8
for ($i = 1; $i -le 30; $i++) {
  $out = & $PY $TK\photo_previews.py $WORK\_is --decisions $WORK\_is\foto\tur1\decisions.json --items-out $WORK\_is\foto\tur1\items.jsonl --width 330 --out $WORK\_is\foto\tur1\onizleme.json 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $son = ($out.Trim() -split "`n" | Select-Object -Last 1)
  "previews tur $i rc=$rc $(Get-Date -Format s) $($son.Substring(0, [Math]::Min(500, $son.Length)))" | Out-File $log -Append -Encoding utf8
  if ($rc -ge 2) { break }
  if ($out -notmatch 'resume_later|429') { break }
  Start-Sleep -Seconds 300
}
$out = & $PY $TK\contact_sheet.py --items $WORK\_is\foto\tur1\items.jsonl --out-dir $WORK\_is\foto\tur1\pafta --per-sheet 30 --cols 6 --dhash-threshold 5 2>&1 | Out-String
"contact_sheet rc=$LASTEXITCODE $(Get-Date -Format s) $($out.Trim())" | Out-File $log -Append -Encoding utf8
