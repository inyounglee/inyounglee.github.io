/**
 * 확장 가능한 HTTP 라우트 레지스트리.
 * 새 API는 routes/*.js 에서 register(router) 만 추가하면 됩니다.
 */

export function createRouter() {
  /** @type {Array<{ method: string, pattern: RegExp, keys: string[], handler: Function }>} */
  const routes = [];

  function compilePath(pathPattern) {
    const keys = [];
    const parts = pathPattern.split("/").map((part) => {
      if (part.startsWith(":")) {
        keys.push(part.slice(1));
        return "([^/]+)";
      }
      return part.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    });
    return {
      keys,
      pattern: new RegExp(`^${parts.join("/")}$`),
    };
  }

  function add(method, pathPattern, handler) {
    const { keys, pattern } = compilePath(pathPattern);
    routes.push({ method: method.toUpperCase(), pattern, keys, handler });
  }

  return {
    get: (pathPattern, handler) => add("GET", pathPattern, handler),
    post: (pathPattern, handler) => add("POST", pathPattern, handler),
    put: (pathPattern, handler) => add("PUT", pathPattern, handler),
    patch: (pathPattern, handler) => add("PATCH", pathPattern, handler),
    delete: (pathPattern, handler) => add("DELETE", pathPattern, handler),
    /**
     * @returns {{ handler: Function, params: Record<string, string> } | null}
     */
    match(method, pathname) {
      const m = method.toUpperCase();
      for (const route of routes) {
        if (route.method !== m) continue;
        const matched = pathname.match(route.pattern);
        if (!matched) continue;
        const params = {};
        route.keys.forEach((key, i) => {
          params[key] = decodeURIComponent(matched[i + 1]);
        });
        return { handler: route.handler, params };
      }
      return null;
    },
  };
}
