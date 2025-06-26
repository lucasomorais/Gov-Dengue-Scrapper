const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");
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

/**
 * Reads the system clipboard using PowerShell
 * @returns {Promise<string>}
 */
async function readClipboard() {
  return new Promise((resolve, reject) => {
    exec("powershell Get-Clipboard", (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

/**
 * Right-clicks on the header and copies the selected data
 */
async function copyAndParseColumn(page, header, headerText) {
  await header.click({ button: "right" });

  const copyButton = page.locator('button[role="menuitem"][title="Copy"].pbi-menu-trigger');
  await copyButton.waitFor({ state: "visible" });
  await copyButton.hover();

  const copySelection = page.locator('button[role="menuitem"][data-testid="pbimenu-item.Copy selection"]');
  await copySelection.waitFor({ state: "visible" });
  await copySelection.click();

  await page.waitForTimeout(500); // Wait for clipboard operation
  const copied = await readClipboard(); // Use PowerShell to read clipboard
  return parseCopiedData(headerText, copied);
}

(async () => {
  const { browser, page } = await navigateToDengue();
  const context = page.context();

  // page.pause();

  // Display as table if not already
  await page.getByRole("columnheader", { name: "Região|UF|Município" }).click({ button: "right" });
  const showAsTable = page.getByTestId("pbimenu-item.Show as a table");
  await showAsTable.waitFor({ state: "visible" });
  await showAsTable.click();
  await page.waitForTimeout(1000);

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
      console.log("⚠️ No headers found.");
      break;
    }

    const newHeaders = [];
    for (let i = 1; i < headers.length; i++) {
      const text = await headers[i].textContent();
      if (!processedHeaders.has(text)) newHeaders.push(headers[i]);
    }

    if (newHeaders.length === 0) {
      console.log("✅ No new headers. End of table.");
      break;
    }

    let shouldBreak = false;

    for (const header of newHeaders.slice(0, 5)) {
      const headerText = await header.textContent();
      processedHeaders.add(headerText);

      if (headerText.trim() === "Total") {
        console.log("🔚 Found 'Total'. Stopping collection.");
        shouldBreak = true;
        break;
      }

      const parsed = await copyAndParseColumn(page, header, headerText);
      allData.push(...parsed);
      // console.log(allData)
      console.log(`📋 Copied and processed: ${headerText}`);
    }

    if (shouldBreak) break;

    const box = await scrollBar.boundingBox();
    if (box) {
      const startX = lastScrollX ?? box.x + box.width / 2;
      const endX = startX + 80;

      await page.mouse.move(startX, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(endX, box.y + box.height / 2);
      await page.mouse.up();

      lastScrollX = endX;
      scrollIterations++;
      await page.waitForTimeout(1000);
    }
  }

  const outputDir = "output";
  fs.mkdirSync(outputDir, { recursive: true });

  const filename = path.join(outputDir, generateDatedFilename("semana_epidemiologica", "yaml", ""));
  const csvContent = ["UF,Ano/Semana,Casos prováveis de Dengue", ...allData.map((r) => r.join(","))].join("\n");

  fs.writeFileSync(filename, csvContent, "utf-8");
  console.log(`✅ Data saved to ${filename}`);

  await context.close();
  await browser.close();
})();