const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Downloads the Dengue CSV from Datasus Tabnet with "Município de residência" selected.
 */
async function cityCases() {
    const scriptDir = __dirname;
    const projectRoot = path.resolve(scriptDir, '..');
    const outputDir = path.join(projectRoot, 'output');

    // Ensure output directory exists
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '_'); // "yy-mm-dd"

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ acceptDownloads: true });
    const page = await context.newPage();

    // Step 1: Go to the page
    await page.goto('http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def');
    console.log(`Page title: ${await page.title()}`);

    // Step 2: Select "Município de residência"
    const select = page.locator('#L');
    await select.scrollIntoViewIfNeeded();
    await select.click();
    const option = page.locator('option[value="Município_de_residência"]');
    await option.scrollIntoViewIfNeeded();
    await option.click();

    // Optional: debug the selected value
    const selected = await select.inputValue();
    console.log(`Selected value: ${selected}`);

    // Step 3: Click "Mostra"
    const mostraButton = page.getByRole('button', { name: 'Mostra' });
    await mostraButton.scrollIntoViewIfNeeded();

    const [popup] = await Promise.all([
        page.waitForEvent('popup'),
        mostraButton.click()
    ]);

    console.log(`New page title: ${await popup.title()}`);
    await popup.waitForLoadState('networkidle');

    // Step 4: Download CSV
    const csvLink = popup.getByRole('link', { name: 'Copia como .CSV' });
    await csvLink.scrollIntoViewIfNeeded();

    const [download] = await Promise.all([
        popup.waitForEvent('download'),
        csvLink.click()
    ]);

    const filePath = path.join(outputDir, `city_cases_${timestamp}.csv`);
    await download.saveAs(filePath);

    console.log(`[SUCCESS] File saved to: ${filePath}`);
    await browser.close();
}

module.exports = { cityCases };
