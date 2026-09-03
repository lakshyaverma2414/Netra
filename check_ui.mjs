import puppeteer from 'puppeteer';

(async () => {
  const depth = process.argv[2] || '1';
  const browser = await puppeteer.launch({ channel: 'chrome', headless: 'new' });
  const page = await browser.newPage();
  
  // Wait for the UI to load
  await page.goto('http://localhost:5173/cases/c1/network');
  await page.waitForSelector('input[placeholder="Entity ID (e.g. P001)"]', { timeout: 10000 });
  
  // wait for the initial fetch to finish so it doesn't pollute our test
  await new Promise(r => setTimeout(r, 2000));
  
  let apiResponse = null;
  page.on('response', async res => {
    if (res.url().includes('/api/v1/graph/explore?entity_id=P001&depth=' + depth)) {
      try {
        apiResponse = await res.json();
      } catch (e) {}
    }
  });
  
  await page.select('select', depth);
  
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const fetchBtn = btns.find(b => b.textContent.includes('Fetch Graph'));
    if(fetchBtn) fetchBtn.click();
  });
  
  await new Promise(r => setTimeout(r, 2000));
  
  const cyElements = await page.evaluate(() => {
    if (!window.cy) return null;
    return window.cy.elements().map(e => e.data());
  });
  
  console.log("API_RESPONSE:", JSON.stringify(apiResponse));
  console.log("CYTOSCAPE_ELEMENTS:", JSON.stringify(cyElements));
  
  await browser.close();
})();
