import { test, expect } from "@playwright/test";

/**
 * Tests for the public System Info endpoint.
 *
 * QA Report:
 *   - GET /System/Info/Public returns HTTP 200 JSON (no auth required)
 *   - JSON fields: Version "12.0.0", ProductName "Jellyfin Server",
 *     LocalAddress "http://127.0.0.1:8096", StartupWizardCompleted true
 *   - The Id field is a per-instance GUID — do NOT assert its value.
 */
test.describe("System Info Public Endpoint", () => {
  test("GET /System/Info/Public returns HTTP 200", async ({ request }) => {
    const response = await request.get("/System/Info/Public");
    expect(response.status()).toBe(200);
  });

  test("System info has correct content-type", async ({ request }) => {
    const response = await request.get("/System/Info/Public");
    const contentType = response.headers()["content-type"];
    expect(contentType).toContain("application/json");
  });

  test("System info reports Jellyfin Server product name", async ({ request }) => {
    const response = await request.get("/System/Info/Public");
    const json = await response.json();
    expect(json.ProductName).toBe("Jellyfin Server");
  });

  test("System info reports correct version 12.0.0", async ({ request }) => {
    const response = await request.get("/System/Info/Public");
    const json = await response.json();
    expect(json.Version).toBe("12.0.0");
  });

  test("System info includes required public fields", async ({ request }) => {
    const response = await request.get("/System/Info/Public");
    const json = await response.json();
    // Id is a per-instance GUID — only assert it exists and is a non-empty string
    expect(typeof json.Id).toBe("string");
    expect(json.Id.length).toBeGreaterThan(0);
    // LocalAddress and ServerName should be present
    expect(json.LocalAddress).toBeTruthy();
    expect(json.ServerName).toBeTruthy();
  });

  test("Startup wizard is marked completed", async ({ request }) => {
    // QA Report: StartupWizardCompleted: true
    const response = await request.get("/System/Info/Public");
    const json = await response.json();
    expect(json.StartupWizardCompleted).toBe(true);
  });
});
