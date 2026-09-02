import puppeteer from 'puppeteer-core';

(async () => {
    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new'
        });
        const page = await browser.newPage();
        
        page.on('console', msg => console.log(`[Browser] ${msg.type().toUpperCase()}: ${msg.text()}`));
        page.on('pageerror', err => console.log(`[Browser] PAGE ERROR: ${err.toString()}`));
        
        console.log("Navigating to dashboard...");
        await page.goto('http://127.0.0.1:4173/dashboard', { waitUntil: 'networkidle0' });
        
        // Wait for loading to finish
        await new Promise(r => setTimeout(r, 1000));
        
        console.log("Typing search query...");
        await page.type('input[placeholder*="Search Case ID"]', 'NCRB-2026-001');
        
        console.log("Clicking search...");
        const [searchBtn] = await page.$x("//button[contains(., 'Search')]");
        if (searchBtn) {
            await searchBtn.click();
        } else {
            console.log("Search button not found!");
        }
        
        await new Promise(r => setTimeout(r, 500));
        
        const html = await page.content();
        if (html.includes("Case Summary: NCRB-2026-001")) {
            console.log("SUCCESS: Case summary rendered correctly.");
        } else if (html.includes("No case found")) {
            console.log("FAILURE: Rendered 'Not found'.");
        } else {
            console.log("FAILURE: Nothing rendered.");
        }
        
        await browser.close();
    } catch (e) {
        console.error("Script error:", e);
    }
})();
