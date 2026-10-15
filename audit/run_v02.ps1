# v0.2 rerun after the adversarial review (local model only). Every stage runs in full; prompts whose text is
# unchanged since v0.1 are answered from the response cache (same key), so only changed prompts reach the model.
# Each step logs to data\run_v02.log and the next step runs even if one fails. Start detached with:
#   Start-Process powershell -ArgumentList "-NoProfile","-File","E:\Projects\math\audit\run_v02.ps1" -WindowStyle Hidden
# Watch with:  Get-Content E:\Projects\math\data\run_v02.log -Wait -Tail 20
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONIOENCODING = "utf-8"
$log = "data\run_v02.log"

function Step($name) {
    Add-Content $log "" -Encoding UTF8
    Add-Content $log "===== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $name =====" -Encoding UTF8
}
function Run([string]$pyArgs) {
    # cmd.exe redirection keeps Python's UTF-8 bytes as-is (PowerShell 5.1 redirection would write UTF-16)
    cmd /c "python -u $pyArgs >> $log 2>&1"
    Add-Content $log "exit $LASTEXITCODE" -Encoding UTF8
}

Step "0 keep a copy of the v0.1 database once, then clear the model-derived tables"
if (-not (Test-Path "data\audit_v0.1.db")) { Copy-Item "data\audit.db" "data\audit_v0.1.db" }
Run "audit\reset_run.py"
Step "1 paper side: OCR attach (page-boundary fix), proof choice log"
Run "audit\ocr_attach.py"
Run "audit\paper_text.py"
Step "2 static checks"
Run "audit\static_checks.py"
Step "3 locating: candidate files for every item"
Run "audit\xref_llm.py files"
Step "4 locating: multi-round search, all items"
Run "audit\xref_search.py --group all"
Step "5 decoy test"
Run "audit\decoy_test.py"
Step "6 comparison: Section 8, Lemma 10.5"
Run "audit\extract.py --section 8"
Run "audit\extract.py --section 10 --items `"Lemma 10.5`""
Step "7 proof steps: locate and compare"
Run "audit\proof_steps.py --items `"Lemma 8.2,Lemma 8.6,Lemma 10.5`""
Run "audit\extract.py --steps"
Step "8 adjudication of grouped differences"
Run "audit\adjudicate.py"
Step "9 report"
Run "audit\report.py"
Run "audit\extract.py --validate"
Step "done"
