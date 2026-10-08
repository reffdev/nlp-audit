# Overnight queue (local model only; no Phase 3). Each step logs to data\overnight.log and the next step
# runs even if one fails. Start detached so it survives closing the app:
#   Start-Process powershell -ArgumentList "-NoProfile","-File","E:\Projects\math\audit\run_overnight.ps1" -WindowStyle Hidden
# Watch with:  Get-Content E:\Projects\math\data\overnight.log -Wait -Tail 20
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONIOENCODING = "utf-8"
$log = "data\overnight.log"

function Step($name) {
    Add-Content $log "" -Encoding UTF8
    Add-Content $log "===== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $name =====" -Encoding UTF8
}
function Run([string]$pyArgs) {
    # cmd.exe redirection keeps Python's UTF-8 bytes as-is (PowerShell 5.1 redirection would write UTF-16)
    cmd /c "python -u $pyArgs >> $log 2>&1"
    Add-Content $log "exit $LASTEXITCODE" -Encoding UTF8
}

Step "1/3 decoy test (does a confident 'found' mean anything?)"
Run "audit\decoy_test.py"
Step "2/3 continue the 21 sampled items (weak 2-of-3 matches go to rounds 2-3)"
Run "audit\xref_search.py --group sample --resume"
Step "3/3 search the remaining 59 items"
Run "audit\xref_search.py --group rest"
Step "summary"
Run "audit\search_summary.py"
Step "done"
