const { chromium } = require('playwright');
const fs = require('fs');
const yaml = require('js-yaml');
const { HEADLESS } = require('./config');

// Função auxiliar para garantir que o dropdown está aberto
async function ensureDropdownOpen(page, selector) {
  const dropdown = page.locator(selector);
  const expanded = await dropdown.getAttribute("aria-expanded");
  if (expanded !== "true") {
    await dropdown.click();
    // Como "div.slicer-dropdown-popup" pode ter múltiplos elementos, pegar apenas o visível
    await page.locator("div.slicer-dropdown-popup", { hasText: '' }).first().waitFor({ state: "visible", timeout: 5000 });
  }
}

// Função para comparar se todos os valores são diferentes do globalData
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

(async () => {
  const browser = await chromium.launch({ headless: HEADLESS });
  const page = await browser.newPage();

  // Abre a visualização pública do Power BI
  await page.goto('https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc');
  // await page.pause();
  await page.waitForLoadState('load');

  // Clica na aba de "Dengue"
  const dengueTab = page.getByRole('group', { name: /Exibir painel de Dengue/i }).locator('path').first();
  await dengueTab.waitFor({ state: 'visible', timeout: 10000 });
  await dengueTab.click();

  const dropdownSelector = "div.slicer-dropdown-menu[aria-label='UF']";
  const dropdown = page.locator(dropdownSelector);
  await dropdown.waitFor({ state: 'visible' });
  await dropdown.click();
  await ensureDropdownOpen(page, dropdownSelector);
  console.log("📂 Dropdown aberto");

  // Captura dados globais (sem UF selecionada)
  const globalData = {};
  const cards = await page.locator("svg.card").all();
  for (const card of cards) {
    const ariaLabel = await card.getAttribute("aria-label");
    const value = await card.locator("text.value tspan").textContent();
    if (ariaLabel && value && !ariaLabel.includes("Letalidade")) {
      const label = ariaLabel.replace(value, "").trim().replace(" - DENV", "");
      globalData[label] = value;
    }
  }

  console.log("🌍 Dados globais capturados.");
  console.log(globalData);

  const processedUFs = new Set();
  const ufData = {};

  while (true) {
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

      // Função que captura dados repetidamente até todos serem diferentes do globalData
      async function captureUFDataUntilDifferent(uf, maxRetries = 10, delayMs = 1500) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          const data = {};
          const cards = await page.locator("svg.card").all();
          for (const card of cards) {
            const ariaLabel = await card.getAttribute("aria-label");
            const value = await card.locator("text.value tspan").textContent();
            if (ariaLabel && value && !ariaLabel.includes("Letalidade")) {
              const label = ariaLabel.replace(value, "").trim().replace(" - DENV", "");
              data[label] = value;
            }
          }

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
        return {};
      }

      const data = await captureUFDataUntilDifferent(uf);
      ufData[uf] = data;

      // Desmarcar UF
      await ensureDropdownOpen(page, dropdownSelector);
      await item.scrollIntoViewIfNeeded();
      await item.click();
      await page.waitForTimeout(1000);

      processedUFs.add(uf);
    }
  }

  // Salvar arquivo final
  fs.mkdirSync("output", { recursive: true });
  fs.writeFileSync("output/dengue_uf_data.yaml", yaml.dump(ufData, { lineWidth: -1 }), "utf-8");
  console.log("✅ Dados salvos em output/dengue_uf_data.yaml");

  await browser.close();
})();
