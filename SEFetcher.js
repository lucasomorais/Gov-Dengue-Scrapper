const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');
const { navigateToDengue, generateDatedFilename, HEADLESS } = require('./utils');

(async () => {
  let browser;
  try {
    console.log("Navigating to Dengue panel...");
    const { browser: launchedBrowser, page } = await navigateToDengue();
    browser = launchedBrowser;
    page.setDefaultTimeout(25000);

    // Wait for the SEM_PRI_SE dropdown to be visible
    const dropdownButton = page.locator("div.slicer-dropdown-menu[aria-label='SEM_PRI_SE']");
    await dropdownButton.waitFor({ state: "visible", timeout: 15000 });
    await dropdownButton.click();
    console.log("SEM_PRI_SE dropdown opened.");

    // Locate the dropdown popup
    let popup = page.locator("div.slicer-dropdown-popup.focused");
    try {
      await popup.waitFor({ state: "visible", timeout: 10000 });
    } catch {
      console.log("Could not find focused popup. Trying generic visible...");
      popup = page.locator("div.slicer-dropdown-popup:visible").first();
      await popup.waitFor({ state: "visible", timeout: 5000 });
    }

    // Access the items container within the popup
    const container = popup.locator(".slicerBody");
    await container.waitFor({ state: "visible", timeout: 10000 });
    console.log("Items container located.");

    // Handle the "Select all" option
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

    // Perform infinite scroll to load all dropdown items
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

    // Fetch data for the last week
    console.log(`Fetching data for week ${lastWeek}...`);
    await page.waitForTimeout(5000);

    try {
      await page.locator("svg.card").first().waitFor({ state: "visible", timeout: 30000 });
    } catch {
      console.warn("Data cards did not become visible.");
    }

    // Extract data from cards
    const cards = await page.locator("svg.card").all();
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
        const value = (await valueLocator.textContent({ timeout: 5000 }))?.trim() || null;

        let label = (await card.getAttribute("aria-label"))?.trim() || null;
        if (!label || (typeof label === 'string' && label.toLowerCase().includes("card"))) {
          try {
            await labelLocator.waitFor({ state: "visible", timeout: 3000 });
            label = (await labelLocator.textContent({ timeout: 3000 }))?.trim() || null;
          } catch {
            label = `Card_${i + 1}_NoLabel`;
          }
        }

        if (label && value) {
          console.log(`Card ${i + 1}: Label='${label}', Value='${value}'`);
          semData.All_Semanas_Data[label] = value;
        } else {
          console.warn(`Card ${i + 1}: Skipped due to missing label or value (Label='${label}', Value='${value}')`);
        }
      } catch (e) {
        console.warn(`Error processing card ${i + 1}: ${e.message}`);
      }
    }

    // Save data to a YAML file
    const outputDir = "output";
    fs.mkdirSync(outputDir, { recursive: true });
    const filePath = generateDatedFilename(`SE-Y-${lastWeek}`, "yaml", outputDir);

    fs.writeFileSync(filePath, yaml.dump(semData, { noRefs: true, sortKeys: false }), 'utf8');
    console.log(`✅ Data saved to ${filePath}`);

  } catch (err) {
    console.error(`❌ Error occurred: ${err.message}`);
  } finally {
    if (browser) {
      console.log("Closing browser.");
      await browser.close();
    }
  }
})();