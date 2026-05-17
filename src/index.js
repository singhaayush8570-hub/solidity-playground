import { createServer } from "node:http";
import { loadEnv } from "./config/env.js";

const env = loadEnv();

const server = createServer((_req, res) => {
  res.writeHead(200, { "content-type": "application/json" });
  res.end(JSON.stringify({ service: "khatabook-saas", status: "ok", env: env.nodeEnv }));
});

server.listen(env.port, () => {
  console.log(`khatabook-saas listening on :${env.port}`);
});
