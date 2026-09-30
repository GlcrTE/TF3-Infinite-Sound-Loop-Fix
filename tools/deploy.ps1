# Copies the mod into the local TF3 mods folder of every Steam user on this machine.
$ErrorActionPreference = 'Stop'

$modName = 'glcrte_infinite_sound_loop_fix_1'
$source = Join-Path $PSScriptRoot "..\mod\$modName"
$userdata = 'C:\Program Files (x86)\Steam\userdata'

$targets = Get-ChildItem $userdata -Directory | ForEach-Object { Join-Path $_.FullName '3493540\local\mods' } | Where-Object { Test-Path $_ }
if (-not $targets) { throw "No TF3 local mods folder found under $userdata" }

foreach ($mods in $targets) {
    $dest = Join-Path $mods $modName
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item $source $dest -Recurse
    Write-Host "Deployed to $dest"
}
