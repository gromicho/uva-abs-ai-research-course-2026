# Downloads Card & Krueger's public replication files and checks them against the
# version the course was tested on. Run from this folder: .\get-data.ps1
$ErrorActionPreference = 'Stop'
$url = 'https://davidcard.berkeley.edu/data_sets/njmin.zip'
$expected = '41A29AEC6B489658B20030D044A2B20A5F5A04B871CDE41DF057AFD6013BA587'
$zip = Join-Path $PSScriptRoot 'njmin.zip'
$dest = Join-Path $PSScriptRoot 'data'

Invoke-WebRequest -Uri $url -OutFile $zip
$hash = (Get-FileHash $zip -Algorithm SHA256).Hash
if ($hash -ne $expected) {
    Write-Warning "njmin.zip differs from the tested version (SHA-256 $hash). Results may not match the reference."
}
Expand-Archive -Path $zip -DestinationPath $dest -Force
Get-ChildItem $dest | Select-Object Name, Length
Write-Host "Paper: https://davidcard.berkeley.edu/papers/min-wage-ff-nj.pdf"
