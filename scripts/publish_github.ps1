# Publish the checked-out source to GitHub using the authenticated GitHub CLI.
# Private by default. Use -Public only when you want a public repository.
param(
    [string]$RepositoryName = "video-bulk-renaming",
    [switch]$Public
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
foreach ($command in @("git", "gh")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Required tool missing: $command. Install Git and GitHub CLI first."
    }
}
gh auth status
if ($LASTEXITCODE -ne 0) { throw "Sign in first with: gh auth login" }
$loggedInAs = gh api user --jq '.login'
if ($LASTEXITCODE -ne 0 -or $loggedInAs -ine 'cumaduran') {
    throw "GitHub CLI must be signed in as cumaduran (current: $loggedInAs)."
}
if (-not (Test-Path ".git")) {
    git init -b main
    if ($LASTEXITCODE -ne 0) { throw "git init failed" }
}
git add --all
if ($LASTEXITCODE -ne 0) { throw "git add failed" }
$pending = git diff --cached --name-only
if ($pending) {
    git commit -m "feat: initial EpisodeFlow desktop app"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed: configure your git user name/email" }
}
$remotes = git remote
if ($remotes -contains "origin") {
    $remote = git remote get-url origin
    if ($remote -notmatch ('(?i)(github\.com[:/])cumaduran/' + [regex]::Escape($RepositoryName) + '(\.git)?$')) {
        throw "Origin remote ($remote) is not cumaduran/$RepositoryName. Refusing to push."
    }
    git push -u origin HEAD
    if ($LASTEXITCODE -ne 0) { throw "git push failed" }
} else {
    $visibility = if ($Public) { "--public" } else { "--private" }
    gh repo create "cumaduran/$RepositoryName" $visibility --source . --remote origin --push
    if ($LASTEXITCODE -ne 0) { throw "GitHub repository creation/push failed" }
}
Write-Host "Published to: https://github.com/cumaduran/$RepositoryName"
Write-Host "For a download-ready EXE release, visit Actions > Build Windows EXE > Run workflow, and enter v1.0.0 in Release tag."
Write-Host "Or run: powershell -ExecutionPolicy Bypass -File .\scripts\create_release.ps1 -Version v1.0.0"
