import { chromium } from 'playwright';

const url = process.argv[2] || 'https://priceoye.pk';
const shot = process.argv[3] || '/tmp/po/shot.png';

const browser = await chromium.launch({ args: ['--no-sandbox','--disable-dev-shm-usage'] });
const ctx = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  viewport: { width: 1366, height: 900 },
  locale: 'en-PK',
});
const page = await ctx.newPage();
const t0 = Date.now();
const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
console.log('STATUS:', resp && resp.status(), '| load ms:', Date.now() - t0);
console.log('URL:', page.url());
console.log('TITLE:', await page.title());
await page.waitForTimeout(3000);
const h1 = await page.locator('h1').first().innerText().catch(() => '(none)');
console.log('H1:', h1.replace(/\s+/g,' ').slice(0,200));
// product cards
const cards = await page.locator('a[href*="/mobiles/"], .productBox, .p-title').count().catch(()=>-1);
console.log('card-ish elements:', cards);
const text = await page.evaluate(() => document.body.innerText);
console.log('BODY TEXT LEN:', text.length);
console.log('--- first 800 chars of rendered text ---');
console.log(text.replace(/\n{2,}/g,'\n').slice(0,800));
await page.screenshot({ path: shot, fullPage: false });
console.log('screenshot ->', shot);
await browser.close();
