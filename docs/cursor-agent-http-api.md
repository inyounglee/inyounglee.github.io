# Cursor Agent HTTP API

`Invoke-CursorAgent.ps1` / `prompt-agent.js` 와 **같은 Cursor agent 호출**을 OpenAPI HTTP로 제공합니다.

- 스펙: [`auto/api/openapi.yaml`](../auto/api/openapi.yaml)
- 서버: [`auto/api`](../auto/api)
- 공용 로직: [`auto/script/lib/agent-service.js`](../auto/script/lib/agent-service.js)

CLI와 HTTP가 동일 서비스를 쓰므로, 동작·agent 해석 우선순위가 일치합니다.

## 아키텍처 (확장 전제)

```
HTTP 요청
  → auto/api/src/server.js
  → router (버전 경로 /v1/…)
  → routes/*.js 핸들러
  → auto/script/lib/agent-service.js
  → @cursor/sdk (Agent.create / resume / send)
```

확장 시:

1. `auto/api/src/routes/<domain>.js` 에 `registerXxxRoutes(router)` 추가
2. `auto/api/src/app.js` 에서 등록
3. `auto/api/openapi.yaml` 의 `paths` / `components` 갱신
4. 필요하면 `agent-service.js` 에 도메인 로직 추가 (CLI·HTTP 공용)

`/v1` 은 호환 계약입니다. 브레이킹 변경은 `/v2` 를 새로 등록하세요.

## 준비

1. **Node.js 22.13+**
2. Cursor API 키: [Dashboard → API Keys](https://cursor.com/dashboard/api)

```powershell
$env:CURSOR_API_KEY = "cursor_..."
# (선택) HTTP API 자체 보호
$env:API_TOKEN = "local-secret"
```

```powershell
cd d:\works\inyounglee.github.io\auto\api
npm install
npm start
```

기본 수신: `http://127.0.0.1:8787`

| 환경 변수 | 기본 | 설명 |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | 바인드 주소 |
| `PORT` | `8787` | 포트 |
| `API_TOKEN` | (없음) | 설정 시 Bearer / `X-API-Key` 필수 |
| `CURSOR_API_KEY` | (없음) | Cursor SDK 인증 |
| `CURSOR_MODEL` | `composer-2.5` | 기본 모델 |

## OpenAPI

- YAML: `GET /openapi.yaml`
- JSON: `GET /openapi.json`
- 헬스: `GET /health` (인증 없음)

Swagger UI / Postman / Insomnia 에 `http://127.0.0.1:8787/openapi.yaml` 을 임포트하면 됩니다.

## 엔드포인트

### `GET /v1/agents`

`Invoke-CursorAgent.ps1 --list` 대응.

```powershell
Invoke-RestMethod http://127.0.0.1:8787/v1/agents
```

쿼리: `cwd`, `limit` (1–100, 기본 20)

### `POST /v1/agents/prompt`

`Invoke-CursorAgent.ps1 --prompt "..."` 대응.

```powershell
$body = @{
  prompt = "README의 로컬 실행 방법을 요약해줘"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method POST `
  -Uri http://127.0.0.1:8787/v1/agents/prompt `
  -ContentType "application/json" `
  -Body $body
```

`API_TOKEN` 사용 시:

```powershell
$headers = @{ Authorization = "Bearer $env:API_TOKEN" }
# 또는: @{ "X-API-Key" = $env:API_TOKEN }

Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8787/v1/agents/prompt `
  -Headers $headers -ContentType "application/json" -Body $body
```

curl:

```bash
curl -s http://127.0.0.1:8787/v1/agents/prompt \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{"prompt":"허브 랜딩 문구를 짧게 다듬어줘","new":false}'
```

#### 요청 본문

| 필드 | 타입 | 설명 | CLI 대응 |
| --- | --- | --- | --- |
| `prompt` | string | 필수 | `--prompt` |
| `agentId` | string | 재개 ID | `--agent-id` |
| `new` | boolean | 새 agent | `--new` |
| `cwd` | string | 작업 디렉터리 | `--cwd` |
| `model` | string | 모델 ID | `--model` |
| `cloud` | boolean | 클라우드 | `--cloud` |
| `repo` | string | 클라우드 Git URL | `--repo` |
| `force` | boolean | 멈춘 run 강제 | `--force` |

Agent 해석 우선순위는 CLI와 동일합니다: `agentId` → `.last-agent-id` → 최근 로컬 agent → 신규 생성.

#### 응답 예

```json
{
  "agentId": "agent-xxxxxxxx",
  "created": false,
  "status": "finished",
  "id": "run-…",
  "requestId": "…",
  "result": "…"
}
```

`status` 가 `error` 이면 HTTP `502` 와 함께 동일 JSON이 반환될 수 있습니다.

## CLI와의 관계

| 방식 | 경로 | 용도 |
| --- | --- | --- |
| PowerShell | `auto/script/Invoke-CursorAgent.ps1` | 터미널·수동 |
| Node CLI | `auto/script/prompt-agent.js` | 스크립트 |
| HTTP | `auto/api` | 다른 앱·자동화·OpenAPI 클라이언트 |

세 경로 모두 `agent-service.js` 를 사용합니다.

## 보안 메모

- 기본은 `127.0.0.1` 바인딩입니다. 외부 노출 시 반드시 `API_TOKEN` 을 설정하세요.
- `CURSOR_API_KEY` 는 서버 프로세스 환경에만 두고, HTTP 클라이언트로 전달하지 마세요.
- 이 트리는 Jekyll 배포에서 제외됩니다 (`_config.yml` 의 `auto`, `docs`).

## 참고

- CLI 가이드: [`auto/script/README.md`](../auto/script/README.md)
- Cursor SDK: https://cursor.com/docs/sdk/typescript
