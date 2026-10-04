// pw.mjs — find Playwright for the review app's browser tests (screens.mjs, save_stress.mjs).
// PLAYWRIGHT_DIR wins; otherwise the npx cache (~/.npm/_npx/*/node_modules/playwright), preferring a non-alpha release.
import { createRequire } from "module";
import { existsSync, readdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";

const require = createRequire(import.meta.url);
function findPlaywright() {
  if (process.env.PLAYWRIGHT_DIR) return process.env.PLAYWRIGHT_DIR;
  const base = join(homedir(), ".npm/_npx");
  const dirs = existsSync(base) ? readdirSync(base).map(d => join(base, d, "node_modules/playwright")).filter(existsSync) : [];
  const stable = dirs.filter(d => !require(join(d, "package.json")).version.includes("alpha"));
  if (!(stable.length || dirs.length)) throw new Error("Playwright not found: set PLAYWRIGHT_DIR");
  return (stable.length ? stable : dirs)[0];
}
export const { chromium } = require(findPlaywright());
