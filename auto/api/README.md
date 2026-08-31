# Cursor Agent HTTP API

OpenAPI HTTP facade for `Invoke-CursorAgent` / `prompt-agent.js`.

## Quick start

```powershell
$env:CURSOR_API_KEY = "cursor_..."
cd auto/api
npm install
npm start
```

- Health: http://127.0.0.1:8787/health
- OpenAPI: http://127.0.0.1:8787/openapi.yaml
- Guide: [docs/cursor-agent-http-api.md](../../docs/cursor-agent-http-api.md)

## Scripts

| npm | 설명 |
| --- | --- |
| `npm start` | 서버 기동 |
| `npm run dev` | `--watch` 재시작 |

## Layout

```
auto/api/
  openapi.yaml          # 계약 (OpenAPI 3.1)
  src/
    server.js           # http 서버
    app.js              # 라우트 등록 허브
    lib/                # router, http helpers
    middleware/         # auth 등
    routes/             # system, agents — 도메인별 확장 지점
```

새 API 추가: `routes/` + `app.js` 등록 + `openapi.yaml` 갱신.
