import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ channel: 'chrome', headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  
  await page.goto('http://localhost:5174/cases/C-001/network');
  
  await page.waitForSelector('input[placeholder="Entity ID (e.g. P-001)"]', { timeout: 10000 });
  
  // Wait for loading to finish
  await new Promise(r => setTimeout(r, 2000));
  
  // Click fetch by evaluating all buttons
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const fetchBtn = btns.find(b => b.textContent.includes('Explore'));
    if(fetchBtn) fetchBtn.click();
  });
  
  await new Promise(r => setTimeout(r, 3000));
  
  const text = await page.evaluate(() => document.body.innerText);
  console.log("BODY TEXT:\n", text);
  
  const isCyRendered = await page.evaluate(() => {
    return document.querySelector('canvas') !== null;
  });
  console.log("Cytoscape Canvas Present:", isCyRendered);
  
  if (isCyRendered) {
      console.log("SUCCESS: Graph rendered successfully from the API.");
  } else {
      console.error("FAILED: Graph did not render.");
      process.exit(1);
  }
  
  await browser.close();
})();
