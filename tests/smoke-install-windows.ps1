# Run only in native Windows PowerShell 5.1+; uses an isolated temporary CODEX_HOME.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$installer = Join-Path $repo 'scripts/install-windows.ps1'
$previous = $env:CODEX_HOME
$work = Join-Path ([IO.Path]::GetTempPath()) ('vdr-smoke-' + [guid]::NewGuid().ToString('N'))
$env:CODEX_HOME = Join-Path $work 'custom-home'
$target = Join-Path $env:CODEX_HOME 'skills/visual-design-review'
function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "FAIL: $Message" }
}
try {
    & $installer -Action install -DryRun | Out-Null
    Assert-True (-not (Test-Path -LiteralPath $env:CODEX_HOME)) 'dry-run wrote to filesystem'
    & $installer -Action install | Out-Null
    & $installer -Action check | Out-Null
    Assert-True (Test-Path -LiteralPath (Join-Path $target 'SKILL.md')) 'installation missing'
    $output = (& $installer -Action install) -join ' '
    Assert-True ($output.Contains('Already up to date')) 'idempotence check failed'
    Add-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'local-change' -Encoding UTF8
    & $installer -Action install -DryRun | Out-Null
    Assert-True ((Get-Content -LiteralPath (Join-Path $target 'SKILL.md') -Tail 1) -eq 'local-change') 'dry-run changed existing files'
    & $installer -Action install | Out-Null
    & $installer -Action check | Out-Null
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Directory -Filter 'visual-design-review.backup.*')
    Assert-True ($backups.Count -eq 1) 'update backup missing'
    Assert-True ((Get-Content -LiteralPath (Join-Path $backups[0].FullName 'SKILL.md') -Tail 1) -eq 'local-change') 'backup lost local edit'
    & $installer -Action remove -DryRun | Out-Null
    Assert-True (Test-Path -LiteralPath $target) 'remove dry-run changed files'
    & $installer -Action remove | Out-Null
    Assert-True (-not (Test-Path -LiteralPath $target)) 'removed skill still active'
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Directory -Filter 'visual-design-review.backup.*')
    Assert-True ($backups.Count -eq 2) 'removal backup missing'
    $checkFailed = $false
    try { & $installer -Action check | Out-Null } catch { $checkFailed = $true }
    Assert-True $checkFailed 'check succeeded after remove'
    Write-Output 'PASS: Windows dry-run, custom home, install, SHA check, idempotence, backup, remove'
} finally {
    $env:CODEX_HOME = $previous
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}
