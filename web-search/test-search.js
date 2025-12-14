import axios from 'axios';
import * as cheerio from 'cheerio';

async function testSearch(query) {
  try {
    console.log(`Testing search for: "${query}"`);
    
    const response = await axios.get('https://www.google.com/search', {
      params: { q: query },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length}`);
    
    const $ = cheerio.load(response.data);
    const results = [];

    console.log('Looking for div.g elements...');
    const divGs = $('div.g');
    console.log(`Found ${divGs.length} div.g elements`);

    divGs.each((i, element) => {
      if (i >= 3) return false; // Limit to 3 results for testing

      const titleElement = $(element).find('h3');
      const linkElement = $(element).find('a');
      const snippetElement = $(element).find('.VwiC3b');

      console.log(`Element ${i}:`);
      console.log(`  Title elements: ${titleElement.length}`);
      console.log(`  Link elements: ${linkElement.length}`);
      console.log(`  Snippet elements: ${snippetElement.length}`);

      if (titleElement.length && linkElement.length) {
        const url = linkElement.attr('href');
        const title = titleElement.text();
        console.log(`  URL: ${url}`);
        console.log(`  Title: ${title}`);
        
        if (url && url.startsWith('http')) {
          results.push({
            title: title,
            url: url,
            description: snippetElement.text() || '',
          });
        }
      }
    });

    console.log(`\nFinal results: ${results.length}`);
    results.forEach((result, i) => {
      console.log(`${i + 1}. ${result.title}`);
      console.log(`   URL: ${result.url}`);
      console.log(`   Description: ${result.description.substring(0, 100)}...`);
      console.log('');
    });

    return results;
  } catch (error) {
    console.error('Search failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
    }
    return [];
  }
}

// Test with a simple query
testSearch('test search').then(() => {
  console.log('Test completed');
});