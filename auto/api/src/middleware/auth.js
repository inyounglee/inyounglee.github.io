/**
 * HTTP API 자체 인증 (CURSOR_API_KEY와 별개).
 * API_TOKEN 미설정 시 로컬 개발용으로 인증을 건너뛴다.
 */

export function createAuthMiddleware({ token } = {}) {
  const expected = token?.trim() || process.env.API_TOKEN?.trim() || "";

  return function requireAuth(req, res, next) {
    if (!expected) return next();

    const header = req.headers.authorization || "";
    const bearer = header.startsWith("Bearer ") ? header.slice(7).trim() : "";
    const apiKey = (req.headers["x-api-key"] || "").toString().trim();
    const provided = bearer || apiKey;

    if (provided && provided === expected) return next();

    const err = new Error("unauthorized — set Authorization: Bearer <API_TOKEN> or X-API-Key");
    err.code = "UNAUTHORIZED";
    err.status = 401;
    throw err;
  };
}
