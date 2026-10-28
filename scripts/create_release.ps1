# Trigger a downloadable GitHub release on a Windows-hosted GitHub Actions runner.
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\create_release.ps1 -Version v1.0.0
param(
    [ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$')]
    [string]$Version = 'v1.0.0'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI (gh) is required. Install it from https://cli.github.com/.'
}
gh auth status
if ($LASTEXITCODE -ne 0) {
    throw 'Sign in first with: gh auth login'
}
$repo = gh repo view --json nameWithOwner --jq '.nameWithOwner'
if ($LASTEXITCODE -ne 0 -or -not $repo) {
    throw 'Publish the repository to GitHub first (scripts/publish_github.ps1).'
}
if ($repo -ine 'cumaduran/video-bulk-renaming') {
    throw "Unexpected repository: $repo. Expected cumaduran/video-bulk-renaming."
}
gh workflow run build-windows.yml --ref main -f "release_tag=$Version"
if ($LASTEXITCODE -ne 0) {
    throw 'Could not start the GitHub Actions release workflow.'
}
Write-Host "Release build queued for $repo @ $Version"
Write-Host "Follow: https://github.com/$repo/actions/workflows/build-windows.yml"
Write-Host "When successful: https://github.com/$repo/releases"
