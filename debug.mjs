import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ channel: 'chrome', headless: 'new' });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5174/cases/C-002/network');
  await new Promise(r => setTimeout(r, 2000));
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const fetchBtn = btns.find(b => b.textContent.includes('Explore'));
    if(fetchBtn) fetchBtn.click();
  });
  
  await new Promise(r => setTimeout(r, 2000));
  
  const nodesFound = await page.evaluate(() => {
    if (!window.cy) return "NO CY INSTANCE";
    return window.cy.nodes().map(n => n.data('label') + " (" + n.data('id') + ")");
  });
  console.log("Nodes Found C-002:", nodesFound);
  
  await browser.close();
})();
