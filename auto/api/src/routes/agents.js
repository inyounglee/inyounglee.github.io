import path from "node:path";
import {
  REPO_ROOT,
  formatAgentError,
  listLocalAgents,
  sendPrompt,
} from "cursor-agent-prompt/lib/agent-service.js";
import { getQuery, readJsonBody, sendError, sendJson } from "../lib/http.js";
import { createAuthMiddleware } from "../middleware/auth.js";

const requireAuth = createAuthMiddleware();

function mapAgent(item) {
  return {
    agentId: item.agentId,
    status: item.status || undefined,
    lastModified: item.lastModified || undefined,
    name: item.name || undefined,
    summary: item.summary || undefined,
  };
}

/**
 * /v1/agents* — Invoke-CursorAgent 대응. 이후 /v1/jobs 등도 동일 패턴으로 등록.
 */
export function registerAgentRoutes(router) {
  router.get("/v1/agents", async (req, res, ctx) => {
    requireAuth(req, res, () => {});
    const query = getQuery(ctx.url);
    const cwd = query.cwd ? path.resolve(query.cwd) : REPO_ROOT;
    const limit = Math.min(100, Math.max(1, Number(query.limit) || 20));

    try {
      const items = await listLocalAgents(cwd, limit);
      sendJson(res, 200, {
        cwd,
        items: items.map(mapAgent),
      });
    } catch (err) {
      const info = formatAgentError(err);
      sendError(res, info.status || 502, info);
    }
  });

  router.post("/v1/agents/prompt", async (req, res) => {
    requireAuth(req, res, () => {});
    const body = await readJsonBody(req);

    if (!body || typeof body.prompt !== "string" || !body.prompt.trim()) {
      sendError(res, 400, {
        name: "ValidationError",
        message: "prompt is required",
        code: "VALIDATION_ERROR",
      });
      return;
    }

    try {
      const result = await sendPrompt({
        prompt: body.prompt,
        agentId: body.agentId || null,
        isNew: Boolean(body.new),
        cwd: body.cwd || REPO_ROOT,
        model: body.model,
        cloud: Boolean(body.cloud),
        repo: body.repo || null,
        force: Boolean(body.force),
        noStream: true,
      });

      const statusCode = result.status === "error" ? 502 : 200;
      sendJson(res, statusCode, result);
    } catch (err) {
      const info = formatAgentError(err);
      sendError(res, info.status || 502, info);
    }
  });
}
