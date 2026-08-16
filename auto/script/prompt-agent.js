#!/usr/bin/env node
/**
 * Send a prompt to a Cursor agent (resume current/last agent, or create one).
 * Requires Node.js 22.13+ and CURSOR_API_KEY (or a prior Cursor.auth.login()).
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Agent, CursorAgentError } from "@cursor/sdk";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, "..", "..");
const LAST_ID_FILE = path.join(SCRIPT_DIR, ".last-agent-id");

const HELP = `
Cursor Agent Prompt — 현재(또는 지정한) Cursor agent에 프롬프트를 보냅니다.

사용법:
  node prompt-agent.js [옵션] [--] <프롬프트>
  node prompt-agent.js --list
  echo "프롬프트" | node prompt-agent.js

인증:
  CURSOR_API_KEY 환경 변수, 또는 Cursor Dashboard API 키.
  키가 없으면 Cursor.auth.login() 브라우저 로그인을 시도합니다.

기본 동작:
  1) --agent-id 또는 CURSOR_AGENT_ID
  2) auto/script/.last-agent-id 에 저장된 ID
  3) 이 저장소 cwd 의 가장 최근 로컬 agent
  4) 없으면 새 로컬 agent 생성

옵션:
  --help, -h              이 도움말
  --prompt, -p <text>     프롬프트 문자열
  --prompt-file, -f <path> 프롬프트를 파일에서 읽기
  --agent-id, -a <id>     이 agent에 이어서 요청 (resume)
  --new                   기존 agent를 무시하고 새로 생성
  --list                  이 cwd 의 로컬 agent 목록만 출력
  --cwd <path>            작업 디렉터리 (기본: 저장소 루트)
  --model <id>            모델 ID (기본: composer-2.5, 로컬 생성 시 필수)
  --cloud                 클라우드 agent 생성 (resume 시 ID가 bc- 이면 자동)
  --repo <url>            클라우드 생성 시 Git 저장소 URL
  --force                 로컬에서 멈춘 run이 있으면 강제 만료 후 전송
  --no-stream             스트리밍 없이 종료 결과만 출력
  --json                  종료 시 JSON으로 결과 출력
`.trim();

function printHelp() {
  console.log(HELP);
}

function fail(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function parseArgs(argv) {
  const opts = {
    help: false,
    list: false,
    isNew: false,
    force: false,
    noStream: false,
    json: false,
    cloud: false,
    prompt: null,
    promptFile: null,
    agentId: process.env.CURSOR_AGENT_ID || null,
    cwd: REPO_ROOT,
    model: process.env.CURSOR_MODEL || "composer-2.5",
    repo: process.env.CURSOR_CLOUD_REPO || null,
    rest: [],
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      const value = argv[++i];
      if (value == null || value.startsWith("-")) {
        fail(`옵션 ${arg} 에 값이 필요합니다.`);
      }
      return value;
    };

    switch (arg) {
      case "--help":
      case "-h":
      case "-Help":
      case "/?":
        opts.help = true;
        break;
      case "--list":
        opts.list = true;
        break;
      case "--new":
        opts.isNew = true;
        break;
      case "--force":
        opts.force = true;
        break;
      case "--no-stream":
        opts.noStream = true;
        break;
      case "--json":
        opts.json = true;
        break;
      case "--cloud":
        opts.cloud = true;
        break;
      case "--prompt":
      case "-p":
        opts.prompt = next();
        break;
      case "--prompt-file":
      case "-f":
        opts.promptFile = next();
        break;
      case "--agent-id":
      case "-a":
        opts.agentId = next();
        break;
      case "--cwd":
        opts.cwd = path.resolve(next());
        break;
      case "--model":
        opts.model = next();
        break;
      case "--repo":
        opts.repo = next();
        break;
      case "--":
        opts.rest.push(...argv.slice(i + 1));
        i = argv.length;
        break;
      default:
        if (arg.startsWith("-")) {
          fail(`알 수 없는 옵션: ${arg}\n--help 로 사용법을 확인하세요.`);
        }
        opts.rest.push(arg);
        break;
    }
  }

  return opts;
}

async function readStdinIfPiped() {
  if (process.stdin.isTTY) return "";
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8").trim();
}

async function resolvePrompt(opts) {
  if (opts.prompt) return opts.prompt;
  if (opts.promptFile) {
    return (await readFile(path.resolve(opts.promptFile), "utf8")).trim();
  }
  if (opts.rest.length) return opts.rest.join(" ").trim();
  return readStdinIfPiped();
}

async function loadLastAgentId() {
  try {
    const id = (await readFile(LAST_ID_FILE, "utf8")).trim();
    return id || null;
  } catch {
    return null;
  }
}

async function saveLastAgentId(agentId) {
  await mkdir(SCRIPT_DIR, { recursive: true });
  await writeFile(LAST_ID_FILE, `${agentId}\n`, "utf8");
}

function apiKey() {
  return process.env.CURSOR_API_KEY?.trim() || undefined;
}

function localOptions(cwd) {
  return { cwd };
}

function createOptions(opts) {
  const base = {
    apiKey: apiKey(),
    model: { id: opts.model },
  };
  if (opts.cloud) {
    base.cloud = {
      repos: opts.repo ? [{ url: opts.repo }] : [],
    };
  } else {
    base.local = localOptions(opts.cwd);
  }
  return base;
}

async function listLocalAgents(cwd) {
  try {
    const { items } = await Agent.list({
      runtime: "local",
      cwd,
      limit: 20,
    });
    return items.slice().sort((a, b) => (b.lastModified || 0) - (a.lastModified || 0));
  } catch (err) {
    console.error(`로컬 agent 목록을 읽지 못했습니다: ${err.message}`);
    return [];
  }
}

async function resolveAgent(opts) {
  if (opts.isNew) {
    const agent = await Agent.create(createOptions(opts));
    return { agent, created: true };
  }

  if (opts.agentId) {
    const agent = await Agent.resume(opts.agentId, {
      apiKey: apiKey(),
      model: { id: opts.model },
      local: opts.agentId.startsWith("bc-") ? undefined : localOptions(opts.cwd),
    });
    return { agent, created: false };
  }

  const lastId = await loadLastAgentId();
  if (lastId) {
    try {
      const agent = await Agent.resume(lastId, {
        apiKey: apiKey(),
        model: { id: opts.model },
        local: lastId.startsWith("bc-") ? undefined : localOptions(opts.cwd),
      });
      return { agent, created: false };
    } catch (err) {
      console.error(`저장된 agent(${lastId})를 재개하지 못했습니다: ${err.message}`);
    }
  }

  if (!opts.cloud) {
    const items = await listLocalAgents(opts.cwd);
    if (items.length) {
      const latest = items[0];
      const agent = await Agent.resume(latest.agentId, {
        apiKey: apiKey(),
        model: { id: opts.model },
        local: localOptions(opts.cwd),
      });
      return { agent, created: false };
    }
  }

  const agent = await Agent.create(createOptions(opts));
  return { agent, created: true };
}

function writeAssistantText(event) {
  if (event?.type !== "assistant" || !event.message?.content) return;
  for (const block of event.message.content) {
    if (block.type === "text" && block.text) process.stdout.write(block.text);
  }
}

async function streamRun(run, noStream) {
  if (noStream || !run.supports?.("stream")) {
    return run.wait();
  }

  try {
    for await (const event of run.stream()) {
      writeAssistantText(event);
    }
  } catch (err) {
    if (err?.name !== "UnsupportedRunOperationError") throw err;
  }

  const result = await run.wait();
  if (!noStream) process.stdout.write("\n");
  return result;
}

async function sendPrompt(agent, prompt, opts) {
  const payload = opts.force
    ? { text: prompt, local: { force: true } }
    : prompt;

  const run = await agent.send(payload);
  if (!opts.json) {
    console.error(`[agent] ${agent.agentId}`);
    if (run.id) console.error(`[run] ${run.id}`);
  }
  return streamRun(run, opts.noStream || opts.json);
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    return;
  }

  if (opts.list) {
    const items = await listLocalAgents(opts.cwd);
    if (!items.length) {
      console.log("이 cwd 에 로컬 agent가 없습니다.");
      return;
    }
    for (const item of items) {
      const when = item.lastModified
        ? new Date(item.lastModified).toISOString()
        : "-";
      console.log(
        [item.agentId, item.status || "-", when, item.name || "", item.summary || ""]
          .filter(Boolean)
          .join("\t"),
      );
    }
    return;
  }

  const prompt = await resolvePrompt(opts);
  if (!prompt) {
    fail("프롬프트가 없습니다. --prompt, 인자, --prompt-file, 또는 stdin을 사용하세요.\n--help 로 사용법을 확인하세요.");
  }

  const { agent, created } = await resolveAgent(opts);
  try {
    if (!opts.json) {
      console.error(created ? `[create] ${agent.agentId}` : `[resume] ${agent.agentId}`);
    }
    await saveLastAgentId(agent.agentId);
    const result = await sendPrompt(agent, prompt, opts);

    if (opts.json) {
      console.log(
        JSON.stringify(
          {
            agentId: agent.agentId,
            status: result.status,
            id: result.id,
            requestId: result.requestId,
            result: result.result,
          },
          null,
          2,
        ),
      );
    }

    if (result.status === "error") {
      fail(`run failed: ${result.id || agent.agentId}`, 2);
    }
  } finally {
    if (typeof agent[Symbol.asyncDispose] === "function") {
      await agent[Symbol.asyncDispose]();
    }
  }
}

main().catch((err) => {
  const retryable = err instanceof CursorAgentError ? ` retryable=${err.isRetryable}` : "";
  const helpUrl = err?.helpUrl ? `\n${err.helpUrl}` : "";
  console.error(`${err.name || "Error"}: ${err.message}${retryable}${helpUrl}`);
  process.exit(1);
});
