Write-Host "[1/4] Exporting all git objects..."
git rev-list --all --objects | Out-File all_files.txt -Encoding ascii

Write-Host "[2/4] Getting object sizes..."
$allObjects = Get-Content all_files.txt | ForEach-Object { $_.Split(" ")[0] }
$allObjects | git cat-file --batch-check | Out-File sizes.txt -Encoding ascii

Write-Host "[3/4] Finding largest files..."
$sizes = Get-Content sizes.txt | Where-Object { $_ -match 'blob' } | ForEach-Object {
    $parts = $_ -split ' '
    [PSCustomObject]@{
        SizeMB = [math]::Round($parts[2]/1MB, 2)
        Hash = $parts[0]
    }
} | Sort-Object SizeMB -Descending | Select-Object -First 20

$paths = Get-Content all_files.txt
foreach ($s in $sizes) {
    $match = $paths | Where-Object { $_ -like "$($s.Hash)*" }
    if ($match) {
        Write-Host "$($s.SizeMB) MB - $($match -replace '^[a-f0-9]+ ', '')"
    }
}
