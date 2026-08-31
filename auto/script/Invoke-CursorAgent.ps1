<#
.SYNOPSIS
  Cursor agent에 API로 프롬프트를 보냅니다.

.DESCRIPTION
  auto/script/prompt-agent.js 를 Node.js로 실행하는 래퍼입니다.
  의존성이 없으면 npm install 을 먼저 수행합니다.

.EXAMPLE
  .\Invoke-CursorAgent.ps1 --help
  .\Invoke-CursorAgent.ps1 --list
  .\Invoke-CursorAgent.ps1 --prompt "README의 로컬 실행 방법을 요약해줘"
#>
[CmdletBinding()]
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$RemainingArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
  [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
  [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
  $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
} catch {
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$JsEntry = Join-Path $ScriptDir "prompt-agent.js"
$PackageJson = Join-Path $ScriptDir "package.json"

function Show-Help {
  @"
Invoke-CursorAgent.ps1 — Cursor agent에 프롬프트를 보냅니다.

사용법:
  .\Invoke-CursorAgent.ps1 --help
  .\Invoke-CursorAgent.ps1 --list
  .\Invoke-CursorAgent.ps1 --prompt "할 일"
  .\Invoke-CursorAgent.ps1 --agent-id <id> --prompt "이어서 요청"
  .\Invoke-CursorAgent.ps1 --new --prompt "새 agent로 요청"
  Get-Content prompt.txt | .\Invoke-CursorAgent.ps1

인증:
  `$env:CURSOR_API_KEY 에 Cursor Dashboard API 키를 넣으세요.
  https://cursor.com/dashboard/api

옵션 (Node 스크립트에 그대로 전달):
  --help, -h                 이 도움말
  --prompt, -p <text>        프롬프트
  --prompt-file, -f <path>   프롬프트 파일
  --agent-id, -a <id>        기존 agent에 resume
  --new                      새 agent 생성
  --list                     로컬 agent 목록
  --cwd <path>               작업 디렉터리 (기본: 저장소 루트)
  --model <id>               모델 (기본: composer-2.5)
  --cloud                    클라우드 agent
  --repo <url>               클라우드 생성 시 저장소 URL
  --force                    멈춘 로컬 run 강제 만료
  --no-stream                스트리밍 없이 대기
  --json                     JSON 결과

종료 코드:
  0  성공
  1  시작 실패 (인증, 설정, Node 없음 등)
  2  agent run 이 실행되었으나 실패
"@
}

function Test-WantsHelp {
  param([string[]]$ArgsList)
  if (-not $ArgsList -or $ArgsList.Count -eq 0) { return $false }
  foreach ($arg in $ArgsList) {
    if ($arg -in @("--help", "-h", "-Help", "-help", "/?", "/help")) {
      return $true
    }
  }
  return $false
}

if (Test-WantsHelp -ArgsList $RemainingArgs) {
  Show-Help
  exit 0
}

if (-not (Test-Path -LiteralPath $JsEntry)) {
  Write-Error "prompt-agent.js 를 찾을 수 없습니다: $JsEntry"
  exit 1
}

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
  Write-Error "Node.js가 PATH에 없습니다. Node 22.13 이상을 설치하세요. https://nodejs.org/"
  exit 1
}

Push-Location $ScriptDir
try {
  $nodeModules = Join-Path $ScriptDir "node_modules\@cursor\sdk"
  if (-not (Test-Path -LiteralPath $nodeModules)) {
    if (-not (Test-Path -LiteralPath $PackageJson)) {
      Write-Error "package.json 이 없습니다: $PackageJson"
      exit 1
    }
    Write-Host "의존성 설치 중 (npm install)..."
    npm install --omit=dev
    if ($LASTEXITCODE -ne 0) {
      Write-Error "npm install 실패"
      exit 1
    }
  }

  $nodeArgs = @($JsEntry)
  if ($RemainingArgs) { $nodeArgs += $RemainingArgs }

  & node @nodeArgs
  exit $LASTEXITCODE
}
finally {
  Pop-Location
}
