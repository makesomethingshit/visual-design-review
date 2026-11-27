# Run only in native Windows PowerShell 5.1+; uses an isolated temporary CODEX_HOME.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$installer = Join-Path $repo 'scripts/install-windows.ps1'
$previous = $env:CODEX_HOME
$work = Join-Path ([IO.Path]::GetTempPath()) ('vdr-smoke-' + [guid]::NewGuid().ToString('N'))
$env:CODEX_HOME = Join-Path $work 'custom-home'
$skillNames = @('visual-design-planning', 'visual-design-drafting', 'visual-design-review')
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
    foreach ($file in @('scripts/install-linux.sh', 'tests/smoke-install-linux.sh', 'tests/smoke-install-macos.sh', 'visual-design-planning/SKILL.md', 'visual-design-drafting/SKILL.md', 'visual-design-review/SKILL.md')) {
        Assert-True (-not ([IO.File]::ReadAllText((Join-Path $repo $file))).Contains([string][char]13)) "CRLF in Linux input: $file"
    }
    & $installer -Action install -DryRun | Out-Null
    Assert-True (-not (Test-Path -LiteralPath $env:CODEX_HOME)) 'dry-run wrote to filesystem'
    & $installer -Action install | Out-Null
    & $installer -Action check | Out-Null
    foreach ($name in $skillNames) {
        Assert-True (Test-Path -LiteralPath (Join-Path $env:CODEX_HOME "skills/$name/SKILL.md")) "installation missing: $name"
    }
    $output = (& $installer -Action install) -join ' '
    Assert-True ($output.Contains('Already up to date')) 'idempotence check failed'
    Add-Content -LiteralPath (Join-Path $target 'SKILL.md') -Value 'local-change' -Encoding UTF8
    & $installer -Action install -DryRun | Out-Null
    Assert-True ((Get-Content -LiteralPath (Join-Path $target 'SKILL.md') -Tail 1) -eq 'local-change') 'dry-run changed existing files'
    & $installer -Action install | Out-Null
    & $installer -Action check | Out-Null
    $backups = @(Get-ChildItem -LiteralPath $backupsRoot -Directory)
    Assert-True ($backups.Count -eq 1) 'update backup missing'
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Recurse -Filter SKILL.md).Count -eq $skillNames.Count) 'duplicate skill after update'
    Assert-True ((Get-Content -LiteralPath (Join-Path $backups[0].FullName 'SKILL.md') -Tail 1) -eq 'local-change') 'backup lost local edit'
    & $installer -Action remove -DryRun | Out-Null
    Assert-True (Test-Path -LiteralPath $target) 'remove dry-run changed files'
    & $installer -Action remove | Out-Null
    foreach ($name in $skillNames) {
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $env:CODEX_HOME "skills/$name"))) "removed skill still active: $name"
    }
    $backups = @(Get-ChildItem -LiteralPath $backupsRoot -Directory)
    Assert-True ($backups.Count -eq 2) 'removal backup missing'
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Recurse -Filter SKILL.md).Count -eq 0) 'backup discoverable after remove'
    foreach ($name in $skillNames) {
        $skillBackups = @(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME "skill-backups/$name") -Directory | Sort-Object Name)
        Assert-True ($skillBackups.Count -ge 1) "removal backup missing: $name"
        $restore = @($skillBackups | Where-Object { (Get-Content -LiteralPath (Join-Path $_.FullName 'SKILL.md') -Tail 1) -ne 'local-change' })
        Assert-True ($restore.Count -ge 1) "removal backup ambiguous: $name"
        Move-Item -LiteralPath $restore[-1].FullName -Destination (Join-Path $env:CODEX_HOME "skills/$name")
    }
    & $installer -Action check | Out-Null
    Assert-True (@(Get-ChildItem -LiteralPath (Join-Path $env:CODEX_HOME 'skills') -Recurse -Filter SKILL.md).Count -eq $skillNames.Count) 'restored skills not unique'
    & $installer -Action remove | Out-Null
    $checkFailed = $false
    try { & $installer -Action check | Out-Null } catch { $checkFailed = $true }
    Assert-True $checkFailed 'check succeeded after remove'

    # F-01: fields outside the first frontmatter block must be rejected.
    $badRepo = Join-Path $work 'bad-repo'
    New-Item -ItemType Directory -Path (Join-Path $badRepo 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'scripts/install-windows.ps1') -Destination (Join-Path $badRepo 'scripts/install-windows.ps1')
    foreach ($name in $skillNames) {
        Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $badRepo -Recurse
    }
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
    # A version belonging to another mapping is not metadata.version.
    $originalSkill = [IO.File]::ReadAllText((Join-Path $repo 'visual-design-review/SKILL.md'))
    [IO.File]::WriteAllText($badSkill, $originalSkill.Replace('metadata:', "metadata:`nother:"), (New-Object Text.UTF8Encoding($false)))
    $badFailed = $false
    try { & (Join-Path $badRepo 'scripts/install-windows.ps1') -Action install -DryRun | Out-Null } catch {
        $badFailed = $_.Exception.Message -match 'Invalid skill frontmatter'
    }
    Assert-True $badFailed 'version outside metadata accepted'
    Assert-True (-not (Test-Path -LiteralPath $env:CODEX_HOME)) 'invalid metadata created files'
    $env:CODEX_HOME = $validHome

    # F-02: remove must not depend on a valid source package.
    $removeRepo = Join-Path $work 'remove-repo'
    New-Item -ItemType Directory -Path (Join-Path $removeRepo 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'scripts/install-windows.ps1') -Destination (Join-Path $removeRepo 'scripts/install-windows.ps1')
    $removeHome = Join-Path $work 'remove-home'
    $env:CODEX_HOME = $removeHome
    & $installer -Action install | Out-Null
    & (Join-Path $removeRepo 'scripts/install-windows.ps1') -Action remove | Out-Null
    foreach ($name in $skillNames) {
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $removeHome "skills/$name"))) "remove failed without source: $name"
        Assert-True (Test-Path -LiteralPath (Join-Path $removeHome "skill-backups/$name")) "remove without source lost backup: $name"
    }
    $env:CODEX_HOME = $validHome

    # CODEX_HOME nested under the source tree must be rejected before creation.
    $nestedHome = Join-Path $repo 'visual-design-review/.nested-codex-home'
    $env:CODEX_HOME = $nestedHome
    $nestedFailed = $false
    $nestedMessage = ''
    try {
        & $installer -Action install -DryRun | Out-Null
    } catch {
        $nestedFailed = $true
        $nestedMessage = $_.Exception.Message
    }
    Assert-True $nestedFailed 'CODEX_HOME inside source accepted'
    Assert-True ($nestedMessage -match 'must not be inside the source directory') 'wrong nested source failure'
    Assert-True (-not (Test-Path -LiteralPath $nestedHome)) 'nested CODEX_HOME was created'
    $env:CODEX_HOME = $validHome

    # Remove must also reject an existing installation whose home is inside source.
    $nestedRemoveRepo = Join-Path $work 'nested-remove-repo'
    New-Item -ItemType Directory -Path (Join-Path $nestedRemoveRepo 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'scripts/install-windows.ps1') -Destination (Join-Path $nestedRemoveRepo 'scripts/install-windows.ps1')
    Copy-Item -LiteralPath (Join-Path $repo 'visual-design-review') -Destination $nestedRemoveRepo -Recurse
    $nestedRemoveInstaller = Join-Path $nestedRemoveRepo 'scripts/install-windows.ps1'
    $nestedRemoveHome = Join-Path $nestedRemoveRepo 'visual-design-review/.nested-remove-home'
    # Install all three so the skills processed before visual-design-review would be moved if the check ran late.
    foreach ($name in $skillNames) {
        New-Item -ItemType Directory -Path (Join-Path $nestedRemoveHome "skills/$name") -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $nestedRemoveHome "skills/$name/SKILL.md"), "sentinel`n")
    }
    $env:CODEX_HOME = $nestedRemoveHome
    $nestedRemoveFailed = $false
    $nestedRemoveMessage = ''
    try {
        & $nestedRemoveInstaller -Action remove | Out-Null
    } catch {
        $nestedRemoveFailed = $true
        $nestedRemoveMessage = $_.Exception.Message
    }
    Assert-True $nestedRemoveFailed 'remove accepted CODEX_HOME inside source'
    Assert-True ($nestedRemoveMessage -match 'must not be inside the source directory') 'wrong nested remove failure'
    foreach ($name in $skillNames) {
        Assert-True (Test-Path -LiteralPath (Join-Path $nestedRemoveHome "skills/$name/SKILL.md")) "nested remove moved the existing installation: $name"
    }
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $nestedRemoveHome 'skill-backups'))) 'nested remove created a backup inside source'
    $env:CODEX_HOME = $validHome

    # An ancestor junction can make a lexical CODEX_HOME path resolve inside the source.
    $junctionRepo = Join-Path $work 'junction-repo'
    New-Item -ItemType Directory -Path (Join-Path $junctionRepo 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'scripts/install-windows.ps1') -Destination (Join-Path $junctionRepo 'scripts/install-windows.ps1')
    foreach ($name in $skillNames) {
        Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $junctionRepo -Recurse
    }
    $junctionSource = Join-Path $junctionRepo 'visual-design-review'
    $junctionAlias = Join-Path $work 'source-alias'
    New-Item -ItemType Junction -Path $junctionAlias -Target $junctionSource | Out-Null
    $junctionHome = Join-Path $junctionAlias 'new-home'
    $junctionBefore = @{}
    $junctionPrefix = $junctionSource.TrimEnd([char[]]@('\', '/')) + [IO.Path]::DirectorySeparatorChar
    Get-ChildItem -LiteralPath $junctionSource -File -Recurse -Force | ForEach-Object {
        $junctionBefore[$_.FullName.Substring($junctionPrefix.Length)] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    }
    $env:CODEX_HOME = $junctionHome
    $junctionFailed = $false
    $junctionMessage = ''
    try {
        & (Join-Path $junctionRepo 'scripts/install-windows.ps1') -Action install | Out-Null
    } catch {
        $junctionFailed = $true
        $junctionMessage = $_.Exception.Message
    }
    Assert-True $junctionFailed 'CODEX_HOME beneath a source junction accepted'
    Assert-True ($junctionMessage -match 'reparse-point ancestor') "wrong source junction failure: $junctionMessage"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $junctionSource 'new-home'))) 'source changed through ancestor junction'
    $junctionAfter = @{}
    Get-ChildItem -LiteralPath $junctionSource -File -Recurse -Force | ForEach-Object {
        $junctionAfter[$_.FullName.Substring($junctionPrefix.Length)] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    }
    Assert-True ($junctionBefore.Count -eq $junctionAfter.Count) 'source file set changed through ancestor junction'
    foreach ($junctionFile in $junctionBefore.Keys) {
        Assert-True ($junctionAfter.ContainsKey($junctionFile) -and $junctionAfter[$junctionFile] -ceq $junctionBefore[$junctionFile]) "source file changed through ancestor junction: $junctionFile"
    }
    [IO.Directory]::Delete($junctionAlias)
    $env:CODEX_HOME = $validHome

    # Parent junctions must not redirect install/remove into the source or backups elsewhere.
    $linkHome = Join-Path $work 'link-home'
    New-Item -ItemType Directory -Path $linkHome -Force | Out-Null
    $env:CODEX_HOME = $linkHome
    foreach ($linked in @('skills', 'skill-backups', 'skill-backups/visual-design-planning', 'skill-backups/visual-design-drafting', 'skill-backups/visual-design-review')) {
        $linkPath = Join-Path $linkHome $linked
        New-Item -ItemType Directory -Path (Split-Path -Parent $linkPath) -Force | Out-Null
        New-Item -ItemType Junction -Path $linkPath -Target $repo | Out-Null
        try {
            foreach ($action in @('install', 'remove')) {
                $rejected = $false
                try { & $installer -Action $action | Out-Null } catch {
                    $rejected = $_.Exception.Message -match 'Refusing linked install or backup directory'
                }
                Assert-True $rejected "linked root accepted: $linked ($action)"
            }
            foreach ($name in $skillNames) {
                Assert-True (Test-Path -LiteralPath (Join-Path $repo "$name/SKILL.md")) "linked remove moved source: $name"
            }
        } finally {
            [IO.Directory]::Delete($linkPath)
        }
    }
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
