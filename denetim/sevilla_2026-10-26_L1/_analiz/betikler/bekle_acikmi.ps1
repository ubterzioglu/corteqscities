$O='C:\temp_private\corteqs\0000_newera\denetim\sevilla_2026-10-26_L1'
$bas = Get-Date
while ($true) {
  $eksik = @()
  foreach ($p in Get-ChildItem "$O\_acikmi\parti_*.jsonl" | ? { $_.Name -notmatch '_dogrulama' }) {
    $n = (Get-Content $p.FullName -Encoding utf8 | ? { $_ }).Count
    $d = "$O\_acikmi\$($p.BaseName)_dogrulama.jsonl"
    $m = if (Test-Path $d) { (Get-Content $d -Encoding utf8 | ? { $_ } | % { ($_ | ConvertFrom-Json).entry_id } | Sort-Object -Unique).Count } else { 0 }
    if ($m -lt $n) { $eksik += "$($p.BaseName) $m/$n" }
  }
  if (-not $eksik) { "TAMAM $(Get-Date -Format HH:mm:ss)"; exit 0 }
  if (((Get-Date) - $bas).TotalMinutes -gt 60) { "ZAMAN ASIMI: $($eksik -join ', ')"; exit 1 }
  Start-Sleep 30
}
