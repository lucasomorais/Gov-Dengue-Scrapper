const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');
const { navigateToDengue, generateDatedFilename, extractCardsData } = require('./utils');

async function ensureDropdownOpen(page, selector) {
    const dropdown = page.locator(selector);
    const expanded = await dropdown.getAttribute("aria-expanded");
    if (expanded !== "true") {
        await dropdown.click();
        await page.locator("div.slicer-dropdown-popup", { hasText: '' }).first().waitFor({ state: "visible", timeout: 5000 });
    }
}

function allValuesChanged(globalData, newData, uf) {
    const keys = Object.keys(globalData);
    const unchanged = keys.filter(key => globalData[key] === newData[key]);

    if (unchanged.length === 0) {
        return true;
    } else {
        console.log(`🔁 Ainda há dados iguais aos globais em ${uf}:`);
        return false;
    }
}

async function bigNumbersUF() {
    let browser;
    try {
        const { browser: launchedBrowser, page } = await navigateToDengue();
        browser = launchedBrowser;

        const dropdownSelector = "div.slicer-dropdown-menu[aria-label='UF']";
        const dropdown = page.locator(dropdownSelector);
        await dropdown.waitFor({ state: 'visible' });
        await dropdown.click();
        await ensureDropdownOpen(page, dropdownSelector);
        console.log("📂 Dropdown aberto");

        const globalData = await extractCardsData(page, { includeLetalidade: false });
        console.log("🌍 Dados globais capturados.");
        console.log(globalData);

        const processedUFs = new Set();
        const ufData = {};

        while (true) {
            // Guarantee the UF dropdown items are visible before querying them
            await ensureDropdownOpen(page, dropdownSelector);
            await page.locator("div.slicerItemContainer").first().waitFor({ state: "visible", timeout: 5000 });

            const ufItems = await page.locator("div.slicerItemContainer").all();
            const ufTitles = [];

            for (const item of ufItems) {
                const title = await item.getAttribute("title");
                if (title && title.toLowerCase() !== "select all" && !processedUFs.has(title)) {
                    ufTitles.push(title);
                }
            }

            if (ufTitles.length === 0) break;

            for (const uf of ufTitles) {
                await ensureDropdownOpen(page, dropdownSelector);
                const item = page.locator(`div.slicerItemContainer[title="${uf}"]`);
                await item.scrollIntoViewIfNeeded();
                await item.waitFor({ state: "visible", timeout: 5000 });

                const isSelected = await item.getAttribute("aria-selected");
                if (isSelected !== "true") {
                    await item.click();
                    console.log(`🟢 Selecionada UF: ${uf}`);
                }

                await page.locator("svg.card").first().waitFor({ state: "visible", timeout: 10000 });

                async function captureUFDataUntilDifferent(uf, maxRetries = 5, delayMs = 2500) {
                    for (let attempt = 1; attempt <= maxRetries; attempt++) {
                        const data = await extractCardsData(page, { includeLetalidade: false });

                        if (allValuesChanged(globalData, data, uf)) {
                            console.log(`✅ Dados atualizados para ${uf}:`);
                            console.log(data);
                            return data;
                        } else {
                            console.log(`⏳ Tentativa ${attempt}/${maxRetries} para ${uf}`);
                            await page.waitForTimeout(delayMs);
                        }
                    }

                    console.warn(`⚠️ Timeout: Dados de ${uf} não mudaram totalmente. Salvando os dados assim mesmo.`);
                    return {data};
                }

                const data = await captureUFDataUntilDifferent(uf);
                ufData[uf] = data;

                await ensureDropdownOpen(page, dropdownSelector);
                await item.scrollIntoViewIfNeeded();
                await item.click();
                await page.waitForTimeout(1000);

                processedUFs.add(uf);
            }
        }

        const outputDir = path.join(__dirname, '..', 'output');
        const outputPath = generateDatedFilename('big_numbers_uf', 'yaml', outputDir);
        fs.mkdirSync('output', { recursive: true });
        fs.writeFileSync(outputPath, yaml.dump(ufData, { lineWidth: -1 }), 'utf-8');
        console.log(`✅ Dados salvos em ${outputPath}`);
    } catch (error) {
        console.error(`❌ Error in bigNumbersUF: ${error.message}`);
    } finally {
        if (browser) {
            console.log("Closing browser.");
            await browser.close();
        }
    }
}

module.exports = { bigNumbersUF };

if (require.main === module) {
    bigNumbersUF().catch(console.error);
}