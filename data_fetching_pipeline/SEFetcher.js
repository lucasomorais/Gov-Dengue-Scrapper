const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');
const { navigateToDengue, generateDatedFilename, extractCardsData } = require('./utils');

async function SEFetcher() {
    let browser;
    try {
        console.log("Navigating to Dengue panel...");
        const { browser: launchedBrowser, page } = await navigateToDengue();
        browser = launchedBrowser;
        page.setDefaultTimeout(25000);

        const dropdownButton = page.locator("div.slicer-dropdown-menu[aria-label='SEM_PRI_SE']");
        await dropdownButton.waitFor({ state: "visible", timeout: 15000 });
        await dropdownButton.click();
        console.log("SEM_PRI_SE dropdown opened.");

        let popup = page.locator("div.slicer-dropdown-popup.focused");
        try {
            await popup.waitFor({ state: "visible", timeout: 10000 });
        } catch {
            console.log("Could not find focused popup. Trying generic visible...");
            popup = page.locator("div.slicer-dropdown-popup:visible").first();
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
        await page.locator("svg.card").first().waitFor({ state: "visible", timeout: 30000 });

        const cardData = await extractCardsData(page, { includeLetalidade: true });
        const semData = {
            Last_Epidemiological_Week: lastWeek,
            All_Semanas_Data: cardData
        };

        const dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '_');
        const outputDir = path.join(__dirname, '..', 'output', `dengue_${dateStr}`);
        fs.mkdirSync(outputDir, { recursive: true });
        const filePath = generateDatedFilename(`SE-Y-${lastWeek}`, "yaml", outputDir);
        fs.writeFileSync(filePath, yaml.dump(semData, { noRefs: true, sortKeys: false }), 'utf8');
        console.log(`✅ Data saved to ${filePath}`);
    } catch (err) {
        console.error(`❌ Error in SEFetcher: ${err.message}`);
        throw err;
    } finally {
        if (browser) {
            console.log("Closing browser.");
            await browser.close();
        }
    }
}

module.exports = { SEFetcher };

if (require.main === module) {
    SEFetcher().catch(console.error);
}