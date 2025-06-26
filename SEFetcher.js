const { chromium } = require('playwright');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

const HEADLESS = false;

(async () => {
  const browser = await chromium.launch({ headless: HEADLESS });
  const page = await browser.newPage();
  page.setDefaultTimeout(25000);

  try {
    console.log("Navigating to page...");
    await page.goto("https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/monitoramento-das-arboviroses", { waitUntil: 'load' });

    const cookieButton = page.locator("button.btn-accept");
    try {
      await cookieButton.waitFor({ state: "visible", timeout: 10000 });
      await cookieButton.click();
      console.log("Cookies accepted.");
    } catch {
      console.log("Cookie consent button not found or already accepted.");
    }

    await page.waitForLoadState("networkidle", { timeout: 35000 });
    console.log("Page loaded and network idle.");

    const frame = page.frameLocator("iframe[title='Sala Nacional de Arboviroses - SNA']").first();
    await frame.locator("body").waitFor({ state: "visible", timeout: 15000 });
    console.log("Iframe accessed");

    const dengueElement = frame.getByRole("group", { name: /Exibir painel de Dengue/i }).locator("path").first();
    await dengueElement.waitFor({ state: "visible", timeout: 10000 });
    await dengueElement.scrollIntoViewIfNeeded();
    await dengueElement.click({ delay: 500 });
    console.log("Dengue panel selected");

    await page.waitForTimeout(2000);

    const dropdownButton = frame.locator("div.slicer-dropdown-menu[aria-label='SEM_PRI_SE']");
    await dropdownButton.waitFor({ state: "visible", timeout: 15000 });
    await dropdownButton.click();
    console.log("SEM_PRI_SE dropdown opened.");

    let popup = frame.locator("div.slicer-dropdown-popup.focused");
    try {
      await popup.waitFor({ state: "visible", timeout: 10000 });
    } catch {
      console.log("Could not find focused popup. Trying generic visible...");
      popup = frame.locator("div.slicer-dropdown-popup:visible").first();
      await popup.waitFor({ state: "visible", timeout: 5000 });
    }

    const container = popup.locator(".slicerBody");
    await container.waitFor({ state: "visible", timeout: 10000 });
    console.log("Items container located.");

    const selectAll = popup.getByText("Select all", { exact: true });
    await selectAll.waitFor({ state: "visible", timeout: 10000 });
    const isChecked = await selectAll.evaluate(node =>
      node.checked || node.getAttribute("aria-checked") === "true" || node.parentElement.classList.contains("selected")
    );
    if (!isChecked) {
      await selectAll.click();
      console.log("Checked 'Select all'.");
      await page.waitForTimeout(1000);
    } else {
      console.log("'Select all' was already checked.");
    }

    console.log("Starting infinite scroll...");
    let lastWeek = null;
    let previousTitle = null;
    let attempts = 0;
    const maxAttempts = 50;

    while (attempts < maxAttempts) {
      attempts++;
      console.log(`Scroll attempt ${attempts}/${maxAttempts}`);

      const items = await container.locator("div.slicerItemContainer").all();
      const numericItems = [];

      for (const item of items) {
        const title = await item.getAttribute("title");
        if (title && /^\d+$/.test(title.trim())) {
          numericItems.push({ element: item, title: title.trim() });
        }
      }

      if (numericItems.length === 0) {
        if (attempts <= 3) await page.waitForTimeout(1000);
        else {
          console.warn("No numeric items found after several attempts.");
          break;
        }
        continue;
      }

      const lastItem = numericItems[numericItems.length - 1];
      const currentTitle = lastItem.title;
      console.log(`Current last visible week: ${currentTitle}`);

      if (attempts > 1 && currentTitle === previousTitle) {
        console.log("End of list detected.");
        lastWeek = currentTitle;
        break;
      }

      previousTitle = currentTitle;

      try {
        await lastItem.element.scrollIntoViewIfNeeded({ timeout: 5000 });
        await page.waitForTimeout(1500);
      } catch (e) {
        console.error(`Error during scroll: ${e}`);
        lastWeek = previousTitle;
        break;
      }
    }

    if (!lastWeek && previousTitle) {
      console.log(`Using last known week: ${previousTitle}`);
      lastWeek = previousTitle;
    }

    if (!lastWeek) {
      console.warn("Could not determine last week.");
      return;
    }

    console.log(`Fetching data for week ${lastWeek}...`);
    await page.waitForTimeout(5000);

    try {
      await frame.locator("svg.card").first().waitFor({ state: "visible", timeout: 30000 });
    } catch {
      console.warn("Data cards did not become visible.");
    }

    const cards = await frame.locator("svg.card").all();
    const semData = {
      Last_Epidemiological_Week: lastWeek,
      All_Semanas_Data: {}
    };

    console.log(`Found ${cards.length} cards.`);
    for (let i = 0; i < cards.length; i++) {
      try {
        const card = cards[i];
        const valueLocator = card.locator("text.value tspan");
        const labelLocator = card.locator("text.label");

        await valueLocator.waitFor({ state: "visible", timeout: 5000 });
        const value = await valueLocator.textContent({ timeout: 5000 });

        let label = await card.getAttribute("aria-label");
        if (!label || label.toLowerCase().includes("card")) {
          try {
            await labelLocator.waitFor({ state: "visible", timeout: 3000 });
            label = await labelLocator.textContent({ timeout: 3000 });
          } catch {
            label = `Card_${i + 1}_NoLabel`;
          }
        }

        if (label && value) {
          console.log(`Card ${i + 1}: Label='${label}', Value='${value}'`);
          semData.All_Semanas_Data[label.trim()] = value.trim();
        }
      } catch (e) {
        console.warn(`Error processing card ${i + 1}: ${e}`);
      }
    }

    const outputDir = "Informe_Semana_Epidemiologica/output";
    fs.mkdirSync(outputDir, { recursive: true });
    const filePath = path.join(outputDir, "SE-Y.yaml");

    fs.writeFileSync(filePath, yaml.dump(semData, { noRefs: true, sortKeys: false }), 'utf8');
    console.log(`✅ Data saved to ${filePath}`);

  } catch (err) {
    console.error(`❌ Error occurred: ${err}`);
  } finally {
    console.log("Closing browser.");
    await browser.close();
  }
})();
