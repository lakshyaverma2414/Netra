import puppeteer from 'puppeteer';

(async () => {
  let hasFailed = false;
  const browser = await puppeteer.launch({ channel: 'chrome', headless: 'new' });
  const page = await browser.newPage();
  
  const testCase = async (caseId, expectedLabels) => {
    console.log(`\nTesting Case: ${caseId}`);
    await page.goto(`http://localhost:5174/cases/${caseId}/network`);
    
    // Wait for the UI
    await page.waitForSelector('input[placeholder="Entity ID (e.g. P-001)"]', { timeout: 10000 });
    await new Promise(r => setTimeout(r, 2000));
    
    // Click fetch
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const fetchBtn = btns.find(b => b.textContent.includes('Explore'));
      if(fetchBtn) fetchBtn.click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    
    const isCyRendered = await page.evaluate(() => {
      return document.querySelector('canvas') !== null;
    });
    console.log("Cytoscape Canvas Present:", isCyRendered);
    if (!isCyRendered) {
        console.error("FAILED: Canvas not rendered.");
        hasFailed = true;
        return;
    }
    
    // Check if the expected ids are in the cytoscape instance
    const missing = await page.evaluate((labels) => {
      if (!window.cy) return labels;
      const nodes = window.cy.nodes();
      const nodeIds = nodes.map(n => n.data('id'));
      
      return labels.filter(l => !nodeIds.includes(l));
    }, expectedLabels);
    
    if (missing.length > 0) {
        console.error(`FAILED: Missing expected nodes in ${caseId}:`, missing);
        hasFailed = true;
    } else {
        console.log(`SUCCESS: Found expected nodes for ${caseId}`);
    }
    
    // Check negative relation P-001 <-> P-003 is NOT there
    const hasBadRelation = await page.evaluate(() => {
       if (!window.cy) return false;
       const edges = window.cy.edges();
       return edges.some(e => {
           return (e.data('source') === 'P-001' && e.data('target') === 'P-003') ||
                  (e.data('source') === 'P-003' && e.data('target') === 'P-001');
       });
    });
    
    if (hasBadRelation) {
        console.error("FAILED: Found NEEDS_REVIEW relationship which should NOT be projected.");
        hasFailed = true;
    } else {
        console.log("SUCCESS: NEEDS_REVIEW relationship is absent as expected.");
    }
  };

  await testCase('C-001', ['P-001', 'PH-001', 'LOC-001']);
  await testCase('C-002', ['P-002', 'PH-002', 'UPI-001']);
  await testCase('C-003', ['P-003', 'VEH-001', 'UPI-001']);

  await browser.close();
  
  if (hasFailed) process.exit(1);
  console.log("ALL TESTS PASSED!");
})();
