import { defineConfig } from "@playwright/test";

const isCI = Boolean(
  (globalThis as { process?: { env?: { CI?: string } } }).process?.env?.CI,
);

const desktop = {
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
  hasTouch: false,
  isMobile: false,
};

const mobile = {
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 1,
  hasTouch: true,
  isMobile: true,
};

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: isCI ? 2 : 0,
  timeout: 30_000,
  expect: {
    timeout: 5_000,
    toHaveScreenshot: {
      animations: "disabled",
      caret: "hide",
      maxDiffPixelRatio: 0.001,
      scale: "css",
    },
  },
  snapshotPathTemplate: "{testDir}/__screenshots__/{testFilePath}/{projectName}/{arg}{ext}",
  reporter: isCI
    ? [["github"], ["html", { open: "never" }]]
    : [["list"]],
  use: {
    baseURL: "http://127.0.0.1:7212",
    browserName: "chromium",
    locale: "en-GB",
    timezoneId: "Europe/Amsterdam",
    serviceWorkers: "block",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    video: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 7212",
    url: "http://127.0.0.1:7212",
    reuseExistingServer: !isCI,
    timeout: 120_000,
  },
  projects: [
    {
      name: "chromium-desktop-dark",
      use: { ...desktop, colorScheme: "dark" },
    },
    {
      name: "chromium-desktop-light",
      use: { ...desktop, colorScheme: "light" },
    },
    {
      name: "chromium-mobile-dark",
      use: { ...mobile, colorScheme: "dark" },
    },
    {
      name: "chromium-mobile-light",
      use: { ...mobile, colorScheme: "light" },
    },
  ],
});
