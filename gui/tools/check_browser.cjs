// Exercise the packaged UI with synthetic transport/worker output. No research inference.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {spawn} = require('node:child_process');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const release = path.resolve(process.argv[2]);
const output = path.resolve(process.argv[3]);
const python = process.env.TEST_PYTHON || 'python3';
const work = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'filterflip-browser-')), 'fixture');
const worker = spawn(python, ['-B', path.join(release, 'tools/browser_lifecycle_fixture.py'),
    '--work', work, '--port', '0']);
let browser;
let transcript = '';
let pageErrors = [];
const checks = [];
const hostile = '<img src=x onerror="window.securityProbe=1"><script>window.securityProbe=2</script>';

async function run() {
    const address = await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(Error('Fixture startup timeout')), 20000);
        worker.stdout.on('data', data => {
            transcript += data;
            const found = transcript.match(/http:\/\/127\.0\.0\.1:\d+/);
            if (found) { clearTimeout(timer); resolve(found[0]); }
        });
        worker.stderr.on('data', data => { transcript += data; });
        worker.on('exit', code => { clearTimeout(timer); reject(Error('Fixture exit ' + code)); });
    });
    browser = await chromium.launch({executablePath: process.env.CHROME_BINARY || '/usr/bin/google-chrome',
        headless: true, args: ['--no-sandbox', '--disable-background-networking']});
    const context = await browser.newContext({viewport: {width: 1440, height: 1000}, acceptDownloads: true});
    const page = await context.newPage();
    page.on('pageerror', error => pageErrors.push(String(error)));
    await context.route('**/*', route => {
        if (new URL(route.request().url()).origin === address) return route.continue();
        return route.abort();
    });
    await page.goto(address);
    await page.locator('#case option').first().waitFor({state: 'attached'});
    await page.selectOption('#mode', 'challenge');
    await page.selectOption('#case', 'NanoNQ:test1009');
    assert.match(await page.locator('#explanation').innerText(), /four fresh answers/);
    assert.doesNotMatch(await page.locator('#explanation').innerText(), /teammate|v2\.4/);
    checks.push('current challenge selection loads and explains fresh generation');
    await page.locator('#study-tab').click();
    await page.locator('#trust-case option').first().waitFor({state:'attached'});
    assert.match(await page.locator('#study').innerText(), /8 \/ 59/);
    checks.push('findings and limitations render');
    const dataset = JSON.parse(fs.readFileSync(path.join(release,'app/data/findings.json'),'utf8'));
    const trustSection = page.locator('.finding-section').filter({has:page.locator('#trust-case')});
    await trustSection.locator(':scope > summary').click();
    for (const c of dataset.trust) {
        await page.selectOption('#trust-case',c.id);
        const actual=await page.locator('#trust-view').textContent();
        for(const ctx of c.contexts){
            for(const arm of ['U','T']) assert.ok(actual.includes(ctx.answers[arm].answer),c.id+' exact answer');
            for(const p of ctx.passages) assert.ok(actual.includes(p.text),c.id+' exact passage');
        }
        assert.ok(actual.includes(c.rationale));
    }
    checks.push('all 12 TrustRAG cases: 72 linked answers, 180 passage positions and current rationales render exactly');
    await page.selectOption('#trust-case','NanoMSMARCO:1028652');
    await page.locator('.trust-context').filter({hasText:/^PN1/}).locator('summary').first().click();
    await page.locator('#study').screenshot({path:path.join(output,'findings_desktop.png')});
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
    await page.screenshot({path:path.join(output,'findings_mobile.png')});
    checks.push('findings remains within mobile viewport with scrollable tables');
    await page.setViewportSize({width:1440,height:1000});
    await page.getByRole('button',{name:'Inspect Heather’s saved evidence',exact:true}).click();
    await page.locator('#saved-focus').getByText('PN1',{exact:false}).first().waitFor();
    checks.push('findings opens the corresponding recorded Heather case');

    await page.locator('#saved-tab').click();
    await page.selectOption('#saved-case', 'NanoNQ:test1009');
    await page.locator('#load-saved').click();
    await page.locator('#saved-overview button').filter({hasText: /^PN2$/}).click();
    assert.match(await page.locator('#saved-focus').innerText(), /PN2/);
    await page.screenshot({path: path.join(output, 'browser_saved_evidence.png'), fullPage: true});
    checks.push('all-nine table opens PN2 and its paired answers');
    await page.route('**/api/reference/NanoNQ:test1009', async route => {
        const response = await route.fetch();
        const body = await response.json();
        body.question = hostile;
        body.conditions.C.answers.filtered.answer = hostile;
        body.conditions.C.passages[0].text = hostile;
        await route.fulfill({response, json: body});
    });
    await page.locator('#live-tab').click();
    await page.selectOption('#mode', 'original');
    await page.selectOption('#case', 'NanoNQ:test1009');
    await page.locator('#reference').click();
    await page.locator('#reference-panel').waitFor({state: 'visible'});
    assert.ok((await page.locator('#reference-panel').innerText()).includes(hostile));
    assert.equal(await page.locator('#reference-panel img, #reference-panel script').count(), 0);
    assert.equal(await page.evaluate(() => window.securityProbe), undefined);
    checks.push('hostile question, saved answer and passage render as literal text');
    await page.selectOption('#mode', 'variants');
    await page.selectOption('#condition', 'PN2');
    await page.locator('#run').click();
    await page.locator('#results').getByText('SYNTHETIC answer, not Qwen output.', {exact: true}).first().waitFor({state: 'attached'});
    await page.locator('#cancel').click();
    await page.waitForFunction(() => !document.getElementById('run').disabled &&
        document.getElementById('cancel').disabled);
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#export').click();
    const download = await downloadPromise;
    const destination = path.join(output, 'synthetic_browser_export.json');
    await download.saveAs(destination);
    const exported = JSON.parse(fs.readFileSync(destination, 'utf8'));
    assert.equal(exported.effective_status, 'cancelled');
    assert.equal(exported.result.generation_attempts, 0);
    assert.equal(exported.result.kind, 'SYNTHETIC_CONTROL_TEST_ONLY');
    checks.push('real browser start, cancellation and JSON download retain synthetic partial output');

    await page.locator('#project-tab').click();
    await page.locator('#project-content .finding-section').first().waitFor();
    assert.equal(await page.locator('#project-content > .finding-section').count(),14);
    assert.match(await page.locator('#project-content').innerText(),/pending/i);
    await page.locator('#project-security > summary').click();
    await page.locator('#project').screenshot({path:path.join(output,'project_desktop.png')});
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.screenshot({path:path.join(output,'project_mobile.png')});
    await page.setViewportSize({width:1440,height:1000});
    checks.push('all 13 project tasks, four security documents, report draft and mobile layout');
    await page.getByRole('button',{name:'TrustRAG live comparison',exact:true}).click();
    assert.equal(await page.locator('#mode').inputValue(),'trust');
    assert.equal(await page.locator('#case option').count(),12);
    assert.equal(await page.locator('#condition option').count(),3);
    assert.match(await page.locator('#explanation').innerText(),/not rerun/);
    await page.selectOption('#case','NanoMSMARCO:1028652');
    await page.selectOption('#condition','C');
    await page.locator('#reference').click();
    assert.equal(await page.locator('#trust-case').inputValue(),'NanoMSMARCO:1028652');
    assert.equal(await page.locator('#reference-panel').isVisible(),false);
    checks.push('TrustRAG uses 12 fixed cases and three conditions; recorded inspection selects TrustRAG rather than native verdict');
    await page.locator('#live-tab').click();
    await page.locator('#run').click();
    await page.locator('#results .policy h4').getByText('TrustRAG stage 1',{exact:true}).waitFor();
    await page.reload();
    await page.waitForFunction(()=>document.getElementById('mode').value==='trust' && document.getElementById('case').value==='NanoMSMARCO:1028652');
    await page.locator('#results .policy h4').getByText('TrustRAG stage 1',{exact:true}).waitFor();
    await page.screenshot({path:path.join(output,'trust_live_synthetic.png'),fullPage:true});
    await page.locator('#cancel').click();
    await page.waitForFunction(()=>!document.getElementById('run').disabled && document.getElementById('cancel').disabled);
    const trustDownload=page.waitForEvent('download');await page.locator('#export').click();
    const trustExport=await trustDownload;const trustPath=path.join(output,'synthetic_trust_export.json');await trustExport.saveAs(trustPath);
    const trustJson=JSON.parse(fs.readFileSync(trustPath,'utf8'));
    assert.equal(trustJson.state.mode,'trust');assert.equal(trustJson.state.condition,'C');
    assert.deepEqual(Object.keys(trustJson.result.conditions.C.answers),['U','T']);
    checks.push('TrustRAG synthetic start, reload recovery, U/T rendering, cancellation and export');
    await page.route('**/api/project',async route=>{const response=await route.fetch();const body=await response.json();body.tasks[0].source_text=hostile;await route.fulfill({response,json:body});});
    await page.route('**/api/findings',async route=>{
        const response=await route.fetch();const body=await response.json();
        body.trust[0].question=hostile;body.trust[0].contexts[0].answers.T.answer=hostile;
        body.trust[0].contexts[0].passages[0].text=hostile;
        await route.fulfill({response,json:body});
    });
    await page.reload();await page.locator('#trust-case option').first().waitFor({state:'attached'});
    await page.locator('#study-tab').click();
    assert.ok((await page.locator('#trust-view').textContent()).includes(hostile));
    assert.equal(await page.locator('#findings-content img, #findings-content script').count(),0);
    assert.equal(await page.evaluate(()=>window.securityProbe),undefined);
    checks.push('hostile TrustRAG question, answer and passage remain literal text');
    await page.locator('#project-tab').click();await page.locator('#project-content .source-text').first().waitFor({state:'attached'});
    assert.ok((await page.locator('#project-content').textContent()).includes(hostile));
    assert.equal(await page.locator('#project-content img,#project-content script').count(),0);assert.equal(await page.evaluate(()=>window.securityProbe),undefined);
    checks.push('project source records render hostile text literally');
    assert.deepEqual(pageErrors, []);
    checks.push('no browser JavaScript errors');
    fs.writeFileSync(path.join(output, 'BROWSER_RESULTS.json'), JSON.stringify({status: 'PASS',
        browser: browser.version(), checks, research_model_calls: 0,
        scope: 'Actual UI and HTTP server, synthetic worker and deliberately substituted XSS fixture'}, null, 2) + '\n');
}

run().catch(error => {
    fs.writeFileSync(path.join(output, 'BROWSER_RESULTS.json'), JSON.stringify({status: 'FAIL',
        error: String(error), checks, pageErrors}, null, 2) + '\n');
    console.error(error);
    process.exitCode = 1;
}).finally(async () => {
    if (browser) await browser.close();
    worker.kill('SIGINT');
    fs.writeFileSync(path.join(output, 'browser_fixture.log'), transcript);
});
