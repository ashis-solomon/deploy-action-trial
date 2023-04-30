const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('file_22.txt', 'utf8');

function parseHtml(html) {
  const $ = cheerio.load(html);
  const result = {
    company_name: '',
    job_title: '',
    location: '',
    avg_base_pay_est: '',
    time_since_posted: '',
    company_rating: '',
    job_description: '',
    company_link: ''
  };
  try {
    result.company_name = $('div.css-87uc0g.e1tk4kwz1').text();
  } catch { result.company_name = '#N/A'; }
  try {
    result.job_title = $('div.css-1vg6q84.e1tk4kwz4').text();
  } catch { result.job_title = '#N/A'; }
  try {
    result.location = $('div.css-56kyx5.e1tk4kwz5').text();
  } catch { result.location = '#N/A'; }
  try {
    result.avg_base_pay_est = $('div.css-1bluz6i.e2u4hf13').text();
  } catch { result.avg_base_pay_est = '#N/A'; }
  try {
    result.time_since_posted = $('div.d-flex.align-items-end.pl-std.css-1vfumx3').text();
  } catch { result.time_since_posted = '#N/A'; }
  try {
    result.company_rating = $('span.css-1m5m32b.e1tk4kwz2').text();
  } catch { result.company_rating = '#N/A'; }
  try {
    result.job_description = $('div.css-jrwyhi.e856ufb5').text();
  } catch { result.job_description = '#N/A'; }
  try {
    const a_tags = $('a.jobLink.css-1rd3saf.eigr9kq2');
    const company_link = a_tags.attr('href');
    result.company_link = company_link ? `https://glassdoor.co.in${company_link}` : '#N/A';
  } catch { result.company_link = '#N/A'; }
  return result;
}

console.log(parseHtml(html));
