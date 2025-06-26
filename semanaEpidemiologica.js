const fs = require("fs");
const path = require("path");
const clipboardy = require("clipboardy");
const { navigateToDengue, generateDatedFilename } = require("./utils");

/**
 * Parse copied data from clipboard into structured rows
 * @param {string} header - Header text (e.g., "2023/01")
 * @param {string} rawData - Tab-separated raw text
 * @returns {Array<Array<string>>}
 */
function parseCopiedData(header, rawData) {
  const lines = rawData.trim().split("\n");
  const parsed = [];
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split("\t");
    if (parts.length >= 4) {
      const uf = parts[1];
      const casos = parts[3].replace(",", "");
      parsed.push([uf, header, casos]);
    }
  }
  return parsed;
}

(async () => {
  const { browser, page } = await navigateToDengue();
  const context = page.context();
  page.pause()

  const allData = [];

  const columnHeaders = page.getByRole("columnheader");
  const scrollBar = page.locator(".pivotTable > div:nth-child(7) > .scroll-bar-part-bar").first();

  await scrollBar.scrollIntoViewIfNeeded();

  const processedHeaders = new Set();
  let lastScrollX = null;
  let scrollIterations = 0;

  while (true) {
    const headers = await columnHeaders.all();
    if (headers.length === 0) {
      console.log("No headers found.");
      break;
    }

    const newHeaders = [];
    for (let i = 1; i < headers.length; i++) {
      const text = await headers[i].textContent();
      if (!processedHeaders.has(text)) newHeaders.push(headers[i]);
    }

    if (newHeaders.length === 0) {
      console.log("No new headers. Finished scrolling.");
      break;
    }

    let shouldBreak = false;

    for (const header of newHeaders.slice(0, 5)) {
      const headerText = await header.textContent();

      await header.click({ button: "right" });

      const copyButton = page.locator('button[role="menuitem"][title="Copy"].pbi-menu-trigger');
      await copyButton.hover();

      const copySelection = page.locator('button[role="menuitem"][data-testid="pbimenu-item.Copy selection"]');
      await copySelection.click();

      await page.waitForTimeout(500);

      processedHeaders.add(headerText);

      if (headerText.trim() !== "Total") {
        const copied = await clipboardy.read();
        const rows = parseCopiedData(headerText, copied);
        allData.push(...rows);
        console.log(`Copied and parsed '${headerText}'`);
      } else {
        console.log("Found 'Total'. Stopping.");
        shouldBreak = true;
        break;
      }
    }

    if (shouldBreak) break;

    const box = await scrollBar.boundingBox();
    if (box) {
      const startX = lastScrollX ?? box.x + box.width / 2;
      const endX = startX + 119;

      await page.mouse.move(startX, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(endX, box.y + box.height / 2);
      await page.mouse.up();

      lastScrollX = endX;
      scrollIterations++;
      await page.waitForTimeout(1000);
    }
  }

  const outputDir = "SE_COMPLETA_2023-24";
  fs.mkdirSync(outputDir, { recursive: true });
  const filename = path.join(outputDir, generateDatedFilename("SE_COMPLETA_2023-24", "csv", ""));
  const csvContent = ["UF,Ano/Semana,Casos prováveis de Dengue", ...allData.map(row => row.join(","))].join("\n");
  fs.writeFileSync(filename, csvContent, "utf-8");

  console.log(`✅ Dados salvos em ${filename}`);
  await context.close();
  await browser.close();
})();
