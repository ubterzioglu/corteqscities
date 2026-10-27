param($L)
$seen=@{}
while ($true) {
  Start-Sleep 60; $now=Get-Date
  foreach ($f in (Get-Content -Encoding utf8 $L | ? { $_ })) {
    if (-not $seen.ContainsKey($f)) { $seen[$f]=$now }
    $t = if (Test-Path $f) { $x=(Get-Item $f).LastWriteTime; if ($x -gt $seen[$f]) {$x} else {$seen[$f]} } else { $seen[$f] }
    if (($now-$t).TotalMinutes -ge 10) { "DURGUN: $f son hareket $($t.ToString('HH:mm:ss')) (şimdi $($now.ToString('HH:mm:ss')))"; exit 0 }
  }
}
