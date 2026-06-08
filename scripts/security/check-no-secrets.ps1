$patterns = @(
  "(?i)(api[_-]?key|password|connection[_-]?string|accountkey|instrumentationkey)\s*[:=]\s*['""][^'""]{16,}['""]",
  "(?i)Bearer\s+[A-Za-z0-9_/\+=.-]{20,}",
  "https://[A-Za-z0-9.-]*webhook\.office\.com/[A-Za-z0-9_/\+=?.&%-]{20,}"
)
$files = Get-ChildItem -Recurse -File | Where-Object {
  $_.FullName -notlike "*\.git\*" `
    -and $_.FullName -notlike "*\node_modules\*" `
    -and $_.FullName -notlike "*\.next\*" `
    -and $_.FullName -notlike "*\__pycache__\*" `
    -and $_.FullName -notlike "*\docs\*" `
    -and $_.FullName -notlike "*\tests\*" `
    -and $_.FullName -notlike "*\scripts\security\*" `
    -and $_.Name -notlike "*.env.example"
}
$matches = $files | Select-String -Pattern $patterns
if ($matches) {
  $matches | ForEach-Object {
    Write-Host "$($_.Path):$($_.LineNumber):$($_.Line.Trim())"
  }
  throw "Potential secret-like value found."
}
Write-Host "No likely hardcoded secrets found."
