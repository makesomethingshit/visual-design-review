# Native Windows PowerShell 5.1+ only. No downloads or dependency installation.
[CmdletBinding()]
param(
    [ValidateSet('install', 'check', 'remove')]
    [string]$Action = 'install',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw 'Use install-linux.sh on Linux/WSL/macOS; this script is for native Windows.'
}
$source = Join-Path (Split-Path -Parent $PSScriptRoot) 'visual-design-review'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
if ($codexHome -notmatch '^(?:[A-Za-z]:[\\/]|[\\/]{2}[^\\/]+[\\/][^\\/]+(?:[\\/]|$))') { throw 'CODEX_HOME must be an absolute Windows path.' }
$skillsRoot = Join-Path $codexHome 'skills'
$target = Join-Path $skillsRoot 'visual-design-review'
$backupsRoot = Join-Path $codexHome 'skill-backups/visual-design-review'

function Assert-Layout([string]$Root) {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw "Missing directory: $Root" }
    $item = Get-Item -LiteralPath $Root -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Refusing linked folder: $Root" }
    $items = @(Get-ChildItem -LiteralPath $Root -Recurse -Force)
    foreach ($entry in $items) {
        if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Refusing linked entry: $($entry.FullName)" }
    }
    $skill = Join-Path $Root 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skill -PathType Leaf)) { throw "Missing SKILL.md in $Root" }
    $lines = @(Get-Content -LiteralPath $skill -Encoding UTF8)
    if ($lines.Count -lt 4 -or $lines[0] -cne '---') {
        throw "Invalid skill frontmatter: $skill"
    }
    $close = -1
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -ceq '---') { $close = $i; break }
    }
    if ($close -lt 2) { throw "Invalid skill frontmatter: $skill" }
    $frontmatter = @($lines[1..($close - 1)])
    if (-not ($frontmatter -ccontains 'name: visual-design-review') -or
        -not (@($frontmatter | Where-Object { $_ -match '^description:' }).Count -gt 0) -or
        -not ($frontmatter -ccontains 'metadata:') -or
        -not (@($frontmatter | Where-Object { $_ -match '^\s+version: "[^"]+"$' }).Count -gt 0)) {
        throw "Invalid skill frontmatter: $skill"
    }
    foreach ($required in @('references/review-protocol.md', 'references/critique-rubric.md')) {
        if (-not (Test-Path -LiteralPath (Join-Path $Root $required) -PathType Leaf)) { throw "Missing $required" }
    }
    $text = $lines -join [Environment]::NewLine
    foreach ($match in [regex]::Matches($text, '\]\((references/[^)#]+\.md)\)')) {
        $reference = $match.Groups[1].Value
        if (-not (Test-Path -LiteralPath (Join-Path $Root $reference) -PathType Leaf)) {
            throw "Broken reference: $reference"
        }
    }
}
function Get-RelativeFiles([string]$Root) {
    $prefix = $Root.TrimEnd([char[]]@('\', '/')) + [IO.Path]::DirectorySeparatorChar
    @(Get-ChildItem -LiteralPath $Root -File -Recurse -Force | ForEach-Object {
        $_.FullName.Substring($prefix.Length)
    } | Sort-Object)
}
function Test-SameTree([string]$Left, [string]$Right) {
    if (-not (Test-Path -LiteralPath $Right -PathType Container)) { return $false }
    try { Assert-Layout $Right } catch { return $false }
    $leftFiles = @(Get-RelativeFiles $Left)
    $rightFiles = @(Get-RelativeFiles $Right)
    if ($leftFiles.Count -ne $rightFiles.Count) { return $false }
    for ($i = 0; $i -lt $leftFiles.Count; $i++) {
        if ($leftFiles[$i] -cne $rightFiles[$i]) { return $false }
        $a = (Get-FileHash -LiteralPath (Join-Path $Left $leftFiles[$i]) -Algorithm SHA256).Hash
        $b = (Get-FileHash -LiteralPath (Join-Path $Right $rightFiles[$i]) -Algorithm SHA256).Hash
        if ($a -cne $b) { return $false }
    }
    return $true
}
function New-BackupName {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    return Join-Path $backupsRoot "$stamp.$PID.$([guid]::NewGuid().ToString('N').Substring(0, 6))"
}

if ($Action -ne 'remove') {
    $sourceFull = [IO.Path]::GetFullPath($source).TrimEnd([char[]]@('\','/'))
    $homeFull = [IO.Path]::GetFullPath($codexHome).TrimEnd([char[]]@('\','/'))
    $sep = [IO.Path]::DirectorySeparatorChar
    if ($homeFull -eq $sourceFull -or $homeFull.StartsWith($sourceFull + $sep, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'CODEX_HOME must not be inside the source directory.'
    }
    Assert-Layout $source
    Write-Output "Source: $source"
}
Write-Output "Target: $target"
if (Test-Path -LiteralPath $target) {
    $existing = Get-Item -LiteralPath $target -Force
    if (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Refusing symlink at install target.' }
}
switch ($Action) {
    'check' {
        if (Test-SameTree $source $target) { Write-Output 'OK: installed files, SHA-256, frontmatter and links match.' }
        else { throw 'NOT SYNCED: missing or different installation.' }
    }
    'remove' {
        if (-not (Test-Path -LiteralPath $target)) { Write-Output 'Already absent; nothing changed.'; break }
        $backup = New-BackupName
        if ($DryRun) { Write-Output "DRY RUN: would move installed skill to $backup"; break }
        New-Item -ItemType Directory -Path $backupsRoot -Force | Out-Null
        Move-Item -LiteralPath $target -Destination $backup
        Write-Output "Removed from active skills; preserved at $backup"
    }
    'install' {
        if (Test-SameTree $source $target) { Write-Output 'Already up to date; nothing changed.'; break }
        if ((Test-Path -LiteralPath $target) -and -not (Test-Path -LiteralPath $target -PathType Container)) {
            throw 'Target is not a directory; refusing to replace.'
        }
        if ($DryRun) {
            Write-Output 'DRY RUN: would stage source and back up any existing installation before activation.'
            break
        }
        New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
        $stage = Join-Path $skillsRoot ('.visual-design-review.stage.' + [guid]::NewGuid().ToString('N'))
        $backup = $null
        try {
            Copy-Item -LiteralPath $source -Destination $stage -Recurse -Force
            if (-not (Test-SameTree $source $stage)) { throw 'Staging verification failed.' }
            if (Test-Path -LiteralPath $target) {
                $backup = New-BackupName
                New-Item -ItemType Directory -Path $backupsRoot -Force | Out-Null
                Move-Item -LiteralPath $target -Destination $backup
            }
            try {
                Move-Item -LiteralPath $stage -Destination $target
            } catch {
                $activationError = $_
                if ($backup -and (Test-Path -LiteralPath $backup)) {
                    try {
                        # A failed cross-device move can leave a partial target; clear it before restoring.
                        if (Test-Path -LiteralPath $target -PathType Container) {
                            Remove-Item -LiteralPath $target -Recurse -Force
                        } elseif (Test-Path -LiteralPath $target) {
                            Remove-Item -LiteralPath $target -Force
                        }
                        Move-Item -LiteralPath $backup -Destination $target
                    } catch {
                        Write-Warning "Rollback failed; previous installation is at $backup"
                    }
                }
                throw $activationError
            }
            Write-Output 'Installed and SHA-256-verified.'
            if ($backup) { Write-Output "Previous installation preserved at $backup" }
        } finally {
            if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
        }
    }
}
