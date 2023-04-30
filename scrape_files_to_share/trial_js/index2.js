const puppeteer = require('puppeteer');
const fs = require('fs');

async function generate_glassdoor_url(job_name, page_number) {
  const BASE_URL = "https://www.glassdoor.co.in/Job/india-";
  job_name = job_name.replace(" ", "-").toLowerCase();
  const srch = `IL.0,5_IN115_KO${'India-'.length},${job_name.length + 'India-'.length}`;
  const ip = `_IP${page_number}`;
  return `${BASE_URL}${job_name}-jobs-SRCH_${srch}${ip}.htm?includeNoSalaryJobs=true`;
}

async function fetch_jobs(url) {
  const html_content = [];

  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto(url);
  await page.waitForSelector("article#MainCol");

  // Close sign-up prompt
  try {
    await page.click("span.SVGInline.modal_closeIcon");
    await page.waitForTimeout(1000);
  } catch (e) {
    await page.waitForTimeout(1000);
  }

  let done = false;
  while (!done) {
    const job_cards = await page.$$("article#MainCol ul li[data-adv-type='GENERAL']");
    for (const card of job_cards) {
      await card.click();
      await page.waitForTimeout(1000);

      // Close sign-up prompt
      try {
        await page.click("span.SVGInline.modal_closeIcon");
        await page.waitForTimeout(1000);
      } catch (e) {
        await page.waitForTimeout(1000);
      }

      html_content.push(await page.content());
      if (html_content.length === job_cards.length) {
        done = true;
        break;
      }
    }
  }

  await browser.close();
  return html_content;
}

async function save_whole_page(html_contents) {
    for (let i = 0; i < html_contents.length; i++) {
      const filename = `file_${i+1}.txt`;
      const page_source = html_contents[i];
      await fs.promises.writeFile(filename, page_source);
      console.log(`File ${filename} saved.`);
    }
  }

async function main() {
  const URL = await generate_glassdoor_url("Data Analyst", 1);
  const html_content = await fetch_jobs(URL);
  await save_whole_page(html_content);
}

main();
