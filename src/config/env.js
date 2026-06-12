export function loadEnv() {
  const port = Number(process.env.PORT ?? "3000");
  const databaseUrl = process.env.DATABASE_URL ?? "";

  if (!databaseUrl) {
    throw new Error("DATABASE_URL is required");
  }

  return {
    nodeEnv: process.env.NODE_ENV ?? "development",
    port,
    databaseUrl,
  };
}
