# Run only in native Windows PowerShell 5.1+; uses an isolated temporary CODEX_HOME.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$installer = Join-Path $repo 'scripts/install-windows.ps1'
$previous = $env:CODEX_HOME
$work = Join-Path ([IO.Path]::GetTempPath()) ('vdr-smoke-' + [guid]::NewGuid().ToString('N'))
$env:CODEX_HOME = Join-Path $work 'custom-home'
$target = Join-Path $env:CODEX_HOME 'skills/visual-design-review'
$backupsRoot = Join-Path $env:CODEX_HOME 'skill-backups/visual-design-review'
function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "FAIL: $Message" }
}
try {
    $validHome = $env:CODEX_HOME
    foreach ($invalid in @('C:CodexHome', '\CodexHome', 'relative/path')) {
        $env:CODEX_HOME = $invalid
        $rejected = $false
        try { & $installer -Action install -DryRun | Out-Null } catch {
            $rejected = $_.Exception.Message -eq 'CODEX_HOME must be an absolute Windows path.'
        }
        Assert-True $rejected "accepted non-absolute path: $invalid"
    }
    $env:CODEX_HOME = $validHome
    foreach ($file in @('scripts/install-linux.sh', 'tests/smoke-install-linux.sh', 'tests/smoke-install-macos.sh', 'visual-design-review/SKILL.md')) {
        Assert-True (-not ([IO.File]::ReadAllText((Join-Path $repo $file))).Contains([string][char]13)) "CRLF in Linux input: $file"
    }
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
    $backups = @(Get-ChildItem -LiteralPath $backupsRoot -Directory)
    Assert-True ($backups.Count -eq 1) 'update backup missing'
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Recurse -Filter SKILL.md).Count -eq 1) 'duplicate skill after update'
    Assert-True ((Get-Content -LiteralPath (Join-Path $backups[0].FullName 'SKILL.md') -Tail 1) -eq 'local-change') 'backup lost local edit'
    & $installer -Action remove -DryRun | Out-Null
    Assert-True (Test-Path -LiteralPath $target) 'remove dry-run changed files'
    & $installer -Action remove | Out-Null
    Assert-True (-not (Test-Path -LiteralPath $target)) 'removed skill still active'
    $backups = @(Get-ChildItem -LiteralPath $backupsRoot -Directory)
    Assert-True ($backups.Count -eq 2) 'removal backup missing'
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Recurse -Filter SKILL.md).Count -eq 0) 'backup discoverable after remove'
    $restore = @($backups | Where-Object { (Get-Content -LiteralPath (Join-Path $_.FullName 'SKILL.md') -Tail 1) -ne 'local-change' })
    Assert-True ($restore.Count -eq 1) 'removal backup ambiguous'
    Move-Item -LiteralPath $restore[0].FullName -Destination $target
    & $installer -Action check | Out-Null
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Recurse -Filter SKILL.md).Count -eq 1) 'restored skill not unique'
    & $installer -Action remove | Out-Null
    $checkFailed = $false
    try { & $installer -Action check | Out-Null } catch { $checkFailed = $true }
    Assert-True $checkFailed 'check succeeded after remove'

    # F-01: fields outside the first frontmatter block must be rejected.
    $badRepo = Join-Path $work 'bad-repo'
    New-Item -ItemType Directory -Path (Join-Path $badRepo 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'scripts/install-windows.ps1') -Destination (Join-Path $badRepo 'scripts/install-windows.ps1')
    Copy-Item -LiteralPath (Join-Path $repo 'visual-design-review') -Destination $badRepo -Recurse
    $badSkill = Join-Path $badRepo 'visual-design-review/SKILL.md'
    $badLines = @(Get-Content -LiteralPath $badSkill -Encoding UTF8)
    $badOut = New-Object System.Collections.Generic.List[string]
    $closed = $false
    for ($i = 0; $i -lt $badLines.Count; $i++) {
        if ($badLines[$i] -ceq 'name: visual-design-review') { continue }
        $badOut.Add($badLines[$i])
        if (-not $closed -and $i -gt 0 -and $badLines[$i] -ceq '---') {
            $badOut.Add('name: visual-design-review')
            $closed = $true
        }
    }
    [IO.File]::WriteAllLines($badSkill, $badOut, (New-Object Text.UTF8Encoding($false)))
    $env:CODEX_HOME = Join-Path $work 'bad-frontmatter-home'
    $badFailed = $false
    $badMessage = ''
    try {
        & (Join-Path $badRepo 'scripts/install-windows.ps1') -Action install -DryRun | Out-Null
    } catch {
        $badFailed = $true
        $badMessage = $_.Exception.Message
    }
    Assert-True $badFailed 'frontmatter fields outside block accepted'
    Assert-True ($badMessage -match 'Invalid skill frontmatter') 'wrong frontmatter failure'
    $env:CODEX_HOME = $validHome

    # F-02: remove must not depend on a valid source package.
    $removeRepo = Join-Path $work 'remove-repo'
    New-Item -ItemType Directory -Path (Join-Path $removeRepo 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'scripts/install-windows.ps1') -Destination (Join-Path $removeRepo 'scripts/install-windows.ps1')
    $removeHome = Join-Path $work 'remove-home'
    $env:CODEX_HOME = $removeHome
    & $installer -Action install | Out-Null
    $removeTarget = Join-Path $removeHome 'skills/visual-design-review'
    & (Join-Path $removeRepo 'scripts/install-windows.ps1') -Action remove | Out-Null
    Assert-True (-not (Test-Path -LiteralPath $removeTarget)) 'remove failed without source'
    Assert-True (Test-Path -LiteralPath (Join-Path $removeHome 'skill-backups/visual-design-review')) 'remove without source lost backup'
    $env:CODEX_HOME = $validHome

    # Force activation and rollback to fail; the backup path must be reported.
    & $installer -Action install | Out-Null
    Add-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'rollback-test' -Encoding UTF8
    $rollbackWarnings = @()
    function Move-Item {
        [CmdletBinding()]
        param(
            [Parameter(Mandatory)][string]$LiteralPath,
            [Parameter(Mandatory)][string]$Destination
        )
        if ($LiteralPath -like '*.visual-design-review.stage.*') { throw 'injected activation failure' }
        if ($LiteralPath -like '*skill-backups*' -and $Destination -eq $target) { throw 'injected rollback failure' }
        Microsoft.PowerShell.Management\Move-Item -LiteralPath $LiteralPath -Destination $Destination
    }
    $installFailed = $false
    try {
        & $installer -Action install -WarningVariable rollbackWarnings -WarningAction Continue | Out-Null
    } catch {
        $installFailed = $true
    }
    if (Test-Path Function:\Move-Item) { Remove-Item Function:\Move-Item }
    Assert-True $installFailed 'injected activation/rollback failure reported success'
    $stuck = @(Get-ChildItem -LiteralPath $backupsRoot -Directory | Where-Object {
        (Get-Content -LiteralPath (Join-Path $_.FullName 'SKILL.md') -Tail 1) -eq 'rollback-test'
    })
    Assert-True ($stuck.Count -eq 1) 'rollback backup not found'
    Assert-True (($rollbackWarnings -join ' ') -match [regex]::Escape($stuck[0].FullName)) 'rollback backup path not reported'
    Assert-True (-not (Test-Path -LiteralPath $target)) 'failed rollback left an active target'
    Write-Output 'PASS: Windows dry-run, custom home, install, SHA check, idempotence, backup, remove, rollback'
} finally {
    $env:CODEX_HOME = $previous
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}
