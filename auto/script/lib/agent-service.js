/**
 * Cursor agent 공용 서비스.
 * CLI(prompt-agent.js)와 HTTP API(auto/api)가 동일 로직을 사용한다.
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Agent, CursorAgentError } from "@cursor/sdk";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PACKAGE_DIR = path.resolve(SCRIPT_DIR, "..");
export const REPO_ROOT = path.resolve(PACKAGE_DIR, "..", "..");
export const LAST_ID_FILE = path.join(PACKAGE_DIR, ".last-agent-id");

export const DEFAULT_MODEL = process.env.CURSOR_MODEL || "composer-2.5";

export function apiKey() {
  return process.env.CURSOR_API_KEY?.trim() || undefined;
}

function localOptions(cwd) {
  return { cwd };
}

export function createOptions({ model = DEFAULT_MODEL, cloud = false, repo = null, cwd = REPO_ROOT } = {}) {
  const base = {
    apiKey: apiKey(),
    model: { id: model },
  };
  if (cloud) {
    base.cloud = {
      repos: repo ? [{ url: repo }] : [],
    };
  } else {
    base.local = localOptions(cwd);
  }
  return base;
}

export async function loadLastAgentId() {
  try {
    const id = (await readFile(LAST_ID_FILE, "utf8")).trim();
    return id || null;
  } catch {
    return null;
  }
}

export async function saveLastAgentId(agentId) {
  await mkdir(PACKAGE_DIR, { recursive: true });
  await writeFile(LAST_ID_FILE, `${agentId}\n`, "utf8");
}

export async function listLocalAgents(cwd = REPO_ROOT, limit = 20) {
  try {
    const { items } = await Agent.list({
      runtime: "local",
      cwd,
      limit,
    });
    return items.slice().sort((a, b) => (b.lastModified || 0) - (a.lastModified || 0));
  } catch (err) {
    const error = new Error(`로컬 agent 목록을 읽지 못했습니다: ${err.message}`);
    error.cause = err;
    throw error;
  }
}

/**
 * @param {object} opts
 * @param {boolean} [opts.isNew]
 * @param {string|null} [opts.agentId]
 * @param {string} [opts.cwd]
 * @param {string} [opts.model]
 * @param {boolean} [opts.cloud]
 * @param {string|null} [opts.repo]
 */
export async function resolveAgent(opts = {}) {
  const cwd = opts.cwd || REPO_ROOT;
  const model = opts.model || DEFAULT_MODEL;
  const cloud = Boolean(opts.cloud);
  const repo = opts.repo || null;

  if (opts.isNew) {
    const agent = await Agent.create(createOptions({ model, cloud, repo, cwd }));
    return { agent, created: true };
  }

  if (opts.agentId) {
    const agent = await Agent.resume(opts.agentId, {
      apiKey: apiKey(),
      model: { id: model },
      local: opts.agentId.startsWith("bc-") ? undefined : localOptions(cwd),
    });
    return { agent, created: false };
  }

  const lastId = await loadLastAgentId();
  if (lastId) {
    try {
      const agent = await Agent.resume(lastId, {
        apiKey: apiKey(),
        model: { id: model },
        local: lastId.startsWith("bc-") ? undefined : localOptions(cwd),
      });
      return { agent, created: false };
    } catch (err) {
      // fall through — resume failed
      console.error(`[agent-service] 저장된 agent(${lastId}) 재개 실패: ${err.message}`);
    }
  }

  if (!cloud) {
    try {
      const items = await listLocalAgents(cwd);
      if (items.length) {
        const latest = items[0];
        const agent = await Agent.resume(latest.agentId, {
          apiKey: apiKey(),
          model: { id: model },
          local: localOptions(cwd),
        });
        return { agent, created: false };
      }
    } catch {
      // create below
    }
  }

  const agent = await Agent.create(createOptions({ model, cloud, repo, cwd }));
  return { agent, created: true };
}

async function streamRun(run, { noStream = true, onAssistantText } = {}) {
  if (noStream || !run.supports?.("stream")) {
    return run.wait();
  }

  try {
    for await (const event of run.stream()) {
      if (event?.type === "assistant" && event.message?.content) {
        for (const block of event.message.content) {
          if (block.type === "text" && block.text && onAssistantText) {
            onAssistantText(block.text);
          }
        }
      }
    }
  } catch (err) {
    if (err?.name !== "UnsupportedRunOperationError") throw err;
  }

  return run.wait();
}

/**
 * Invoke-CursorAgent와 동일한 프롬프트 전송.
 * @returns {Promise<{ agentId: string, created: boolean, status: string, id?: string, requestId?: string, result?: unknown }>}
 */
export async function sendPrompt(options = {}) {
  const prompt = typeof options.prompt === "string" ? options.prompt.trim() : "";
  if (!prompt) {
    const err = new Error("prompt is required");
    err.code = "VALIDATION_ERROR";
    err.status = 400;
    throw err;
  }

  const cwd = options.cwd ? path.resolve(options.cwd) : REPO_ROOT;
  const { agent, created } = await resolveAgent({
    isNew: Boolean(options.isNew || options.new),
    agentId: options.agentId || null,
    cwd,
    model: options.model || DEFAULT_MODEL,
    cloud: Boolean(options.cloud),
    repo: options.repo || null,
  });

  try {
    await saveLastAgentId(agent.agentId);

    const payload = options.force
      ? { text: prompt, local: { force: true } }
      : prompt;

    const run = await agent.send(payload);
    const result = await streamRun(run, {
      noStream: options.noStream !== false,
      onAssistantText: options.onAssistantText,
    });

    return {
      agentId: agent.agentId,
      created,
      status: result.status,
      id: result.id,
      requestId: result.requestId,
      result: result.result,
    };
  } finally {
    if (typeof agent[Symbol.asyncDispose] === "function") {
      await agent[Symbol.asyncDispose]();
    }
  }
}

export function formatAgentError(err) {
  const retryable = err instanceof CursorAgentError ? err.isRetryable : undefined;
  return {
    name: err?.name || "Error",
    message: err?.message || String(err),
    code: err?.code,
    status: err?.status || (err instanceof CursorAgentError ? 502 : 500),
    retryable,
    helpUrl: err?.helpUrl,
  };
}

export { Agent, CursorAgentError };
