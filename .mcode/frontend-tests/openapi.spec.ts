import { test, expect } from "@playwright/test";

/**
 * Tests for the OpenAPI JSON spec endpoint.
 *
 * QA Report:
 *   - GET /api-docs/openapi.json returns HTTP 200 with Content-Type application/json
 *   - JSON body contains: openapi "3.0.4", title "Jellyfin API", version "12.0.0"
 *   - x-jellyfin-version "12.0.0"
 *   - server URL: http://localhost:8096
 *   - paths include /System/ActivityLog/Entries
 */
test.describe("OpenAPI JSON Spec", () => {
  test("GET /api-docs/openapi.json returns HTTP 200", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    expect(response.status()).toBe(200);
  });

  test("OpenAPI spec has correct content-type", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    const contentType = response.headers()["content-type"];
    expect(contentType).toContain("application/json");
  });

  test("OpenAPI spec contains correct title and version", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    const json = await response.json();
    expect(json.info.title).toBe("Jellyfin API");
    expect(json.info.version).toBe("12.0.0");
  });

  test("OpenAPI spec declares OAS 3.0.x", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    const json = await response.json();
    // QA Report: "openapi": "3.0.4"
    expect(json.openapi).toMatch(/^3\.0\./);
    expect(json.openapi).toBe("3.0.4");
  });

  test("OpenAPI spec contains x-jellyfin-version extension", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    const json = await response.json();
    expect(json.info["x-jellyfin-version"]).toBe("12.0.0");
  });

  test("OpenAPI spec server URL is localhost:8096", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    const json = await response.json();
    // QA Report: server URL is http://localhost:8096
    const urls: string[] = (json.servers ?? []).map((s: { url: string }) => s.url);
    expect(urls).toContain("http://localhost:8096");
  });

  test("OpenAPI spec includes System/ActivityLog/Entries path", async ({ request }) => {
    const response = await request.get("/api-docs/openapi.json");
    const json = await response.json();
    // QA Report: paths start with /System/ActivityLog/Entries
    expect(json.paths).toHaveProperty("/System/ActivityLog/Entries");
  });
});
