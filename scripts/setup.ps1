# Thin Windows launcher for the client-neutral installer.
param(
    [ValidateSet("claude", "codex", "both")][string]$Client = "both",
    [switch]$Check,
    [switch]$Update,
    [switch]$MigrateLegacy
)

$ErrorActionPreference = "Stop"
$RepoDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required: https://docs.astral.sh/uv/"
}
$Arguments = @("run", "--no-project", "python", (Join-Path $RepoDir "scripts/install.py"), "--client", $Client)
if ($Check) { $Arguments += "--check" }
if ($Update) { $Arguments += "--update" }
if ($MigrateLegacy) { $Arguments += "--migrate-legacy" }
& uv @Arguments
exit $LASTEXITCODE
