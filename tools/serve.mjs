// Zero-dependency static server that mirrors GitHub Pages for this repo:
// the repository root is served under /Roofing-JM/ (the Pages project base path),
// with HTTP Range support so video seeking behaves like production.
//   node tools/serve.mjs            -> http://127.0.0.1:4410/Roofing-JM/prototype/roof-sequence/
//   PORT=5000 BASE=/ node tools/serve.mjs
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const BASE = (process.env.BASE ?? "/Roofing-JM/").replace(/\/?$/, "/");
const PORT = Number(process.env.PORT || 4410);
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".mp4": "video/mp4", ".md": "text/plain; charset=utf-8" };
const BLOCK = [/^\/review\//, /^\/\.git/, /\/evidence-local\//, /\.blend$/];

export function createServer() {
  return http.createServer((req, res) => {
    let url = decodeURIComponent((req.url || "/").split("?")[0]);
    if (!url.startsWith(BASE)) { res.writeHead(404); return res.end("outside base path " + BASE); }
    let rel = "/" + url.slice(BASE.length);
    if (rel.endsWith("/")) rel += "index.html";
    if (BLOCK.some((r) => r.test(rel))) { res.writeHead(404); return res.end(); }
    const file = path.join(ROOT, rel);
    if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
    fs.stat(file, (err, st) => {
      if (err || !st.isFile()) {
        if (!err && st.isDirectory()) { res.writeHead(301, { Location: url + "/" }); return res.end(); }
        res.writeHead(404); return res.end("not found");
      }
      const type = TYPES[path.extname(file)] || "application/octet-stream";
      const range = req.headers.range && /bytes=(\d*)-(\d*)/.exec(req.headers.range);
      const headers = { "Content-Type": type, "Accept-Ranges": "bytes", "Cache-Control": "no-cache" };
      if (range) {
        let start = range[1] ? +range[1] : st.size - +range[2];
        let end = range[1] && range[2] ? +range[2] : st.size - 1;
        if (start >= st.size || start > end) { res.writeHead(416, { "Content-Range": `bytes */${st.size}` }); return res.end(); }
        end = Math.min(end, st.size - 1);
        res.writeHead(206, { ...headers, "Content-Range": `bytes ${start}-${end}/${st.size}`, "Content-Length": end - start + 1 });
        if (req.method === "HEAD") return res.end();
        return fs.createReadStream(file, { start, end }).pipe(res);
      }
      res.writeHead(200, { ...headers, "Content-Length": st.size });
      if (req.method === "HEAD") return res.end();
      fs.createReadStream(file).pipe(res);
    });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  createServer().listen(PORT, "127.0.0.1", () => console.log(`serving ${ROOT} at http://127.0.0.1:${PORT}${BASE}prototype/roof-sequence/`));
}
