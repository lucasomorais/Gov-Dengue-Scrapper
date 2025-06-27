const { chromium } = require('playwright');
const path = require('path');

const HEADLESS = true;

/**
 * Navega até o painel de Dengue no Power BI.
 * @returns {Promise<{ browser: Browser, page: Page }>}
 */
async function navigateToDengue() {
    const browser = await chromium.launch({ headless: HEADLESS });
    const page = await browser.newPage();

    await page.goto('https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc');
    await page.waitForLoadState('load');

    const dengueTab = page.getByRole('group', { name: /Exibir painel de Dengue/i }).locator('path').first();
    await dengueTab.waitFor({ state: 'visible', timeout: 10000 });
    await dengueTab.click();

    return { browser, page };
}

async function navigateToDengueHeadless() {
    const browser = await chromium.launch({ headless: false }); // Align with HEADLESS variable
    const page = await browser.newPage();

    await page.goto('https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc');
    await page.waitForLoadState('load');

    const dengueTab = page.getByRole('group', { name: /Exibir painel de Dengue/i }).locator('path').first();
    await dengueTab.waitFor({ state: 'visible', timeout: 10000 });
    await dengueTab.click();

    return { browser, page };
}

/**
 * Gera um nome de arquivo com data no formato YYYY_MM_DD
 * @param {string} baseName
 * @param {string} extension
 * @param {string} [outputDir='output']
 * @returns {string}
 */
function generateDatedFilename(baseName, extension, outputDir = 'output') {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0].replace(/-/g, '_');
    const filename = `${baseName}_${dateStr}.${extension}`;
    return path.join(outputDir, filename);
}

/**
 * Extrai dados dos cards SVG no formato { label: value }.
 * @param {import('playwright').Page | import('playwright').Locator} context - Contexto como `page` ou `section.locator(...)`
 * @param {Object} [options]
 * @param {boolean} [options.includeLetalidade=false] - Se deve incluir cards com "Letalidade"
 * @returns {Promise<Object>}
 */
async function extractCardsData(context, options = {}) {
    const { includeLetalidade = false } = options;

    const data = {};
    const cards = await context.locator("svg.card").all();

    for (let i = 0; i < cards.length; i++) {
        const card = cards[i];
        try {
            const valueLocator = card.locator("text.value tspan");
            const labelLocator = card.locator("text.label");

            await valueLocator.waitFor({ state: "visible", timeout: 5000 });
            const value = (await valueLocator.textContent())?.trim();

            let label = (await card.getAttribute("aria-label"))?.trim() || null;

            if (!label || label.toLowerCase().includes("card")) {
                try {
                    await labelLocator.waitFor({ state: "visible", timeout: 3000 });
                    label = (await labelLocator.textContent())?.trim();
                } catch {
                    label = `Card_${i + 1}_NoLabel`;
                }
            }

            // Clean the label: remove trailing numbers, values, or suffixes
            label = label?.replace(/\s*[:-]?\s*DENV.*$/, "")  // Remove "- DENV" or similar
                          .replace(/\s+\d+[.,]?\d*.*$/, "")   // Remove trailing numbers/values (e.g., "9,074")
                          .replace(/[:\-]\s*$/, "")           // Remove trailing colon or dash
                          .trim();

            if (!value || !label) continue;
            if (!includeLetalidade && label.toLowerCase().includes("letalidade")) continue;

            data[label] = value;
        } catch (e) {
            console.warn(`Erro ao processar card ${i + 1}: ${e.message}`);
        }
    }

    return data;
}

module.exports = {
    navigateToDengue,
    navigateToDengueHeadless,
    generateDatedFilename,
    extractCardsData
};