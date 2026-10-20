import { test, expect } from "@playwright/test";

/**
 * Tests for the Swagger/OpenAPI documentation UI.
 *
 * QA Report:
 *   - Root URL (/) redirects to /api-docs/swagger/index.html
 *   - Page title is "Jellyfin API"
 *   - h2.title contains "Jellyfin API"
 *   - Badge shows "12.0.0" and "OAS 3.0"
 *   - Link to /api-docs/openapi.json is visible
 *   - Authorize button is present
 *   - System section header is visible
 *   - Loading takes 8-10 seconds for the full API reference to appear
 */
test.describe("Swagger UI", () => {
  test("root URL redirects to Swagger UI", async ({ page }) => {
    const response = await page.goto("/");
    // After redirects, we should be on the Swagger UI page
    expect(page.url()).toContain("/api-docs/swagger/index.html");
  });

  test("Swagger page title is Jellyfin API", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await expect(page).toHaveTitle("Jellyfin API");
  });

  test("Swagger h2.title heading contains Jellyfin API", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    // Wait for Swagger UI to render its title
    await page.waitForSelector("h2.title", { timeout: 15000 });
    const heading = page.locator("h2.title");
    await expect(heading).toContainText("Jellyfin API");
  });

  test("Swagger UI shows API version badge 12.0.0", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await page.waitForSelector("h2.title", { timeout: 15000 });
    // QA Report: version badge contains "12.0.0"
    const versionBadge = page.locator(".version");
    await expect(versionBadge).toContainText("12.0.0");
  });

  test("Swagger UI shows link to openapi.json", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await page.waitForSelector("h2.title", { timeout: 15000 });
    // QA Report: a[href="/api-docs/openapi.json"] is visible
    const openapiLink = page.locator('a[href="/api-docs/openapi.json"]');
    await expect(openapiLink).toBeVisible();
  });

  test("Swagger UI shows Authorize button", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    await page.waitForSelector("h2.title", { timeout: 15000 });
    // QA Report: button.authorize.unlocked
    const authorizeBtn = page.locator("button.authorize");
    await expect(authorizeBtn).toBeVisible();
  });

  test("Swagger UI loading spinner disappears after API spec loads", async ({ page }) => {
    await page.goto("/api-docs/swagger/index.html");
    // Wait for the full API reference to render (LOADING spinner disappears)
    // QA Report: allow up to 10-15s for the large openapi.json to parse
    await page.waitForSelector(".loading-container", {
      state: "hidden",
      timeout: 20000,
    });
    // After loading, the System section should be visible
    const systemTag = page.locator(".opblock-tag", { hasText: "System" });
    await expect(systemTag).toBeVisible();
  });
});
