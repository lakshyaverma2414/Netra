import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ channel: 'chrome', headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  
  await page.goto('http://localhost:5173');
  
  // Wait for the input
  await page.waitForSelector('#entity-input');
  
  await page.select('#depth-select', '2');
  await page.click('#fetch-btn');
  
  // Wait for API response
  await new Promise(r => setTimeout(r, 2000));
  
  // Dump the dom
  const cyContainer = await page.evaluate(() => {
    return document.getElementById('cy-container')?.innerHTML || "NO_CONTAINER";
  });
  const errorMsg = await page.evaluate(() => {
    return document.getElementById('error-msg')?.innerText || "NO_ERROR";
  });
  
  console.log("Cytoscape Container HTML:", cyContainer);
  console.log("Error MSG:", errorMsg);
  
  await browser.close();
})();
