import { test, expect } from "@playwright/test";

/**
 * Tests for the /health endpoint.
 *
 * QA Report: The endpoint returns plain-text "Healthy" with HTTP 200.
 * After server start there is a brief window (~2-4s) where it returns "Degraded"
 * while EF Core/SQLite migrations are running. Tests poll until the body equals
 * "Healthy" (with up to 10 seconds of retries).
 */
test.describe("Health Endpoint", () => {
  test("GET /health returns HTTP 200 with body Healthy", async ({ request }) => {
    // Poll until we get "Healthy" — the server may still be settling migrations.
    let lastBody = "";
    const deadline = Date.now() + 10_000;
    while (Date.now() < deadline) {
      const response = await request.get("/health");
      expect(response.status()).toBe(200);
      lastBody = (await response.text()).trim();
      if (lastBody === "Healthy") break;
      await new Promise((r) => setTimeout(r, 1000));
    }
    expect(lastBody).toBe("Healthy");
  });
});
