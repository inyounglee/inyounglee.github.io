import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";
import { sendJson, sendText } from "../lib/http.js";

const API_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const OPENAPI_PATH = path.join(API_ROOT, "openapi.yaml");
const SERVICE_VERSION = "1.0.0";

let cachedYaml;
let cachedJson;

async function loadOpenApi() {
  if (!cachedYaml) {
    cachedYaml = await readFile(OPENAPI_PATH, "utf8");
    cachedJson = YAML.parse(cachedYaml);
  }
  return { yaml: cachedYaml, json: cachedJson };
}

/**
 * @param {import('../lib/router.js').createRouter extends Function ? any : never} router
 */
export function registerSystemRoutes(router) {
  router.get("/health", async (_req, res) => {
    sendJson(res, 200, {
      status: "ok",
      service: "cursor-agent-http-api",
      version: SERVICE_VERSION,
      time: new Date().toISOString(),
    });
  });

  router.get("/openapi.yaml", async (_req, res) => {
    const { yaml } = await loadOpenApi();
    sendText(res, 200, yaml, "application/yaml; charset=utf-8");
  });

  router.get("/openapi.json", async (_req, res) => {
    const { json } = await loadOpenApi();
    sendJson(res, 200, json);
  });
}
