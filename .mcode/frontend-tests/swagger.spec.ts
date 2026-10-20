import { test, expect } from "@playwright/test";

/**
 * Tests for the Swagger/OpenAPI documentation UI.
 *
 * QA Report:
 *   - Root URL (/) redirects to /api-docs/swagger/index.html
 *   - Page title is "Jellyfin API"
 *   - h1.title contains "Jellyfin API" (browser inspection confirmed h1, not h2)
 *   - .version badge shows "12.0.0"
 *   - Link to /api-docs/openapi.json is visible
 *   - button.authorize is present
 *   - h3.opblock-tag sections visible including "System"
 *
 * The large OpenAPI JSON (served from /api-docs/openapi.json) takes time to
 * parse — use waitForLoadState('networkidle') to ensure all resources have
 * settled before asserting on rendered content.
 */
test.describe("Swagger UI", () => {
  test("root URL redirects to Swagger UI", async ({ page }) => {
    await page.goto("/");
    // After redirects, we should land on the Swagger UI page
    expect(page.url()).toContain("/api-docs/swagger/index.html");
  });

  test("Swagger page title is Jellyfin API", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await expect(page).toHaveTitle("Jellyfin API");
  });

  test("Swagger h1.title heading contains Jellyfin API", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    // Wait for Swagger React app to fully render (fetches and parses openapi.json)
    await page.waitForLoadState("networkidle", { timeout: 45000 });
    // Browser inspection confirms the title element is h1.title (not h2)
    const heading = page.locator("h1.title");
    await expect(heading).toContainText("Jellyfin API");
  });

  test("Swagger UI shows API version badge 12.0.0", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await page.waitForLoadState("networkidle", { timeout: 45000 });
    // Browser inspection: .version elements contain "12.0.0" and "OAS 3.0"
    const versionBadge = page.locator(".version").first();
    await expect(versionBadge).toContainText("12.0.0");
  });

  test("Swagger UI shows link to openapi.json", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await page.waitForLoadState("networkidle", { timeout: 45000 });
    // QA Report: a[href="/api-docs/openapi.json"] is visible
    const openapiLink = page.locator('a[href="/api-docs/openapi.json"]');
    await expect(openapiLink).toBeVisible();
  });

  test("Swagger UI shows Authorize button", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await page.waitForLoadState("networkidle", { timeout: 45000 });
    // QA Report: button.authorize is present
    const authorizeBtn = page.locator("button.authorize");
    await expect(authorizeBtn).toBeVisible();
  });

  test("Swagger UI shows System API section after loading", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    // Wait for the full API reference to render
    await page.waitForLoadState("networkidle", { timeout: 45000 });
    // Browser inspection: h3.opblock-tag elements hold section names including "System"
    const systemTag = page.locator(".opblock-tag", { hasText: "System" }).first();
    await expect(systemTag).toBeVisible();
  });
});
