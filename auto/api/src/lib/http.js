export function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(payload),
  });
  res.end(payload);
}

export function sendText(res, status, text, contentType = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": contentType,
    "Content-Length": Buffer.byteLength(text),
  });
  res.end(text);
}

export function sendError(res, status, error) {
  sendJson(res, status, {
    error: {
      name: error?.name || "Error",
      message: error?.message || String(error),
      code: error?.code,
      retryable: error?.retryable,
      helpUrl: error?.helpUrl,
    },
  });
}

export async function readJsonBody(req, { limitBytes = 1_000_000 } = {}) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > limitBytes) {
      const err = new Error(`request body exceeds ${limitBytes} bytes`);
      err.code = "PAYLOAD_TOO_LARGE";
      err.status = 413;
      throw err;
    }
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  const raw = Buffer.concat(chunks).toString("utf8").trim();
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    const err = new Error("invalid JSON body");
    err.code = "VALIDATION_ERROR";
    err.status = 400;
    throw err;
  }
}

export function getQuery(url) {
  const out = {};
  for (const [key, value] of url.searchParams.entries()) {
    out[key] = value;
  }
  return out;
}
