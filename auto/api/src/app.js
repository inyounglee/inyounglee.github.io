/**
 * 라우트 등록 허브.
 * 새 도메인 API를 추가할 때:
 *   1) src/routes/<domain>.js 에 registerXxxRoutes(router) 작성
 *   2) 아래에서 import 후 호출
 *   3) openapi.yaml paths 에 문서 추가
 */

import { createRouter } from "./lib/router.js";
import { registerAgentRoutes } from "./routes/agents.js";
import { registerSystemRoutes } from "./routes/system.js";

export function buildRouter() {
  const router = createRouter();
  registerSystemRoutes(router);
  registerAgentRoutes(router);
  return router;
}
