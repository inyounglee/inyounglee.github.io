#!/usr/bin/env node
/**
 * Cursor Agent HTTP API — OpenAPI 기반 로컬 서버.
 *
 *   cd auto/api
 *   npm install
 *   npm start
 *
 * ENV:
 *   PORT / HOST     기본 8787 / 127.0.0.1
 *   API_TOKEN       설정 시 Bearer / X-API-Key 필수
 *   CURSOR_API_KEY  Cursor SDK 인증
 */

import http from "node:http";
import { buildRouter } from "./app.js";
import { sendError, sendJson } from "./lib/http.js";

const HOST = process.env.HOST || "127.0.0.1";
const PORT = Number(process.env.PORT) || 8787;

const router = buildRouter();

const server = http.createServer(async (req, res) => {
  const started = Date.now();
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || `${HOST}:${PORT}`}`);
    const matched = router.match(req.method || "GET", url.pathname);

    if (!matched) {
      sendJson(res, 404, {
        error: {
          name: "NotFound",
          message: `no route for ${req.method} ${url.pathname}`,
          code: "NOT_FOUND",
        },
      });
      return;
    }

    await matched.handler(req, res, { url, params: matched.params });
  } catch (err) {
    const status = err?.status || 500;
    sendError(res, status, {
      name: err?.name || "Error",
      message: err?.message || String(err),
      code: err?.code,
      retryable: err?.retryable,
      helpUrl: err?.helpUrl,
    });
  } finally {
    const ms = Date.now() - started;
    console.error(`[http] ${req.method} ${req.url} ${res.statusCode || "-"} ${ms}ms`);
  }
});

server.listen(PORT, HOST, () => {
  console.error(`cursor-agent-http-api listening on http://${HOST}:${PORT}`);
  console.error(`OpenAPI: http://${HOST}:${PORT}/openapi.yaml`);
  console.error(`Health:  http://${HOST}:${PORT}/health`);
});
