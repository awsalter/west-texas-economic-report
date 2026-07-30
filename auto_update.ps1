# Weekly auto-update for the West Texas Economic Report.
#
# Why this exists: the GitHub repo is a fork, and GitHub does not fire `schedule`
# events in forked repositories, so .github/workflows/update-data.yml never runs
# on its cron. This script does the same job from a local Windows Scheduled Task.
# If the fork is ever detached (Settings -> Danger Zone -> Leave fork network),
# the GitHub Action will start working again and this task can be deleted.

$ErrorActionPreference = 'Stop'
$repo = 'C:\Users\alexa\OneDrive\Documents\West Texas Economic Report'
$log  = Join-Path $repo 'auto_update.log'

function Log($msg) {
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -Path $log -Value $line -Encoding utf8
}

try {
    Set-Location $repo
    Log '--- run start ---'

    # 1. Rebuild the static dashboard (build.py loads .env for FRED/BEA keys).
    $py = Join-Path $repo '.venv\Scripts\python.exe'
    if (-not (Test-Path $py)) { throw "venv python not found at $py" }

    $out = & $py build.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        Log "BUILD FAILED (exit $LASTEXITCODE):"
        $out | ForEach-Object { Log "    $_" }
        exit 1
    }
    $out | ForEach-Object { Log "    $_" }

    # 2. Commit only the generated docs/ tree; leave everything else alone.
    & git add docs
    $staged = & git diff --cached --name-only
    if (-not $staged) {
        Log 'No data changes; nothing to commit.'
        Log '--- run end (no-op) ---'
        exit 0
    }
    Log ("Staged: {0}" -f ($staged -join ', '))

    & git commit -m 'Update dashboard data' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git commit failed (exit $LASTEXITCODE)" }

    # 3. Rebase onto any commits the GitHub Action pushed, so this task and the
    #    Action can coexist safely if the fork's cron starts firing again.
    & git pull --rebase 2>&1 | ForEach-Object { Log "    $_" }
    if ($LASTEXITCODE -ne 0) { throw "git pull --rebase failed (exit $LASTEXITCODE)" }

    # 4. Push to GitHub Pages.
    & git push 2>&1 | ForEach-Object { Log "    $_" }
    if ($LASTEXITCODE -ne 0) { throw "git push failed (exit $LASTEXITCODE)" }

    Log '--- run end (pushed) ---'
}
catch {
    Log ("ERROR: {0}" -f $_.Exception.Message)
    exit 1
}
