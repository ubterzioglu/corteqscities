$O='C:\temp_private\corteqs\0000_newera\denetim\sevilla_2026-10-26_L1'
$bas = Get-Date
while ($true) {
  $eksik = @()
  foreach ($d in Get-ChildItem "$O\_iddia\girdi" -Directory) {
    $nn = $d.Name.Split('_')[1]
    $n = (Get-Content "$($d.FullName)\kartlar.jsonl" -Encoding utf8 | ? { $_ }).Count
    $k = "$O\_iddia\kart_$nn.jsonl"
    $m = if (Test-Path $k) { (Get-Content $k -Encoding utf8 | ? { $_ } | % { try { ($_ | ConvertFrom-Json).entry_id } catch {} } | Sort-Object -Unique).Count } else { 0 }
    if ($m -lt $n) { $eksik += "$nn $m/$n" }
  }
  if (-not $eksik) { "TAMAM $(Get-Date -Format HH:mm:ss)"; exit 0 }
  if (((Get-Date) - $bas).TotalMinutes -gt 75) { "ZAMAN ASIMI: $($eksik -join ', ')"; exit 1 }
  Start-Sleep 30
}
