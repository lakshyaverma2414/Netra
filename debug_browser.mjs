import puppeteer from 'puppeteer-core';

(async () => {
    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new'
        });
        const page = await browser.newPage();
        
        page.on('console', msg => print(`[Browser] ${msg.type().toUpperCase()}: ${msg.text()}`));
        page.on('pageerror', err => print(`[Browser] PAGE ERROR: ${err.toString()}`));
        
        console.log("Navigating to http://127.0.0.1:4173/");
        await page.goto('http://127.0.0.1:4173/', { waitUntil: 'networkidle0' });
        
        const html = await page.content();
        console.log("HTML length:", html.length);
        if (html.length < 500) {
            console.log("HTML:", html);
        }
        
        await browser.close();
    } catch (e) {
        console.error("Script error:", e);
    }
})();
