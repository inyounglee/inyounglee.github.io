# Cursor Agent Prompt

이 폴더의 스크립트는 **Cursor SDK API**로 현재 작업 중인(또는 지정한) agent에 프롬프트를 보냅니다.

- JavaScript: `prompt-agent.js` (`@cursor/sdk`)
- PowerShell: `Invoke-CursorAgent.ps1`

로컬 런타임은 이 저장소 디스크를 대상으로 agent 루프를 돌립니다. 모델 추론은 Cursor 호스트에서 이루어집니다.

## 준비

1. **Node.js 22.13 이상**
2. **API 키** — [Cursor Dashboard → API Keys](https://cursor.com/dashboard/api)

PowerShell:

```powershell
$env:CURSOR_API_KEY = "cursor_..."
```

키가 없으면 SDK가 브라우저 로그인(`Cursor.auth.login`)을 시도할 수 있습니다.

## 실행

저장소에서:

```powershell
cd d:\works\inyounglee.github.io\auto\script
.\Invoke-CursorAgent.ps1 --help
```

처음 실행 시 `node_modules`가 없으면 `npm install`을 자동으로 합니다.

### 프롬프트 보내기

```powershell
.\Invoke-CursorAgent.ps1 --prompt "검은사막 주제 페이지 레이아웃을 점검해줘"
```

위치 인자도 됩니다.

```powershell
.\Invoke-CursorAgent.ps1 허브 랜딩의 검색창 문구를 더 짧게 바꿔줘
```

파일 또는 파이프:

```powershell
.\Invoke-CursorAgent.ps1 --prompt-file .\task.txt
Get-Content .\task.txt -Raw | .\Invoke-CursorAgent.ps1
```

### 어떤 agent에 붙는가

우선순위:

1. `--agent-id` 또는 환경 변수 `CURSOR_AGENT_ID`
2. 이 폴더의 `.last-agent-id` (직전 성공한 호출의 ID)
3. 이 저장소 cwd에서 가장 최근에 수정된 **로컬** agent
4. 없으면 **새 로컬 agent** 생성

항상 새로 만들려면:

```powershell
.\Invoke-CursorAgent.ps1 --new --prompt "처음부터 이 저장소 구조를 설명해줘"
```

목록만 보려면:

```powershell
.\Invoke-CursorAgent.ps1 --list
```

이어서 같은 대화에 보내려면 출력된 `[agent] ...` ID를 쓰거나, 그냥 다시 실행하면 `.last-agent-id`를 재개합니다.

```powershell
.\Invoke-CursorAgent.ps1 --agent-id agent-xxxxxxxx --prompt "방금 변경을 커밋 메시지 초안으로 적어줘"
```

### Node로 직접 실행

```powershell
cd d:\works\inyounglee.github.io\auto\script
npm install
node prompt-agent.js --help
node prompt-agent.js --prompt "..."
```

## 옵션

| 옵션 | 설명 |
| --- | --- |
| `--help`, `-h` | 도움말 (`ps1` / `js` 모두 지원) |
| `--prompt`, `-p` | 프롬프트 문자열 |
| `--prompt-file`, `-f` | 프롬프트 파일 |
| `--agent-id`, `-a` | 기존 agent resume |
| `--new` | 새 agent |
| `--list` | 로컬 agent 목록 |
| `--cwd` | 작업 디렉터리 (기본: 저장소 루트) |
| `--model` | 모델 ID (기본 `composer-2.5`) |
| `--cloud` | 클라우드 agent 생성 |
| `--repo` | 클라우드용 Git URL |
| `--force` | 멈춘 로컬 run 만료 후 전송 |
| `--no-stream` | 스트림 없이 대기 |
| `--json` | JSON 결과 |

`bc-` 로 시작하는 ID는 클라우드, 그 외는 로컬로 재개합니다.

## 종료 코드

| 코드 | 의미 |
| --- | --- |
| 0 | 성공 |
| 1 | 시작 실패 (Node/키/설정/네트워크) |
| 2 | run은 시작됐으나 agent가 실패 |

## 참고

- SDK 문서: https://cursor.com/docs/sdk/typescript
- 이 경로는 Jekyll 사이트 배포에서 제외됩니다 (`_config.yml` `exclude: auto`).
- `.last-agent-id` 와 `node_modules` 는 git에 올리지 않습니다.
