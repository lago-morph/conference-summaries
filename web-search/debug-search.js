import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';

async function debugSearch(query) {
  try {
    console.log(`Debugging search for: "${query}"`);
    
    const response = await axios.get('https://www.google.com/search', {
      params: { q: query },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length}`);
    
    // Save the HTML to a file for inspection
    fs.writeFileSync('google-response.html', response.data);
    console.log('Saved response to google-response.html');
    
    const $ = cheerio.load(response.data);
    
    // Look for different possible selectors
    const selectors = [
      'div.g',
      '.g',
      '[data-ved]',
      'div[data-ved]',
      '.yuRUbf',
      '.tF2Cxc',
      'div.tF2Cxc',
      'h3',
      'a h3'
    ];
    
    selectors.forEach(selector => {
      const elements = $(selector);
      console.log(`Selector "${selector}": ${elements.length} elements`);
    });

    // Look for any links that might be search results
    const links = $('a[href^="http"]');
    console.log(`Total HTTP links: ${links.length}`);
    
    // Show first few links
    links.slice(0, 5).each((i, element) => {
      const href = $(element).attr('href');
      const text = $(element).text().trim();
      console.log(`Link ${i + 1}: ${text.substring(0, 50)}... -> ${href}`);
    });

  } catch (error) {
    console.error('Debug failed:', error.message);
  }
}

debugSearch('test search').then(() => {
  console.log('Debug completed');
});